from fastapi import APIRouter, HTTPException

from app.i18n.loader import UnsupportedLanguageError, get_catalogue

router = APIRouter(prefix="/i18n", tags=["i18n"])


@router.get("/{language}")
def get_locale_catalogue(language: str) -> dict[str, str]:
    """Return the full localization catalogue for a supported language."""
    try:
        return get_catalogue(language)
    except UnsupportedLanguageError as exc:
        raise HTTPException(status_code=404, detail=f"Unsupported language: {exc}") from exc
