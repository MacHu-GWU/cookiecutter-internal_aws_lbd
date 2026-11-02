
.. image:: https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.package_name }}-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.package_name }}-project/actions?query=workflow:CI

.. image:: https://img.shields.io/badge/Cloudflare%20Pages-📔_Document-None.svg?style=flat&logo=cloudflare&color=darkorange
    :target: https://{{ cookiecutter.package_name | slugify }}.pages.dev

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.package_name }}-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.package_name }}-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://{{ cookiecutter.package_name | slugify }}.pages.dev/py-modindex.html

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.package_name }}-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.package_name }}-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.package_name }}-project/releases


Welcome to ``{{ cookiecutter.package_name }}`` Documentation
==============================================================================
.. image:: https://raw.githubusercontent.com/{{ cookiecutter.github_username }}/{{ cookiecutter.package_name }}-project/main/docs/source/_static/{{ cookiecutter.package_name }}-logo.png


About
------------------------------------------------------------------------------
A template for a Python project of AWS Lambda functions, deployed with AWS CDK from a developer machine to several environments.

- **Environments**: workload environments ``dev``, ``tst``, ``prd``, plus a ``devops`` environment that owns what they share: the Lambda layer and its artifacts bucket. They can be separate AWS accounts or one account, kept apart by name.
- **Config**: one pydantic model, loaded from ``config/*.json5`` on a developer machine and from SSM Parameter Store in Lambda. Every resource name, ARN, and console URL is computed from it.
- **Lambda layer**: the ``[project] dependencies``, built with uv for Linux without Docker, published once in the devops account, and pinned to a version per environment.
- **Private packages**: from the company's AWS CodeArtifact repository, an explicit uv index in ``pyproject.toml``; the mise tasks fetch the token, for ``.venv`` and for the layer.
- **Infrastructure**: two CDK stacks per environment, ``infra`` (the IAM role) and ``lbd`` (the functions and their triggers).
- **Tasks**: every step is a ``mise run`` task, so there is no CI/CD pipeline to deploy; CI only runs the unit tests and, on the ``doc`` branch, deploys the docs.
- **Docs**: Sphinx, hosted on Cloudflare Pages behind Cloudflare Access (only company email addresses get in); the docs of each version are kept on S3.


Quick Start
------------------------------------------------------------------------------
Prerequisites: `mise <https://mise.jdx.dev/>`_, an AWS CLI profile for each account, an AWS CLI profile that can read the CodeArtifact repository (``AWS_CODEARTIFACT_PROFILE`` in ``mise.toml``), and each workload account bootstrapped for CDK.

1. Install the tools (Python, uv, Node, AWS CLI, CDK CLI) and the Python dependencies:

   .. code-block:: console

       $ mise install
       $ mise run inst

   ``inst`` fetches a CodeArtifact token when it has to download a package. Never run a bare ``uv sync`` or ``uv lock``: it fails on the private index.

2. Name your AWS profiles. Copy ``.env.example`` to ``.env`` (git-ignored) and set ``AWS_PROFILE_FOR_DEV``, ``_TST``, ``_PRD``, and ``_DEVOPS``.

3. Fill in the values that stay out of git. Copy ``config/example/config-shared-secret.json5.example`` to ``config/config-shared-secret.json5``, and ``config/example/config-dev-secret.json5.example`` to ``config/config-<env>-secret.json5`` for each of ``dev``, ``tst``, ``prd``; set the account IDs.

4. Check the setup; this makes no AWS call:

   .. code-block:: console

       $ mise run cov
       $ mise run cdk-synth-dev-all


Deploy
------------------------------------------------------------------------------
One environment at a time, ``dev`` first:

1. ``mise run lambda-layer-deploy``: publish the layer if ``uv.lock`` changed, and grant every environment access to it. If it prints a new version, set ``lambda_layer_version`` in ``config/config-<env>.json5``.
2. ``mise run cdk-up-dev-all``: build the source, check the layer, deploy the config to SSM, then deploy both stacks.
3. ``ENV_NAME=dev mise run int-test``: test the deployed functions.
4. Repeat 2 and 3 for ``tst``, then ``prd``.

.. list-table::
    :header-rows: 1

    * - What changed
      - Run
    * - function code, infrastructure, or a config value
      - ``cdk-up-<env>-all``
    * - ``[project] dependencies`` / ``uv.lock``
      - ``lambda-layer-deploy``, pin the version, then ``cdk-up-<env>-all``

After a config change, run ``mise run gen-quick-links`` and commit ``QUICK_LINKS.md``. The full flow: `23-lbd-deploy-flow.md <https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.package_name }}-project/blob/main/.claude/skills/pywf-aws-lbd-base/references/23-lbd-deploy-flow.md>`_.


Common Tasks
------------------------------------------------------------------------------
``mise tasks ls`` lists every task. A task whose description says "writes to AWS" changes AWS resources; the others only read, or run locally.

.. list-table::
    :header-rows: 1

    * - Task
      - What it does
    * - ``inst``
      - install the Python dependencies into ``.venv`` (fetches a CodeArtifact token only when a package must be downloaded)
    * - ``cov`` / ``format`` / ``lint``
      - unit tests with coverage, format, lint; run all three after a change
    * - ``lambda-layer-build-only``
      - build the layer locally, to check the dependencies
    * - ``lambda-layer-deploy``
      - publish the layer in the devops account and grant every environment (writes to AWS)
    * - ``lambda-layer-check-<env>``
      - check that ``<env>`` can use its pinned layer version
    * - ``lambda-layer-cleanup`` / ``-real-run``
      - list / delete old layer versions (the real run writes to AWS)
    * - ``config-deploy-<env>`` / ``config-delete-<env>``
      - write / delete the config of ``<env>`` in SSM (writes to AWS)
    * - ``cdk-synth-<env>-all``
      - synthesize the stacks, no AWS call
    * - ``cdk-plan-<env>-all``
      - diff the stacks against what is deployed
    * - ``cdk-up-<env>-all`` / ``cdk-down-<env>-all``
      - deploy / destroy every stack of ``<env>`` (writes to AWS); ``-infra-stack`` and ``-lbd-stack`` act on one stack
    * - ``int-test``
      - integration tests against ``ENV_NAME`` (writes to AWS)
    * - ``build-doc`` / ``deploy-pages``
      - build the docs / deploy them to Cloudflare Pages; normally CI deploys them on ``git push origin main:doc``
    * - ``gen-quick-links``
      - regenerate ``QUICK_LINKS.md`` from the config
    * - ``cdk-gen-tasks``
      - regenerate the per-environment tasks in ``mise.toml`` after adding a stack or an environment


AWS Console Links
------------------------------------------------------------------------------
`QUICK_LINKS.md <https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.package_name }}-project/blob/main/QUICK_LINKS.md>`_ links to the console of every AWS resource of the project, one table per environment.


For Maintainers and AI Agents
------------------------------------------------------------------------------
The conventions of this project, what each part does and why, are in the ``pywf-aws-lbd-base`` Agent Skill: `.claude/skills/pywf-aws-lbd-base/ <https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.package_name }}-project/tree/main/.claude/skills/pywf-aws-lbd-base>`_. Start from its ``SKILL.md``; ``24-lbd-change-recipes.md`` lists the files to touch for common changes.
