# -*- coding: utf-8 -*-

"""
Facts that belong to this tpl repo + seed repo pair, for the generic task code.

Everything else under ``.mise/tasks/`` works for any pair, except the
parameterization declarations in ``make_template.py``. When this family is
forked to another pair (/cctpl-fork-cn), this file is rewritten as a whole.

Where every pair-specific fact lives:
``.claude/skills/cctpl-base-cn/references/02-repo-layout.md``, "Where Facts Live".
"""

import tomllib
from pathlib import Path

# --- GitHub coordinates of the tpl repo (publish, verify, README)
GITHUB_OWNER = "MacHu-GWU"
GITHUB_REPO = "cookiecutter-internal_aws_lbd"

# --- the template dir: the project folder name inside the template
TEMPLATE_DIR_NAME = "{{ cookiecutter.package_name }}-project"

# --- generated projects (06-verification.md, L4, L5 and Local Trial)

# The cookiecutter variable holding the Python version a generated project uses.
PYTHON_VERSION_VARIABLE = "dev_python_version"

# The preset whose values point at a private package index this machine can
# read. Generated projects install their dependencies from AWS CodeArtifact,
# and the seed depends on a package that only the esc repository has, so only
# a project rendered with this preset can install: L4 (test-output) and L5
# (verify-release) install and test that one and only build a wheel of the
# others; try-template without an argument (so also e2e) uses it.
# None for a pair whose default-value project installs from public indexes.
TRIAL_PRESET = "esc-sanhe-dev"

# How L4 / L5 install a generated project and run its tests, without mise.
# Run in the project dir after "uv venv --python <version>", with the extra
# environment of project_install_env(). The project's own codeartifact-env.sh
# fetches a read-only CodeArtifact token with the AWS profile named there.
INSTALL_COMMAND = [
    "bash",
    "-c",
    ". .mise/tasks/codeartifact-env.sh && uv sync --all-extras",
]
TEST_COMMAND = [".venv/bin/pytest", "tests", "-q"]


def project_install_env(dir_project: Path) -> dict[str, str]:
    """
    The extra environment ``INSTALL_COMMAND`` needs in ``dir_project``: the
    plain (non-secret) ``AWS_CODEARTIFACT_*`` values of the project's
    ``mise.toml`` [env], which mise would otherwise provide.
    """
    path = dir_project / "mise.toml"
    if not path.is_file():
        return {}
    with open(path, "rb") as f:
        env = tomllib.load(f).get("env", {})
    return {k: str(v) for k, v in env.items() if k.startswith("AWS_CODEARTIFACT_")}


# The generated project's own mise tasks that the Local Trial runs, in order.
# All local, no write to AWS: lambda-layer-build-only builds the layer (reading
# private packages from CodeArtifact, like inst), cdk-synth-dev-all runs
# lambda-source-build and synthesizes every stack of dev with the cdk CLI.
PROJECT_TASKS = [
    "venv-create",
    "inst",
    "cov",
    "build-doc",
    "lambda-layer-build-only",
    "cdk-synth-dev-all",
]
