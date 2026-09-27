from app.config import get_settings


def test_default_language_is_marathi() -> None:
    # FR-01: default interface shall be Marathi.
    assert get_settings().default_language == "mr"


def test_supported_languages_include_marathi_and_english() -> None:
    languages = get_settings().supported_languages
    assert "mr" in languages
    assert "en" in languages
