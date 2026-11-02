---
description: "The two stacks of a Lambda project: infra (the execution role per environment, least privilege) and lbd (one function per config entry, all sharing the source asset, the pinned layer, the role, and four environment variables, plus event sources on imported resources), and why there are no versions or aliases. Read before changing a Lambda function's infrastructure, its permissions, or its triggers."
---

# Lambda Stacks

Seed repo: [`infra_stack.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/cookiecutter_internal_aws_lbd_demo/cdk/stacks/infra_stack.py), [`lbd_stack.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/cookiecutter_internal_aws_lbd_demo/cdk/stacks/lbd_stack.py), [`stack_enum.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/cookiecutter_internal_aws_lbd_demo/cdk/stack_enum.py).

---

## 1. Two stacks, split by how often they change

- **`infra`:** what changes rarely, above all the execution role. A code deploy never touches it, so a bad deploy cannot change permissions.
- **`lbd`:** the functions, which change on every deploy. It gets the role as an argument from `infra` (`15-cdk-stack-enums.md`).

Add a stack for a resource with its own life cycle, such as a queue other projects use; keep the functions in `lbd`.

---

## 2. The execution role

One role per workload environment, named `config.iam_role_name_lambda`, shared by its functions, with the least privilege they need:

- `AWSLambdaBasicExecutionRole` for logs.
- `ssm:GetParameter` on this environment's config parameter only (`13-lbd-config-ssm.md`).
- For every other resource, only the actions the code calls, on the ARNs or key prefixes of this environment, never `*` on a resource shared with other environments or projects.

A function that needs much more than the others gets its own role.

---

## 3. The functions

`LbdStack` loops over `config.lambda_functions` (`09-lbd-handlers.md`), so a new function is a config entry, not stack code. Every function shares:

- `Code.from_asset` of the built source folder (`20-lbd-source-asset.md`);
- the pinned layer, `LayerVersion.from_layer_version_arn(config.lambda_layer_version_arn)` (`21-lbd-layer.md`);
- the role, the runtime `python<lambda_python_version>`, and the architecture from `IS_LAMBDA_X86`;
- four environment variables: `ENV_NAME`, `CONFIG_SSM_PARAM_NAME`, `CONFIG_HASH` (`13-lbd-config-ssm.md`), `PACKAGE_VERSION` (`10-lbd-dependencies.md`). Settings belong in the config, not here.

Its own: `function_name`, `handler` (`<package_name>.lambda_function.<handler>`), `memory_size`, `timeout`, `reserved_concurrent_executions`. Each function's ARN is an output, `LambdaFunctionArn<X>`, read by `lbd_stack_exports.py` (`16-cdk-stack-exports.md`).

---

## 4. Triggers on existing resources

A trigger whose source this project does not own, such as an existing bucket, is wired in the `lbd` stack on the imported resource (`s3.Bucket.from_bucket_name(...).add_event_notification(...)`), filtered to this environment's prefix. CDK manages only the notifications it adds; never deploy two environments that share the resource at the same time, since each deploy rewrites the resource's notification set.

---

## 5. Deliberately minimal

No published versions, aliases, provisioned concurrency, or canary deployments: each deploy updates `$LATEST` in place. They are easy to add on top when a project needs them (`current_version_options`, a `lambda_.Alias` per function, its name in the config); until then they would only add moving parts.
