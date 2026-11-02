# -*- coding: utf-8 -*-

"""
Build, publish the Lambda layer in the DEVOPS account, and grant every environment access.
"""

from {{ cookiecutter.package_name }}.one.api import one

if __name__ == "__main__":
    one.deploy_lambda_layer()
