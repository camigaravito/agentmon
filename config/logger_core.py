from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Optional

from dotenv import load_dotenv
from .logger_colors import attach_colored_console, parse_level
from .messages import get_message, load_messages

_LOGGER: Optional[logging.Logger] = None
_LOG_FILE_PATH: Optional[str] = None

def _ensure_logs_dir(logs_dir: str = "./logs") -> str:
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir

def _timestamp_filename() -> str:
    return datetime.now().strftime("%d%m%y_%H%M%S")

def _build_log_filepath(logs_dir: str = "./logs") -> str:
    _ensure_logs_dir(logs_dir)
    return os.path.join(logs_dir, f"{_timestamp_filename()}.log")

def _file_formatter() -> logging.Formatter:
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    datefmt = "%d-%m-%Y %H:%M:%S"
    return logging.Formatter(fmt=fmt, datefmt=datefmt)

def get_logger() -> logging.Logger:
    global _LOGGER, _LOG_FILE_PATH
    if _LOGGER is not None:
        return _LOGGER

    load_dotenv()
    load_messages()

    level = parse_level()
    logger = logging.getLogger("project")
    logger.setLevel(level)
    logger.propagate = False

    attach_colored_console(logger, level)

    _LOG_FILE_PATH = _build_log_filepath()
    fh = logging.FileHandler(_LOG_FILE_PATH, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(_file_formatter())
    logger.addHandler(fh)

    _LOGGER = logger
    return logger

def get_log_file_path() -> Optional[str]:
    return _LOG_FILE_PATH

def format_message(key: str, **kwargs: Any) -> str:
    template = get_message(key)
    try:
        return template.format(**kwargs)
    except Exception:
        return f"{template} | {kwargs}"

def log_msg(level: str, key: str, **kwargs: Any) -> None:
    logger = get_logger()
    msg = format_message(key, **kwargs)
    lvl = level.lower()
    if lvl == "debug":
        logger.debug(msg)
    elif lvl == "info":
        logger.info(msg)
    elif lvl == "warning":
        logger.warning(msg)
    elif lvl == "error":
        logger.error(msg)
    elif lvl == "critical":
        logger.critical(msg)
    else:
        logger.info(msg)