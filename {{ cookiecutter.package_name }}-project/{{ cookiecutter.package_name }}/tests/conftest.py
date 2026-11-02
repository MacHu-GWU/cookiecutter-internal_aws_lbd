# -*- coding: utf-8 -*-

"""
Pytest configuration and fixtures for Lambda function testing.
"""

import pytest
from {{ cookiecutter.package_name }}.logger import logger


@pytest.fixture
def disable_logger():
    """
    Disable logging output during test execution.
    """
    with logger.disabled():
        yield
