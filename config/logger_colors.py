from __future__ import annotations
import logging
import os
import sys
from typing import Optional

import coloredlogs

try:
    import colorama
    colorama.just_fix_windows_console()
except Exception:
    pass

def attach_colored_console(logger: logging.Logger, level: int) -> None:
    is_tty = sys.stdout.isatty()
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    datefmt = "%d-%m-%Y %H:%M:%S"

    if is_tty:
        coloredlogs.install(level=level, logger=logger, fmt=fmt, datefmt=datefmt)
    else:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
        logger.addHandler(ch)

def parse_level(default: int = logging.INFO) -> int:
    level_str = (os.getenv("LOG_LEVEL") or "").upper().strip()
    mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return mapping.get(level_str, default)
