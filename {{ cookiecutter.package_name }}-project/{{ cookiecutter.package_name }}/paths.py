# -*- coding: utf-8 -*-

from pathlib import Path
from functools import cached_property

_dir_here = Path(__file__).absolute().parent
PACKAGE_NAME = _dir_here.name


class PathEnum:
    """
    Every path of the repo, absolute, so no code depends on the current directory.
    """

    @cached_property
    def dir_home(self):
        return Path.home()

    dir_project_root = _dir_here.parent
    dir_tmp = dir_project_root / "tmp"

    # Source Code
    dir_package = _dir_here
    path_pyproject_toml = dir_project_root / "pyproject.toml"
    path_uv_lock = dir_project_root / "uv.lock"
    path_requirements_txt = dir_project_root / "requirements.txt"
    path_authors = dir_project_root / "AUTHORS.rst"
    path_license = dir_project_root / "LICENSE.txt"
    path_release_history = dir_project_root / "release-history.rst"
    path_mise_toml = dir_project_root / "mise.toml"
    path_quick_links_md = dir_project_root / "QUICK_LINKS.md"

    # Config files, see Config.load_from_local_config_file
    dir_config = dir_project_root / "config"

    # CDK
    dir_cdk = dir_project_root / "cdk"
    path_cdk_app_py = dir_cdk / "cdk_app.py"
    dir_cdk_out = dir_cdk / "cdk.out"

    # Virtual Environment
    dir_venv = dir_project_root / ".venv"
    dir_venv_bin = dir_venv / "bin"
    path_venv_bin_pip = dir_venv_bin / "pip"
    path_venv_bin_python = dir_venv_bin / "python"
    path_venv_bin_pytest = dir_venv_bin / "pytest"

    # Test
    dir_htmlcov = dir_project_root / "htmlcov"
    path_cov_index_html = dir_htmlcov / "index.html"
    dir_unit_test = dir_project_root / "tests"
    dir_int_test = dir_project_root / "tests_int"
    dir_load_test = dir_project_root / "tests_load"

    # Documentation
    dir_docs_source = dir_project_root / "docs" / "source"
    dir_docs_build_html = dir_project_root / "docs" / "build" / "html"

    # Build
    dir_build = dir_project_root / "build"
    dir_dist = dir_project_root / "dist"

    # Lambda Functions
    dir_build_lambda = dir_project_root / "build" / "lambda"
    dir_build_lambda_source = dir_build_lambda / "source"
    # Code.from_asset of the lbd stack points here, see build_lambda_source
    dir_build_lambda_source_build = dir_build_lambda_source / "build"


path_enum = PathEnum()
"""
The single :class:`PathEnum` instance of this project.
"""
