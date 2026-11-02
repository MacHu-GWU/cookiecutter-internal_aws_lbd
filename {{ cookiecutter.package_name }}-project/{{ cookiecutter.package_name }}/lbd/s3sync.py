# -*- coding: utf-8 -*-

"""
Triggered by a new object under ``config.s3dir_source``; copies it to the same
relative path under ``config.s3dir_target``.
"""

import typing as T
from pydantic import Field
from s3pathlib.api import S3Path
from aws_lambda_powertools.utilities.data_classes import S3Event
from aws_lambda_powertools.utilities.data_classes import event_source

from ..logger import logger
from ..one.api import one
from .base import BaseInput
from .base import BaseOutput

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client


class Output(BaseOutput):
    """
    Lambda function output containing the target S3 URI after copy operation.
    """

    s3uri_target: str = Field()

    @property
    def s3path_target(self) -> S3Path:
        """
        Convert target S3 URI to S3Path object for path operations.
        """
        return S3Path(self.s3uri_target)


class Input(BaseInput[Output]):
    """
    Lambda function input with source S3 URI for file copy operations.
    """

    s3uri_source: str = Field()

    @property
    def s3path_source(self) -> S3Path:
        """
        Convert source S3 URI to S3Path object for path operations.
        """
        return S3Path(self.s3uri_source)

    def sync(self, s3_client: "S3Client") -> Output:
        """
        Copy S3 object from source to target location using environment configuration.
        """
        s3path_source = self.s3path_source

        logger.info(f"copy {s3path_source.uri}")
        logger.info(f"preview: {s3path_source.console_url}", indent=1)

        s3path_target = one.config.s3dir_target.joinpath(
            s3path_source.relative_to(one.config.s3dir_source)
        )
        logger.info(f"to {s3path_target.uri}")
        logger.info(f"preview: {s3path_target.console_url}", indent=1)
        s3path_source.copy_to(s3path_target, overwrite=True, s3_client=s3_client)

        return Output(
            s3uri_target=s3path_target.uri,
        )

    @logger.pretty_log()
    def main(self, context=None) -> Output:  # pragma: no cover
        """
        Copy S3 object from source to target location using environment configuration.
        """
        return self.sync(s3_client=one.s3_client)


@event_source(data_class=S3Event)
def lambda_handler(event: S3Event, context):  # pragma: no cover
    """
    AWS Lambda handler for S3 events with automatic event parsing and validation.
    """
    return (
        Input(
            s3uri_source=f"s3://{event.record.s3.bucket.name}/{event.record.s3.get_object.key}",
        )
        .main(context)
        .model_dump()
    )
