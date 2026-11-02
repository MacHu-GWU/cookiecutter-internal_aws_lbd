# -*- coding: utf-8 -*-

"""
The module AWS Lambda calls: every handler, imported as ``<x>_handler``. The
``handler`` of each entry of ``lambda_functions`` in the config names one of them.
"""

from {{ cookiecutter.package_name }}.lbd.hello import lambda_handler as hello_handler
from {{ cookiecutter.package_name }}.lbd.s3sync import lambda_handler as s3sync_handler
