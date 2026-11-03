---
description: "Resource names, ARNs, and console URLs are computed once, as properties of the config, in config_01_name.py, with the naming pattern <resource type>_<attribute>_<short name> and a per-environment prefix; QUICK_LINKS.md lists every console URL. Read before naming any AWS resource, or before writing a name, ARN, or URL as a string anywhere else."
---

# Names in the Config

Seed repo: [`config/config_01_name.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.1.0/cookiecutter_internal_aws_lbd_demo/config/config_01_name.py).

---

## 1. Compute every name once, in the config

Every AWS resource name, its ARN, and its console URL is a `cached_property` of `ConfigNameMixin` in `<package_name>/config/config_01_name.py`. Infrastructure code, scripts, and tests all read the same property (`one.config.sns_topic_name_<x>`) and never rebuild the string. Then a name changes in one place, and code that runs where the infrastructure code does not (a script, a test, another service) still agrees with it.

---

## 2. Naming pattern

- Property: `<resource type>_<attribute>_<short name>`, such as `sns_topic_name_<x>`, `sns_topic_arn_<x>`, `iam_role_name_<x>`, `ssm_param_url_<x>`.
- Value: starts with `prefix_name_slug`, `<project-name>-<env>`, so environments and projects never collide in one account.
- A resource type with many members gets helpers, `get_<type>_url(name)` / `get_<type>_arn(name)`, and each member's properties call them.
- An ARN or URL that can be computed from the name, account, and region is a property too; skip an ARN that holds an ID assigned at creation.

---

## 3. Grouping and tests

Group the properties by resource type, under a `# ---` banner comment per type. `tests/config/test_config_config_01_name.py` checks the value of every property with the `config` fixture; add a line there for each new one.

---

## 4. Quick links

`QUICK_LINKS.md` at the repo root holds the console URL of every resource of the project, one table per environment, so a maintainer finds a resource without running a command. `mise run gen-quick-links` renders it from the config files with `.mise/tasks/gen-quick-links.py`, without an AWS call, and it is committed. The script only arranges URL properties the config already has.

- A new URL property gets a row in `gen-quick-links.py`.
- It holds no account ID: no ARN, and no URL with the account ID in it, such as the bootstrap bucket of the deployment tool.
- Run the task after adding, removing, or renaming a resource; nothing checks the file automatically.

Seed repo: [`gen-quick-links.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.1.0/.mise/tasks/gen-quick-links.py), [`QUICK_LINKS.md`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.1.0/QUICK_LINKS.md).
