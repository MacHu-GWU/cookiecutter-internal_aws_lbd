# -*- coding: utf-8 -*-

import pytest

import os
import sys
import subprocess
from pathlib import Path
from pathlib import PurePath

import moto
import boto3
import aws_cdk as cdk

from {{ cookiecutter.package_name }}.paths import path_enum
from {{ cookiecutter.package_name }}.constants import LAMBDA_SOURCE_INCLUDE
from {{ cookiecutter.package_name }}.config.api import Config
from {{ cookiecutter.package_name }}.one.api import One
from {{ cookiecutter.package_name }}.one.one_03_devops import load_all_env_configs
from {{ cookiecutter.package_name }}.one.one_03_devops import check_layer_binaries
from {{ cookiecutter.package_name }}.one.one_03_devops import (
    get_private_index_credentials,
)
from {{ cookiecutter.package_name }}.one.one_03_devops import build_lambda_source

PACKAGE_NAME = path_enum.dir_package.name


def test_load_all_env_configs():
    configs = load_all_env_configs()
    assert list(configs) == ["dev", "tst", "prd"]
    assert configs["prd"].env_name == "prd"


def test_check_layer_binaries(tmp_path: Path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "a.so").write_bytes(b"\x7fELF and more")
    check_layer_binaries(tmp_path)

    (tmp_path / "pkg" / "b.so").write_bytes(b"\xcf\xfa\xed\xfe")  # Mach-O
    (tmp_path / "pkg" / "c.dylib").write_bytes(b"")
    with pytest.raises(ValueError) as e:
        check_layer_binaries(tmp_path)
    assert "b.so" in str(e.value)
    assert "c.dylib" in str(e.value)


def test_get_private_index_credentials(tmp_path: Path, monkeypatch):
    path = tmp_path / "pyproject.toml"
    path.write_text(
        '[[tool.uv.index]]\nname = "my-index"\nurl = "https://example.com/simple/"\n'
    )
    monkeypatch.delenv("UV_INDEX_MY_INDEX_USERNAME", raising=False)
    monkeypatch.delenv("UV_INDEX_MY_INDEX_PASSWORD", raising=False)
    assert get_private_index_credentials(path) is None

    monkeypatch.setenv("UV_INDEX_MY_INDEX_PASSWORD", "token")
    credentials = get_private_index_credentials(path)
    assert credentials.index_name == "my-index"
    assert credentials.index_url == "https://example.com/simple/"
    assert credentials.username == "aws"
    assert credentials.password == "token"

    path.write_text("[project]\n")
    assert get_private_index_credentials(path) is None


def test_make_layer_builder(config: Config):
    one = One()
    one.config = config
    builder = one._make_layer_builder()
    assert type(builder).__name__ == "UvLambdaLayerLocalBuilder"
    args = builder.uv_sync_options.to_args()
    assert "--python-platform" in args
    assert "x86_64-manylinux_2_34" in args
    assert "--no-build" in args

    one.config = config.model_copy(update={"lambda_layer_build_in_container": True})
    builder = one._make_layer_builder()
    assert type(builder).__name__ == "UvLambdaLayerContainerBuilder"
    assert builder.is_arm is False


def test_print_lambda_layer_versions(config: Config, capsys):
    """
    The pins come from the committed config files, which change with every
    layer deploy, so the expected lines are built from them.
    """
    pinned = load_all_env_configs()["dev"].lambda_layer_version
    one = One()
    one.config = config

    one.print_lambda_layer_versions(latest_version=pinned + 1)
    out = capsys.readouterr().out
    assert f"arn:aws:lambda:us-east-1:999988887777:layer:my_project:{pinned + 1}" in out
    assert f"#/layers/my_project/versions/{pinned + 1}" in out
    assert "my-devops-artifacts?prefix=projects/my_project/lambda/" in out
    assert f"set lambda_layer_version: {pinned + 1} in config/config-dev.json5" in out

    one.print_lambda_layer_versions(latest_version=pinned)
    out = capsys.readouterr().out
    assert f"dev: version {pinned}, up to date" in out


def test_deploy_and_delete_config(config: Config, capsys):
    """
    The parameter is written only when the config changed, so an unchanged
    deploy adds no version; each call prints its status and the console URL.
    """
    with moto.mock_aws():
        one = One()
        one.config = config
        one.ssm_client = boto3.client("ssm", region_name="us-east-1")

        assert one.deploy_config() == "created"
        assert one.deploy_config() == "unchanged"
        out = capsys.readouterr().out
        assert "Config of 'dev' created (version 1, " in out
        assert "Config of 'dev' unchanged (version 1, nothing written, " in out
        assert config.ssm_param_url_config in out

        one.config = config.model_copy(update={"lambda_layer_version": 8})
        assert one.deploy_config() == "updated"
        assert "updated (version 1 -> 2, " in capsys.readouterr().out
        response = one.ssm_client.get_parameter(
            Name=config.ssm_param_name_config,
            WithDecryption=True,
        )
        assert response["Parameter"]["Type"] == "SecureString"
        assert (
            Config.model_validate_json(
                response["Parameter"]["Value"]
            ).lambda_layer_version
            == 8
        )

        assert one.delete_config() is True
        assert one.delete_config() is False
        out = capsys.readouterr().out
        assert "Config of 'dev' deleted: " in out
        assert "Config of 'dev' not found, nothing deleted: " in out


def _relpaths(dir_build: Path) -> list[PurePath]:
    return sorted(
        PurePath(path.relative_to(dir_build).as_posix())
        for path in dir_build.rglob("*")
        if path.is_file()
    )


class TestBuildLambdaSource:
    """
    The folder deployed with ``Code.from_asset``. Its CDK asset hash must only
    depend on the source files, so an unchanged code base is not redeployed, from
    any machine.
    """

    def test_hash_is_stable(self, tmp_path: Path):
        dir_1 = tmp_path / "1" / "build"
        dir_2 = tmp_path / "2" / "build"
        build_lambda_source(dir_build=dir_1)
        # a new mtime must not change the hash
        os.utime(path_enum.dir_package / "lambda_function.py")
        build_lambda_source(dir_build=dir_2)
        assert _relpaths(dir_1) == _relpaths(dir_2)
        assert cdk.FileSystem.fingerprint(str(dir_1)) == cdk.FileSystem.fingerprint(
            str(dir_2)
        )

    def test_content(self, tmp_path: Path):
        dir_build = tmp_path / "build"
        (dir_build / "stale").mkdir(parents=True)
        (dir_build / "stale" / "old.py").write_text("")
        build_lambda_source(dir_build=dir_build)
        relpaths = _relpaths(dir_build)
        assert PurePath("stale/old.py") not in relpaths
        assert PurePath(f"{PACKAGE_NAME}/lambda_function.py") in relpaths
        for relpath in relpaths:
            assert relpath.parts[0] == PACKAGE_NAME
            # every file is in the whitelist
            assert any(relpath.match(pattern) for pattern in LAMBDA_SOURCE_INCLUDE)
            # nothing from a dev-only folder, at any depth
            assert relpath.parts[1] not in ("tests", "docs", "vendor", "cdk")
            assert "__pycache__" not in relpath.parts

    def test_lambda_function_imports(self, tmp_path: Path):
        """
        Every handler imports from the built folder alone (the dependencies come
        from this venv, as from the layer in Lambda), so no deployed module needs
        a file that was left out.
        """
        dir_build = tmp_path / "build"
        build_lambda_source(dir_build=dir_build)
        code = (
            f"import {PACKAGE_NAME}.lambda_function, sys; "
            f"assert {PACKAGE_NAME}.lambda_function.__file__.startswith(sys.argv[1])"
        )
        subprocess.run(
            [sys.executable, "-c", code, str(dir_build)],
            cwd=tmp_path,
            env={
                # without pytest-cov's variables, so it does not measure the copy
                **{k: v for k, v in os.environ.items() if not k.startswith("COV_")},
                "PYTHONPATH": str(dir_build),
                "PYTHONSAFEPATH": "1",
            },
            check=True,
        )


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.one.one_03_devops",
        preview=False,
    )
