"""Tiny translation layer. Stores KEYS in data; resolves to text at display time
so switching language never mutates results. Falls back to English, then key.
"""
from __future__ import annotations

import json

from ..core import paths

_DEFAULT = "en"


class Translator:
    def __init__(self, lang: str = "id") -> None:
        self._fallback = _load(_DEFAULT)
        self._lang = lang
        self._strings = _load(lang)

    def set_language(self, lang: str) -> None:
        self._lang = lang
        self._strings = _load(lang)

    @property
    def language(self) -> str:
        return self._lang

    def t(self, key: str) -> str:
        return self._strings.get(key) or self._fallback.get(key) or key

    def __call__(self, key: str) -> str:
        return self.t(key)


def _load(lang: str) -> dict:
    for rel in (f"abilithic_scan/i18n/locales/{lang}.json",
                f"i18n/locales/{lang}.json"):
        try:
            with open(paths.resource_path(rel), "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            continue
    return {}


def available_languages() -> list:
    return ["id", "en"]
