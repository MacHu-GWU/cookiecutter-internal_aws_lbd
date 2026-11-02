# -*- coding: utf-8 -*-

"""
Write the config of the current environment (ENV_NAME) to SSM Parameter Store.
"""

from {{ cookiecutter.package_name }}.one.api import one

if __name__ == "__main__":
    one.deploy_config()
