# -*- coding: utf-8 -*-

"""
Convert the seed repo into a cookiecutter template.

Input: the git-visible files of the seed repo (``CCTPL_SEED_DIR``).
Output: ``tmp/cctpl/template/``, a complete cookiecutter template root.

Rules: ``.claude/skills/cctpl-base-cn/references/03-parameterization.md``.
"""

import re
import sys
import json
import tomllib

from cookiecutter_maker.api import Parameter, Maker

import cctpl

try:
    dir_seed = cctpl.get_seed_dir()
except cctpl.TaskError as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)

with open(dir_seed / "pyproject.toml", "rb") as f:
    _pyproject = tomllib.load(f)
with open(dir_seed / "mise.toml", "rb") as f:
    _mise_config = tomllib.load(f)

# Every environment of the seed deploys to the same region as its CodeArtifact
# domain; it becomes one variable.
_ENV_CONFIG_FILES = [
    "config/config-dev.json5",
    "config/config-tst.json5",
    "config/config-prd.json5",
]
_CONSOLE_URL_FILES = ["mise.toml", "QUICK_LINKS.md"]
_aws_regions = {
    re.search(r'aws_region: "([^"]+)"', (dir_seed / path).read_text(encoding="utf-8")).group(1)
    for path in _ENV_CONFIG_FILES
}
_aws_regions.add(_mise_config["env"]["AWS_CODEARTIFACT_REGION"])
assert len(_aws_regions) == 1, (
    f"Every config-<env>.json5 and AWS_CODEARTIFACT_REGION must use one region: {_aws_regions}"
)

# The devops account owns the Lambda layer and is also the CodeArtifact domain
# owner; it becomes one variable.
assert _mise_config["env"]["DEVOPS_AWS_ACCOUNT_ID"] == _mise_config["env"]["AWS_CODEARTIFACT_DOMAIN_OWNER"], (
    "DEVOPS_AWS_ACCOUNT_ID and AWS_CODEARTIFACT_DOMAIN_OWNER in mise.toml must be equal"
)


class SeedValues:
    """Concrete values in the seed repo that become cookiecutter variables."""

    # --- identity
    package_name = "cookiecutter_internal_aws_lbd_demo"
    package_name_slug = "cookiecutter-internal-aws-lbd-demo"
    github_username = "MacHu-GWU"
    # Not a parameter: only scanned for leaks (UNIQUE_SEED_VALUES).
    pypi_username = "machugwu"

    # --- author
    author = "Sanhe Hu"
    author_email = "husanhe@gmail.com"

    # --- license
    license = "LicenseRef-Proprietary"

    # --- versioning (read from the seed)
    version = _pyproject["project"]["version"]
    dev_python_version = _mise_config["tools"]["python"]

    # --- secret token fields
    github_token_field = "github.accounts.sh.users.sh.secrets.dev.value"
    cloudflare_token_field = "cloudflare.accounts.esc.users.sh_esc.secrets.cloudflare_pages_upload.value"

    # --- AWS (read from the seed)
    aws_region = _aws_regions.pop()
    devops_aws_account_id = _mise_config["env"]["DEVOPS_AWS_ACCOUNT_ID"]
    # Every bucket name is <prefix>-<account>-<region>-<data|artifacts>, where
    # <account> is devops, dev, test or prod (config/config-*.json5).
    aws_account_prefix = "esc-app"
    aws_codeartifact_profile = _mise_config["env"]["AWS_CODEARTIFACT_PROFILE"]
    doc_host_aws_profile = _mise_config["env"]["DOC_HOST_AWS_PROFILE"]
    doc_host_s3_bucket = _mise_config["env"]["DOC_HOST_S3_BUCKET"]
    aws_codeartifact_domain = _mise_config["env"]["AWS_CODEARTIFACT_DOMAIN"]
    aws_codeartifact_repository = _mise_config["env"]["AWS_CODEARTIFACT_REPO"]
    # The IAM role GitHub Actions assumes through OIDC (.github/workflows/main.yml).
    aws_github_oidc_role_name = "ghoidc-esc_aws_codeartifacts_only-devops-us-east-1"


_parts = SeedValues.version.split(".")
assert len(_parts) == 3 and all(v.isdigit() for v in _parts), (
    f"Invalid version: {SeedValues.version}"
)

_HOME_SECRET_HELP = "see https://github.com/MacHu-GWU/home_secret_toml-project"

# The uv index is named after the CodeArtifact domain, and uv reads its
# credentials from UV_INDEX_<NAME>_USERNAME / _PASSWORD, where <NAME> is the
# index name upper-cased with every non-alphanumeric character turned into "_".
_DOMAIN = SeedValues.aws_codeartifact_domain
_DOMAIN_ENV = _DOMAIN.upper().replace("-", "_")
_REGION = SeedValues.aws_region
_PY = SeedValues.dev_python_version

# Files that link to the seed repo on GitHub as the reference implementation,
# such as ``github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/<version>/...``.
# The links must keep pointing at the seed, so package_name and github_username
# leave them alone.
_SEED_LINK_FILES = sorted(
    str(path.relative_to(dir_seed))
    for path in (dir_seed / ".claude/skills/pywf-aws-lbd-base").rglob("*.md")
    if "github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project"
    in path.read_text(encoding="utf-8")
)

# Files that only mention the maintainer's own projects (plugin marketplace,
# home_secret_toml, docfly, cdk_mate).
_MAINTAINER_LINK_FILES = [
    ".claude/settings.local.json.example",
    ".claude/skills/pypi-cdk_mate/SKILL.md",
    ".claude/skills/pypi-cdk_mate/ref/best-practices.md",
    ".claude/skills/pypi-cdk_mate/ref/public-api.md",
    ".claude/skills/pywf-priv-base/references/01-secrets.md",
    ".claude/skills/pywf-priv-base/references/15-docfly.md",
]

# The seed depends on the demo private package ``esc-aws-org-struct``
# (pyproject.toml). It stays literal: a generated project keeps a working
# private dependency to replace with its own. No parameter touches it: the
# aws_codeartifact_domain contexts below never match inside it.
PARAMETERS = [
    # Also the config's project_name (config/config-shared.json5), from which
    # every AWS resource name derives, such as the stack names in the
    # generated <cdk-stack-tasks> block of mise.toml (package_name_slug).
    Parameter(
        selector=[SeedValues.package_name],
        name="package_name",
        default="your_package_name",
        prompt="Your Python package name, in snake case (e.g. my_package)",
        exclude=_SEED_LINK_FILES,
    ),
    Parameter(
        selector=[SeedValues.package_name_slug],
        name="package_name_slug",
        custom_placeholder="{{ cookiecutter.package_name | slugify }}",
        in_cookiecutter_json=False,
    ),
    # The seed also links to itself, to the maintainer's own projects, and
    # credits the template's author in AUTHORS.rst. Those must stay literal.
    Parameter(
        selector=[SeedValues.github_username],
        name="github_username",
        default="your_github_username",
        prompt="Your GitHub username, the owner of the new repo",
        exclude=[*_SEED_LINK_FILES, *_MAINTAINER_LINK_FILES, "AUTHORS.rst"],
    ),
    # AUTHORS.rst is the template author's bio, kept as is (LEGAL_RESIDUES).
    Parameter(
        selector=[SeedValues.author],
        name="author",
        default="Firstname Lastname",
        prompt="Author name for pyproject.toml file",
        exclude=["AUTHORS.rst"],
    ),
    Parameter(
        selector=[SeedValues.author_email],
        name="author_email",
        default="firstname.lastname@email.com",
        prompt="Author email for pyproject.toml file",
    ),
    # Generic value: only the project license field in pyproject.toml. A text
    # variable; LICENSE.txt is always the proprietary one (hooks/post_gen_project.py).
    Parameter(
        selector=[f'license = "{SeedValues.license}"', SeedValues.license],
        name="license",
        default=SeedValues.license,
        prompt="SPDX license expression for pyproject.toml (e.g. LicenseRef-Proprietary)",
        include=["pyproject.toml"],
    ),
    # Generic value: only the project version line in pyproject.toml.
    Parameter(
        selector=[f'version = "{SeedValues.version}"', SeedValues.version],
        name="version",
        default="0.1.1",
        prompt="Semantic Version, in {major}.{minor}.{micro} (e.g. 0.1.1)",
        include=["pyproject.toml"],
    ),
    # Generic value: only the dev Python pin in mise.toml. The Lambda runtime
    # pins everything else to the one supported version (hooks/pre_gen_project.py).
    Parameter(
        selector=[f'python = "{_PY}"', _PY],
        name="dev_python_version",
        default=_PY,
        prompt=f"Python version for local development, in {{major}}.{{minor}} (e.g. {_PY})",
        include=["mise.toml"],
    ),
    Parameter(
        selector=[SeedValues.github_token_field],
        name="github_token_field",
        default="your_github_token_field",
        prompt=f"GitHub token field path in home_secret.toml, {_HOME_SECRET_HELP}",
    ),
    Parameter(
        selector=[SeedValues.cloudflare_token_field],
        name="cloudflare_token_field",
        default="your_cloudflare_token_field",
        prompt=f"Cloudflare API token field path in home_secret.toml, {_HOME_SECRET_HELP}",
    ),
    # Generic value: one region for every environment and the CodeArtifact
    # domain. The aws_region field of each environment's config
    # (config/example/ keeps its placeholder) ...
    Parameter(
        selector=[f'aws_region: "{_REGION}"', _REGION],
        name="aws_region",
        default=_REGION,
        prompt=f"AWS region of every environment (dev, tst, prd) and of the CodeArtifact domain (e.g. {_REGION})",
        include=_ENV_CONFIG_FILES,
    ),
    # ... the console URLs in mise.toml (the generated <cdk-stack-tasks> block;
    # the seed's test_mise_toml_is_up_to_date fails if it and the config
    # disagree) and QUICK_LINKS.md (generated by gen-quick-links from config/) ...
    Parameter(
        selector=[f"https://{_REGION}.console.aws.amazon.com/", _REGION],
        name="aws_region",
        include=_CONSOLE_URL_FILES,
        in_cookiecutter_json=False,
    ),
    Parameter(
        selector=[f"region={_REGION}", _REGION],
        name="aws_region",
        include=_CONSOLE_URL_FILES,
        in_cookiecutter_json=False,
    ),
    # ... the bucket names in config/config-*.json5 (and QUICK_LINKS.md) ...
    Parameter(
        selector=[f"-{_REGION}-data", _REGION],
        name="aws_region",
        in_cookiecutter_json=False,
    ),
    Parameter(
        selector=[f"-{_REGION}-artifacts", _REGION],
        name="aws_region",
        in_cookiecutter_json=False,
    ),
    # ... and the CodeArtifact region: mise.toml, the index URL, the CI step.
    Parameter(
        selector=[f'AWS_CODEARTIFACT_REGION = "{_REGION}"', _REGION],
        name="aws_region",
        in_cookiecutter_json=False,
        include=["mise.toml"],
    ),
    Parameter(
        selector=[f".codeartifact.{_REGION}.amazonaws.com", _REGION],
        name="aws_region",
        in_cookiecutter_json=False,
    ),
    Parameter(
        selector=[f"aws-region: {_REGION}", _REGION],
        name="aws_region",
        in_cookiecutter_json=False,
        include=[".github/workflows/main.yml"],
    ),
    # The bucket name prefix in config/config-*.json5 and QUICK_LINKS.md. The
    # doc-host bucket (doc_host_s3_bucket) is longer, so it is matched as a whole.
    Parameter(
        selector=[f"{SeedValues.aws_account_prefix}-", SeedValues.aws_account_prefix],
        name="aws_account_prefix",
        default="your-aws-account-prefix",
        prompt=(
            "Prefix of your AWS account names; bucket names derive from it, such as "
            "<prefix>-dev-<aws_region>-data and <prefix>-devops-<aws_region>-artifacts"
        ),
    ),
    # The devops account: DEVOPS_AWS_ACCOUNT_ID and AWS_CODEARTIFACT_DOMAIN_OWNER
    # in mise.toml and the CodeArtifact index URL. hooks/post_gen_project.py also
    # writes it into config/config-shared-secret.json5.
    Parameter(
        selector=[SeedValues.devops_aws_account_id],
        name="devops_aws_account_id",
        default="111122223333",
        prompt=(
            "AWS account id of the devops environment: it owns the Lambda layer, "
            "the artifacts bucket and the CodeArtifact domain"
        ),
    ),
    # The two profiles have the same value in the seed: each one only in its
    # own mise.toml line.
    Parameter(
        selector=[
            f'AWS_CODEARTIFACT_PROFILE = "{SeedValues.aws_codeartifact_profile}"',
            SeedValues.aws_codeartifact_profile,
        ],
        name="aws_codeartifact_profile",
        default="your_aws_codeartifact_profile",
        prompt="AWS CLI profile for reading private packages from AWS CodeArtifact",
        include=["mise.toml"],
    ),
    Parameter(
        selector=[
            f'DOC_HOST_AWS_PROFILE = "{SeedValues.doc_host_aws_profile}"',
            SeedValues.doc_host_aws_profile,
        ],
        name="doc_host_aws_profile",
        default="your_doc_host_aws_profile",
        prompt="AWS CLI profile for deploying documentation to AWS S3",
        include=["mise.toml"],
    ),
    Parameter(
        selector=[SeedValues.doc_host_s3_bucket],
        name="doc_host_s3_bucket",
        default="your-doc-host-s3-bucket",
        prompt="AWS S3 bucket for storing versioned documentation",
    ),
    # Generic value ("esc" is a common substring): only these contexts. The
    # longer seed values that contain it (buckets, repository, token field,
    # OIDC role, the demo private package) are matched as a whole first.
    # A context never includes another seed value (e.g. the account id next
    # to it): replaced text is never replaced again.
    Parameter(
        selector=[f'AWS_CODEARTIFACT_DOMAIN = "{_DOMAIN}"', _DOMAIN],
        name="aws_codeartifact_domain",
        default="your-aws-codeartifact-domain",
        prompt="AWS CodeArtifact domain name, also the uv index name",
    ),
    Parameter(
        selector=[f"https://{_DOMAIN}-", _DOMAIN],
        name="aws_codeartifact_domain_url",
        custom_placeholder="{{ cookiecutter.aws_codeartifact_domain }}",
        in_cookiecutter_json=False,
    ),
    # uv index name, in [[tool.uv.index]] and [tool.uv.sources]
    Parameter(
        selector=[f'name = "{_DOMAIN}"', _DOMAIN],
        name="aws_codeartifact_domain_uv_index",
        custom_placeholder="{{ cookiecutter.aws_codeartifact_domain }}",
        in_cookiecutter_json=False,
        include=["pyproject.toml"],
    ),
    Parameter(
        selector=[f'index = "{_DOMAIN}"', _DOMAIN],
        name="aws_codeartifact_domain_uv_source",
        custom_placeholder="{{ cookiecutter.aws_codeartifact_domain }}",
        in_cookiecutter_json=False,
        include=["pyproject.toml"],
    ),
    Parameter(
        selector=[f"UV_INDEX_{_DOMAIN_ENV}_", _DOMAIN_ENV],
        name="aws_codeartifact_domain_uv_env",
        custom_placeholder="{{ cookiecutter.aws_codeartifact_domain | upper | replace('-', '_') }}",
        in_cookiecutter_json=False,
    ),
    Parameter(
        selector=[SeedValues.aws_codeartifact_repository],
        name="aws_codeartifact_repository",
        default="your-aws-codeartifact-repository",
        prompt="AWS CodeArtifact Python repository name",
    ),
    Parameter(
        selector=[SeedValues.aws_github_oidc_role_name],
        name="aws_github_oidc_role_name",
        default="your_aws_github_oidc_role_name",
        prompt="IAM role name that GitHub Actions assumes through OIDC to read AWS CodeArtifact (role/<name> in .github/workflows/main.yml)",
    ),
]

# Variables that only hooks/post_gen_project.py uses: it writes them into the
# git-ignored config/config-<env>-secret.json5 of a generated project. They have
# no seed value (the seed's secret files are not git-visible), so they are added
# to cookiecutter.json directly. Each entry: (name, default, prompt). The default
# is the placeholder id of config/example/config-dev-secret.json5.example.
HOOK_VARIABLES: list[tuple[str, str, str]] = [
    (f"{env}_aws_account_id", "123456789012", f"AWS account id of the {env} environment")
    for env in ("dev", "tst", "prd")
]

# Git-visible seed files that must not enter the template.
EXCLUDE = [
    "LICENSE.txt",  # generated by hooks/post_gen_project.py
    "uv.lock",  # carries the seed's own package name; generated projects re-lock
    # Seed-only maintenance files: the seed's own changelog and the skill that
    # writes it (02-repo-layout.md, "seed repo").
    "release-history-seed-repo.rst",
    ".claude/skills/pywf-priv-changelog-seed-repo/",
]

# Seed files whose links pin the seed's own version tag (blob/<version>/...).
# check-version requires every pinned version to equal the seed version, so a
# version bump cannot leave them behind (08-versioning-and-release.md).
SEED_VERSION_PIN_FILES: list[str] = _SEED_LINK_FILES

# Files copied byte for byte (no variable replacement).
NO_RENDER = [
    "*/vendor/**/*.*",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-doc.txt",
    "requirements-mise.txt",
    "requirements-test.txt",
    "*.jinja",
    "*.j2",
    "*.html",
]

# Choice variables whose values send hooks or the template down different
# branches. test-template generates once per extra choice value
# (03-parameterization.md, "Choice Coverage"). There is no choice variable.
CHOICE_COVERAGE: list[str] = []

# Files the hooks create or rewrite in a generated project. check-roundtrip
# allows them to differ from the seed.
HOOK_OUTPUTS = [
    "LICENSE.txt",  # hooks/post_gen_project.py writes it with the current year
    # hooks/post_gen_project.py copies these from their examples; git-ignored in the seed
    ".env",
    "config/config-shared-secret.json5",
    "config/config-dev-secret.json5",
    "config/config-tst-secret.json5",
    "config/config-prd-secret.json5",
]

# Seed values unique enough that any occurrence left in the template is a
# leak, scanned by check-seed-values. Generic values (license, version,
# dev_python_version, aws_region, aws_codeartifact_domain) also appear
# legitimately elsewhere; check-roundtrip verifies them instead.
UNIQUE_SEED_VALUES = {
    "package_name": SeedValues.package_name,
    "package_name_slug": SeedValues.package_name_slug,
    "github_username": SeedValues.github_username,
    "pypi_username": SeedValues.pypi_username,
    "author": SeedValues.author,
    "author_email": SeedValues.author_email,
    "github_token_field": SeedValues.github_token_field,
    "cloudflare_token_field": SeedValues.cloudflare_token_field,
    "devops_aws_account_id": SeedValues.devops_aws_account_id,
    "aws_account_prefix": SeedValues.aws_account_prefix,
    "aws_codeartifact_profile": SeedValues.aws_codeartifact_profile,
    "doc_host_s3_bucket": SeedValues.doc_host_s3_bucket,
    "aws_codeartifact_repository": SeedValues.aws_codeartifact_repository,
    "aws_github_oidc_role_name": SeedValues.aws_github_oidc_role_name,
    "aws_codeartifact_domain_uv_env": f"UV_INDEX_{_DOMAIN_ENV}_",
}

_SEED_LINK = "links to the seed repo as the reference implementation, must stay literal"
_MAINTAINER_LINK = "links to the maintainer's own project, must stay literal"
_TEMPLATE_AUTHOR = "credits the template's author, not the generated project's"

# Unique seed values that may legally remain in the template, consumed by
# check-seed-values. Each entry: (seed value name, template-relative file, reason).
LEGAL_RESIDUES: list[tuple[str, str, str]] = [
    *[("package_name", path, _SEED_LINK) for path in _SEED_LINK_FILES],
    *[("github_username", path, _SEED_LINK) for path in _SEED_LINK_FILES],
    *[("github_username", path, _MAINTAINER_LINK) for path in _MAINTAINER_LINK_FILES],
    ("github_username", "AUTHORS.rst", _TEMPLATE_AUTHOR),
    ("pypi_username", "AUTHORS.rst", _TEMPLATE_AUTHOR),
    ("author", "AUTHORS.rst", _TEMPLATE_AUTHOR),
]


def get_seed_context() -> dict[str, str]:
    """
    The cookiecutter context that renders the template back into the seed.
    """
    return {
        p.name: getattr(SeedValues, p.name)
        for p in PARAMETERS
        if p.in_cookiecutter_json
    }


def add_hook_variables(path_json) -> None:
    """
    Add ``HOOK_VARIABLES`` and their prompts to ``cookiecutter.json``, right
    after the last variable that came from a parameter.
    """
    data = json.loads(path_json.read_text(encoding="utf-8"))
    result = {}
    for key, value in data.items():
        if key.startswith("_") and HOOK_VARIABLES[0][0] not in result:
            for name, default, _ in HOOK_VARIABLES:
                result[name] = default
        result[key] = value
    for name, _, prompt in HOOK_VARIABLES:
        result["__prompts__"][name] = prompt
    path_json.write_text(json.dumps(result, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")


def add_template_version(path_json) -> None:
    """
    Record the shared version (the seed's) as the private variable
    ``_template_version``: cookiecutter never prompts for it, but it is part of
    every generation's context. It goes right after the last prompted variable.
    """
    data = json.loads(path_json.read_text(encoding="utf-8"))
    result = {}
    for key, value in data.items():
        if key.startswith("_") and "_template_version" not in result:
            result["_template_version"] = cctpl.get_seed_version()
        result[key] = value
    path_json.write_text(json.dumps(result, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    dir_stage_seed = cctpl.dir_stage / dir_seed.name
    cctpl.reset_dir(cctpl.dir_stage)
    n_files = cctpl.stage_git_visible_files(dir_seed, dir_stage_seed)
    print(f"Staged {n_files} git-visible files from {dir_seed}")

    if cctpl.dir_template.exists():
        cctpl.reset_dir(cctpl.dir_template)
        cctpl.dir_template.rmdir()
    maker = Maker(
        dir_input=dir_stage_seed,
        dir_output=cctpl.dir_template,
        parameters=PARAMETERS,
        exclude=EXCLUDE,
        no_render=NO_RENDER,
        dir_hooks=cctpl.dir_project_root / "hooks",
        verbose=False,
    )
    maker.make_template()
    add_hook_variables(maker.path_cookiecutter_json)
    add_template_version(maker.path_cookiecutter_json)
    print(f"Template written to {cctpl.dir_template}")
    return 0


if __name__ == "__main__":
    cctpl.run_task(main)
