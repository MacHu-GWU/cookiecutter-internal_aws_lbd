---
description: "The files to touch, in order, for the common Lambda changes: add a function, add a trigger or a permission, add or upgrade a dependency, add a config field a function reads, change the files that are deployed, add a workload environment, remove a function, and the checks after each. Read before adding or removing a Lambda function, a trigger, a permission, a runtime dependency, a config field a function reads, or a workload environment, or when checking that such a change is complete."
---

# Lambda Change Recipes

Finish every recipe with section 8.

---

## 1. Add a function `<x>`

1. `lbd/<x>.py` (or `lbd/<x>/`): `Input`, `Output`, `main`, `lambda_handler` (`09-lbd-handlers.md`).
2. Import `<x>_handler` in `lambda_function.py`.
3. An entry `<x>` in `lambda_functions` of `config-shared.json5`. The example file keeps one sample function; it shows the shape, not every function.
4. `tests/lbd/test_lbd_<x>.py`, and `tests_int/lbd/test_lbd_<x>.py` (`11-lbd-tests.md`).
5. If it calls AWS resources the role cannot reach yet: section 2.
6. A property `lambda_function_arn_<x>` in `lbd_stack_exports.py` (`16-cdk-stack-exports.md`); the `lbd` stack adds the ARN output of every function itself.
7. Deploy: `cdk-up-<env>-all`, with the user's yes (`23-lbd-deploy-flow.md`).

---

## 2. Add a trigger or a permission

1. The names of the resource in the config (`05-config-names.md`).
2. The permission in the role of the infra stack, scoped to this environment (`22-lbd-stacks.md` section 2).
3. A trigger on a resource this project owns goes with that resource's stack; on an existing resource, in the `lbd` stack (`22-lbd-stacks.md` section 4).
4. An event-source adapter for the function, if the trigger sends its own event shape (`09-lbd-handlers.md` section 3).

---

## 3. Add or upgrade a runtime dependency

1. `[project] dependencies` in `pyproject.toml`, only if a function imports it (`10-lbd-dependencies.md`); a private package, and every private package it depends on, also gets a `[tool.uv.sources]` line (`10-lbd-dependencies.md` section 4); `mise run inst`, never a bare `uv lock`.
2. `mise run lambda-layer-build-only`. If it fails on `--no-build`, the package has no Linux wheel: switch to the container build (`21-lbd-layer.md` section 1).
3. With the user's yes, `lambda-layer-deploy`, then pin the printed version in each `config-<env>.json5` as it is deployed.

A dev-only dependency goes in an extra and needs no layer.

---

## 4. Add a config field a function reads

Add it as for any field (`07-config-load.md` section 3). Then `config-deploy-<env>` for each environment, with the user's yes. Deploy the code that reads it only after its config is deployed (`cdk-up` does both, config first).

---

## 5. Change which files are deployed

Edit `LAMBDA_SOURCE_INCLUDE` / `LAMBDA_SOURCE_EXCLUDE` (`20-lbd-source-asset.md`). A new excluded folder with subfolders needs a pattern per depth, and the source tests' list of excluded folders.

---

## 6. Add a workload environment `<env>`

1. The general and CDK steps (`03-env.md`, `19-cdk-change-recipes.md` section 4).
2. Its own values in `config-<env>.json5`, `lambda_layer_version` among them, and `aws_account_id` in its `-secret` file.
3. With the user's yes: `lambda-layer-deploy` (grants the new account), `config-deploy-<env>`, then `cdk-up-<env>-all`.

---

## 7. Remove a function `<x>`

Undo section 1, then deploy every environment with the user's yes: the function disappears from the `lbd` stack.

---

## 8. Checks after any change

1. `mise run gen-env-tasks`, if the stacks or environments changed.
2. `mise run gen-quick-links`, if the config or a URL property changed (`05-config-names.md`).
3. `mise run cov`, then `mise run format` and `mise run lint`.
4. `mise run cdk-synth-<env>-all` for one environment.
5. Deploying, and `int-test`, are separate steps after the user's yes.
