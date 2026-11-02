# -*- coding: utf-8 -*-

"""
Integration test of the deployed s3sync function: write an object under
``s3dir_source``, then poll ``s3dir_target`` until the copy appears; the S3
event and the function run asynchronously.
"""

import time
import uuid

from {{ cookiecutter.package_name }}.api import one
from {{ cookiecutter.package_name }}.logger import logger


def test():
    # --------------------------------------------------------------------------
    # before
    # --------------------------------------------------------------------------
    basename = "test.txt"
    s3path_source = one.config.s3dir_source.joinpath(basename)
    s3path_target = one.config.s3dir_target.joinpath(basename)

    logger.info(f"preview s3 source: {s3path_source.console_url}")
    logger.info(f"preview s3 target: {s3path_target.console_url}")

    s3path_target.delete(s3_client=one.s3_client)
    assert s3path_target.exists(s3_client=one.s3_client) is False

    # --------------------------------------------------------------------------
    # run: a new source object triggers the function through the S3 event
    # --------------------------------------------------------------------------
    content = uuid.uuid4().hex
    s3path_source.write_text(content, s3_client=one.s3_client)

    # --------------------------------------------------------------------------
    # after: the target appears within about 10 seconds
    # --------------------------------------------------------------------------
    time.sleep(3)
    n = 7
    succeeded = False
    for i in range(n):
        time.sleep(1)
        if s3path_target.exists(s3_client=one.s3_client):
            assert s3path_target.read_text(s3_client=one.s3_client) == content
            succeeded = True
            break
    if succeeded is False:
        raise RuntimeError(
            f"s3path target {s3path_target} does not exist!"
            f"S3 event and Lambda function did not work!"
        )


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_unit_test

    run_unit_test(__file__)
