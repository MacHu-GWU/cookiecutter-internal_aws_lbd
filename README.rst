.. This file is the source of README.rst. Do not edit README.rst by hand:
   apply-template (mise run sync) renders it from this file.

.. image:: https://img.shields.io/badge/Release_History!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/cookiecutter-internal_aws_lbd/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/cookiecutter-internal_aws_lbd


``cookiecutter-internal_aws_lbd``
==============================================================================


Overview
------------------------------------------------------------------------------
This template provides a ready-to-use structure for internal, closed source AWS Lambda projects: a multi-environment (``dev``, ``tst``, ``prd``) Lambda code base deployed with AWS CDK, whose private Python packages come from an `AWS CodeArtifact <https://aws.amazon.com/codeartifact/>`_ repository, never from or to PyPI.

**Key Features:**

- **Modern tooling**: Uses `mise-en-place <https://mise.jdx.dev/>`_ for task management and `uv <https://docs.astral.sh/uv/>`_ for fast Python package management
- **Multi-environment Lambda**: A pydantic config in local json5 files and SSM Parameter Store, sample ``hello`` and ``s3sync`` functions, and a shared Lambda layer built with uv and published from a ``devops`` account
- **Infrastructure as code**: ``infra`` and ``lbd`` AWS CDK stacks, with one generated mise task per environment and stack (synth, plan, up, down)
- **Private packages**: Resolves private packages through AWS CodeArtifact, both in the local ``.venv`` and in the Lambda layer; ``mise run inst`` fetches the token with your AWS CLI profile
- **Complete CI/CD**: Pre-configured GitHub Actions that authenticate to AWS through OIDC, no long-lived AWS keys
- **Private documentation**: Sphinx documentation, hosted on Cloudflare Pages behind Cloudflare Access (latest) and AWS S3 (one copy per released version)
- **AI ready**: Ships Claude Code skills that know the project's toolchain, the Lambda runtime and the CDK layout

Disclaimer
------------------------------------------------------------------------------
The best practices implemented in this repository reflect my personal experience from developing `over 150 open source Python libraries <https://pypi.org/user/machugwu/>`_, 200+ proof-of-concept initiatives, 100+ enterprise-grade applications, and 50+ production systems, many of them internal serverless applications that run on AWS Lambda in a company's own AWS accounts. While these practices have proven effective for me, please use them at your own discretion.


Usage
------------------------------------------------------------------------------
Enter the following command to use the latest template version:

.. code-block:: bash

    pip install "cookiecutter>=2.6.0,<3.0.0" && cookiecutter https://github.com/MacHu-GWU/cookiecutter-internal_aws_lbd

To use a specific released version (see the `full list of releases <https://github.com/MacHu-GWU/cookiecutter-internal_aws_lbd/releases>`_):

.. code-block:: bash

    cookiecutter https://github.com/MacHu-GWU/cookiecutter-internal_aws_lbd --checkout tags/${version}

For example, to use ``1.1.0``, the latest version:

.. code-block:: bash

    cookiecutter https://github.com/MacHu-GWU/cookiecutter-internal_aws_lbd --checkout tags/1.1.0

You'll then be prompted to provide the following information (defaults in parentheses):

.. code-block:: bash

    [1/21] Your Python package name, in snake case (e.g. my_package) (your_package_name): your_package_name
    [2/21] Your GitHub username, the owner of the new repo (your_github_username): your_github_username
    [3/21] Author name for pyproject.toml file (Firstname Lastname): Firstname Lastname
    [4/21] Author email for pyproject.toml file (firstname.lastname@email.com): firstname.lastname@email.com
    [5/21] SPDX license expression for pyproject.toml (e.g. LicenseRef-Proprietary) (LicenseRef-Proprietary): LicenseRef-Proprietary
    [6/21] Semantic Version, in {major}.{minor}.{micro} (e.g. 0.1.1) (0.1.1): 0.1.1
    [7/21] Python version for local development, in {major}.{minor} (e.g. 3.12) (3.12): 3.12
    [8/21] GitHub token field path in home_secret.toml, see https://github.com/MacHu-GWU/home_secret_toml-project (your_github_token_field): your_github_token_field
    [9/21] Cloudflare API token field path in home_secret.toml, see https://github.com/MacHu-GWU/home_secret_toml-project (your_cloudflare_token_field): your_cloudflare_token_field
    [10/21] AWS region of every environment (dev, tst, prd) and of the CodeArtifact domain (e.g. us-east-1) (us-east-1): us-east-1
    [11/21] Prefix of your AWS account names; bucket names derive from it, such as <prefix>-dev-<aws_region>-data and <prefix>-devops-<aws_region>-artifacts (your-aws-account-prefix): your-aws-account-prefix
    [12/21] AWS account id of the devops environment: it owns the Lambda layer, the artifacts bucket and the CodeArtifact domain (111122223333): 111122223333
    [13/21] AWS CLI profile for reading private packages from AWS CodeArtifact (your_aws_codeartifact_profile): your_aws_codeartifact_profile
    [14/21] AWS CLI profile for deploying documentation to AWS S3 (your_doc_host_aws_profile): your_doc_host_aws_profile
    [15/21] AWS S3 bucket for storing versioned documentation (your-doc-host-s3-bucket): your-doc-host-s3-bucket
    [16/21] AWS CodeArtifact domain name, also the uv index name (your-aws-codeartifact-domain): your-aws-codeartifact-domain
    [17/21] AWS CodeArtifact Python repository name (your-aws-codeartifact-repository): your-aws-codeartifact-repository
    [18/21] IAM role name that GitHub Actions assumes through OIDC to read AWS CodeArtifact (role/<name> in .github/workflows/main.yml) (your_aws_github_oidc_role_name): your_aws_github_oidc_role_name
    [19/21] AWS account id of the dev environment (123456789012): 123456789012
    [20/21] AWS account id of the tst environment (123456789012): 123456789012
    [21/21] AWS account id of the prd environment (123456789012): 123456789012

This will generate a repository structure similar to `cookiecutter_internal_aws_lbd_demo-project <https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project>`_.

Once generated, navigate to your project directory and explore the available automation tasks:

.. code-block:: bash

    cd your_package_name-project
    mise tasks ls  # List all available tasks


Project Maintainer Note
------------------------------------------------------------------------------
**Project Architecture:**

- **Seed Repository**: `cookiecutter_internal_aws_lbd_demo-project <https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project>`_ - A concrete, runnable project used as the source for template generation
- **Cookiecutter Template**: `cookiecutter-internal_aws_lbd <https://github.com/MacHu-GWU/cookiecutter-internal_aws_lbd>`_ - This repository

**Maintenance Workflow:**

This template is maintained using a "reverse engineering" approach, driven by Claude Code skills (``.claude/skills/cctpl-*-cn``):

1. Make changes in the Seed project (``cookiecutter_internal_aws_lbd_demo-project``)
2. In the Seed, bump the version and record the changes in its own ``release-history-seed-repo.rst``. The Seed and this template share one version number, and the Seed's ``pyproject.toml`` is its only source
3. Run ``mise run e2e``: it converts the Seed into a template, checks it, applies it to this repo (version included), then generates a project and runs its tests and docs build
4. Commit and push the Seed, then tag it with ``mise run publish`` and ``mise run release`` in the Seed
5. Run ``/cctpl-release-cn`` to write this repo's changelog section, which links to the Seed's section of the same version, then ``mise run publish-template`` to publish the template to GitHub. A published version is never overwritten
6. Run ``/cctpl-verify-cn`` to verify the published template

**Toolchain:**

- **mise-en-place**: Task runner and tool version manager
- **uv**: Fast Python package installer and resolver
- **cookiecutter-maker**: Reverse-engineering tool that converts concrete projects into templates

For the full maintenance specification, see `cctpl-base-cn <./.claude/skills/cctpl-base-cn/SKILL.md>`_.
