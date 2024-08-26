import subprocess
import logging
import sys
from enum import Enum
from typing import Annotated
from pydantic import BaseModel


class Flags(BaseModel):
    silent: bool = False
    destination_dir: str = "./data"
    force_remove: bool = False
    detailed: bool = False
    output_by_type: bool = False
    flat: bool = False

    namespaces: str | None = None
    namespaced_resources: str | None = None
    cluster_resources: str | None = None
    kube_config: str | None = None
    kube_context: str | None = None
    kube_cluster: str | None = None
    kube_insecure_tls: bool = False


class Dump(Enum):
    ALL = "all"
    NAMESPACES = "ns"
    CLUSTERS = "cls"


def run(
    dump: Annotated[Dump, "What to dump"],
    flags: Annotated[Flags, "Flags for kube-dump"] = Flags(),
    kube_dump: Annotated[str, "The path to the command"] = "kube-dump",
) -> None:
    logger = logging.getLogger("kube-dump")

    argv = [kube_dump, dump.value]
    for flag, value in flags.model_dump().items():
        flag = "--" + flag.replace("_", "-")
        if flag == "--destination-dir":
            # There's an upstream bug where the getopt definition is wrong.
            # This is why I didn't want to use Bash :)
            flag = "-d"

        if value is None:
            continue

        if isinstance(value, bool):
            if value:
                argv.append(flag)
            continue

        argv.append(flag)
        argv.append(str(value))

    logger.debug(f"Running {" ".join(argv)}")
    subprocess.run(
        argv,
        check=True,
        shell=False,
        stdin=subprocess.DEVNULL,
        stderr=sys.stderr,
        stdout=sys.stderr,
    )
