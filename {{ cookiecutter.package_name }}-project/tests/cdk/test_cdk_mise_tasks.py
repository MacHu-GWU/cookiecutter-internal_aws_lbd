# -*- coding: utf-8 -*-

from {{ cookiecutter.package_name }}.paths import path_enum
from {{ cookiecutter.package_name }}.cdk.mise_tasks import render_project_cdk_tasks


def test_mise_toml_is_up_to_date():
    """
    ``mise.toml`` holds the tasks of exactly the stacks of StackCtxEnum in every
    environment. If this fails, run ``mise run cdk-gen-tasks``.
    """
    text = path_enum.path_mise_toml.read_text(encoding="utf-8")
    assert render_project_cdk_tasks() in text


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_unit_test

    run_unit_test(__file__)
