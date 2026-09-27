from fastapi import APIRouter

from app.api.v1 import health, i18n

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(i18n.router)
