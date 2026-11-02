# -*- coding: utf-8 -*-

"""
Build the Lambda layer locally, no zip/upload/publish.
"""

from {{ cookiecutter.package_name }}.one.api import one

if __name__ == "__main__":
    one.build_lambda_layer_only()
