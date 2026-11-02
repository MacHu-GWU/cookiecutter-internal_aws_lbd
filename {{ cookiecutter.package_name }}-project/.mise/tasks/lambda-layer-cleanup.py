# -*- coding: utf-8 -*-

"""
Delete old Lambda layer versions in the DEVOPS account. Keeps the latest 3 and
every version a config uses. Dry run unless called with ``--real-run``.
"""

import sys

from {{ cookiecutter.package_name }}.one.api import one

if __name__ == "__main__":
    one.cleanup_old_layer_versions(real_run="--real-run" in sys.argv)
