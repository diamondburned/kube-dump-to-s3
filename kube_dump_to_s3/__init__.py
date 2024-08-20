from .config import Config, Secrets
from . import kube_dump, zstd

import boto3
import coloredlogs
import tempfile
import datetime
import logging
import glob
import sys


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
    now = datetime.datetime.now().isoformat(timespec="seconds")

    with tempfile.TemporaryDirectory(
        prefix="kube-dump-",
        delete=not config.debug,
    ) as tmpdir:
        logger.debug(f"Dumping to {tmpdir}")

        kube_dump.run(
            dump=kube_dump.Dump.ALL if config.cluster else kube_dump.Dump.NAMESPACES,
            flags=kube_dump.Flags(
                namespaces=",".join(config.namespaces) if config.namespaces else None,
                kube_config=config.kubeconfig,
                destination_dir=tmpdir,
                output_by_type=True,
                archivate=True,
                archive_type="tar",
                silent=not config.debug,
            ),
        )

        # kube-dump doesn't give deterministic filenames, so we'll have to
        # search for one.
        dumps = glob.glob(f"{tmpdir}/dump_*.tar", recursive=False)
        assert len(dumps) == 1, dumps

        dump_tarball = dumps[0]
        logger.info(f"Dumped to {dump_tarball}")

        if config.use_zstd:
            zstd.run([dump_tarball])
            dump_tarball += ".zst"
            logger.info(f"Compressed to {dump_tarball}")

        s3 = boto3.client(
            "s3",
            region_name=config.s3_region,
            endpoint_url=config.s3_endpoint,
            aws_access_key_id=secrets.s3_access_key,
            aws_secret_access_key=secrets.s3_secret_key,
        )

        # Make the explicit decision to generate our own name instead of using
        # what kube-dump generated. This way, we can be sure that the name is
        # what we expect for future use.
        s3_object_name = f"{now}.tar" + (".zst" if config.use_zstd else "")

        s3_key = f"{config.s3_prefix}/{s3_object_name}"
        s3_uri = f"s3://{config.s3_bucket}/{s3_key}"

        logger.info(f"Uploading to {s3_uri}")
        s3.upload_file(dump_tarball, config.s3_bucket, s3_key)

        if config.debug:
            logger.debug(f"Finished dumping to {tmpdir} but not deleting it.")
