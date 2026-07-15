from __future__ import annotations

from fastapi import APIRouter

from app.schemas.methodology import MethodologySummary
from app.services.methodology_service import get_methodology_summary

router = APIRouter(tags=["methodology"])


@router.get("/methodology/summary", response_model=MethodologySummary)
def methodology_summary() -> dict:
    return get_methodology_summary()
