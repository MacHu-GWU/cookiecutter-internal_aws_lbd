# -*- coding: utf-8 -*-

"""
Read the outputs of the lbd stack, from this project or from any other. It
imports only the standard library, so another project can copy it as is::

    import boto3

    cf_client = boto3.Session(profile_name="my_dev_profile").client("cloudformation")
    exports = LbdStackExports.load(cf_client=cf_client, env_name="dev")
    print(exports.lambda_function_arn_hello)
"""

import typing as T
import dataclasses

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_cloudformation.client import CloudFormationClient

STACK_NAMES: dict[str, str] = {
    "dev": "{{ cookiecutter.package_name | slugify }}-dev-lbd",
    "tst": "{{ cookiecutter.package_name | slugify }}-tst-lbd",
    "prd": "{{ cookiecutter.package_name | slugify }}-prd-lbd",
}
"""
The CloudFormation stack name of each environment.
"""


@dataclasses.dataclass
class LbdStackExports:
    """
    The outputs of one deployed lbd stack. Create it with :meth:`load`.
    """

    # fmt: off
    env_name: str = dataclasses.field()  #: The environment, such as ``dev``.
    stack_name: str = dataclasses.field()  #: The CloudFormation stack name.
    outputs: dict[str, str] = dataclasses.field()  #: Every output, ``OutputKey`` to ``OutputValue``.
    exports: dict[str, str] = dataclasses.field()  #: Every exported output, ``ExportName`` to ``OutputValue``.
    # fmt: on

    @classmethod
    def from_describe_stacks_response(
        cls,
        env_name: str,
        response: dict[str, T.Any],
    ) -> "LbdStackExports":
        """
        Build it from the response of ``cloudformation.describe_stacks``.
        """
        stack = response["Stacks"][0]
        outputs = {}
        exports = {}
        for dct in stack.get("Outputs", []):
            outputs[dct["OutputKey"]] = dct["OutputValue"]
            if "ExportName" in dct:
                exports[dct["ExportName"]] = dct["OutputValue"]
        return cls(
            env_name=env_name,
            stack_name=stack["StackName"],
            outputs=outputs,
            exports=exports,
        )

    @classmethod
    def load(
        cls,
        cf_client: "CloudFormationClient",
        env_name: str,
    ) -> "LbdStackExports":  # pragma: no cover
        """
        Read the outputs of the stack of ``env_name`` with one ``describe_stacks`` call.

        :param cf_client: a CloudFormation client of the account of ``env_name``.
        :param env_name: a key of :data:`STACK_NAMES`, such as ``dev``.
        """
        response = cf_client.describe_stacks(StackName=STACK_NAMES[env_name])
        return cls.from_describe_stacks_response(env_name=env_name, response=response)

    @property
    def lambda_function_arn_hello(self) -> str:
        """
        The ARN of the hello function.
        """
        return self.outputs["LambdaFunctionArnHello"]

    @property
    def lambda_function_arn_s3sync(self) -> str:
        """
        The ARN of the s3sync function.
        """
        return self.outputs["LambdaFunctionArnS3sync"]

    def to_dict(self) -> dict[str, str]:
        """
        Every value this module provides, by property name. Reading them all
        raises ``KeyError`` if the deployed stack lacks one of the outputs.
        """
        return {
            "lambda_function_arn_hello": self.lambda_function_arn_hello,
            "lambda_function_arn_s3sync": self.lambda_function_arn_s3sync,
        }
