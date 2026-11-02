# -*- coding: utf-8 -*-

"""
Integration test pytest configuration. These tests call the stacks deployed in
``ENV_NAME`` (default dev), with the real config files and AWS profiles.
"""

from {{ cookiecutter.package_name }}.tests.conftest import *  # noqa: F401,F403
