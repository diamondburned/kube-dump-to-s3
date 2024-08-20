import logging
from .config import Config, Secrets
from . import kube_dump

import boto3
import tempfile


def run(
    config: Config,  # pyright: ignore
    secrets: Secrets | None = None,  # pyright: ignore
):
    secrets = secrets or Secrets(_secrets_dir=config.secrets_dir)  # pyright: ignore

    logger = logging.getLogger("kube-dump-to-s3")

    with tempfile.TemporaryDirectory(
        prefix="kube-dump-",
        delete=not config.debug,
    ) as tmpdir:
        kube_dump.run(
            dump=kube_dump.Dump.ALL,
            flags=kube_dump.Flags(
                destination_dir=tmpdir,
                output_by_type=True,
                detailed=True,
            ),
        )

        s3 = boto3.client(
            "s3",
            region_name=config.s3_region,
            endpoint_url=config.s3_endpoint,
            aws_access_key_id=secrets.s3_access_key,
            aws_secret_access_key=secrets.s3_secret_key,
        )
        print(s3)

        logger.debug(f"Finished dumping to {tmpdir} but not deleting it.")
