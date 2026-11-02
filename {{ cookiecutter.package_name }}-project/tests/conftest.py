# -*- coding: utf-8 -*-

"""
Root-level pytest configuration: the fixtures of the package's test utilities
(``disable_logger``), plus the ones that isolate every test from this machine.
"""

import pytest

import shutil

from {{ cookiecutter.package_name }}.paths import path_enum
from {{ cookiecutter.package_name }}.env import EnvNameEnum
from {{ cookiecutter.package_name }}.config.api import LambdaFunction
from {{ cookiecutter.package_name }}.config.api import Config
from {{ cookiecutter.package_name }}.tests.conftest import *  # noqa: F401,F403


@pytest.fixture(autouse=True)
def local_runtime(monkeypatch):
    """
    Run every test as the local runtime, even on a CI runner (which sets ``CI``),
    and in the ``dev`` environment, whatever ``ENV_NAME`` the shell or ``.env`` sets.
    """
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("AWS_LAMBDA_FUNCTION_NAME", raising=False)
    monkeypatch.setenv("ENV_NAME", "dev")


@pytest.fixture(scope="session", autouse=True)
def fake_dir_config(tmp_path_factory):
    """
    Point ``path_enum.dir_config`` at a copy of the committed config files plus
    fake ``-secret`` files, so tests never read the real, git-ignored secrets and
    behave the same on a CI runner that has none.
    """
    dir_config = tmp_path_factory.mktemp("config")
    for path in path_enum.dir_config.glob("config-*.json5"):
        if not path.name.endswith("-secret.json5"):
            shutil.copy(path, dir_config / path.name)
    (dir_config / "config-shared-secret.json5").write_text(
        '{devops_aws_account_id: "999988887777"}'
    )
    for env_name in EnvNameEnum.get_workloads():
        path = dir_config / f"config-{env_name.value}-secret.json5"
        path.write_text('{aws_account_id: "111122223333"}')
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(path_enum, "dir_config", dir_config)
        yield dir_config


@pytest.fixture
def config() -> Config:
    """
    A config with fixed sample values, independent of the files in ``config/``.
    """
    return Config(
        project_name="my_project",
        env_name="dev",
        aws_account_id="111122223333",
        aws_region="us-east-1",
        devops_aws_account_id="999988887777",
        devops_s3_bucket_artifacts="my-devops-artifacts",
        s3_bucket_data="my-data",
        lambda_python_version="3.12",
        lambda_layer_version=7,
        lambda_functions={
            "hello": LambdaFunction(handler="hello_handler", timeout=3, memory=128),
            "s3sync": LambdaFunction(handler="s3sync_handler", timeout=10, memory=256),
        },
    )
