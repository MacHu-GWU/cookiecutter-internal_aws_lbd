# -*- coding: utf-8 -*-

"""
The logger of the package; the ``disable_logger`` pytest fixture silences it.
"""

from vislog import VisLog

from .paths import PACKAGE_NAME

logger = VisLog(
    name=PACKAGE_NAME,
    log_format="%(message)s",
)
"""
The single logger of this project.
"""
