from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


SECRETS_DIR = "/run/secrets"


class Secrets(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir=SECRETS_DIR)

    s3_access_key: str = Field(description="AWS access key")
    s3_secret_key: str = Field(description="AWS secret key")

    @staticmethod
    def secrets_str() -> str:
        """
        Returns the list of wanted secrets as a string for documentation.
        """
        fields = Secrets.model_fields
        field_names = ", ".join(fields.keys())
        return field_names


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        cli_prog_name="kube-dump-to-s3",
        cli_parse_args=True,
        cli_avoid_json=True,
    )

    debug: bool = Field(
        default=False,
        description="Debug mode (logging + keep export dir)",
    )

    use_zstd: bool = Field(
        default=True,
        description="Compress the final tarball with zstd (otherwise, tar will be used)",
    )

    kubeconfig: str = Field(description="Path to the kubeconfig file")
    namespaces: list[str] | None = Field(
        default=None,
        description="List of namespaces to dump (none = all namespaces)",
    )
    cluster: bool = Field(
        default=True,
        description="Include cluster-wide resources",
    )

    s3_prefix: str = Field(default="kube-dump", description="Prefix for the S3 keys")
    s3_bucket: str = Field(description="S3 bucket name")
    s3_region: str = Field(description="AWS region")
    s3_endpoint: str = Field(description="S3 endpoint URL")

    secrets_dir: str = Field(
        default=SECRETS_DIR,
        description=f"Directory for secrets (want files: {Secrets.secrets_str()})",
    )
