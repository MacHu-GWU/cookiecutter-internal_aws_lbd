# -*- coding: utf-8 -*-

"""
Check that the current environment (ENV_NAME) can use the layer version of its
config; exit 1 if not, so a cdk-up task stops before CloudFormation fails.
"""

import sys

from {{ cookiecutter.package_name }}.one.api import one

if __name__ == "__main__":
    if one.check_lambda_layer_access() is False:
        sys.exit(1)
