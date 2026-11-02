# -*- coding: utf-8 -*-

"""
The AWS session part of ``one``:

- :attr:`~OneBotoSesMixin.bsm`, the boto session of the current environment,
  and the clients built from it. The account and region are
  ``one.config.aws_account_id`` / ``one.config.aws_region``.
- :attr:`~OneBotoSesMixin.bsm_devops`, the boto session of the ``devops``
  environment, which owns the Lambda layer.
"""

from __future__ import annotations

import typing as T
import os
from functools import cached_property

import boto3
from boto_session_manager.api import BotoSesManager

from ..env import EnvNameEnum
from ..runtime import RuntimeNameEnum

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client
    from mypy_boto3_lambda.client import LambdaClient
    from mypy_boto3_cloudformation.client import CloudFormationClient
    from mypy_boto3_ssm.client import SSMClient
    from .one_00_main import One


def get_aws_profile_env_var(env_name: str) -> str:
    """
    The environment variable that names the local AWS profile of an environment,
    such as ``AWS_PROFILE_FOR_DEV`` for ``dev``, or ``AWS_PROFILE_FOR_DEVOPS`` for
    ``devops``; mise loads it from ``.env``.
    """
    return f"AWS_PROFILE_FOR_{env_name.upper()}"


class OneBotoSesMixin:
    """
    Lazily built boto sessions and AWS clients.
    """

    def _new_bsm(self: One, name: str) -> BotoSesManager:  # pragma: no cover
        """
        On the local runtime use the profile ``AWS_PROFILE_FOR_<NAME>`` when it is
        set. Otherwise use the default credential chain.

        Inside Lambda it reads nothing from the config: the region and the
        credentials (the execution role) come from the Lambda environment. The
        config itself is loaded with this session's SSM client, so it must not
        depend on the config.
        """
        runtime_name = self.runtime.current_runtime_name()
        if runtime_name == RuntimeNameEnum.aws_lambda.value:
            return BotoSesManager()
        region_name = self.config.aws_region
        if runtime_name == RuntimeNameEnum.local.value:
            profile_name = os.environ.get(get_aws_profile_env_var(name), "")
            if profile_name:
                return BotoSesManager(
                    profile_name=profile_name, region_name=region_name
                )
        return BotoSesManager(region_name=region_name)

    @cached_property
    def bsm(self: One) -> BotoSesManager:  # pragma: no cover
        """
        The boto session of the current environment, in the region of its config;
        creating it makes no AWS call.
        """
        return self._new_bsm(self.env.current_env_name)

    @cached_property
    def bsm_devops(self: One) -> BotoSesManager:  # pragma: no cover
        """
        The boto session of the DEVOPS account, from ``AWS_PROFILE_FOR_DEVOPS``.
        """
        return self._new_bsm(EnvNameEnum.devops.value)

    @cached_property
    def boto_ses(self: One) -> boto3.Session:  # pragma: no cover
        """
        The boto3 session of :attr:`bsm`.
        """
        return self.bsm.boto_ses

    @cached_property
    def s3_client(self: One) -> S3Client:  # pragma: no cover
        """
        An S3 client of :attr:`bsm`.
        """
        return self.bsm.s3_client

    @cached_property
    def lambda_client(self: One) -> LambdaClient:  # pragma: no cover
        """
        A Lambda client of :attr:`bsm`.
        """
        return self.bsm.lambda_client

    @cached_property
    def cloudformation_client(self: One) -> CloudFormationClient:  # pragma: no cover
        """
        A CloudFormation client of :attr:`bsm`.
        """
        return self.bsm.cloudformation_client

    @cached_property
    def ssm_client(self: One) -> SSMClient:  # pragma: no cover
        """
        An SSM client of :attr:`bsm`.
        """
        return self.bsm.ssm_client
