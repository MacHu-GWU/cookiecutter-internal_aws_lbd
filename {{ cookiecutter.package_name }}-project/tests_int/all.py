# -*- coding: utf-8 -*-

"""
Run every integration test, against what is deployed in ``ENV_NAME``.
"""

if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_unit_test

    run_unit_test(
        __file__,
        is_folder=True,
    )
