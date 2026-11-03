---
description: "Where Lambda function code lives and how a handler is written: <package_name>/lbd/, one pydantic Input and Output per function, Input.main as the entry of the business logic, lambda_handler from BaseInput, event-source adapters, the lambda_function.py registry, and the lambda_functions entry in the config. Read before writing, renaming, or reviewing a Lambda function."
---

# Lambda Handlers

Seed repo: [`lbd/base.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.1.0/cookiecutter_internal_aws_lbd_demo/lbd/base.py), [`lbd/hello.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.1.0/cookiecutter_internal_aws_lbd_demo/lbd/hello.py), [`lbd/s3sync.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.1.0/cookiecutter_internal_aws_lbd_demo/lbd/s3sync.py), [`lambda_function.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.1.0/cookiecutter_internal_aws_lbd_demo/lambda_function.py).

---

## 1. Layout

```text
<package_name>/
├── lambda_function.py   # imports every handler, the only module Lambda calls
└── lbd/
    ├── base.py          # BaseInput, BaseOutput
    ├── <x>.py           # a small function: one module
    └── <y>/             # a function that grew: a folder
        └── __init__.py  # exposes Input, Output, lambda_handler
```

One function per module (or folder), named after its short name `<x>`, the same key it has in the config (section 4).

---

## 2. Input, Output, and `main`: a command

- **Output** subclasses `BaseOutput`, a pydantic model of what the function returns.
- **Input** subclasses `BaseInput[Output]`, a pydantic model of the event, with typed, validated fields and defaults.
- **`Input.main(self, context=None) -> Output`** is the entry of the business logic. Everything the function does starts here; tests call it directly.
- Split `main` into smaller methods that take their AWS clients as arguments, such as `sync(s3_client)`, so a test can pass a mocked client. `main` itself takes the clients from `one` (`08-one-singleton.md`).
- The handler is `lambda_handler = Input.lambda_handler`: `BaseInput.lambda_handler` builds `Input(**event)`, calls `main`, and returns `output.model_dump()`.

---

## 3. Event-source adapters

When an AWS service calls the function (an S3 event, an SQS batch), its event is not an `Input`. Write a module-level `lambda_handler` that parses the event, preferably with a Powertools data class (`@event_source(data_class=S3Event)`), builds the `Input`, and calls `main`. The adapter holds no business logic.

---

## 4. Registering a function

1. Import its handler in `lambda_function.py` as `<x>_handler`. The Lambda handler setting is always `<package_name>.lambda_function.<x>_handler`, so this file lists every deployed function at a glance.
2. Add an entry `<x>` to `lambda_functions` in `config-shared.json5`: `handler`, `timeout`, `memory`, optionally `reserved_concurrency`. The function name is `<project>-<env>-<x>` (`config.get_lambda_function_name("<x>")`, `05-config-names.md`).
3. The Lambda stack creates one function per entry; nothing else in the infrastructure code names a function.

---

## 5. Logging

Use `<package_name>.logger.logger`, never `print`. Decorate `main` with `@logger.pretty_log()` to frame each invocation's log.
