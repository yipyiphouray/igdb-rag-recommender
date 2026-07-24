from __future__ import annotations

from fastapi import APIRouter

from app.schemas.recommendations import RecommendationRequest, RecommendationResponse
from app.services.recommendation_service import recommend_from_request

router = APIRouter(tags=["recommendations"])


@router.post("/recommendations", response_model=RecommendationResponse)
def recommendations(request: RecommendationRequest) -> dict:
    return recommend_from_request(request)
