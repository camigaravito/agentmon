from __future__ import annotations
import json
import os
from typing import Dict

_MESSAGES: Dict[str, str] = {}
_DEFAULT_MESSAGES: Dict[str, str] = {}

def load_messages(path: str | None = None) -> None:
    global _MESSAGES
    path = path or os.getenv("MESSAGE_PATH", "../src/json/messages.json")
    try:
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                _MESSAGES = json.load(f)
        else:
            _MESSAGES = _DEFAULT_MESSAGES.copy()
    except Exception:
        _MESSAGES = _DEFAULT_MESSAGES.copy()

def get_message(key: str) -> str:
    return _MESSAGES.get(key, key)