from __future__ import annotations

from typing import Any

import math
import os
import re

import pandas as pd

from app.schemas.recommendations import RecommendationRequest
from app.services.catalog_service import load_catalog, serialize_game
from src.app.filters import apply_catalog_filters
from src.app.formatting import split_list
from src.app.metadata_cosine_recommendation import (
    MetadataCosineRecommendationOutput,
    MetadataCosineRecommender,
)
from src.app.recommendation_service import recommend_games


MAX_STRUCTURED_SCORE = 85.0
DEFAULT_COSINE_CANDIDATE_LIMIT = 2500
MIN_COSINE_CANDIDATE_LIMIT = 300


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


def _cosine_candidate_limit() -> int:
    raw_value = os.getenv("RECOMMENDATION_COSINE_CANDIDATE_LIMIT", "")
    if not raw_value:
        return DEFAULT_COSINE_CANDIDATE_LIMIT
    try:
        return max(MIN_COSINE_CANDIDATE_LIMIT, int(raw_value))
    except ValueError:
        return DEFAULT_COSINE_CANDIDATE_LIMIT


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


def _normalized_selected(values: list[str]) -> set[str]:
    return {value.strip().lower() for value in values if value and value.strip()}


def _normalize_title(value: object) -> str:
    text = "" if value is None else str(value).strip().lower()
    text = re.sub(r"[â€™']", "", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _overlap_count(value: object, selected_values: set[str]) -> int:
    if not selected_values:
        return 0
    return sum(
        1
        for item in split_list(value)
        if item.strip().lower() in selected_values
    )


def _candidate_priority_score(row: pd.Series, request: RecommendationRequest) -> float:
    rating = _safe_float(row.get("total_rating")) or 0.0
    rating_count = max(_safe_float(row.get("total_rating_count")) or 0.0, 0.0)
    interest_percentile = _safe_float(row.get("custom_interest_percentile")) or 0.0

    selected_genres = _normalized_selected(request.genres)
    selected_themes = _normalized_selected(request.themes)
    selected_platforms = _normalized_selected(_platforms(request))

    score = 0.0
    score += min(max(rating / 100.0, 0.0), 1.0) * 2.0
    score += math.log1p(rating_count) * 0.35
    score += min(max(interest_percentile, 0.0), 1.0) * 1.0
    score += _overlap_count(row.get("genres_list"), selected_genres) * 2.0
    score += _overlap_count(row.get("themes_list"), selected_themes) * 1.25
    score += _overlap_count(row.get("platforms_list"), selected_platforms) * 1.0

    if "hidden" in request.discovery_preference.strip().lower():
        score += 2.0 if _safe_float(row.get("hidden_gem_balanced_flag")) == 1 else 0.0

    return score


def _has_preference_overlap(row: pd.Series, request: RecommendationRequest) -> bool:
    selected_genres = _normalized_selected(request.genres)
    selected_themes = _normalized_selected(request.themes)

    return bool(
        _overlap_count(row.get("genres_list"), selected_genres)
        or _overlap_count(row.get("themes_list"), selected_themes)
    )


def _seed_rows(catalog: pd.DataFrame, request: RecommendationRequest) -> pd.DataFrame:
    if not request.favorite_games or "name" not in catalog.columns:
        return catalog.iloc[0:0]

    wanted_titles = {
        _normalize_title(title)
        for title in request.favorite_games
        if _normalize_title(title)
    }
    if not wanted_titles:
        return catalog.iloc[0:0]

    normalized_names = catalog["name"].map(_normalize_title)
    return catalog[normalized_names.isin(wanted_titles)]


def _candidate_catalog_for_cosine(
    catalog: pd.DataFrame,
    request: RecommendationRequest,
) -> pd.DataFrame:
    """Limit cosine vectorization to a deployment-safe candidate pool.

    The full catalog can be large enough to crash or time out a free hosted
    backend when vectors are built on demand. Hard filters are applied first,
    then a relevance/quality priority score keeps the best candidate pool for
    cosine ranking.
    """

    filtered = apply_catalog_filters(
        catalog,
        release_year_range=_release_year_range(request),
        platforms=_platforms(request),
    )
    if filtered.empty:
        return filtered

    limit = _cosine_candidate_limit()

    if request.genres or request.themes:
        preference_matched = filtered[
            filtered.apply(lambda row: _has_preference_overlap(row, request), axis=1)
        ]
        minimum_preference_pool = max(request.max_results * 30, MIN_COSINE_CANDIDATE_LIMIT)
        if len(preference_matched) >= minimum_preference_pool:
            filtered = preference_matched

    if len(filtered) <= limit:
        limited = filtered
    else:
        prioritized = filtered.copy()
        prioritized["_cosine_candidate_priority"] = prioritized.apply(
            lambda row: _candidate_priority_score(row, request),
            axis=1,
        )
        limited = prioritized.sort_values(
            [
                "_cosine_candidate_priority",
                "total_rating_count",
                "total_rating",
                "custom_interest_percentile",
            ],
            ascending=False,
            na_position="last",
        ).head(limit)
        limited = limited.drop(columns=["_cosine_candidate_priority"], errors="ignore")

    seeds = _seed_rows(catalog, request)
    if not seeds.empty:
        limited = pd.concat([limited, seeds], axis=0)
        limited = limited.drop_duplicates(subset=["game_id"], keep="first")

    return limited


def _recommend_with_cosine(
    *,
    catalog: pd.DataFrame,
    request: RecommendationRequest,
    discovery_preference: str,
) -> MetadataCosineRecommendationOutput:
    recommender = MetadataCosineRecommender(catalog)
    return recommender.recommend(
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
        cosine_catalog = _candidate_catalog_for_cosine(catalog, request)
        output = _recommend_with_cosine(
            catalog=cosine_catalog,
            request=request,
            discovery_preference=discovery_preference,
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
