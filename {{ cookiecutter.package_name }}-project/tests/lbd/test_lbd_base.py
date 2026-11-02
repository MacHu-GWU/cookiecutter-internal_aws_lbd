# -*- coding: utf-8 -*-

"""
Unit test of ``BaseInput.lambda_handler``: event in, ``Input``, ``main``, dict out.
"""

import pytest
from pydantic import ValidationError

from {{ cookiecutter.package_name }}.lbd.base import BaseInput
from {{ cookiecutter.package_name }}.lbd.base import BaseOutput


class Output(BaseOutput):
    message: str


class Input(BaseInput[Output]):
    name: str

    def main(self, context=None) -> Output:
        return Output(message=f"hello {self.name}")


def test_lambda_handler():
    # --------------------------------------------------------------------------
    # run
    # --------------------------------------------------------------------------
    result = Input.lambda_handler({"name": "alice"})

    # --------------------------------------------------------------------------
    # after
    # --------------------------------------------------------------------------
    assert result == {"message": "hello alice"}
    with pytest.raises(ValidationError):
        Input.lambda_handler({})


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.lbd.base",
        preview=False,
    )
