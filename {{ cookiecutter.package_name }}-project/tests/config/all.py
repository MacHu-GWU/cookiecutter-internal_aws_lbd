# -*- coding: utf-8 -*-

"""
Run all config unit tests with coverage scoped to ``config/``.
"""

if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.config",
        is_folder=True,
        preview=False,
    )
