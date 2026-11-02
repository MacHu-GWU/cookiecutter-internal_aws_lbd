# -*- coding: utf-8 -*-

"""
Read every output of the infra stack deployed in ``ENV_NAME`` through
``infra_stack_exports.py``. This catches a mismatch between the outputs the stack
creates and the properties of the exports module, and between the literal stack
names there and the config.
"""

from {{ cookiecutter.package_name }}.api import one
from {{ cookiecutter.package_name }}.cdk.stacks.infra_stack_exports import STACK_NAMES
from {{ cookiecutter.package_name }}.cdk.stacks.infra_stack_exports import InfraStackExports


def test():
    env_name = one.config.env_name
    assert STACK_NAMES[env_name] == one.config.cft_stack_name_infra
    exports = InfraStackExports.load(
        cf_client=one.cloudformation_client,
        env_name=env_name,
    )
    _ = exports.to_dict()
    assert exports.iam_role_for_lambda_arn == one.config.iam_role_arn_lambda


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_unit_test

    run_unit_test(__file__)
