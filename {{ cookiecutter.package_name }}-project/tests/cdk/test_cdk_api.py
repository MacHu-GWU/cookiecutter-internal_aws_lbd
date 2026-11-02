# -*- coding: utf-8 -*-

from {{ cookiecutter.package_name }}.cdk import api


def test():
    _ = api
    _ = api.InfraStack
    _ = api.LbdStack
    _ = api.StackCtxEnum
    _ = api.StackEnum


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.cdk.api",
        preview=False,
    )
