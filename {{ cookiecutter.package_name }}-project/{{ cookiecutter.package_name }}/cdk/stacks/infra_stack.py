# -*- coding: utf-8 -*-

"""
The infra stack: the Lambda execution role, which the lbd stack receives as
an argument.
"""

from __future__ import annotations

import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from constructs import Construct

from ...config.api import Config


class InfraStack(cdk.Stack):
    """
    Takes the standard arguments of :meth:`cdk_mate.stack_ctx.StackCtx.to_stack_kwargs`
    plus the config of its environment; every name comes from the config.
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        stack_name: str,
        env: cdk.Environment,
        config: Config,
    ) -> None:
        super().__init__(
            scope=scope,
            id=id,
            stack_name=stack_name,
            env=env,
        )
        self.config = config
        self.s01_create_iam_role_for_lambda()
        self.s02_create_outputs()

    def s01_create_iam_role_for_lambda(self) -> None:
        """
        The execution role of every Lambda function of this environment:

        - CloudWatch Logs, through ``AWSLambdaBasicExecutionRole``.
        - Read its config from SSM. The parameter is a ``SecureString`` encrypted
          with the AWS managed key ``aws/ssm``, whose key policy already lets every
          principal of the account decrypt through SSM, so no KMS statement is needed.
        - Read and write only the ``s3dir_data`` folder of the shared data bucket.
        """
        config = self.config
        bucket_arn = f"arn:aws:s3:::{config.s3dir_data.bucket}"
        statements = [
            iam.PolicyStatement(
                actions=["ssm:GetParameter"],
                resources=[config.ssm_param_arn_config],
            ),
            iam.PolicyStatement(
                actions=["s3:ListBucket"],
                resources=[bucket_arn],
                conditions={
                    "StringLike": {"s3:prefix": [f"{config.s3dir_data.key}*"]},
                },
            ),
            iam.PolicyStatement(
                actions=[
                    "s3:GetObject",
                    "s3:GetObjectAttributes",
                    "s3:GetObjectTagging",
                    "s3:PutObject",
                    "s3:PutObjectTagging",
                    "s3:DeleteObject",
                    "s3:DeleteObjectTagging",
                ],
                resources=[f"{bucket_arn}/{config.s3dir_data.key}*"],
            ),
        ]
        self.iam_role_for_lambda = iam.Role(
            self,
            "IamRoleForLambda",
            role_name=config.iam_role_name_lambda,
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
            ],
            inline_policies={
                "main": iam.PolicyDocument(statements=statements),
            },
        )

    def s02_create_outputs(self) -> None:
        """
        Export the values other projects may use. Each output has a property in
        :mod:`~{{ cookiecutter.package_name }}.cdk.stacks.infra_stack_exports`.
        """
        self.output_iam_role_for_lambda_arn = cdk.CfnOutput(
            self,
            "IamRoleForLambdaArn",
            value=self.iam_role_for_lambda.role_arn,
            export_name=self.config.cft_export_name_lambda_role_arn,
        )
