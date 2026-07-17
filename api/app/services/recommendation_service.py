from __future__ import annotations

from typing import Any

import pandas as pd

from app.schemas.recommendations import RecommendationRequest
from app.services.catalog_service import load_catalog, serialize_game
from src.app.metadata_cosine_recommendation import (
    MetadataCosineRecommendationOutput,
    MetadataCosineRecommender,
)
from src.app.recommendation_service import recommend_games


MAX_STRUCTURED_SCORE = 85.0

_COSINE_RECOMMENDER: MetadataCosineRecommender | None = None
_COSINE_CATALOG_ID: int | None = None


def _first_platform(request: RecommendationRequest) -> str | None:
    if request.platform:
        return request.platform
    return request.platforms[0] if request.platforms else None


def _platforms(request: RecommendationRequest) -> list[str]:
    selected: list[str] = []
    if request.platform:
        selected.append(request.platform)
    selected.extend(request.platforms)
    return list(dict.fromkeys(value for value in selected if value))


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


def _score_to_match_score(value: object) -> float | None:
    if pd.isna(value):
        return None
    return round(min(max(float(value) / MAX_STRUCTURED_SCORE, 0.0), 1.0), 3)


def _safe_float(value: object) -> float | None:
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _rounded_float(value: object, digits: int = 3) -> float | None:
    converted = _safe_float(value)
    return None if converted is None else round(converted, digits)


def _get_cosine_recommender(catalog: pd.DataFrame) -> MetadataCosineRecommender:
    global _COSINE_CATALOG_ID, _COSINE_RECOMMENDER

    catalog_id = id(catalog)
    if _COSINE_RECOMMENDER is None or _COSINE_CATALOG_ID != catalog_id:
        _COSINE_RECOMMENDER = MetadataCosineRecommender(catalog)
        _COSINE_CATALOG_ID = catalog_id
    return _COSINE_RECOMMENDER


def _has_cosine_profile_input(request: RecommendationRequest) -> bool:
    return any(
        [
            request.platform,
            request.platforms,
            request.genres,
            request.themes,
            request.mood_words,
            request.favorite_games,
            request.playstyle_preferences,
            request.desired_playtime != "Any length",
        ]
    )


def _structured_fallback_response(
    *,
    catalog: pd.DataFrame,
    request: RecommendationRequest,
    similarity_status: str = "structured_fallback_active",
    fallback_reason: str = "Metadata cosine similarity did not have enough usable input.",
) -> dict[str, Any]:
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
                    f"Using structured fallback scoring. Reason: {fallback_reason}"
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
        "similarity_status": similarity_status,
        "request_summary": {
            "hard_filters": _platforms(request),
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


def _cosine_response(
    *,
    output: MetadataCosineRecommendationOutput,
    request: RecommendationRequest,
    discovery_preference: str,
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for rank, (_, row) in enumerate(output.recommendations.iterrows(), start=1):
        recommendation_score = _rounded_float(row.get("recommendation_score"))
        game = serialize_game(row)
        game.update(
            {
                "rank": rank,
                "match_score": recommendation_score,
                "recommendation_score": recommendation_score,
                "similarity_score": _rounded_float(row.get("similarity_score_component")),
                "rating_score": _rounded_float(row.get("quality_score_component")),
                "hidden_gem_boost": _rounded_float(row.get("discovery_score_component")),
                "explanation": str(row.get("recommendation_explanation", "")),
                "caveats": list(row.get("recommendation_caveats", [])),
            }
        )
        items.append(game)

    return {
        "mode": "cosine_similarity",
        "similarity_status": "metadata_cosine_similarity_active",
        "request_summary": {
            "hard_filters": _platforms(request),
            "profile_terms": output.profile_terms,
            "favorite_games": request.favorite_games,
            "matched_seed_games": output.matched_seed_games,
            "unmatched_seed_games": output.unmatched_seed_games,
            "rating_level": _rating_level(request.rating_quality_importance),
            "discovery_preference": discovery_preference,
            "desired_playtime": request.desired_playtime,
            "ranking_adjustments": [
                "cosine_similarity",
                "rating_quality",
                "rating_evidence",
                "discovery_preference",
                "playtime_fit",
            ],
        },
        "items": items,
    }


def recommend_from_request(request: RecommendationRequest) -> dict[str, Any]:
    catalog = load_catalog()
    discovery_preference = _discovery_preference(request.discovery_preference)

    if not _has_cosine_profile_input(request):
        return _structured_fallback_response(
            catalog=catalog,
            request=request,
            fallback_reason="No platform, metadata preference, playtime preference, or recent-game seed was provided.",
        )

    try:
        output = _get_cosine_recommender(catalog).recommend(
            platform=request.platform,
            platforms=request.platforms,
            genres=request.genres,
            themes=request.themes,
            mood_words=request.mood_words,
            favorite_games=request.favorite_games,
            playstyle_preferences=request.playstyle_preferences,
            release_year_range=_release_year_range(request),
            discovery_preference=discovery_preference,
            desired_playtime=request.desired_playtime,
            top_n=request.max_results,
        )
    except (KeyError, TypeError, ValueError) as error:
        return _structured_fallback_response(
            catalog=catalog,
            request=request,
            similarity_status="metadata_cosine_unavailable_fallback_active",
            fallback_reason=f"Metadata cosine scoring could not run cleanly: {error}",
        )

    if output.recommendations.empty:
        return _structured_fallback_response(
            catalog=catalog,
            request=request,
            fallback_reason="Metadata cosine scoring did not return candidates after hard filters and seed exclusion.",
        )

    return _cosine_response(
        output=output,
        request=request,
        discovery_preference=discovery_preference,
    )
