from __future__ import annotations
import json
import os
from typing import Dict

_DEFAULT_MESSAGES: Dict[str, str] = {}
_MESSAGES: Dict[str, str] = {}

def load_messages(path: str | None = None) -> None:
    global _MESSAGES
    path = path or os.getenv("MESSAGE_PATH") or "../src/json/messages.json"
    try:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                _MESSAGES = json.load(f)
        else:
            _MESSAGES = dict(_DEFAULT_MESSAGES)
    except Exception:
        _MESSAGES = dict(_DEFAULT_MESSAGES)

def get_message(key: str) -> str:
    return _MESSAGES.get(key, key)
