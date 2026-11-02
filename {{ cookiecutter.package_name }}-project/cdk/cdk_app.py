#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
The CDK app entry point, run by the cdk CLI (see ``cdk.json``).

It creates the stacks of the current environment, the one ``ENV_NAME`` selects,
such as ``ENV_NAME=prd cdk synth``. The lbd stack deploys
``build/lambda/source/build/``, so run ``mise run lambda-source-build`` first;
the generated ``cdk-*`` mise tasks do.
"""

from {{ cookiecutter.package_name }}.one.api import one

one.stack_enum.synth()
