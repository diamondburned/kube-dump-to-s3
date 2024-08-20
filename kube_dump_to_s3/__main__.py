import logging

from . import run
from .config import Config

config = Config()  # pyright: ignore
if config.debug:
    logging.basicConfig(level=logging.DEBUG)

run(config)
