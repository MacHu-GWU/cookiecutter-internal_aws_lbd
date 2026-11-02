# -*- coding: utf-8 -*-

"""
:class:`One`, the single entry point to every project-level object:
``one.env``, ``one.runtime``, ``one.config``, ``one.bsm``, and the rest, each from
a numbered mixin. Every property is computed on first access, so importing
``one`` does no work and makes no AWS call.
"""

from __future__ import annotations

from ..env import env
from ..runtime import runtime
from .one_01_config import OneConfigMixin
from .one_02_boto_ses import OneBotoSesMixin
from .one_03_devops import OneDevOpsMixin
from .one_04_cdk import OneCdkMixin


class One(
    OneConfigMixin,
    OneBotoSesMixin,
    OneDevOpsMixin,
    OneCdkMixin,
):
    """
    Aggregates every project-level singleton. Use the module-level :data:`~{{ cookiecutter.package_name }}.one.one_00_main.one`.
    """

    # fmt: off
    env = env  #: The deployment environment detector, see :mod:`{{ cookiecutter.package_name }}.env`.
    runtime = runtime #: The runtime detector, see :mod:`{{ cookiecutter.package_name }}.runtime`.
    # fmt: on


one = One()
"""
The single :class:`One` instance of this project.
"""
