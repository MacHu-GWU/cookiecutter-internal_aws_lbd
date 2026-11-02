---
description: "What may run inside Lambda: the [project] dependencies are exactly the layer, dev-only libraries stay in extras and are imported lazily, importing <package_name> must work with the layer alone, no package metadata at runtime, the version comes from PACKAGE_VERSION, and private packages come from AWS CodeArtifact through an explicit uv index. Read before adding a dependency, importing a library, or reading the package version."
---

# Lambda Dependencies and Imports

Seed repo: [`pyproject.toml`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/pyproject.toml), [`lazy_imports.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/cookiecutter_internal_aws_lbd_demo/lazy_imports.py).

---

## 1. Two kinds of dependencies

| Where in `pyproject.toml` | What | In Lambda |
| :--- | :--- | :--- |
| `[project] dependencies` | what the functions need at runtime | yes: the layer is built from exactly this list |
| `dev`, `test`, `doc`, `mise` extras | build, deploy, and test tools: CDK, `cdk-mate`, `json5`, the layer builder, the layer-version helpers (`simple-aws-lambda`), `moto` | no |

Every package in `[project] dependencies` makes the layer bigger and every cold start slower. Put a package there only if code inside a function imports it.

---

## 2. Importing `<package_name>` inside Lambda

The function's code is the whole package (minus dev-only folders), and only the layer is installed next to it. So:

- A module a function imports must import only `[project] dependencies` at module level.
- A dev-only library is imported inside the function body that needs it, or through `lazy_imports.py`, which falls back to a `MissingDependency` that raises only when used.
- `one` is imported in every function, so every `one` mixin must follow this (`08-one-singleton.md`): the CDK mixin imports `aws_cdk` inside its properties; the deploy mixin imports its tools through `lazy_imports.py`, which tries them at load time and leaves a `MissingDependency` in Lambda, where they are not installed.
- A test imports every handler from the built source folder, so a module left out of the copy fails in `mise run cov`, not in AWS. It runs with the venv's packages, so it does not catch a dev-only import at module level: keep to the two rules above.

---

## 3. No package metadata

The deployed code is the source files, not an installed package: there is no `dist-info`, so `importlib.metadata` raises inside Lambda. Code that runs in a function never reads metadata. The version of the deployed code is the `PACKAGE_VERSION` environment variable, which the Lambda stack sets from `[project].version` of `pyproject.toml` at synth time; `pyproject.toml` is the only place the version is written.

---

## 4. Private packages: AWS CodeArtifact

A private package comes from the company's AWS CodeArtifact repository, declared in `pyproject.toml` as an explicit uv index (`[[tool.uv.index]]`, `explicit = true`, `authenticate = "always"`). Only the packages pinned to it in `[tool.uv.sources]` come from it; everything else resolves from PyPI. The general rules of the private index are in the AWS CodeArtifact reference of the `pywf-priv-base` skill; this section adds what is specific to this project.

- **Pin every private package, transitive ones included.** uv reads `[tool.uv.sources]` only from this project, never from a dependency's own `pyproject.toml`, so each private package is both a requirement and a `[tool.uv.sources]` line. A private package a function imports is a `[project] dependencies` requirement like any other (section 1), so it is in the layer.
- **The token.** `.mise/tasks/codeartifact-env.sh`, sourced by a task, gets a CodeArtifact token (valid 12 hours) with the AWS profile, domain, and owner of the `AWS_CODEARTIFACT_*` variables in `mise.toml` `[env]`, and exports it as `UV_INDEX_<INDEX>_USERNAME` / `_PASSWORD` for uv. In CI (`CI` set) it uses the credentials of the OIDC role instead of a profile.
- **Who needs it.** `inst` syncs offline first, so it needs no network and no AWS while `.venv` matches `uv.lock`; only when a package must be downloaded does it source the script. Every task depends on `inst`, so this keeps them free of AWS calls. The layer tasks always source it, because the layer build downloads Linux wheels.
- **Never a bare `uv sync`, `uv lock`, or `uv add`:** they fail on the private index. Run `mise run inst`, or wrap the command: `mise exec -- sh -c '. .mise/tasks/codeartifact-env.sh && uv lock --upgrade-package <name>'`.
- **Docs** are built locally or by the `deploy-doc` job of CI, which gets the token through OIDC like the `test` job, so a docs page may import a private package.
- **Never print the token** or the `UV_INDEX_*_PASSWORD` variable.
