---
description: "How a change reaches AWS: all from a developer machine with mise, no CI/CD; the order lambda-layer-deploy, pin the version, cdk-up-<env>-all (which builds the source, checks the layer, and deploys the config first), int-test, then the next environment; and which steps need the user's yes. Read before deploying, or when deciding which task a change needs."
---

# Lambda Deploy Flow

Seed repo: [`mise.toml`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.1.0/mise.toml).

---

## 1. Local only

Every deploy runs from a developer machine through `mise run <task>`, with the profiles of `.env` (`06-boto-session.md`). There is no CI/CD pipeline that deploys; CI only runs the unit tests. The runtime `ci` has no config source on purpose (`07-config-load.md`).

---

## 2. Which tasks a change needs

| What changed | Run |
| :--- | :--- |
| function code only | `cdk-up-<env>-all` (or `cdk-up-<env>-lbd-stack`) |
| a config value | `cdk-up-<env>-all`: it deploys the config, and the config hash in the template updates the functions (`13-lbd-config-ssm.md`) |
| `[project] dependencies` / `uv.lock` | `lambda-layer-deploy`, pin the printed version in `config-<env>.json5`, then `cdk-up-<env>-all` |
| infrastructure (roles, triggers, a new function) | `cdk-up-<env>-all` |

After a config change that adds, removes, or renames a resource (a function, for example), run `gen-quick-links` and commit `QUICK_LINKS.md` with it (`05-config-names.md`).

`cdk-up-<env>-*` already runs `lambda-source-build`, `lambda-layer-check-<env>`, and `config-deploy-<env>` first (`17-cdk-mise-tasks.md`), so the code, the layer pin, and the config of one environment never drift apart.

---

## 3. One environment at a time

1. `dev`: deploy, then `ENV_NAME=dev mise run int-test`.
2. Pin and deploy `tst`, test, then `prd`, in the order of `EnvNameEnum.get_workloads()`.

Never deploy two environments in parallel.

---

## 4. The user's yes

| Task | Needs a yes |
| :--- | :--- |
| `lambda-source-build`, `lambda-layer-build-only`, `gen-quick-links`, `cdk-synth-*`, `cdk-plan-*`, `lambda-layer-check-*`, `cdk-gc-*`, `lambda-layer-cleanup`, `cov` | no |
| `lambda-layer-deploy`, `lambda-layer-cleanup-real-run` (write to the devops account) | yes |
| `config-deploy-*`, `config-delete-*`, `cdk-up-*`, `cdk-down-*` | yes, one environment per yes |
| `int-test` (invokes deployed functions, writes test data) | yes |

Every task that needs a yes says `writes to AWS` in its description in `mise.toml`, so `mise tasks ls` shows which ones they are. Keep that true for a new task.
