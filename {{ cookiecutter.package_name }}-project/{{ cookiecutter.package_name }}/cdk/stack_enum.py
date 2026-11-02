# -*- coding: utf-8 -*-

"""
Layer 2 of the cdk_mate two-layer pattern: one CDK stack per entry of
:class:`~{{ cookiecutter.package_name }}.cdk.stack_ctx_enum.StackCtxEnum`, of the same
name, with its arguments by name.
"""

from __future__ import annotations

import typing as T
import dataclasses
from functools import cached_property

import aws_cdk as cdk

from .stack_ctx_enum import list_entry_names
from .stacks.infra_stack import InfraStack
from .stacks.lbd_stack import LbdStack

if T.TYPE_CHECKING:  # pragma: no cover
    from ..one.api import One


@dataclasses.dataclass
class StackEnum:
    """
    The stacks of the current environment, created in :attr:`app` on first access.
    """

    # fmt: off
    app: cdk.App = dataclasses.field()  #: The CDK app that owns every stack.
    one: One = dataclasses.field()  #: The project singleton, for ``config`` and ``stack_ctx_enum``.
    # fmt: on

    @cached_property
    def infra(self) -> InfraStack:
        return InfraStack(
            scope=self.app,
            **self.one.stack_ctx_enum.infra.to_stack_kwargs(),
            config=self.one.config,
        )

    @cached_property
    def lbd(self) -> LbdStack:
        return LbdStack(
            scope=self.app,
            **self.one.stack_ctx_enum.lbd.to_stack_kwargs(),
            config=self.one.config,
            iam_role_for_lambda=self.infra.iam_role_for_lambda,
        )

    def get(self, stack: str) -> cdk.Stack:
        """
        Create (once) and return the stack given by name, such as ``get("infra")``.

        :raises AttributeError: there is no such entry.
        """
        return getattr(self, stack)

    def get_all(self) -> list[cdk.Stack]:
        """
        Create every stack, in creation order, and return them; loop over this
        instead of naming each stack.
        """
        return [self.get(name) for name in list_entry_names(type(self))]

    def synth(self) -> None:
        """
        Create every stack, then synthesize the app into ``cdk.out``.
        """
        self.get_all()
        self.app.synth()
