# -*- coding: utf-8 -*-

"""
Takes a name and returns ``hello {name}``.
"""

import importlib.metadata

from pydantic import Field
import esc_aws_org_struct  # private, from CodeArtifact, via the layer

from ..logger import logger
from .base import BaseInput
from .base import BaseOutput


class Output(BaseOutput):
    """
    Lambda function output containing the greeting message.
    """

    message: str = Field()


class Input(BaseInput[Output]):
    """
    Lambda function input with name parameter for greeting generation.
    """

    name: str = Field(default="Mr X")

    @logger.pretty_log()
    def main(self, context=None) -> Output:
        """
        Generate greeting message and return formatted output.
        """
        # test of the private package: its dist-info is in the layer
        print(
            f"{esc_aws_org_struct.__name__} version: "
            f"{importlib.metadata.version('esc_aws_org_struct')}"
        )
        message = f"hello {self.name}"
        logger.info(message)
        return Output(message=message)


lambda_handler = Input.lambda_handler
