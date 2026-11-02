# -*- coding: utf-8 -*-

"""
Every AWS resource name of the project, with its console URL, ARN, and S3
location. Building one makes no AWS call.
"""

from __future__ import annotations

import typing as T
from functools import cached_property

from s3pathlib.api import S3Path

if T.TYPE_CHECKING:  # pragma: no cover
    from .config_00_main import Config


class ConfigNameMixin:
    """
    Resource names, console URLs, ARNs and S3 locations derived from the config values.
    """

    # --------------------------------------------------------------------------
    # Prefixes
    # --------------------------------------------------------------------------
    @cached_property
    def project_name_snake(self: Config) -> str:
        """
        Project name in snake_case, such as ``my_project``.
        """
        return self.project_name.replace("-", "_")

    @cached_property
    def project_name_slug(self: Config) -> str:
        """
        Project name in slug-case, such as ``my-project``.
        """
        return self.project_name_snake.replace("_", "-")

    @cached_property
    def prefix_name_slug(self: Config) -> str:
        """
        Prefix of every resource name of this environment, such as ``my-project-dev``.
        """
        return f"{self.project_name_slug}-{self.env_name}"

    # --------------------------------------------------------------------------
    # CloudFormation stacks
    # --------------------------------------------------------------------------
    def get_cft_stack_name(self: Config, short_name: str) -> str:
        """
        The name of a stack, ``<prefix_name_slug>-<short_name>``; also its construct ID.
        """
        return f"{self.prefix_name_slug}-{short_name}"

    def get_cft_stack_url(self: Config, stack_name: str) -> str:
        """
        The CloudFormation console URL of the stack, found by its name, so it needs
        no stack ARN (which ends in an ID assigned at creation) and works before the
        stack exists.
        """
        return (
            f"https://{self.aws_region}.console.aws.amazon.com/cloudformation/home"
            f"?region={self.aws_region}#/stacks/stackinfo?filteringText={stack_name}"
            f"&filteringStatus=active&viewNested=true"
        )

    @cached_property
    def cft_stack_name_infra(self: Config) -> str:
        """
        Name of the infra stack, such as ``my-project-dev-infra``.
        """
        return self.get_cft_stack_name("infra")

    @cached_property
    def cft_stack_url_infra(self: Config) -> str:
        """
        Console URL of :attr:`cft_stack_name_infra`.
        """
        return self.get_cft_stack_url(self.cft_stack_name_infra)

    @cached_property
    def cft_stack_name_lbd(self: Config) -> str:
        """
        Name of the Lambda stack, such as ``my-project-dev-lbd``.
        """
        return self.get_cft_stack_name("lbd")

    @cached_property
    def cft_stack_url_lbd(self: Config) -> str:
        """
        Console URL of :attr:`cft_stack_name_lbd`.
        """
        return self.get_cft_stack_url(self.cft_stack_name_lbd)

    # --------------------------------------------------------------------------
    # CloudFormation exports, read by other projects through *_stack_exports.py
    # --------------------------------------------------------------------------
    @cached_property
    def cft_export_name_lambda_role_arn(self: Config) -> str:
        """
        Export name of the Lambda execution role ARN, such as ``my-project-dev-lambda-role-arn``.
        """
        return f"{self.prefix_name_slug}-lambda-role-arn"

    # --------------------------------------------------------------------------
    # IAM roles
    # --------------------------------------------------------------------------
    @cached_property
    def iam_role_name_lambda(self: Config) -> str:
        """
        Name of the Lambda execution role, such as ``my-project-dev-us-east-1-lambda``.
        IAM is global, so the name includes the region.
        """
        return f"{self.prefix_name_slug}-{self.aws_region}-lambda"

    @cached_property
    def iam_role_arn_lambda(self: Config) -> str:
        """
        ARN of :attr:`iam_role_name_lambda`.
        """
        return f"arn:aws:iam::{self.aws_account_id}:role/{self.iam_role_name_lambda}"

    @cached_property
    def iam_role_url_lambda(self: Config) -> str:
        """
        Console URL of :attr:`iam_role_name_lambda`.
        """
        return (
            f"https://{self.aws_region}.console.aws.amazon.com/iam/home"
            f"?region={self.aws_region}#/roles/details/{self.iam_role_name_lambda}"
        )

    # --------------------------------------------------------------------------
    # SSM parameters
    # --------------------------------------------------------------------------
    def get_ssm_param_url(self: Config, name: str) -> str:
        """
        The console URL of an SSM parameter, given its name (which starts with ``/``).
        """
        return (
            f"https://{self.aws_region}.console.aws.amazon.com/systems-manager"
            f"/parameters{name}/description?region={self.aws_region}&tab=Table"
        )

    def get_ssm_param_arn(self: Config, name: str) -> str:
        """
        The ARN of an SSM parameter, given its name (which starts with ``/``).
        """
        return f"arn:aws:ssm:{self.aws_region}:{self.aws_account_id}:parameter{name}"

    @cached_property
    def ssm_param_name_config(self: Config) -> str:
        """
        Name of the parameter that holds the whole config of this environment as
        JSON, such as ``/my-project-dev/config``.
        """
        return f"/{self.prefix_name_slug}/config"

    @cached_property
    def ssm_param_url_config(self: Config) -> str:
        """
        Console URL of :attr:`ssm_param_name_config`.
        """
        return self.get_ssm_param_url(self.ssm_param_name_config)

    @cached_property
    def ssm_param_arn_config(self: Config) -> str:
        """
        ARN of :attr:`ssm_param_name_config`.
        """
        return self.get_ssm_param_arn(self.ssm_param_name_config)

    # --------------------------------------------------------------------------
    # Lambda functions and layer
    # --------------------------------------------------------------------------
    def get_lambda_function_name(self: Config, short_name: str) -> str:
        """
        The name of a Lambda function, such as ``my-project-dev-hello``.

        :param short_name: a key of :attr:`~{{ cookiecutter.package_name }}.config.config_00_main.Config.lambda_functions`.
        """
        return f"{self.prefix_name_slug}-{short_name}"

    def get_lambda_function_url(self: Config, short_name: str) -> str:
        """
        The console URL of a Lambda function.
        """
        name = self.get_lambda_function_name(short_name)
        return (
            f"https://{self.aws_region}.console.aws.amazon.com/lambda/home"
            f"?region={self.aws_region}#/functions/{name}?tab=code"
        )

    def get_lambda_log_group_name(self: Config, short_name: str) -> str:
        """
        The CloudWatch log group of a Lambda function, such as
        ``/aws/lambda/my-project-dev-hello``. Lambda creates it on the first run.
        """
        return f"/aws/lambda/{self.get_lambda_function_name(short_name)}"

    def get_lambda_log_group_url(self: Config, short_name: str) -> str:
        """
        The console URL of :meth:`get_lambda_log_group_name`.
        """
        # the console escapes "/" in the log group name as "$252F"
        name = self.get_lambda_log_group_name(short_name).replace("/", "$252F")
        return (
            f"https://{self.aws_region}.console.aws.amazon.com/cloudwatch/home"
            f"?region={self.aws_region}#logsV2:log-groups/log-group/{name}"
        )

    @cached_property
    def lambda_layer_name(self: Config) -> str:
        """
        Name of the Lambda layer in the DEVOPS account, such as ``my_project``;
        every environment uses it.
        """
        return self.project_name_snake

    def get_lambda_layer_version_arn(self: Config, version: int) -> str:
        """
        The ARN of a version of :attr:`lambda_layer_name` in the DEVOPS account.
        """
        return (
            f"arn:aws:lambda:{self.aws_region}:{self.devops_aws_account_id}"
            f":layer:{self.lambda_layer_name}:{version}"
        )

    @cached_property
    def lambda_layer_version_arn(self: Config) -> str:
        """
        The ARN of the layer version this environment uses, :attr:`lambda_layer_version`.
        """
        return self.get_lambda_layer_version_arn(self.lambda_layer_version)

    @cached_property
    def lambda_layer_url(self: Config) -> str:
        """
        Console URL of :attr:`lambda_layer_name`, listing every version.
        Open it signed in to the DEVOPS account.
        """
        return (
            f"https://{self.aws_region}.console.aws.amazon.com/lambda/home"
            f"?region={self.aws_region}#/layers/{self.lambda_layer_name}"
        )

    def get_lambda_layer_version_url(self: Config, version: int) -> str:
        """
        Console URL of one version of :attr:`lambda_layer_name`, with its
        permissions. Open it signed in to the DEVOPS account.
        """
        return f"{self.lambda_layer_url}/versions/{version}"

    # --------------------------------------------------------------------------
    # S3 locations
    # --------------------------------------------------------------------------
    @cached_property
    def s3dir_lambda(self: Config) -> S3Path:
        """
        Where the Lambda layer artifacts go, in the DEVOPS account, such as
        ``s3://<devops-artifacts>/projects/my_project/lambda/``. The layout below
        it is the one of ``aws_lbd_art_builder``.
        """
        return S3Path(
            f"s3://{self.devops_s3_bucket_artifacts}"
            f"/projects/{self.project_name_snake}/lambda/"
        )

    @cached_property
    def s3dir_lambda_url(self: Config) -> str:
        """
        S3 console URL of :attr:`s3dir_lambda`. Open it signed in to the DEVOPS account.
        """
        return self.s3dir_lambda.console_url

    @cached_property
    def s3_bucket_data_properties_url(self: Config) -> str:
        """
        S3 console URL of the properties of :attr:`s3_bucket_data`, where its
        event notifications are.
        """
        return (
            f"https://{self.aws_region}.console.aws.amazon.com/s3/buckets"
            f"/{self.s3_bucket_data}?region={self.aws_region}&tab=properties"
        )

    @cached_property
    def s3dir_data(self: Config) -> S3Path:
        """
        The data folder of this environment, such as
        ``s3://<data-bucket>/projects/my_project/envs/dev/``.
        """
        return S3Path(
            f"s3://{self.s3_bucket_data}"
            f"/projects/{self.project_name_snake}/envs/{self.env_name}/"
        )

    @cached_property
    def s3dir_data_url(self: Config) -> str:
        """
        S3 console URL of :attr:`s3dir_data`.
        """
        return self.s3dir_data.console_url

    @cached_property
    def s3dir_source(self: Config) -> S3Path:
        """
        Where the s3sync function is triggered: every new object under it is copied
        to :attr:`s3dir_target`.
        """
        return self.s3dir_data.joinpath("source/")

    @cached_property
    def s3dir_source_url(self: Config) -> str:
        """
        S3 console URL of :attr:`s3dir_source`.
        """
        return self.s3dir_source.console_url

    @cached_property
    def s3dir_target(self: Config) -> S3Path:
        """
        Where the s3sync function copies objects to.
        """
        return self.s3dir_data.joinpath("target/")

    @cached_property
    def s3dir_target_url(self: Config) -> str:
        """
        S3 console URL of :attr:`s3dir_target`.
        """
        return self.s3dir_target.console_url
