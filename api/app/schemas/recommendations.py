from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.schemas.catalog import GameSummary


class RecommendationRequest(BaseModel):
    platform: str | None = None
    platforms: list[str] = Field(default_factory=list)
    genres: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)
    mood_words: list[str] = Field(default_factory=list)
    favorite_games: list[str] = Field(default_factory=list)
    playstyle_preferences: list[str] = Field(default_factory=list)
    discovery_preference: str = "Balanced"
    rating_quality_importance: str = "Any rating"
    desired_playtime: str = "Any length"
    release_year_min: int | None = None
    release_year_max: int | None = None
    max_results: int = Field(default=10, ge=1, le=50)


class RecommendationResult(GameSummary):
    rank: int
    match_score: float | None = None
    recommendation_score: float | None = None
    similarity_score: float | None = None
    rating_score: float | None = None
    hidden_gem_boost: float | None = None
    explanation: str
    caveats: list[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    mode: str
    similarity_status: str
    request_summary: dict[str, Any]
    items: list[RecommendationResult]
