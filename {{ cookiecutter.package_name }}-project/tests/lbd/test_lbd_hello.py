# -*- coding: utf-8 -*-

"""
Unit test of the hello function: calls ``Input.main`` directly.
"""

from {{ cookiecutter.package_name }}.lbd.hello import Input


def test_hello(
    disable_logger,
):
    # --------------------------------------------------------------------------
    # run
    # --------------------------------------------------------------------------
    output = Input(name="alice").main()

    # --------------------------------------------------------------------------
    # after
    # --------------------------------------------------------------------------
    assert output.message == "hello alice"


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.lbd.hello",
        preview=False,
    )
