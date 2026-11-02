# -*- coding: utf-8 -*-

"""
:class:`Config`, the settings of one environment, and how it is loaded: from
``config/*.json5`` on a developer machine, from SSM in Lambda.
"""

from __future__ import annotations

import typing as T
import os
import hashlib
from pathlib import Path

from pydantic import BaseModel
from pydantic import Field
from simple_aws_ssm_parameter_store.api import get_parameter

from ..paths import path_enum
from ..env import EnvNameEnum
from ..runtime import RuntimeNameEnum
from .config_01_name import ConfigNameMixin

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_ssm.client import SSMClient


CONFIG_SSM_PARAM_NAME_VAR = "CONFIG_SSM_PARAM_NAME"
"""
The Lambda environment variable that names the SSM parameter holding the config;
the lbd stack sets it.
"""


class LambdaFunction(BaseModel):
    """
    Settings of one Lambda function. The function name is derived from its key
    in :attr:`Config.lambda_functions`, see
    :meth:`~{{ cookiecutter.package_name }}.config.config_01_name.ConfigNameMixin.get_lambda_function_name`.
    """

    # fmt: off
    handler: str = Field()  #: Attribute name in ``lambda_function.py``, such as ``hello_handler``.
    timeout: int = Field()  #: Timeout in seconds.
    memory: int = Field()  #: Memory size in MB.
    reserved_concurrency: int | None = Field(default=None)  #: Reserved concurrent executions, ``None`` for unreserved.
    # fmt: on


class Config(
    BaseModel,
    ConfigNameMixin,
):
    """
    Project-wide settings of one environment, validated on load.

    Every resource name is derived from these values in
    :class:`~{{ cookiecutter.package_name }}.config.config_01_name.ConfigNameMixin`.
    """

    # fmt: off
    project_name: str = Field()  #: Project name in snake_case or slug-case, such as ``my_project``.
    env_name: str = Field()  #: The environment these values are for, such as ``dev``.
    aws_account_id: str = Field()  #: The AWS account this environment deploys to, kept in ``config-<env>-secret.json5``.
    aws_region: str = Field()  #: The AWS region this environment deploys to.
    devops_aws_account_id: str = Field()  #: The DEVOPS account that owns the Lambda layer, kept in ``config-shared-secret.json5``.
    devops_s3_bucket_artifacts: str = Field()  #: Artifacts bucket in the DEVOPS account, where layer zips go.
    s3_bucket_data: str = Field()  #: Pre-existing data bucket of this environment; this project only uses its own prefix.
    lambda_python_version: str = Field()  #: Lambda Python version, such as ``3.12``.
    lambda_layer_version: int = Field()  #: The layer version this environment uses, printed by ``mise run lambda-layer-deploy``.
    lambda_layer_build_in_container: bool = Field(default=False)  #: Build the layer in the AWS SAM image (needs Docker) instead of on the host.
    lambda_functions: dict[str, LambdaFunction] = Field()  #: Every Lambda function, by short name, such as ``hello``.
    # fmt: on

    @property
    def config_hash(self) -> str:
        """
        sha256 of the config JSON; the lbd stack puts it in the ``CONFIG_HASH``
        environment variable of every function.
        """
        return hashlib.sha256(self.model_dump_json().encode("utf-8")).hexdigest()

    @classmethod
    def load_from_local_config_file(
        cls,
        env_name: str,
        dir_config: Path | None = None,
    ) -> Config:
        """
        Load the config of one environment from the json5 files in ``dir_config``.

        Four files are merged, a later one overriding the keys of an earlier one:
        ``config-shared.json5``, ``config-shared-secret.json5``,
        ``config-<env_name>.json5``, ``config-<env_name>-secret.json5``.
        The ``-secret`` files are git-ignored and may be missing; the others are required.
        ``config/example/`` shows the shape of every file.

        :param env_name: such as ``dev``, see :class:`~{{ cookiecutter.package_name }}.env.EnvNameEnum`.
        :param dir_config: the folder of the config files; defaults to ``path_enum.dir_config``.
        """
        # json5 is a dev dependency; it is not in the Lambda layer.
        import json5

        if env_name == EnvNameEnum.devops.value:
            raise ValueError(
                "the devops environment has no config: nothing of the application "
                "is deployed to it; its values are the devops_* fields of every config"
            )

        if dir_config is None:
            dir_config = path_enum.dir_config
        data = {}
        for name in ["shared", env_name]:
            path = dir_config / f"config-{name}.json5"
            data.update(json5.loads(path.read_text(encoding="utf-8")))
            path_secret = dir_config / f"config-{name}-secret.json5"
            if path_secret.exists():
                data.update(json5.loads(path_secret.read_text(encoding="utf-8")))
        data["env_name"] = env_name
        return cls(**data)

    @classmethod
    def load_from_ssm(
        cls,
        ssm_client: SSMClient,
        name: str,
    ) -> Config:
        """
        Load the config from the SSM parameter ``name``.

        :raises ValueError: the parameter does not exist; deploy it with
            ``mise run config-deploy-<env>``.
        """
        parameter = get_parameter(ssm_client, name, with_decryption=True)
        if parameter is None:
            raise ValueError(f"config SSM parameter {name!r} does not exist")
        return cls.model_validate_json(parameter.value)

    @classmethod
    def load(
        cls,
        env_name: str,
        runtime_name: str,
        ssm_client: SSMClient | None = None,
    ) -> Config:
        """
        Load the config the way the current runtime supports.

        :param env_name: such as ``dev``.
        :param runtime_name: such as ``local``, see :class:`~{{ cookiecutter.package_name }}.runtime.RuntimeNameEnum`.
        :param ssm_client: required on ``aws_lambda``, to read the config from SSM.

        :raises NotImplementedError: on any other runtime, such as CI.
        """
        if runtime_name == RuntimeNameEnum.local.value:
            return cls.load_from_local_config_file(env_name=env_name)
        elif runtime_name == RuntimeNameEnum.aws_lambda.value:
            return cls.load_from_ssm(
                ssm_client=ssm_client,
                name=os.environ[CONFIG_SSM_PARAM_NAME_VAR],
            )
        else:
            raise NotImplementedError(
                f"loading config on runtime {runtime_name!r} is not supported, "
                "deploy from a local machine"
            )
