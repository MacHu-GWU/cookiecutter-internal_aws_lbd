# -*- coding: utf-8 -*-

"""
Synth smoke test of the lbd stack: create it through ``StackEnum``, the way
``cdk/cdk_app.py`` does, and synthesize it. Passing means the constructs, names,
and cross-stack references are wired up; what each resource looks like is not
checked here (the names are checked in ``tests/config/test_config_config_01_name.py``).
"""

from {{ cookiecutter.package_name }}.cdk.stacks.lbd_stack import LbdStack

import aws_cdk as cdk

from {{ cookiecutter.package_name }}.config.api import Config
from {{ cookiecutter.package_name }}.one.api import One
from {{ cookiecutter.package_name }}.one.one_03_devops import build_lambda_source
from {{ cookiecutter.package_name }}.cdk.stack_enum import StackEnum


def test_synth(config: Config):
    build_lambda_source()  # Code.from_asset needs the folder
    one = One()
    one.config = config
    stack_enum = StackEnum(app=cdk.App(), one=one)
    assert isinstance(stack_enum.lbd, LbdStack)
    stack_enum.app.synth()


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.cdk.stacks.lbd_stack",
        preview=False,
    )
