#!/usr/bin/env python
import logging
from jpb.utils import get_env


def init_logging():
    # create console handler and set level to debug
    if get_env("JPB_DEBUG"):
        ll = logging.DEBUG
    else:
        ll = logging.INFO
    logging.basicConfig(level=ll, format="%(name)s: %(levelname)s - %(message)s")


# vim:foldmethod=marker ts=2 ft=python ai sw=2
