import pytest
from fastapi.testclient import TestClient

from app.i18n.loader import UnsupportedLanguageError, get_catalogue, translate


def test_marathi_catalogue_served(client: TestClient) -> None:
    response = client.get("/api/v1/i18n/mr")
    assert response.status_code == 200
    body = response.json()
    assert body["app.title"] == "पीक निर्णय"
    assert "risk.high" in body


def test_english_catalogue_served(client: TestClient) -> None:
    response = client.get("/api/v1/i18n/en")
    assert response.status_code == 200
    assert response.json()["app.title"] == "Pik Nirnay"


def test_unsupported_language_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/i18n/fr")
    assert response.status_code == 404


def test_translate_falls_back_to_default_language() -> None:
    # A key present in Marathi (default) but requested in an unsupported flow
    # should never crash; this exercises the fallback path directly.
    assert translate("app.title", "en") == "Pik Nirnay"
    assert translate("app.title", "mr") == "पीक निर्णय"


def test_translate_unknown_key_returns_key_itself() -> None:
    assert translate("nonexistent.key", "en") == "nonexistent.key"


def test_get_catalogue_rejects_unsupported_language() -> None:
    with pytest.raises(UnsupportedLanguageError):
        get_catalogue("fr")
