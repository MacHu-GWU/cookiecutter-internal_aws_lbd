# -*- coding: utf-8 -*-

"""
Read the outputs of the infra stack, from this project or from any other. It
imports only the standard library, so another project can copy it as is::

    import boto3

    cf_client = boto3.Session(profile_name="my_dev_profile").client("cloudformation")
    exports = InfraStackExports.load(cf_client=cf_client, env_name="dev")
    print(exports.iam_role_for_lambda_arn)
"""

import typing as T
import dataclasses

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_cloudformation.client import CloudFormationClient

STACK_NAMES: dict[str, str] = {
    "dev": "{{ cookiecutter.package_name | slugify }}-dev-infra",
    "tst": "{{ cookiecutter.package_name | slugify }}-tst-infra",
    "prd": "{{ cookiecutter.package_name | slugify }}-prd-infra",
}
"""
The CloudFormation stack name of each environment.
"""


@dataclasses.dataclass
class InfraStackExports:
    """
    The outputs of one deployed infra stack. Create it with :meth:`load`.
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
    ) -> "InfraStackExports":
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
    ) -> "InfraStackExports":  # pragma: no cover
        """
        Read the outputs of the stack of ``env_name`` with one ``describe_stacks`` call.

        :param cf_client: a CloudFormation client of the account of ``env_name``.
        :param env_name: a key of :data:`STACK_NAMES`, such as ``dev``.
        """
        response = cf_client.describe_stacks(StackName=STACK_NAMES[env_name])
        return cls.from_describe_stacks_response(env_name=env_name, response=response)

    @property
    def iam_role_for_lambda_arn(self) -> str:
        """
        The ARN of the Lambda execution role.
        """
        return self.outputs["IamRoleForLambdaArn"]

    def to_dict(self) -> dict[str, str]:
        """
        Every value this module provides, by property name. Reading them all
        raises ``KeyError`` if the deployed stack lacks one of the outputs.
        """
        return {
            "iam_role_for_lambda_arn": self.iam_role_for_lambda_arn,
        }
