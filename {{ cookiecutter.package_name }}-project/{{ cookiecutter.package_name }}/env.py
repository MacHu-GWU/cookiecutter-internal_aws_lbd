# -*- coding: utf-8 -*-

"""
Which environment this code targets, from ``ENV_NAME``. Ask the :data:`env`
singleton instead of reading ``os.environ``::

    from .env import env

    if env.current_env_name == "prd":
        ...
"""

from __future__ import annotations

import os
import enum
from functools import cached_property


class EnvNameEnum(enum.StrEnum):
    """
    Every environment of this project: ``devops``, plus the workload environments
    (:meth:`get_workloads`) the application is deployed to.
    """

    #: Shared tooling: the Lambda layer every workload environment uses.
    devops = "devops"
    #: Development, where engineers deploy and test freely.
    dev = "dev"
    #: Test, a production-like environment for integration and acceptance tests.
    tst = "tst"
    #: Production, serving real users.
    prd = "prd"

    @classmethod
    def get_workloads(cls) -> list[EnvNameEnum]:
        """
        Every workload environment, in deployment order: all but :attr:`devops`.
        """
        return [member for member in cls if member is not cls.devops]


ENV_NAME_VAR = "ENV_NAME"
"""
The environment variable that selects the current environment, such as ``ENV_NAME=prd``.
"""


class Env:
    """
    Detects the current deployment environment.

    Use the module-level :data:`env` singleton instead of creating new instances.
    """

    def get_current_env_name(self) -> EnvNameEnum:
        """
        Work out the current environment; :attr:`current_env_name` caches the result.

        It reads the ``ENV_NAME`` environment variable, and defaults to
        :attr:`EnvNameEnum.dev` when it is not set.

        :raises ValueError: ``ENV_NAME`` is not a member of :class:`EnvNameEnum`.
        """
        value = os.environ.get(ENV_NAME_VAR, "")
        if value:
            return EnvNameEnum(value)
        else:
            return EnvNameEnum.dev

    @cached_property
    def current_env_name(self) -> str:
        """
        The current environment name, such as ``"dev"``, computed once on first access.
        """
        return self.get_current_env_name().value


env = Env()
"""
The single :class:`Env` instance of this project.
"""
