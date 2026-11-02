# -*- coding: utf-8 -*-

from {{ cookiecutter.package_name }}.cdk.stack_enum import StackEnum

import json

import aws_cdk as cdk

from {{ cookiecutter.package_name }}.config.api import Config
from {{ cookiecutter.package_name }}.one.api import One
from {{ cookiecutter.package_name }}.one.one_03_devops import build_lambda_source
from {{ cookiecutter.package_name }}.cdk.stack_ctx_enum import StackCtxEnum
from {{ cookiecutter.package_name }}.cdk.stack_ctx_enum import list_entry_names
from {{ cookiecutter.package_name }}.cdk.stacks.lbd_stack import read_package_version


def test_entries_match_stack_ctx_enum():
    """
    Layer 2 has exactly the entries of layer 1, in the same order.
    """
    assert list_entry_names(StackEnum) == list_entry_names(StackCtxEnum)


def test_synth(config: Config, tmp_path):
    """
    Every stack is synthesized under its stack name, the role wired by attribute
    access becomes a stack dependency, and every function gets the same
    environment variables and the layer of its config.
    """
    build_lambda_source()  # Code.from_asset needs the folder
    one = One()
    one.config = config
    se = StackEnum(app=cdk.App(outdir=str(tmp_path)), one=one)
    se.synth()
    names = sorted(p.name for p in tmp_path.glob("*.template.json"))
    assert names == [
        "my-project-dev-infra.template.json",
        "my-project-dev-lbd.template.json",
    ]
    assert se.infra in se.lbd.dependencies
    assert se.get("infra") is se.infra
    assert se.get_all() == [se.infra, se.lbd]

    template = json.loads((tmp_path / "my-project-dev-lbd.template.json").read_text())
    functions = {
        res["Properties"]["FunctionName"]: res["Properties"]
        for res in template["Resources"].values()
        # skip the handler of the S3 notification custom resource, which has no name
        if res["Type"] == "AWS::Lambda::Function"
        and "FunctionName" in res["Properties"]
    }
    assert sorted(functions) == ["my-project-dev-hello", "my-project-dev-s3sync"]
    for props in functions.values():
        assert props["Layers"] == [config.lambda_layer_version_arn]
        assert props["Environment"]["Variables"] == {
            "ENV_NAME": "dev",
            "CONFIG_SSM_PARAM_NAME": "/my-project-dev/config",
            "CONFIG_HASH": config.config_hash,
            "PACKAGE_VERSION": read_package_version(),
        }


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.cdk.stack_enum",
        preview=False,
    )
