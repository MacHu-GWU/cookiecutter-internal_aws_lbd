---
description: "The devops environment: a member of EnvNameEnum that is not a workload, owning the shared Lambda layer and its artifacts bucket; its profile AWS_PROFILE_FOR_DEVOPS, one.bsm_devops, the devops_* config fields, and why it has no config file of its own. Read before code or a task touches the devops account, or when setting up a machine to deploy."
---

# The devops Environment

Seed repo: [`env.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/cookiecutter_internal_aws_lbd_demo/env.py), [`one/one_02_boto_ses.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/cookiecutter_internal_aws_lbd_demo/one/one_02_boto_ses.py), [`.env.example`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/.env.example).

---

## 1. One devops plus N workloads

`EnvNameEnum.devops` holds what every workload environment shares and the application itself is not: the Lambda layer, and the artifacts bucket the layer is built into. Publishing it once, there, instead of once per workload account, keeps one version history and one place to clean up. It is not a workload (`03-env.md`): `get_workloads()` leaves it out, so it gets no stack, no SSM config, and no per-environment task.

devops and the workloads may all be one AWS account; they are kept apart by name, like the workloads.

---

## 2. Credentials

`AWS_PROFILE_FOR_DEVOPS` in `.env` names its profile, like every environment (`06-boto-session.md`). `one.bsm_devops` is its session, built the same way as `one.bsm`. Only local deploy code uses it: building and publishing the layer, granting access, cleaning up versions. Code that runs in a function never does.

---

## 3. Its values live in every workload config

The devops environment has no `config-devops.json5`; loading its config raises `ValueError`. What a workload needs to know about it is a field of every workload config (`04-config-model.md`):

| Field | Kept in |
| :--- | :--- |
| `devops_aws_account_id` | `config-shared-secret.json5` |
| `devops_s3_bucket_artifacts` | `config-shared.json5` |

So a workload computes the ARN of its layer version from its own config, without a call to the devops account (`05-config-names.md`: `lambda_layer_version_arn`, `lambda_layer_url`, `s3dir_lambda`). Console URLs of devops resources open only when signed in to the devops account; say so where they are printed.
