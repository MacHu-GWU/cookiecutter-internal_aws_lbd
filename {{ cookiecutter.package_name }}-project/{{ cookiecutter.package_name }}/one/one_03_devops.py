# -*- coding: utf-8 -*-

"""
The deploy steps of ``one`` other than ``cdk deploy``: the config in SSM, the
Lambda layer, and the Lambda source. Safe to import in Lambda: the build tools
come through ``lazy_imports``.
"""

from __future__ import annotations

import os
import typing as T
import shutil
import tomllib
from pathlib import Path
from functools import cached_property

from ..paths import path_enum
from ..env import EnvNameEnum
from ..constants import IS_LAMBDA_X86
from ..constants import LAMBDA_LAYER_GLIBC
from ..constants import LAMBDA_SOURCE_INCLUDE
from ..constants import LAMBDA_SOURCE_EXCLUDE
from ..config.api import Config
from ..lazy_imports import simple_aws_lambda
import simple_aws_ssm_parameter_store.api as simple_aws_ssm_parameter_store
from ..lazy_imports import aws_lbd_art_builder_uv
from ..lazy_imports import aws_lbd_art_builder_core

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_ssm.client import SSMClient
    from .one_00_main import One


def load_all_env_configs() -> dict[str, Config]:
    """
    The config of every workload environment whose config files are complete, by name.
    An environment without its ``-secret`` file (not set up on this machine yet)
    is skipped with a warning.
    """
    configs = {}
    for member in EnvNameEnum.get_workloads():
        try:
            configs[member.value] = Config.load_from_local_config_file(
                env_name=member.value
            )
        except Exception as e:  # pragma: no cover
            print(
                f"WARNING: skip env {member.value!r}, cannot load its config: "
                f"{type(e).__name__}: {e}"
            )
    return configs


def check_layer_binaries(dir_python: Path):
    """
    Make sure every compiled extension in the layer is a Linux binary.

    ``validate_artifacts`` only checks the direct dependencies, while most
    compiled code (e.g. ``pydantic_core``) comes from transitive ones.

    :raises ValueError: a ``.so`` file is not ELF, or there is a ``.dylib``.
    """
    errors = [str(p) for p in dir_python.rglob("*.dylib")]
    for path in dir_python.rglob("*.so"):
        with path.open("rb") as f:
            if f.read(4) != b"\x7fELF":
                errors.append(str(path))
    if errors:
        raise ValueError(
            "Found non-Linux binaries in the Lambda layer:\n" + "\n".join(errors)
        )


def get_private_index_credentials(
    path_pyproject_toml: Path = path_enum.path_pyproject_toml,
):
    """
    The credentials of the first ``[[tool.uv.index]]`` of ``pyproject.toml`` (AWS
    CodeArtifact) whose ``UV_INDEX_<NAME>_PASSWORD`` env var is set, for the layer
    build. ``.mise/tasks/codeartifact-env.sh`` sets these env vars; the container
    build needs them as ``Credentials``, because the host env does not reach it.

    :returns: ``Credentials``, or ``None`` when no index has a token.
    """
    data = tomllib.loads(path_pyproject_toml.read_text(encoding="utf-8"))
    for index in data.get("tool", {}).get("uv", {}).get("index", []):
        prefix = "UV_INDEX_" + index["name"].replace("-", "_").upper()
        password = os.environ.get(f"{prefix}_PASSWORD")
        if password:
            return aws_lbd_art_builder_core.layer_api.Credentials(
                index_name=index["name"],
                index_url=index["url"],
                username=os.environ.get(f"{prefix}_USERNAME", "aws"),
                password=password,
            )
    return None


def build_lambda_source(dir_build: Path = path_enum.dir_build_lambda_source_build):
    """
    Copy the package files matching :data:`~{{ cookiecutter.package_name }}.constants.LAMBDA_SOURCE_INCLUDE`
    to ``dir_build/<package_name>/``, the folder the lbd stack deploys with
    ``Code.from_asset``. The folder is wiped first, so the CDK asset hash
    depends only on the source files.
    """
    shutil.rmtree(dir_build, ignore_errors=True)
    aws_lbd_art_builder_core.copy_source_for_lambda_deployment(
        source_dir=path_enum.dir_package,
        target_dir=dir_build / path_enum.dir_package.name,
        include=LAMBDA_SOURCE_INCLUDE,
        exclude=LAMBDA_SOURCE_EXCLUDE,
    )


def deploy_config(
    config: Config,
    ssm_client: SSMClient,
) -> str:
    """
    Write the whole config as JSON to its SSM parameter,
    :attr:`~{{ cookiecutter.package_name }}.config.config_01_name.ConfigNameMixin.ssm_param_name_config`,
    a ``SecureString``, only when the parameter is missing or differs.

    :param ssm_client: an SSM client of the account of ``config``.

    :returns: ``"created"``, ``"updated"``, or ``"unchanged"``.
    """
    ssm = simple_aws_ssm_parameter_store
    value = config.model_dump_json()
    before, after = ssm.put_parameter_if_changed(
        ssm_client=ssm_client,
        name=config.ssm_param_name_config,
        value=value,
        type=ssm.ParameterType.SECURE_STRING,
        tier=ssm.ParameterTier.INTELLIGENT_TIERING,
    )
    if before is None:
        status = "created"
        detail = f"version {after.version}"
    elif after is None:
        status = "unchanged"
        detail = f"version {before.version}, nothing written"
    else:
        status = "updated"
        detail = f"version {before.version} -> {after.version}"
    print(
        f"Config of {config.env_name!r} {status} ({detail}, {len(value)} bytes): "
        f"SSM parameter {config.ssm_param_name_config}"
    )
    print(f"  {config.ssm_param_url_config}")
    return status


def delete_config(
    config: Config,
    ssm_client: SSMClient,
) -> bool:
    """
    Delete the SSM parameter of :func:`deploy_config`; ``cdk-down`` does not.
    The functions of this environment fail after this. A missing parameter
    is not an error.

    :param ssm_client: an SSM client of the account of ``config``.

    :returns: ``True`` if it was deleted, ``False`` if it did not exist.
    """
    deleted = simple_aws_ssm_parameter_store.delete_parameter(
        ssm_client=ssm_client,
        name=config.ssm_param_name_config,
    )
    status = "deleted" if deleted else "not found, nothing deleted"
    print(
        f"Config of {config.env_name!r} {status}: "
        f"SSM parameter {config.ssm_param_name_config}"
    )
    print(f"  {config.ssm_param_url_config}")
    return deleted


class OneDevOpsMixin:
    """
    Config, Lambda layer, and Lambda source deployment.
    """

    # --------------------------------------------------------------------------
    # Config
    # --------------------------------------------------------------------------
    def deploy_config_for_env(self: One, env_name: str) -> str:  # pragma: no cover
        """
        :func:`deploy_config` for any workload environment: its local config
        files, written with its own AWS profile ``AWS_PROFILE_FOR_<ENV>``.
        """
        config = Config.load_from_local_config_file(env_name=env_name)
        bsm = self._new_bsm(env_name, region_name=config.aws_region)
        return deploy_config(config=config, ssm_client=bsm.ssm_client)

    def delete_config_for_env(self: One, env_name: str) -> bool:  # pragma: no cover
        """
        :func:`delete_config` for any workload environment, like
        :meth:`deploy_config_for_env`.
        """
        config = Config.load_from_local_config_file(env_name=env_name)
        bsm = self._new_bsm(env_name, region_name=config.aws_region)
        return delete_config(config=config, ssm_client=bsm.ssm_client)

    def deploy_config(self: One) -> str:
        """
        :func:`deploy_config` for the current environment.
        """
        return deploy_config(config=self.config, ssm_client=self.ssm_client)

    def delete_config(self: One) -> bool:
        """
        :func:`delete_config` for the current environment.
        """
        return delete_config(config=self.config, ssm_client=self.ssm_client)

    # --------------------------------------------------------------------------
    # Layer
    # --------------------------------------------------------------------------
    @cached_property
    def lambda_architecture(self: One) -> str:  # pragma: no cover
        """
        Lambda architecture name, ``x86_64`` or ``arm64``.
        """
        return "x86_64" if IS_LAMBDA_X86 else "arm64"

    @cached_property
    def lambda_python_version_tuple(self: One) -> tuple[int, int]:
        """
        ``(3, 12)`` for ``lambda_python_version = "3.12"``.
        """
        major, minor = self.config.lambda_python_version.split(".")
        return int(major), int(minor)

    def _make_layer_builder(self: One):
        """
        The layer builder: ``uv sync`` for Linux on the host, or in the AWS SAM
        image (Docker) when ``lambda_layer_build_in_container`` is set.
        ``--no-build`` fails on a dependency that has no Linux wheel.
        Private packages come from CodeArtifact with :func:`get_private_index_credentials`.
        """
        layer_api = aws_lbd_art_builder_uv.layer_api
        py_major, py_minor = self.lambda_python_version_tuple
        credentials = get_private_index_credentials()
        if self.config.lambda_layer_build_in_container:
            return layer_api.UvLambdaLayerContainerBuilder(
                path_pyproject_toml=path_enum.path_pyproject_toml,
                py_ver_major=py_major,
                py_ver_minor=py_minor,
                is_arm=not IS_LAMBDA_X86,
                credentials=credentials,
                skip_prompt=True,
            )
        cpu = "x86_64" if IS_LAMBDA_X86 else "aarch64"
        return layer_api.UvLambdaLayerLocalBuilder(
            path_pyproject_toml=path_enum.path_pyproject_toml,
            credentials=credentials,
            skip_prompt=True,
            uv_sync_options=layer_api.UvSyncOptions(
                extra_args=[
                    "--python-platform",
                    f"{cpu}-manylinux_{LAMBDA_LAYER_GLIBC}",
                    "--python",
                    self.config.lambda_python_version,
                    "--no-build",
                ],
            ),
        )

    def build_lambda_layer_only(self: One):  # pragma: no cover
        """
        Build the Lambda layer only, no zip/upload/publish. The artifacts are left
        in ``build/lambda/layer/artifacts/python/``.
        """
        builder = self._make_layer_builder()
        builder.run()
        check_layer_binaries(builder.path_layout.dir_python)

    def _make_layer_publisher(self: One):  # pragma: no cover
        """
        The publisher, in the DEVOPS account, used to ask whether ``uv.lock``
        changed since the latest published version.
        """
        return aws_lbd_art_builder_core.layer_api.LambdaLayerVersionPublisher(
            path_pyproject_toml=path_enum.path_pyproject_toml,
            s3dir_lambda=self.config.s3dir_lambda,
            path_manifest=path_enum.path_uv_lock,
            s3_client=self.bsm_devops.s3_client,
            layer_name=self.config.lambda_layer_name,
            lambda_client=self.bsm_devops.lambda_client,
        )

    def deploy_lambda_layer(self: One):  # pragma: no cover
        """
        Build, zip, upload, and publish the layer in the DEVOPS account if
        ``uv.lock`` changed, then grant every environment the latest version.

        It asks the publisher first: ``LayerDeploymentWorkflow`` would build,
        zip and upload before finding ``uv.lock`` unchanged and raising ``ValueError``.
        """
        publisher = self._make_layer_publisher()
        if publisher.has_dependency_manifest_changed() is False:
            version = publisher.latest_layer_version.version
            print(f"uv.lock unchanged since layer version {version}, skip publish.")
        else:
            builder = self._make_layer_builder()
            workflow = aws_lbd_art_builder_core.layer_api.LayerDeploymentWorkflow(
                builder=builder,
                path_manifest=path_enum.path_uv_lock,
                s3dir_lambda=self.config.s3dir_lambda,
                layer_name=self.config.lambda_layer_name,
                s3_client=self.bsm_devops.s3_client,
                lambda_client=self.bsm_devops.lambda_client,
                publish_layer_version_kwargs={
                    "CompatibleRuntimes": [
                        f"python{self.config.lambda_python_version}"
                    ],
                    "CompatibleArchitectures": [self.lambda_architecture],
                },
            )
            # Same steps as workflow.run(), with a binary check before upload.
            workflow.step_1_build()
            check_layer_binaries(builder.path_layout.dir_python)
            workflow.step_2_package()
            workflow.step_3_upload()
            layer_deployment = workflow.step_4_publish()
            version = layer_deployment.layer_version
        self.grant_lambda_layer_access(version=version)
        self.print_lambda_layer_versions(latest_version=version)

    def grant_lambda_layer_access(self: One, version: int):  # pragma: no cover
        """
        Let the account of every environment use a layer version. Idempotent.
        """
        configs = load_all_env_configs()
        account_ids = sorted({config.aws_account_id for config in configs.values()})
        for account_id in account_ids:
            simple_aws_lambda.grant_aws_account_or_aws_organization_lambda_layer_version_access(
                lambda_client=self.bsm_devops.lambda_client,
                layer_name=self.config.lambda_layer_name,
                version_number=version,
                principal=account_id,
            )
            print(f"Granted layer version {version} to account {account_id}")

    def print_lambda_layer_versions(self: One, latest_version: int):
        """
        Print the latest layer version, and the version each environment uses.
        """
        config = self.config
        print(f"Latest layer: {config.get_lambda_layer_version_arn(latest_version)}")
        print("Console (sign in to the DEVOPS account):")
        print(f"  layer version: {config.get_lambda_layer_version_url(latest_version)}")
        print(f"  all versions:  {config.lambda_layer_url}")
        print(f"  artifacts:     {config.s3dir_lambda_url}")
        print("Layer version of each environment:")
        for env_name, config in load_all_env_configs().items():
            if config.lambda_layer_version == latest_version:
                status = "up to date"
            else:
                status = (
                    f"to use the latest, set lambda_layer_version: {latest_version} "
                    f"in config/config-{env_name}.json5"
                )
            print(f"  {env_name}: version {config.lambda_layer_version}, {status}")

    def check_lambda_layer_access(self: One) -> bool:  # pragma: no cover
        """
        Check that the current environment can use its pinned layer version:
        ``GetLayerVersion`` with its own credentials, as CloudFormation will.
        A missing version and a missing grant give the same error.

        :returns: ``True`` if the layer version is usable.
        """
        config = self.config
        arn = config.lambda_layer_version_arn
        try:
            self.lambda_client.get_layer_version_by_arn(Arn=arn)
        except self.lambda_client.exceptions.ClientError as e:
            print(
                f"ERROR: env {config.env_name!r} (account {config.aws_account_id}) cannot use layer:"
            )
            print(f"  {arn}")
            print(f"  {e.response['Error']['Code']}: {e.response['Error']['Message']}")
            print(
                "Either this version does not exist in the DEVOPS account, or it is not"
            )
            print(
                "shared with this account. Run `mise run lambda-layer-deploy` (it publishes"
            )
            print("if uv.lock changed, and always grants every environment), then set")
            print(
                f"lambda_layer_version in config/config-{config.env_name}.json5 to the version it prints."
            )
            print(f"  all versions (DEVOPS account): {config.lambda_layer_url}")
            return False
        print(f"Env {config.env_name!r} can use layer {arn}")
        return True

    def cleanup_old_layer_versions(
        self: One,
        keep_last_n_versions: int = 3,
        real_run: bool = False,
    ) -> list[int]:  # pragma: no cover
        """
        Delete old layer versions in the DEVOPS account, keeping the latest
        ``keep_last_n_versions`` and every version a config on this machine pins.
        Without ``real_run`` it only prints.

        :returns: the versions to delete.
        """
        lambda_client = self.bsm_devops.lambda_client
        layer_name = self.config.lambda_layer_name
        in_use = {
            config.lambda_layer_version for config in load_all_env_configs().values()
        }
        versions = sorted(
            (
                layer_version.version
                for layer_version in simple_aws_lambda.list_layer_versions(
                    lambda_client=lambda_client,
                    layer_name=layer_name,
                )
            ),
            reverse=True,
        )
        keep = set(versions[:keep_last_n_versions]) | in_use
        to_delete = [version for version in versions if version not in keep]
        print(f"Layer {layer_name!r} versions: {versions}")
        print(
            f"  keep (latest {keep_last_n_versions} + in use {sorted(in_use)}): {sorted(keep)}"
        )
        print(f"  delete: {to_delete}")
        if real_run:
            for version in to_delete:
                lambda_client.delete_layer_version(
                    LayerName=layer_name,
                    VersionNumber=version,
                )
                print(f"  deleted version {version}")
        else:
            print("  dry run, nothing deleted")
        return to_delete

    # --------------------------------------------------------------------------
    # Source
    # --------------------------------------------------------------------------
    def build_lambda_source(self: One):  # pragma: no cover
        """
        See :func:`build_lambda_source`.
        """
        build_lambda_source()
        print(f"Built Lambda source in {path_enum.dir_build_lambda_source_build}")
