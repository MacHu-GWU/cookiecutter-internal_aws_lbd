# -*- coding: utf-8 -*-

import pytest

from {{ cookiecutter.package_name }}.env import EnvNameEnum
from {{ cookiecutter.package_name }}.env import Env


def test_get_workloads():
    assert [member.value for member in EnvNameEnum.get_workloads()] == [
        "dev",
        "tst",
        "prd",
    ]


def test_get_current_env_name(monkeypatch):
    env = Env()
    assert env.current_env_name == "dev"
    monkeypatch.setenv("ENV_NAME", "")
    assert env.get_current_env_name().value == "dev"
    monkeypatch.setenv("ENV_NAME", "prd")
    assert env.get_current_env_name().value == "prd"
    monkeypatch.setenv("ENV_NAME", "invalid")
    with pytest.raises(ValueError):
        env.get_current_env_name()


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.env",
        preview=False,
    )
