# -*- coding: utf-8 -*-

"""
Set required secret environment variables as GitHub Actions secrets.

This script:
1. Reads the DevOps AWS account ID from the environment
2. Sets it as a GitHub Actions secret so CI/CD workflows can reference it

Required environment variables:
- GITHUB_TOKEN: GitHub personal access token with repo scope
- DEVOPS_AWS_ACCOUNT_ID: AWS account ID for the DevOps account

The script is idempotent - it will create or update the secret as needed.
"""

# ------------------------------------------------------------------------------
# Environment Variable Names
# ------------------------------------------------------------------------------
ENV_GITHUB_TOKEN = "GITHUB_TOKEN"
ENV_DEVOPS_AWS_ACCOUNT_ID = "DEVOPS_AWS_ACCOUNT_ID"

# ------------------------------------------------------------------------------
# GitHub Secret Names
# ------------------------------------------------------------------------------
GITHUB_SECRET_DEVOPS_AWS_ACCOUNT_ID = "DEVOPS_AWS_ACCOUNT_ID"

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
    devops_aws_account_id = os.environ.get(ENV_DEVOPS_AWS_ACCOUNT_ID)

    if not github_token:
        print(f"Error: {ENV_GITHUB_TOKEN} environment variable not set")
        print("Create a token at: https://github.com/settings/tokens")
        sys.exit(1)

    if not devops_aws_account_id:
        print(f"Error: {ENV_DEVOPS_AWS_ACCOUNT_ID} environment variable not set")
        sys.exit(1)

    owner, repo_name = get_github_repo_info()
    repo_fullname = f"{owner}/{repo_name}"

    secrets_url = f"https://github.com/{repo_fullname}/settings/secrets/actions"
    print(f"Setting up GitHub Actions secrets for: {repo_fullname}")
    print(f"Preview at: {secrets_url}")

    gh = Github(auth=Auth.Token(github_token))

    try:
        repo = gh.get_repo(repo_fullname)
    except GithubException as e:
        print(f"Error: Could not access repository {repo_fullname}")
        print(f"Details: {e}")
        sys.exit(1)

    # Create or update secrets (idempotent)
    try:
        repo.create_secret(
            secret_name=GITHUB_SECRET_DEVOPS_AWS_ACCOUNT_ID,
            unencrypted_value=devops_aws_account_id,
            secret_type="actions",
        )
        print(
            f"✅ Successfully set {GITHUB_SECRET_DEVOPS_AWS_ACCOUNT_ID} on {repo_fullname}"
        )
    except GithubException as e:
        print(
            f"Error: Failed to create/update secret {GITHUB_SECRET_DEVOPS_AWS_ACCOUNT_ID}"
        )
        print(f"Details: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
