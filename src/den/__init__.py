"""Den is a home for your home's data."""

from pkg_resources import resource_string
from tempfile import gettempdir
import logging
import logging.handlers
import os

__title__ = "den"
__version__ = resource_string(__name__, "VERSION").decode()


def _configure_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(gettempdir(), os.extsep.join([name, "log"])), maxBytes=2**20)
    fmt = logging.Formatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(module)s.%(funcName)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z")
    file_handler.setFormatter(fmt)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    backoff_logger = logging.getLogger("backoff")
    backoff_logger.addHandler(console_handler)
    backoff_logger.addHandler(file_handler)
    backoff_logger.setLevel(logging.INFO)

    return logger


LOG = _configure_logger(__title__)
LOG.debug("Version %s", __version__)
