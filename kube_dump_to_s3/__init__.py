from .config import Config, Secrets
from . import kube_dump, tar

import boto3
import coloredlogs
import tempfile
import datetime
import logging
import sys
import os


def main() -> None:
    config = Config()  # pyright: ignore
    coloredlogs.install(level="DEBUG" if config.debug else "INFO")

    try:
        run(config)
    except Exception as e:
        logging.error(e)
        sys.exit(1)


def run(
    config: Config,  # pyright: ignore
    secrets: Secrets | None = None,  # pyright: ignore
) -> None:
    secrets = secrets or Secrets(_secrets_dir=config.secrets_dir)  # pyright: ignore
    logger = logging.getLogger("kube-dump-to-s3")
    now = int(datetime.datetime.now().timestamp())

    s3 = boto3.client(
        "s3",
        region_name=config.s3_region,
        endpoint_url=config.s3_endpoint,
        aws_access_key_id=secrets.s3_access_key,
        aws_secret_access_key=secrets.s3_secret_key,
    )

    with tempfile.TemporaryDirectory(
        prefix="kube-dump-",
        delete=not config.debug,
    ) as tmpdir:
        logger.debug(f"Dumping to {tmpdir}")

        kube_dump_out = os.path.join(tmpdir, "dump")
        kube_dump.run(
            dump=kube_dump.Dump.ALL if config.cluster else kube_dump.Dump.NAMESPACES,
            flags=kube_dump.Flags(
                namespaces=",".join(config.namespaces) if config.namespaces else None,
                kube_config=config.kubeconfig,
                destination_dir=kube_dump_out,
                output_by_type=True,
                silent=not config.debug,
            ),
        )

        logger.debug(f"Dumped to {kube_dump_out}")

        tar_name = f"kube-dump-{now}.tar" + (".zst" if config.use_zstd else "")
        tar_out = os.path.join(tmpdir, tar_name)
        tar.run(kube_dump_out, tar_out, zstd=config.use_zstd)

        logger.debug(f"Tarballed to {tar_out}")

        s3_key = f"{config.s3_prefix}/{tar_name}"
        s3_uri = f"s3://{config.s3_bucket}/{s3_key}"

        logger.info(f"Uploading to {s3_uri}")
        s3.upload_file(tar_out, config.s3_bucket, s3_key)

        if config.debug:
            logger.debug(f"Finished dumping to {tmpdir} but not deleting it.")
