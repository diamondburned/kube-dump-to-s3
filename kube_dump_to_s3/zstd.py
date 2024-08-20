import subprocess
import logging
import sys


def run(files: list[str], level: int | None = None) -> None:
    args = ["zstd"]
    if level:
        assert 1 <= level <= 19
        args.extend(["-{}".format(level)])
    args.append("--")
    args.extend(files)

    logger = logging.getLogger("zstd")
    logger.debug(f"Running {' '.join(args)}")

    subprocess.run(args, check=True, stderr=sys.stderr)
