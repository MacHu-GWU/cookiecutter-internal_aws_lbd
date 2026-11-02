# -*- coding: utf-8 -*-

"""
Create a Cloudflare Pages project for hosting documentation.

Run this once during initial project setup.
Requires CLOUDFLARE_API_TOKEN to be set in the environment (via mise.toml).
The project name is derived from the package name (underscores replaced with hyphens).
"""

import subprocess
from utils import config

project_name = config.readthedocs_slug  # e.g. {{ cookiecutter.package_name | slugify }}

print(f"Creating Cloudflare Pages project: {project_name}")
subprocess.run(
    [
        "wrangler",
        "pages",
        "project",
        "create",
        project_name,
        "--production-branch",
        "main",
    ],
    check=True,
)
print(f"✅ Cloudflare Pages project '{project_name}' created")
