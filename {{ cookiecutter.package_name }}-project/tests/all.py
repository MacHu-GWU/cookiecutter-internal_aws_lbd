# -*- coding: utf-8 -*-

"""
Run every unit test, with the coverage of the whole package: ``python tests/all.py``.
"""

if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}",
        is_folder=True,
        preview=False,
    )
