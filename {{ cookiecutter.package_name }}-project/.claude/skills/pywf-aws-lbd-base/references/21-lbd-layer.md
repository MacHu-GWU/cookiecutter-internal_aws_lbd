---
description: "The Lambda layer: built from [project] dependencies and uv.lock with uv for the Linux platform on the host (a container only when a dependency has no Linux wheel), published in the devops account only when uv.lock changed, granted to every workload account, pinned per environment by lambda_layer_version, checked before each deploy, and cleaned up without touching versions in use. Read before building, publishing, granting, pinning, or deleting a layer version, or when a deploy fails on a layer."
---

# Lambda Layer

Seed repo: [`one/one_03_devops.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.1.0/cookiecutter_internal_aws_lbd_demo/one/one_03_devops.py), [`constants.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.1.0/cookiecutter_internal_aws_lbd_demo/constants.py), [`config/config-shared.json5`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.1.0/config/config-shared.json5).

---

## 1. Build: Linux wheels, no container

`mise run lambda-layer-build-only` builds `build/lambda/layer/artifacts/python/` with `UvLambdaLayerLocalBuilder` of `aws_lbd_art_builder_uv`: `uv sync` of `[project] dependencies` from `uv.lock`, on the host, with

- `--python-platform <cpu>-manylinux_<glibc>`: uv downloads the Linux wheels. `<cpu>` follows `IS_LAMBDA_X86`; `LAMBDA_LAYER_GLIBC` is the glibc of the Lambda runtime (`2_34`, Amazon Linux 2023).
- `--python <lambda_python_version>` from the config.
- `--no-build`: a dependency without a Linux wheel fails the build, instead of being compiled into a macOS binary that fails only in Lambda.

After the build, `check_layer_binaries` fails on any binary that is not Linux.

Private packages come from AWS CodeArtifact (`10-lbd-dependencies.md` section 4): the layer tasks source `.mise/tasks/codeartifact-env.sh`, and `get_private_index_credentials` hands the token to the builder as `Credentials`, which the container build needs because the host's environment variables do not reach the container.

When a dependency ships source only and has C extensions, set `lambda_layer_build_in_container: true` in `config-shared.json5`: it then builds in the AWS SAM image with `UvLambdaLayerContainerBuilder`, which needs Docker and a `.venv` of the same Python.

---

## 2. Publish: in devops, only when `uv.lock` changed

`mise run lambda-layer-deploy`, `one.deploy_lambda_layer()`, works in the devops account (`12-lbd-devops-env.md`):

1. Ask `LambdaLayerVersionPublisher.has_dependency_manifest_changed()` whether `uv.lock` differs from the one stored with the latest version. If not, skip to step 4: no build, no new version.
2. Build (section 1), zip, and upload to `config.s3dir_lambda`: `layer/layer.zip` (overwritten), and `layer/<NNNNNN>/uv.lock` per published version.
3. Publish a layer version named `config.lambda_layer_name`, one name for every environment.
4. Grant (section 3).
5. Print the latest version, and for each workload the version it pins and what to change.

---

## 3. Grant: every workload account

The layer belongs to the devops account, so a workload account can use a version only with a `lambda:GetLayerVersion` permission on it. Step 4 grants it to the account of every workload config, every time, whether it published or not; the grant is idempotent, so an account added later gets access on the next run.

---

## 4. Pin: `lambda_layer_version` per environment

Each `config-<env>.json5` says which version its functions use; the Lambda stack builds the ARN from it (`config.lambda_layer_version_arn`). A new version changes nothing until it is pinned, so `dev` can move first and `prd` later. Commit the change.

---

## 5. Check before deploy

`mise run lambda-layer-check-<env>` calls `GetLayerVersion` on the pinned ARN with the workload's own credentials, the call CloudFormation will make. On failure, run `lambda-layer-deploy`, then pin the version it prints. Every `cdk-up` task runs it first (`17-cdk-mise-tasks.md`).

---

## 6. Clean up

`mise run lambda-layer-cleanup` lists the versions it would delete: all but the latest 3 and every version a workload config pins. `mise run lambda-layer-cleanup-real-run` deletes them, after the user's yes. It only sees the configs on this machine; a pin changed elsewhere and not yet pulled is not protected.
