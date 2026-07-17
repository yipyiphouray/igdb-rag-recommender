from __future__ import annotations

from app.schemas.insights import InsightsSummary
from app.services.insights_service import get_insights_summary
from fastapi import APIRouter

router = APIRouter(tags=["insights"])


@router.get("/insights/summary", response_model=InsightsSummary)
def insights_summary() -> dict:
    return get_insights_summary()
