from fastapi import APIRouter

from app.config import get_settings
from app.db.session import database_is_reachable

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
def liveness() -> dict[str, str]:
    """Process is up. Does not depend on any external service."""
    settings = get_settings()
    return {"status": "ok", "service": settings.app_name}


@router.get("/ready")
def readiness() -> dict[str, str | bool]:
    """Whether dependencies (currently: the database) are reachable.

    A down database degrades this endpoint but must not crash the process
    (CLAUDE.md, Architecture Principles — graceful degradation).
    """
    db_ok = database_is_reachable()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": db_ok,
    }
