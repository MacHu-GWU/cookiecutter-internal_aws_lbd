---
description: "How a Lambda function gets its config: config-deploy-<env> writes the whole local Config of a workload environment as JSON to one SSM SecureString parameter, only when it changed; the function knows only the parameter name, CONFIG_SSM_PARAM_NAME, and loads it once per container on the aws_lambda runtime; a new config reaches the functions by redeploying them, which a config hash in the template forces. Read before adding a config field a function reads, changing how a function loads its config, or running a config task."
---

# Lambda Config in SSM

Seed repo: [`config/config_00_main.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/cookiecutter_internal_aws_lbd_demo/config/config_00_main.py), [`one/one_01_config.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/cookiecutter_internal_aws_lbd_demo/one/one_01_config.py), [`one/one_03_devops.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/cookiecutter_internal_aws_lbd_demo/one/one_03_devops.py).

---

## 1. The local files stay the source of truth

The config is edited only in `config/*.json5` (`07-config-load.md`). Each workload environment has one SSM parameter, `config.ssm_param_name_config` (`/<project>-<env>/config`), that holds a copy: the whole merged `Config` as JSON, `-secret` values included. So a function sees exactly the `Config` the developer sees, nested fields included, and no setting needs its own environment variable.

---

## 2. Deploying the copy

`mise run config-deploy-<env>` (`config-deploy-all` for every workload), `one.deploy_config()`:

- **Only when it changed:** `put_parameter_if_changed` of `simple_aws_ssm_parameter_store` writes only when the parameter is missing or its value differs. An unchanged config writes nothing and does not use up one of the 100 versions SSM keeps, so every `cdk-up` can deploy it safely.
- **`SecureString`,** because the `-secret` values are in it; tier `Intelligent-Tiering`, which turns advanced (8 KB) only when the value outgrows 4 KB. A unit test keeps each environment's JSON under 3000 bytes as an early warning.
- **boto3, not the infrastructure code,** so no value ends up in a template.
- `mise run config-delete-<env>` / `config-delete-all` delete it. Destroying the stacks does not delete it.

---

## 3. Reading it in a function

- The runtime `aws_lambda` (`02-runtime.md`) is detected by `AWS_LAMBDA_FUNCTION_NAME`, which Lambda always sets.
- Every function gets the environment variable `CONFIG_SSM_PARAM_NAME`, the parameter name, plus `ENV_NAME`. No other config goes into environment variables.
- `Config.load` on `aws_lambda` reads that parameter with `Config.load_from_ssm`; `one.config` passes it `one.ssm_client`.
- On `aws_lambda`, `one.bsm` reads nothing from the config: the region and the credentials come from the Lambda environment and the execution role. Otherwise loading the config would need the config (`06-boto-session.md`).
- `one.config` is a `cached_property` on every runtime (`08-one-singleton.md`): a container loads the config on first use and keeps it for its whole life, across warm invocations. Do not preload it in `lambda_function.py`; the first request loads it anyway.
- The execution role needs `ssm:GetParameter` on that one parameter, and no KMS permission (`aws/ssm` key).

---

## 4. A new config means a redeploy

The config is part of what is deployed, like the code: no hot reload, no parameter cache. Writing the parameter alone changes nothing a running container sees. So the Lambda stack puts `config.config_hash` (sha256 of the config JSON) into each function's `CONFIG_HASH` environment variable: a new config changes the template, `cdk-up-<env>-*` updates the functions, and every container that loaded the old config is replaced. Since every `up` task deploys the config first, `cdk-up-<env>-all` ships a config change on its own.
