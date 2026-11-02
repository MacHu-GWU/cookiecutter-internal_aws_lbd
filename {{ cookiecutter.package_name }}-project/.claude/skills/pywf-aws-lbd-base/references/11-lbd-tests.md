---
description: "How Lambda functions are tested: unit tests in tests/lbd/ call Input.main (or its client-taking methods) with mocked AWS through moto and BaseMockAwsTest, integration tests in tests_int/lbd/ invoke the deployed function, and both follow before / run / after. Read when writing or fixing a test of a Lambda function."
---

# Lambda Tests

Seed repo: [`tests/lbd/`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/tree/1.0.0/tests/lbd), [`tests_int/lbd/`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/tree/1.0.0/tests_int/lbd), [`<package_name>/tests/mock_aws.py`](https://github.com/MacHu-GWU/cookiecutter_internal_aws_lbd_demo-project/blob/1.0.0/cookiecutter_internal_aws_lbd_demo/tests/mock_aws.py).

---

## 1. Before, run, after

Every test of a function has three parts, each under a `# ---` banner comment:

- **before:** put the world in the state the function expects (write the input object, delete a stale output), and assert that state. Skip it when there is none.
- **run:** one call: `Input(...).main()` in a unit test, an invoke or the triggering action in an integration test.
- **after:** assert the output and the new state of the world.

---

## 2. Unit tests: `tests/lbd/test_lbd_<x>.py`

- Test the business logic, not the handler: call `Input(...).main()`, or a method that takes its client, such as `sync(s3_client=...)`.
- AWS goes through moto. Subclass `BaseMockAwsTest` from `<package_name>.tests.mock_aws` with `use_mock = True`, and create the resources the function expects to exist (a bucket) in `setup_class_post_hook`. Pass `self.s3_client` (or the client you need) to the code under test.
- Locations come from the test config (`one.config.s3dir_<x>`, `05-config-names.md`), never from literal strings.
- The `disable_logger` fixture keeps the output short.

---

## 3. Integration tests: `tests_int/lbd/test_lbd_<x>.py`

- The same three parts against what is deployed in `ENV_NAME` (`mise run int-test`): invoke the function by `one.config.get_lambda_function_name("<x>")`, or trigger it the way production does (write the S3 object) and poll for the result with a timeout.
- They need the stacks and the config of that environment deployed; ask the user's yes before relying on them.
