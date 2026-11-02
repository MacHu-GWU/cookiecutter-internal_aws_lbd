# -*- coding: utf-8 -*-

"""
Fixed values of the Lambda deployment.
"""

IS_LAMBDA_X86 = True
"""
``True``: the functions and the layer are x86_64; ``False``: arm64.
"""

LAMBDA_LAYER_GLIBC = "2_34"
"""
glibc version of the Lambda Python runtime (Amazon Linux 2023 for python3.12).
Used to pick the manylinux wheel tag for ``uv sync --python-platform``.
"""

LAMBDA_SOURCE_INCLUDE = ["*.py"]
"""
Glob patterns of the package files deployed as Lambda source code, see
:func:`~{{ cookiecutter.package_name }}.one.one_03_devops.build_lambda_source`.
Add ``"*.json"`` and so on when the functions read data files next to the code.

Patterns are matched with ``PurePath.match``, which anchors at the end of the
path relative to the package folder, so ``"*.py"`` matches at any depth.
"""

LAMBDA_SOURCE_EXCLUDE = ["tests/*", "docs/*", "vendor/*", "cdk/*", "cdk/*/*"]
"""
Glob patterns of the package files never deployed: dev-only code (``cdk/``
needs ``aws_cdk``, which is not in the layer). ``*`` matches one path part only,
so ``"tests/*"`` does not exclude ``tests/sub/x.py``; add a pattern per depth,
as for ``cdk/``. ``tests/one/test_one_one_03_devops.py`` checks the result.
"""
