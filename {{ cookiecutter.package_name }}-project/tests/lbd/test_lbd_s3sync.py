# -*- coding: utf-8 -*-

"""
Unit test of the s3sync function against moto: an object under
``s3dir_source`` is copied to ``s3dir_target``.
"""

from {{ cookiecutter.package_name }}.lbd.s3sync import Input

from {{ cookiecutter.package_name }}.one.api import one
from {{ cookiecutter.package_name }}.tests.mock_aws import BaseMockAwsTest


class Test(BaseMockAwsTest):
    use_mock = True

    @classmethod
    def setup_class_post_hook(cls):
        # the AWS resources the function expects to exist already
        cls.create_s3_bucket(bucket_name=one.config.s3dir_data.bucket)

    def test_sync(
        self,
        disable_logger,
    ):
        # ----------------------------------------------------------------------
        # before
        # ----------------------------------------------------------------------
        s3path_source = one.config.s3dir_source.joinpath("file.txt")
        s3path_target = one.config.s3dir_target.joinpath("file.txt")
        s3path_source.write_text("hello", s3_client=self.s3_client)
        assert s3path_target.exists(s3_client=self.s3_client) is False

        # ----------------------------------------------------------------------
        # run
        # ----------------------------------------------------------------------
        output = Input(s3uri_source=s3path_source.uri).sync(s3_client=self.s3_client)

        # ----------------------------------------------------------------------
        # after
        # ----------------------------------------------------------------------
        assert output.s3path_target == s3path_target
        assert s3path_target.read_text(s3_client=self.s3_client) == "hello"


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.lbd.s3sync",
        preview=False,
    )
