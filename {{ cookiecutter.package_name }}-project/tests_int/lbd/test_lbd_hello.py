# -*- coding: utf-8 -*-

"""
Integration test of the deployed hello function: with a name, and with the default.
"""

import json

from {{ cookiecutter.package_name }}.api import one


def invoke(payload: dict) -> dict:
    """
    Invoke the deployed hello function of ``ENV_NAME`` and return its output.
    """
    response = one.lambda_client.invoke(
        FunctionName=one.config.get_lambda_function_name("hello"),
        InvocationType="RequestResponse",
        LogType="Tail",
        Payload=json.dumps(payload),
    )
    # print(response["LogResult"])  # base64 encoded log, for debug only
    return json.loads(response["Payload"].read().decode("utf-8"))


def test(
    disable_logger,
):
    # --------------------------------------------------------------------------
    # run
    # --------------------------------------------------------------------------
    result_1 = invoke({"name": "bob"})
    result_2 = invoke({})

    # --------------------------------------------------------------------------
    # after
    # --------------------------------------------------------------------------
    assert result_1["message"] == "hello bob"
    assert result_2["message"] == "hello Mr X"


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_unit_test

    run_unit_test(__file__)
