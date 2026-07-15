from __future__ import annotations

from typing import Any

import pandas as pd

from app import config
from app.schemas.recommendations import RecommendationRequest
from app.services.catalog_service import load_catalog, serialize_game
from src.app.recommendation_service import recommend_games


MAX_STRUCTURED_SCORE = 85.0


def _first_platform(request: RecommendationRequest) -> str | None:
    if request.platform:
        return request.platform
    return request.platforms[0] if request.platforms else None


def _release_year_range(request: RecommendationRequest) -> tuple[int, int] | None:
    if request.release_year_min is None or request.release_year_max is None:
        return None
    return (request.release_year_min, request.release_year_max)


def _rating_level(value: str) -> str:
    if value in {
        "Any rating",
        "Good or better (70+)",
        "Highly rated (80+)",
        "Exceptional (90+)",
    }:
        return value

    normalized = value.strip().lower()
    if normalized in {"high", "high quality", "highly rated", "quality"}:
        return "Highly rated (80+)"
    if normalized in {"good", "medium", "balanced"}:
        return "Good or better (70+)"
    if normalized in {"exceptional", "best", "top"}:
        return "Exceptional (90+)"
    return "Any rating"


def _discovery_preference(value: str) -> str:
    normalized = value.strip().lower()
    if "hidden" in normalized:
        return "Hidden gems"
    if "popular" in normalized or "visible" in normalized:
        return "Popular / visible games"
    return "Balanced"


def _similarity_status() -> str:
    expected = [
        config.PREDICTIVE_DIR / "similarity_config.json",
        config.PREDICTIVE_DIR / "game_similarity_profiles.parquet",
    ]
    if all(path.exists() for path in expected):
        return "similarity_artifacts_available_not_integrated"
    return "structured_fallback_active"


def _score_to_match_score(value: object) -> float | None:
    if pd.isna(value):
        return None
    return round(min(max(float(value) / MAX_STRUCTURED_SCORE, 0.0), 1.0), 3)


def recommend_from_request(request: RecommendationRequest) -> dict[str, Any]:
    catalog = load_catalog()
    platform = _first_platform(request)
    rating_level = _rating_level(request.rating_quality_importance)
    discovery_preference = _discovery_preference(request.discovery_preference)

    recommendations = recommend_games(
        catalog,
        platform=platform,
        genres=request.genres,
        themes=request.themes,
        release_year_range=_release_year_range(request),
        rating_level=rating_level,
        prefer_hidden_gems=discovery_preference == "Hidden gems",
        discovery_preference=discovery_preference,
        desired_playtime=request.desired_playtime,
        top_n=request.max_results,
    )

    items: list[dict[str, Any]] = []
    for rank, (_, row) in enumerate(recommendations.iterrows(), start=1):
        game = serialize_game(row)
        recommendation_score = row.get("recommendation_score")
        game.update(
            {
                "rank": rank,
                "match_score": _score_to_match_score(recommendation_score),
                "recommendation_score": None if pd.isna(recommendation_score) else float(recommendation_score),
                "similarity_score": None,
                "rating_score": None
                if pd.isna(row.get("quality_score_component"))
                else round(float(row.get("quality_score_component")) / 15.0, 3),
                "hidden_gem_boost": None
                if pd.isna(row.get("hidden_gem_score_component"))
                else float(row.get("hidden_gem_score_component")),
                "explanation": str(row.get("recommendation_explanation", "")),
                "caveats": [
                    "Using structured fallback scoring until teammate cosine-similarity artifacts are integrated."
                ],
            }
        )
        items.append(game)

    profile_terms = [
        *request.genres,
        *request.themes,
        *request.mood_words,
        *request.playstyle_preferences,
    ]

    return {
        "mode": "structured_fallback",
        "similarity_status": _similarity_status(),
        "request_summary": {
            "hard_filters": [platform] if platform else [],
            "profile_terms": profile_terms,
            "favorite_games": request.favorite_games,
            "rating_level": rating_level,
            "discovery_preference": discovery_preference,
            "desired_playtime": request.desired_playtime,
            "ranking_adjustments": [
                "rating_quality",
                "rating_evidence",
                "hidden_gem_preference",
                "visibility_preference",
                "playtime_fit",
            ],
        },
        "items": items,
    }
