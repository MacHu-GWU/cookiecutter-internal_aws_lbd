# -*- coding: utf-8 -*-

"""
Deploy the documentation site to Cloudflare Pages.

Requires docs/build/html to exist (run 'mise run build-doc' first).
Requires CLOUDFLARE_API_TOKEN to be set in the environment (via mise.toml).
"""

import subprocess
from utils import config

project_name = config.readthedocs_slug  # e.g. {{ cookiecutter.package_name | slugify }}
pages_url = f"https://{project_name}.pages.dev/"

print(f"Deploying documentation to Cloudflare Pages: {pages_url}")
subprocess.run(
    [
        "wrangler",
        "pages",
        "deploy",
        "docs/build/html",
        f"--project-name={project_name}",
    ],
    check=True,
)
print(f"✅ Deployed to {pages_url}")
