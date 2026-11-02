# -*- coding: utf-8 -*-

from {{ cookiecutter.package_name }}.config.api import Config


def test_names(config: Config):
    # fmt: off
    assert config.project_name_snake == "my_project"
    assert config.project_name_slug == "my-project"
    assert config.prefix_name_slug == "my-project-dev"

    assert config.cft_stack_name_infra == "my-project-dev-infra"
    assert config.cft_stack_name_lbd == "my-project-dev-lbd"
    assert "filteringText=my-project-dev-infra&" in config.cft_stack_url_infra
    assert "filteringText=my-project-dev-lbd&" in config.cft_stack_url_lbd
    assert config.cft_export_name_lambda_role_arn == "my-project-dev-lambda-role-arn"

    assert config.iam_role_name_lambda == "my-project-dev-us-east-1-lambda"
    assert config.iam_role_arn_lambda == "arn:aws:iam::111122223333:role/my-project-dev-us-east-1-lambda"
    assert config.iam_role_url_lambda.endswith("#/roles/details/my-project-dev-us-east-1-lambda")

    assert config.ssm_param_name_config == "/my-project-dev/config"
    assert config.ssm_param_arn_config == "arn:aws:ssm:us-east-1:111122223333:parameter/my-project-dev/config"
    assert "/parameters/my-project-dev/config/description" in config.ssm_param_url_config

    assert config.get_lambda_function_name("hello") == "my-project-dev-hello"
    assert "#/functions/my-project-dev-hello?" in config.get_lambda_function_url("hello")
    assert config.get_lambda_log_group_name("hello") == "/aws/lambda/my-project-dev-hello"
    assert config.get_lambda_log_group_url("hello").endswith("#logsV2:log-groups/log-group/$252Faws$252Flambda$252Fmy-project-dev-hello")
    assert config.lambda_layer_name == "my_project"
    assert config.lambda_layer_version_arn == "arn:aws:lambda:us-east-1:999988887777:layer:my_project:7"
    assert config.lambda_layer_url.endswith("?region=us-east-1#/layers/my_project")
    assert config.get_lambda_layer_version_url(7).endswith("#/layers/my_project/versions/7")

    assert config.s3dir_lambda.uri == "s3://my-devops-artifacts/projects/my_project/lambda/"
    assert "my-devops-artifacts?prefix=projects/my_project/lambda/" in config.s3dir_lambda_url
    assert config.s3_bucket_data_properties_url.endswith("/s3/buckets/my-data?region=us-east-1&tab=properties")
    assert config.s3dir_data.uri == "s3://my-data/projects/my_project/envs/dev/"
    assert config.s3dir_source.uri == "s3://my-data/projects/my_project/envs/dev/source/"
    assert config.s3dir_target.uri == "s3://my-data/projects/my_project/envs/dev/target/"
    assert "my-data?prefix=projects/my_project/envs/dev/" in config.s3dir_data_url
    assert "my-data?prefix=projects/my_project/envs/dev/source/" in config.s3dir_source_url
    assert "my-data?prefix=projects/my_project/envs/dev/target/" in config.s3dir_target_url
    # fmt: on


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.config.config_01_name",
        preview=False,
    )
