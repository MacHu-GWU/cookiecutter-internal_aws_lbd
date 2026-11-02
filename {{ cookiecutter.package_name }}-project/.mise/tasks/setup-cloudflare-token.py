# -*- coding: utf-8 -*-

"""
Set Cloudflare API token as a GitHub Actions secret.

This script:
1. Reads the Cloudflare API token from the environment
2. Sets it as a GitHub Actions secret so CI/CD can deploy to Cloudflare Pages

Required environment variables:
- GITHUB_TOKEN: GitHub personal access token with repo scope
- CLOUDFLARE_API_TOKEN: Cloudflare API token with Cloudflare Pages permissions

The script is idempotent - it will create or update the secret as needed.
"""

# ------------------------------------------------------------------------------
# Environment Variable Names
# ------------------------------------------------------------------------------
ENV_GITHUB_TOKEN = "GITHUB_TOKEN"
ENV_CLOUDFLARE_API_TOKEN = "CLOUDFLARE_API_TOKEN"

# ------------------------------------------------------------------------------
# GitHub Secret Name
# ------------------------------------------------------------------------------
GITHUB_SECRET_NAME = "CLOUDFLARE_API_TOKEN"

import os
import sys

try:
    from github import Github
    from github import GithubException
    from github import Auth
except ImportError:
    print("Error: PyGithub not installed. Run: uv sync --extra mise")
    sys.exit(1)

from utils import get_github_repo_info


def main():
    github_token = os.environ.get(ENV_GITHUB_TOKEN)
    cloudflare_token = os.environ.get(ENV_CLOUDFLARE_API_TOKEN)

    if not github_token:
        print(f"Error: {ENV_GITHUB_TOKEN} environment variable not set")
        print("Create a token at: https://github.com/settings/tokens")
        sys.exit(1)

    if not cloudflare_token:
        print(f"Error: {ENV_CLOUDFLARE_API_TOKEN} environment variable not set")
        print("Create a token at: https://dash.cloudflare.com/profile/api-tokens")
        sys.exit(1)

    owner, repo_name = get_github_repo_info()
    repo_fullname = f"{owner}/{repo_name}"

    secrets_url = f"https://github.com/{repo_fullname}/settings/secrets/actions"
    print(f"Setting up Cloudflare API token for: {repo_fullname}")
    print(f"Setting GitHub secret... (preview at: {secrets_url})")

    gh = Github(auth=Auth.Token(github_token))

    try:
        repo = gh.get_repo(repo_fullname)
    except GithubException as e:
        print(f"Error: Could not access repository {repo_fullname}")
        print(f"Details: {e}")
        sys.exit(1)

    # Create or update the secret (idempotent)
    try:
        repo.create_secret(
            secret_name=GITHUB_SECRET_NAME,
            unencrypted_value=cloudflare_token,
            secret_type="actions",
        )
        print(f"✅ Successfully set {GITHUB_SECRET_NAME} secret on {repo_fullname}")
    except GithubException as e:
        print(f"Error: Failed to create/update secret")
        print(f"Details: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
