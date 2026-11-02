# -*- coding: utf-8 -*-

"""
Deploy versioned documentation to AWS S3.

Uploads docs/build/html to:
  s3://{bucket}/projects/{package_name}/{version}/

Requires docs/build/html to exist (run 'mise run build-doc' first).

Required environment variables (set in mise.toml):
- DOC_HOST_AWS_PROFILE: AWS profile with S3 write permissions
- DOC_HOST_S3_BUCKET: S3 bucket with static website hosting enabled
"""

# ------------------------------------------------------------------------------
# Environment Variable Names
# ------------------------------------------------------------------------------
ENV_DOC_HOST_AWS_PROFILE = "DOC_HOST_AWS_PROFILE"
ENV_DOC_HOST_S3_BUCKET = "DOC_HOST_S3_BUCKET"

import os
import sys
import subprocess

from utils import config

S3_PREFIX = "projects/"


def main():
    aws_profile = os.environ.get(ENV_DOC_HOST_AWS_PROFILE)
    bucket = os.environ.get(ENV_DOC_HOST_S3_BUCKET)

    for name, value in [
        (ENV_DOC_HOST_AWS_PROFILE, aws_profile),
        (ENV_DOC_HOST_S3_BUCKET, bucket),
    ]:
        if not value:
            print(f"Error: {name} environment variable not set")
            sys.exit(1)

    package_name = config.project_name
    version = config.pyproject_data["project"]["version"]
    s3_uri = f"s3://{bucket}/{S3_PREFIX}{package_name}/{version}/"

    print(f"Deploying versioned documentation to S3...")
    print(f"Source : docs/build/html")
    print(f"Target : {s3_uri}")

    try:
        subprocess.run(
            ["aws", "s3", "sync", "docs/build/html", s3_uri, "--profile", aws_profile],
            check=True,
        )
        print(f"✅ Deployed versioned doc to {s3_uri}")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to sync to S3")
        print(f"Details: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
