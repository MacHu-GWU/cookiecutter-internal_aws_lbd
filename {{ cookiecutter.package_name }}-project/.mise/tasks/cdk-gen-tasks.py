# -*- coding: utf-8 -*-

"""
Rewrite the <cdk-stack-tasks> block of mise.toml from the entries of StackCtxEnum,
the members of EnvNameEnum, and the config of each environment.
"""

from {{ cookiecutter.package_name }}.paths import path_enum
from {{ cookiecutter.package_name }}.cdk.mise_tasks import render_project_cdk_tasks
from {{ cookiecutter.package_name }}.cdk.mise_tasks import update_mise_toml


def main():
    changed = update_mise_toml(
        path=path_enum.path_mise_toml,
        block=render_project_cdk_tasks(),
    )
    if changed:
        print(f"Updated {path_enum.path_mise_toml}")
    else:
        print(f"{path_enum.path_mise_toml} is already up to date")


if __name__ == "__main__":
    main()
