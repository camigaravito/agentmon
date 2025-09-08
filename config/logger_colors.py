from __future__ import annotations
import logging
import os
import sys
import coloredlogs

try:
    import colorama
    colorama.just_fix_windows_console()
except ImportError:
    pass

def attach_colored_console(logger: logging.Logger, level: int) -> None:
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    datefmt = "%d-%m-%Y %H:%M:%S"
    if sys.stdout.isatty():
        coloredlogs.install(level=level, logger=logger, fmt=fmt, datefmt=datefmt)
    else:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
        logger.addHandler(ch)

def parse_level(default: int = logging.INFO) -> int:
    level_str = os.getenv("LOG_LEVEL", "").upper().strip()
    return {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }.get(level_str, default)