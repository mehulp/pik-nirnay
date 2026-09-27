"""Loads the curated locale catalogues from disk.

Business logic must never depend on the *content* of a translated string —
only on the localization key (CLAUDE.md, Marathi-First Requirement).
"""

import json
from functools import lru_cache
from pathlib import Path

from app.config import get_settings

_LOCALES_DIR = Path(__file__).parent / "locales"


class UnsupportedLanguageError(ValueError):
    pass


@lru_cache
def _load_catalogue(language: str) -> dict[str, str]:
    path = _LOCALES_DIR / f"{language}.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def get_catalogue(language: str) -> dict[str, str]:
    settings = get_settings()
    if language not in settings.supported_languages:
        raise UnsupportedLanguageError(language)
    return _load_catalogue(language)


def translate(key: str, language: str) -> str:
    """Look up a single key, falling back to the default language, then the key itself."""
    settings = get_settings()
    catalogue = get_catalogue(language)
    if key in catalogue:
        return catalogue[key]
    if language != settings.default_language:
        default_catalogue = get_catalogue(settings.default_language)
        if key in default_catalogue:
            return default_catalogue[key]
    return key
