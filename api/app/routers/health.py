from __future__ import annotations

from fastapi import APIRouter

from app import config

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": config.API_NAME,
        "version": config.API_VERSION,
    }
