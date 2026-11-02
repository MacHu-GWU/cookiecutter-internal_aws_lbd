# -*- coding: utf-8 -*-

"""
The lbd stack: the Lambda functions, with their code
(``build/lambda/source/build/``, from ``mise run lambda-source-build``), layer,
environment variables, and the S3 trigger of s3sync.
"""

from __future__ import annotations

import tomllib

import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_notifications as s3_notifications
from aws_cdk import aws_lambda as lambda_
from constructs import Construct

from ...paths import PACKAGE_NAME
from ...paths import path_enum
from ...env import ENV_NAME_VAR
from ...constants import IS_LAMBDA_X86
from ...config.api import CONFIG_SSM_PARAM_NAME_VAR
from ...config.api import Config

CONFIG_HASH_VAR = "CONFIG_HASH"
"""
The Lambda environment variable that holds ``config.config_hash``. No code
reads it; it makes a new config change the template, so the functions update.
"""

PACKAGE_VERSION_VAR = "PACKAGE_VERSION"
"""
The Lambda environment variable that holds ``[project].version`` of ``pyproject.toml``.
"""


def read_package_version() -> str:
    """
    ``[project].version`` of ``pyproject.toml``, read at synth time. The deployed
    source has no package metadata, so Lambda reads it from
    :data:`PACKAGE_VERSION_VAR` instead.
    """
    data = tomllib.loads(path_enum.path_pyproject_toml.read_text(encoding="utf-8"))
    return data["project"]["version"]


def to_camel(name: str) -> str:
    """
    ``s3sync`` -> ``S3sync``, ``my_func`` -> ``MyFunc``, for construct IDs.
    """
    return "".join(part.capitalize() for part in name.replace("-", "_").split("_"))


class LbdStack(cdk.Stack):
    """
    Takes the standard arguments of :meth:`cdk_mate.stack_ctx.StackCtx.to_stack_kwargs`,
    the config of its environment, and the execution role from the infra stack.
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        stack_name: str,
        env: cdk.Environment,
        config: Config,
        iam_role_for_lambda: iam.IRole,
    ) -> None:
        super().__init__(
            scope=scope,
            id=id,
            stack_name=stack_name,
            env=env,
        )
        self.config = config
        self.iam_role_for_lambda = iam_role_for_lambda
        self.s01_create_lambda_functions()
        self.s02_configure_s3_event_source()
        self.s03_create_outputs()

    def s01_create_lambda_functions(self) -> None:
        """
        One function per entry of ``config.lambda_functions``, all sharing the
        same code, layer, role, and environment variables.
        """
        config = self.config
        self.layer = lambda_.LayerVersion.from_layer_version_arn(
            self,
            "LambdaLayer",
            layer_version_arn=config.lambda_layer_version_arn,
        )
        code = lambda_.Code.from_asset(str(path_enum.dir_build_lambda_source_build))
        runtime = lambda_.Runtime(
            f"python{config.lambda_python_version}",
            family=lambda_.RuntimeFamily.PYTHON,
        )
        architecture = (
            lambda_.Architecture.X86_64
            if IS_LAMBDA_X86
            else lambda_.Architecture.ARM_64
        )
        environment = {
            ENV_NAME_VAR: config.env_name,
            CONFIG_SSM_PARAM_NAME_VAR: config.ssm_param_name_config,
            CONFIG_HASH_VAR: config.config_hash,
            PACKAGE_VERSION_VAR: read_package_version(),
        }
        self.lambda_functions: dict[str, lambda_.Function] = {}
        for short_name, lambda_function in config.lambda_functions.items():
            self.lambda_functions[short_name] = lambda_.Function(
                self,
                f"LambdaFunction{to_camel(short_name)}",
                function_name=config.get_lambda_function_name(short_name),
                code=code,
                handler=f"{PACKAGE_NAME}.lambda_function.{lambda_function.handler}",
                runtime=runtime,
                architecture=architecture,
                memory_size=lambda_function.memory,
                timeout=cdk.Duration.seconds(lambda_function.timeout),
                layers=[self.layer],
                environment=environment,
                role=self.iam_role_for_lambda,
                reserved_concurrent_executions=lambda_function.reserved_concurrency,
            )

    def s02_configure_s3_event_source(self) -> None:
        """
        Trigger the s3sync function on every new object under ``s3dir_source``.

        The data bucket is shared and not owned by any stack, so this goes
        through ``add_event_notification`` on the imported bucket: a CDK custom
        resource adds this one notification and keeps the ones of other projects.
        ``S3EventSource`` only works with a bucket defined in the same stack
        (https://github.com/aws/aws-cdk/issues/23940).
        """
        if "s3sync" not in self.lambda_functions:  # pragma: no cover
            return
        bucket = s3.Bucket.from_bucket_name(
            self,
            "DataBucket",
            bucket_name=self.config.s3dir_data.bucket,
        )
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notifications.LambdaDestination(self.lambda_functions["s3sync"]),
            s3.NotificationKeyFilter(prefix=self.config.s3dir_source.key),
        )

    def s03_create_outputs(self) -> None:
        """
        The ARN of every function. Each output has a property in
        :mod:`~{{ cookiecutter.package_name }}.cdk.stacks.lbd_stack_exports`.
        """
        for short_name, lambda_function in self.lambda_functions.items():
            cdk.CfnOutput(
                self,
                f"LambdaFunctionArn{to_camel(short_name)}",
                value=lambda_function.function_arn,
            )
