# -*- coding: utf-8 -*-

"""
Reject inputs the generated project cannot work with, before anything is written.
"""

import re
import sys

# The generated project pins requires-python, its classifiers and its CI matrix
# to these versions; mise.toml must use one of them.
# The Lambda runtime pins requires-python to one version (lambda_python_version
# in config/config-shared.json5), so the dev Python must match it.
SUPPORTED_PYTHON_VERSIONS = ["3.12"]

dev_python_version = "{{ cookiecutter.dev_python_version }}"

if dev_python_version not in SUPPORTED_PYTHON_VERSIONS:
    print(
        f"ERROR: dev_python_version must be one of "
        f"{', '.join(SUPPORTED_PYTHON_VERSIONS)}, got {dev_python_version!r}."
    )
    sys.exit(1)

# An AWS region code such as us-east-1, ap-southeast-2 or us-gov-west-1. It is
# written into config/config-<env>.json5, the console URLs in mise.toml, and
# the CodeArtifact region (mise.toml, the index URL in pyproject.toml, CI).
aws_region = "{{ cookiecutter.aws_region }}"

if not re.fullmatch(r"[a-z]{2}(-[a-z]+)+-\d+", aws_region):
    print(f"ERROR: aws_region must be an AWS region code such as us-east-1, got {aws_region!r}.")
    sys.exit(1)

# Bucket names derive from it (<prefix>-dev-<aws_region>-data), so it must keep
# them valid S3 bucket names: lowercase letters, digits and hyphens.
aws_account_prefix = "{{ cookiecutter.aws_account_prefix }}"

if not re.fullmatch(r"[a-z0-9]([a-z0-9-]*[a-z0-9])?", aws_account_prefix):
    print(
        f"ERROR: aws_account_prefix must be lowercase letters, digits and hyphens, "
        f"such as my-app, got {aws_account_prefix!r}."
    )
    sys.exit(1)

# Written into config/config-*-secret.json5; every stack is bound to its account.
aws_account_ids = {
    "devops_aws_account_id": "{{ cookiecutter.devops_aws_account_id }}",
    "dev_aws_account_id": "{{ cookiecutter.dev_aws_account_id }}",
    "tst_aws_account_id": "{{ cookiecutter.tst_aws_account_id }}",
    "prd_aws_account_id": "{{ cookiecutter.prd_aws_account_id }}",
}

for name, value in aws_account_ids.items():
    if not re.fullmatch(r"\d{12}", value):
        print(f"ERROR: {name} must be a 12-digit AWS account id, got {value!r}.")
        sys.exit(1)
