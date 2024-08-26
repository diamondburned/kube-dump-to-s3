import subprocess
import logging
import sys


def run(
    dir: str,
    output: str,
    zstd=True,
) -> None:
    """
    Run tar to create a tarball of the given directory.
    The tarball will be created in the same directory as the directory to tar.
    """

    args = ["tar", "-c", "--absolute-names", "-f", output, "-C", dir]
    if zstd:
        args.append("--zstd")
    args.append(".")

    logger = logging.getLogger("tar")
    logger.debug(f"Running {' '.join(args)}")

    subprocess.run(args, check=True, stderr=sys.stderr)
