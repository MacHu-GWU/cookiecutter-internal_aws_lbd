# -*- coding: utf-8 -*-

import pytest

import moto
import boto3

from {{ cookiecutter.package_name }}.config.api import CONFIG_SSM_PARAM_NAME_VAR
from {{ cookiecutter.package_name }}.config.api import Config


def test_load_from_local_config_file():
    config = Config.load_from_local_config_file(env_name="prd")
    assert config.env_name == "prd"
    assert config.project_name == "{{ cookiecutter.package_name }}"
    # from the fake -secret files of conftest.py
    assert config.aws_account_id == "111122223333"
    assert config.devops_aws_account_id == "999988887777"
    assert set(config.lambda_functions) == {"hello", "s3sync"}


def test_load_devops():
    with pytest.raises(ValueError):
        Config.load_from_local_config_file(env_name="devops")


def test_load_unsupported_runtime():
    with pytest.raises(NotImplementedError):
        Config.load(env_name="dev", runtime_name="ci")


def test_config_fits_in_standard_ssm_parameter():
    """
    A standard SSM parameter holds 4 KB. A bigger config still deploys (as an
    advanced parameter, which costs money), so this is a warning sign, not a limit.
    """
    for env_name in ["dev", "tst", "prd"]:
        config = Config.load_from_local_config_file(env_name=env_name)
        assert len(config.model_dump_json()) < 3000


def test_config_hash(config: Config):
    assert len(config.config_hash) == 64
    assert (
        config.config_hash
        == Config.model_validate_json(config.model_dump_json()).config_hash
    )
    changed = config.model_copy(update={"lambda_layer_version": 8})
    assert changed.config_hash != config.config_hash


def test_load_from_ssm(config: Config, monkeypatch):
    """
    Inside Lambda the config is read from SSM, and is the same as the local one.
    """
    with moto.mock_aws():
        ssm_client = boto3.client("ssm", region_name="us-east-1")
        with pytest.raises(ValueError):
            Config.load_from_ssm(
                ssm_client=ssm_client, name=config.ssm_param_name_config
            )

        ssm_client.put_parameter(
            Name=config.ssm_param_name_config,
            Value=config.model_dump_json(),
            Type="SecureString",
        )
        monkeypatch.setenv(CONFIG_SSM_PARAM_NAME_VAR, config.ssm_param_name_config)
        loaded = Config.load(
            env_name="dev",
            runtime_name="aws_lambda",
            ssm_client=ssm_client,
        )
        assert loaded == config


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.config.config_00_main",
        preview=False,
    )
