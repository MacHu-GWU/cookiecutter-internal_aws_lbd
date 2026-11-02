# -*- coding: utf-8 -*-

from {{ cookiecutter.package_name }}.config.api import Config
from {{ cookiecutter.package_name }}.one.api import One
from {{ cookiecutter.package_name }}.config import config_00_main


def test_config_local():
    """
    Locally the config is loaded once, from the files.
    """
    one = One()
    assert one.config.env_name == "dev"
    assert one.config is one.config


def test_config_assigned(config: Config):
    one = One()
    one.config = config
    assert one.config is config


def test_config_aws_lambda(config: Config, monkeypatch):
    """
    Inside Lambda the config is loaded once, from SSM, with ``one.ssm_client``.
    """
    monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "my-func")
    monkeypatch.setenv(config_00_main.CONFIG_SSM_PARAM_NAME_VAR, "/my/config")
    calls = []

    def load_from_ssm(ssm_client, name: str):
        calls.append((ssm_client, name))
        return config

    monkeypatch.setattr(Config, "load_from_ssm", load_from_ssm)
    one = One()
    one.ssm_client = "my-ssm-client"
    assert one.config is config
    assert one.config is config
    assert calls == [("my-ssm-client", "/my/config")]


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.one.one_01_config",
        preview=False,
    )
