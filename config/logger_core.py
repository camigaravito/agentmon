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

def _ensure_logs_dir(dir: str = "./logs") -> str:
    os.makedirs(dir, exist_ok=True)
    return dir

def _timestamp() -> str:
    return datetime.now().strftime("%d%m%y_%H%M%S")

def _log_filepath(dir: str = "./logs") -> str:
    _ensure_logs_dir(dir)
    return os.path.join(dir, f"{_timestamp()}.log")

def _file_formatter() -> logging.Formatter:
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    datefmt = "%d-%m-%Y %H:%M:%S"
    return logging.Formatter(fmt=fmt, datefmt=datefmt)

def get_logger() -> logging.Logger:
    global _LOGGER, _LOG_FILE_PATH
    if _LOGGER:
        return _LOGGER

    load_dotenv()
    load_messages()
    level = parse_level()
    logger = logging.getLogger("project")
    logger.setLevel(level)
    logger.propagate = False

    attach_colored_console(logger, level)

    _LOG_FILE_PATH = _log_filepath()
    fh = logging.FileHandler(_LOG_FILE_PATH, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(_file_formatter())
    logger.addHandler(fh)

    _LOGGER = logger
    return logger

def get_log_file_path() -> Optional[str]:
    return _LOG_FILE_PATH

def format_message(key: str, **kwargs: Any) -> str:
    tpl = get_message(key)
    try:
        return tpl.format(**kwargs)
    except Exception:
        return f"{tpl} | {kwargs}"

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