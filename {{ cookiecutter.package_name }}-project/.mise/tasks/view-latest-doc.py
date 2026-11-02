# -*- coding: utf-8 -*-

"""
Open the latest documentation hosted on AWS S3 in the browser.

URL format:
  https://{bucket}.s3.amazonaws.com/projects/{package_name}/latest/index.html

Required environment variables (set in mise.toml):
- DOC_HOST_S3_BUCKET: S3 bucket with static website hosting enabled
"""

# ------------------------------------------------------------------------------
# Environment Variable Names
# ------------------------------------------------------------------------------
ENV_DOC_HOST_S3_BUCKET = "DOC_HOST_S3_BUCKET"

import os
import sys
import subprocess

from utils import config

S3_PREFIX = "projects/"


def main():
    bucket = os.environ.get(ENV_DOC_HOST_S3_BUCKET)

    if not bucket:
        print(f"Error: {ENV_DOC_HOST_S3_BUCKET} environment variable not set")
        sys.exit(1)

    package_name = config.project_name
    url = (
        f"https://{bucket}.s3.amazonaws.com/{S3_PREFIX}{package_name}/latest/index.html"
    )

    print(f"Opening: {url}")
    subprocess.run(["open", url], check=True)


if __name__ == "__main__":
    main()
