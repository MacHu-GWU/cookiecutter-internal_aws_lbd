# -*- coding: utf-8 -*-

"""
``run_unit_test`` and ``run_cov_test`` of the vendored ``pytest_cov_helper``,
with ``root_dir`` and ``htmlcov_dir`` filled in from ``path_enum``, for the
``if __name__ == "__main__":`` block of every test file.
"""

from ..paths import path_enum
from ..vendor.pytest_cov_helper import run_unit_test as _run_unit_test
from ..vendor.pytest_cov_helper import run_cov_test as _run_cov_test


def run_unit_test(
    script: str,
    is_folder: bool = False,
):
    _run_unit_test(
        script=script,
        root_dir=f"{path_enum.dir_project_root}",
        is_folder=is_folder,
    )


def run_cov_test(
    script: str,
    module: str,
    preview: bool = False,
    is_folder: bool = False,
):
    _run_cov_test(
        script=script,
        module=module,
        root_dir=f"{path_enum.dir_project_root}",
        htmlcov_dir=f"{path_enum.dir_htmlcov}",
        preview=preview,
        is_folder=is_folder,
    )
