---
description: "The boto session of the current environment, one.bsm: one AWS profile per environment named in .env as AWS_PROFILE_FOR_<ENV>, the fallback to the default credential chain, the region from the config, and the clients built from it. Read when code needs AWS credentials or a boto3 client, when setting up profiles, or when credentials go to the wrong account."
---

# Boto Session

Seed repo: [`one/one_02_boto_ses.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.1.0/cookiecutter_internal_aws_lbd_demo/one/one_02_boto_ses.py).

---

## 1. One session per process

`one.bsm` is a `boto_session_manager.BotoSesManager` for the current environment (`03-env.md`), created on first use with no AWS call. `one.boto_ses` is its `boto3.Session`, and each client the project uses is a cached property next to it, such as `one.ssm_client`. Code takes clients from `one`, never creates its own session.

---

## 2. Credentials depend on the runtime

| Runtime (`02-runtime.md`) | Credentials |
| :--- | :--- |
| `local`, with `AWS_PROFILE_FOR_<ENV>` set | that named profile |
| `local` without it | the default credential chain |

`ci` has no AWS access yet: CI only runs the unit tests, which run as `local` with mocked AWS. A CI that calls AWS will get short-lived credentials through GitHub OIDC (`aws-actions/configure-aws-credentials`), which the default credential chain picks up, and will need its own config source first.

`AWS_PROFILE_FOR_<ENV>` (from `get_aws_profile_env_var(env_name)`) is set in the git-ignored `.env`, because profile names differ per person; `.env.example` lists one per environment with a placeholder value. Never put a profile name in a committed file.

---

## 3. Region and account

The region is `one.config.aws_region`, so the session depends on the loaded config. The exception is a runtime whose config is itself loaded with the session's clients: there the session reads nothing from the config and takes the region and credentials from the runtime, or loading would be circular. The account is `one.config.aws_account_id`, kept in a secret config file; the session's credentials must belong to it.
