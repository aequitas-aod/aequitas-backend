import logging
from typing import Callable

import utils.env

if utils.env.is_testing():
    DEFAULT_LOG_LEVEL = logging.DEBUG
    logging.basicConfig(level=DEFAULT_LOG_LEVEL)
else:
    DEFAULT_LOG_LEVEL = logging.INFO

logger = logging.getLogger("aequitas.backend")
logger.setLevel(DEFAULT_LOG_LEVEL)


def _all_loggers(root=logging.root):
    return {root} | {logging.getLogger(l) for l in root.manager.loggerDict}


def _our_loggers():
    result = set()
    l = logger
    while l is not None:
        result.add(l)
        l = l.parent
    return result


def set_loggers_level(selector: Callable, level: int | str = DEFAULT_LOG_LEVEL):
    if isinstance(level, str):
        level = logging.ERROR
    for l in _all_loggers():
        if selector(l):
            l.setLevel(level)


def set_other_loggers_level(level: int | str = logging.ERROR):
    set_loggers_level(lambda l: l not in _our_loggers(), level)


# if testing, lowers the visibility of non-aequitas logs
if utils.env.is_testing():
    set_other_loggers_level()
