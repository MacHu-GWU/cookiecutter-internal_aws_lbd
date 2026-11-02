---
description: "Where CDK code lives: everything in <package_name>/cdk/, one stack per module under stacks/ in a single-file or a folder-with-mixins form, the stack constructor signature, names read from the config, and the thin cdk/ folder at the repo root. Read before writing or reviewing a stack, or when deciding where CDK code goes."
---

# CDK Layout

---

## 1. All CDK code is in the package

```text
<package_name>/cdk/
├── stack_ctx_enum.py, stack_enum.py   # the two enums of stacks
├── mise_tasks.py                      # generates the cdk mise tasks
└── stacks/
    ├── <x>_stack.py                   # a small stack, one file
    ├── <x>_stack_exports.py           # its outputs, for other projects
    └── <y>_stack/                     # a stack that grew: one mixin per resource group
        ├── stack.py
        ├── stack_01_<topic>.py
        └── stack_02_<topic>.py
```

Seed repo: [`infra_stack.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/cookiecutter_internal_aws_lbd_demo/cdk/stacks/infra_stack.py), [`lbd_stack.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/cookiecutter_internal_aws_lbd_demo/cdk/stacks/lbd_stack.py), both in the one-file form. Switch a stack to the folder form when its file gets long.

---

## 2. A stack class

- `__init__(self, scope, id, stack_name, env, config, <resources of other stacks, by name>)`: the first four come from `StackCtx.to_stack_kwargs()`; `config` is the `Config` of the environment (`04-config-model.md`).
- The body stores `self.config`, then calls `self.s01_<verb>_<what>()`, `self.s02_...()` in order, one method per resource group. In the folder form each method lives in its `stack_0N_<topic>.py` mixin.
- **Every name comes from the config** (`05-config-names.md`): `role_name=self.config.iam_role_name_<x>`. A stack builds no name string. Add CloudFormation names there too: `cft_stack_name_<x>`, `cft_stack_url_<x>`, `cft_export_name_<value>`.
- Outputs other projects need are a `cdk.CfnOutput`, in a last `s0N_create_outputs` method. Give it `export_name=self.config.cft_export_name_<value>` only when a stack imports it with `Fn::ImportValue`; the `*_stack_exports.py` modules read outputs by output key and need none.

---

## 3. The thin `cdk/` folder at the root

Only `cdk.json` (`"app": "../.venv/bin/python cdk_app.py"`) and [`cdk_app.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/cdk/cdk_app.py), whose body is `one.stack_enum.synth()`. The app holds the stacks of the current environment only (`03-env.md`), so `ENV_NAME=prd cdk synth` synthesizes prd and never needs another environment's config. Never put stack logic here.
