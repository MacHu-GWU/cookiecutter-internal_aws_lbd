---
description: "The one singleton: the only entry point to every project-level object (runtime, env, config, the boto session, and what later topics add), built lazily from numbered one_0N mixins. Read before adding a project-level object, a client, or anything environment specific, or when code imports a singleton from somewhere other than one."
---

# The `one` Singleton

Seed repo: [`one/one_00_main.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/cookiecutter_internal_aws_lbd_demo/one/one_00_main.py), [`one/one_01_config.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/cookiecutter_internal_aws_lbd_demo/one/one_01_config.py).

---

## 1. The only entry point

Code gets every project-level object from `one`: `from <package_name>.one.api import one`, then `one.runtime`, `one.env`, `one.config`, `one.bsm`, `one.<client>`. It does not import the singletons of `runtime.py`, `env.py`, or build a `Config` or a session itself. Everything environment specific on `one` belongs to the current environment (`03-env.md`).

---

## 2. Lazy

Every property is a `cached_property`: computed on first access, once. Importing `one` does no work and makes no AWS call. A property that needs a heavy library imports it inside its body; an optional tool may instead come from a module of optional imports, which tries each import at load time and leaves a placeholder that raises only when used.

---

## 3. One mixin per concern

- `One` inherits one mixin per concern, each in `one/one_0N_<topic>.py` as `One<Topic>Mixin`: `one_01_config.py` (`config`), `one_02_boto_ses.py` (`bsm`, `boto_ses`, clients).
- The number is the dependency order; a mixin reads what lower ones provide through `self`, with `self: One` as the type hint.
- To add a concern: a new `one_0N_<topic>.py` with its mixin, then add the mixin to the bases of `One` in `one_00_main.py`.

---

## 4. In tests

Build a fresh `One()` and assign its inputs, such as `one.config = config` (the `config` fixture), instead of patching the module-level `one`. A cached property can be assigned directly.
