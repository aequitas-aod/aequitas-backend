import logging
import utils.env

if utils.env.is_testing():
    DEFAULT_LOG_LEVEL = logging.DEBUG
    logging.basicConfig(level=DEFAULT_LOG_LEVEL)
else:
    DEFAULT_LOG_LEVEL = logging.ERROR

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


def set_loggers_level(selector, level: int | str = DEFAULT_LOG_LEVEL):
    if isinstance(level, str):
        level = logging.ERROR
    for l in _all_loggers():
        if selector(l):
            l.setLevel(level)


def set_other_loggers_level(level: int | str = logging.ERROR):
    critical_loggers = _our_loggers()
    set_loggers_level(lambda l: l not in critical_loggers, level)
