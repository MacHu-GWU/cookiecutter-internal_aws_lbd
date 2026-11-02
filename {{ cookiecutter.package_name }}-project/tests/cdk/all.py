# -*- coding: utf-8 -*-

"""
Run all CDK unit tests with coverage scoped to ``cdk/``.
"""

if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.cdk",
        is_folder=True,
        preview=False,
    )
