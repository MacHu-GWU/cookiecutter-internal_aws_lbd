# -*- coding: utf-8 -*-

"""
Where this code runs: a developer machine, CI, or AWS Lambda. Ask the
:data:`runtime` singleton instead of reading ``os.environ``::

    from .runtime import runtime

    if runtime.current_runtime_name() == "aws_lambda":
        ...
"""

from __future__ import annotations

import os
import enum


class RuntimeNameEnum(enum.Enum):
    """
    Every runtime this project's code can run in.
    """

    #: A developer's machine.
    local = "local"
    #: A CI/CD runner, such as GitHub Actions.
    ci = "ci"
    #: Inside an AWS Lambda function.
    aws_lambda = "aws_lambda"


class Runtime:
    """
    Detects the current runtime.

    Use the module-level :data:`runtime` singleton instead of creating new instances.
    """

    def get_current_runtime_name(self) -> RuntimeNameEnum:
        """
        Work out the current runtime.

        ``AWS_LAMBDA_FUNCTION_NAME`` is set by the Lambda service in every
        function. The ``CI`` environment variable counts as the CI signal,
        because GitHub Actions and most other CI services set it on every runner.
        """
        if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
            return RuntimeNameEnum.aws_lambda
        elif "CI" in os.environ:
            return RuntimeNameEnum.ci
        else:
            return RuntimeNameEnum.local

    def current_runtime_name(self) -> str:
        """
        The current runtime name, such as ``"local"``.
        """
        return self.get_current_runtime_name().value


runtime = Runtime()
"""
The single :class:`Runtime` instance of this project.
"""
