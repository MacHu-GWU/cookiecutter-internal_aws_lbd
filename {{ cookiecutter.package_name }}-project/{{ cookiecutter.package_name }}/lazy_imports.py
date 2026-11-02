# -*- coding: utf-8 -*-

"""
Dev-only packages, which are not in the Lambda layer. A missing one becomes a
``MissingDependency`` that raises only when it is used, so importing this
module is safe in Lambda.
"""

from soft_deps.api import MissingDependency

try:
    import simple_aws_lambda.api as simple_aws_lambda
except ImportError:  # pragma: no cover
    simple_aws_lambda = MissingDependency(
        name="simple_aws_lambda",
        error_message="please run 'mise run inst'",
    )

try:
    import aws_lbd_art_builder_uv.api as aws_lbd_art_builder_uv
except ImportError:  # pragma: no cover
    aws_lbd_art_builder_uv = MissingDependency(
        name="aws_lbd_art_builder_uv",
        error_message="please run 'mise run inst'",
    )

try:
    import aws_lbd_art_builder_core.api as aws_lbd_art_builder_core
except ImportError:  # pragma: no cover
    aws_lbd_art_builder_core = MissingDependency(
        name="aws_lbd_art_builder_core",
        error_message="please run 'mise run inst'",
    )
