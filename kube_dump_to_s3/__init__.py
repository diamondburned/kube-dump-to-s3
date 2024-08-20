from .config import Config, Secrets
from . import kube_dump, zstd

import boto3
import tempfile
import logging
import glob


def main():
    config = Config()  # pyright: ignore
    if config.debug:
        logging.basicConfig(level=logging.DEBUG)

    run(config)


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
                kube_config=config.kubeconfig,
                destination_dir=tmpdir,
                output_by_type=True,
                archivate=True,
                archive_type="tar",
            ),
        )

        # kube-dump doesn't give deterministic filenames, so we'll have to
        # search for one.
        dumps = glob.glob(f"{tmpdir}/dump_*.tar", recursive=False)
        assert len(dumps) == 1, dumps

        dump_tarball = dumps[0]
        logger.debug(f"Dumped to {dump_tarball}")

        if config.use_zstd:
            zstd.run([dump_tarball])
            dump_tarball += ".zst"
            logger.debug(f"Compressed to {dump_tarball}")

        s3 = boto3.client(
            "s3",
            region_name=config.s3_region,
            endpoint_url=config.s3_endpoint,
            aws_access_key_id=secrets.s3_access_key,
            aws_secret_access_key=secrets.s3_secret_key,
        )
        print(s3)

        logger.debug(f"Finished dumping to {tmpdir} but not deleting it.")
