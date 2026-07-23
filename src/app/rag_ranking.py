from __future__ import annotations

import math
from typing import Any


DEFAULT_RELEVANCE_WEIGHT = 0.60
DEFAULT_POPULARITY_WEIGHT = 0.18
DEFAULT_RATING_COUNT_WEIGHT = 0.10
DEFAULT_RATING_WEIGHT = 0.08
DEFAULT_CONFIDENCE_WEIGHT = 0.04
DEFAULT_HIDDEN_GEM_PENALTY = 0.08

HIDDEN_RELEVANCE_WEIGHT = 0.55
HIDDEN_POPULARITY_WEIGHT = 0.10
HIDDEN_RATING_COUNT_WEIGHT = 0.12
HIDDEN_RATING_WEIGHT = 0.12
HIDDEN_CONFIDENCE_WEIGHT = 0.06
HIDDEN_GEM_BOOST = 0.15

RATING_COUNT_LOG_CAP = 1000


def safe_float(value: object, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        parsed = float(value)
    except Exception:
        return default
    if math.isnan(parsed) or math.isinf(parsed):
        return default
    return parsed


def safe_bool(value: object) -> bool:
    if value is None:
        return False
    try:
        return bool(int(float(value)))
    except Exception:
        return bool(value)


def clamp01(value: object) -> float:
    return max(0.0, min(1.0, safe_float(value, 0.0)))


def normalize_percentile(value: object) -> float:
    parsed = safe_float(value, 0.0)
    if parsed > 1.0:
        parsed = parsed / 100.0
    return clamp01(parsed)


def rating_count_score(value: object) -> float:
    count = max(0.0, safe_float(value, 0.0))
    if count <= 0:
        return 0.0
    return clamp01(math.log1p(count) / math.log1p(RATING_COUNT_LOG_CAP))


def rating_score(value: object) -> float:
    rating = safe_float(value, 0.0)
    if rating > 1.0:
        rating = rating / 100.0
    return clamp01(rating)


def metadata_confidence_score(candidate: dict[str, Any]) -> float:
    checks = [
        bool(str(candidate.get("summary") or "").strip()),
        bool(str(candidate.get("genres") or candidate.get("genres_list") or "").strip()),
        bool(str(candidate.get("themes") or candidate.get("themes_list") or "").strip()),
        bool(str(candidate.get("platforms") or candidate.get("platforms_list") or "").strip()),
        safe_float(candidate.get("total_rating_count"), 0.0) > 0,
    ]
    return sum(1 for item in checks if item) / len(checks)


def extraction_cohort_boost(value: object, *, hidden_gem_mode: bool) -> float:
    cohort = str(value or "").strip().lower()
    if hidden_gem_mode:
        if "hidden" in cohort:
            return 0.04
        if "quality" in cohort:
            return 0.03
        return 0.0

    if "popularity" in cohort:
        return 0.06
    if "quality" in cohort:
        return 0.04
    return 0.0


def has_hidden_gem_intent(query: str | None = None, ranking_mode: str | None = None) -> bool:
    mode = str(ranking_mode or "").strip().lower()
    if mode in {"hidden", "hidden_gem", "hidden_gems", "underrated", "overlooked"}:
        return True

    normalized = str(query or "").lower()
    return any(
        phrase in normalized
        for phrase in (
            "hidden gem",
            "hidden gems",
            "underrated",
            "overlooked",
            "less obvious",
            "lesser known",
            "less-known",
            "niche",
        )
    )


def compute_ranking_scores(
    candidate: dict[str, Any],
    *,
    hidden_gem_mode: bool = False,
) -> dict[str, float | str]:
    metadata_boost = safe_float(candidate.get("metadata_boost", 0.0), 0.0)
    normalized_vec = safe_float(candidate.get("normalized_vec", candidate.get("semantic_score", 0.0)), 0.0)
    normalized_bm25 = safe_float(candidate.get("normalized_bm25", candidate.get("bm25_score_norm", 0.0)), 0.0)
    semantic_weight = safe_float(candidate.get("vector_weight", 0.8), 0.8)
    lexical_weight = safe_float(candidate.get("bm25_weight", 0.2), 0.2)
    hybrid_rrf = safe_float(candidate.get("hybrid_score", 0.0), 0.0)

    weighted_hybrid = (semantic_weight * normalized_vec) + (lexical_weight * normalized_bm25)
    relevance_score = clamp01(metadata_boost + max(hybrid_rrf, weighted_hybrid))

    popularity_score = normalize_percentile(
        candidate.get("custom_interest_percentile", candidate.get("custom_interest_score", 0.0))
    )
    review_volume_score = rating_count_score(candidate.get("total_rating_count", 0.0))
    quality_score = rating_score(candidate.get("total_rating", 0.0))
    confidence_score = metadata_confidence_score(candidate)
    hidden_gem_flag = 1.0 if safe_bool(candidate.get("hidden_gem_balanced_flag", False)) else 0.0
    cohort_boost = extraction_cohort_boost(
        candidate.get("extraction_cohort"),
        hidden_gem_mode=hidden_gem_mode,
    )

    if hidden_gem_mode:
        final_score = (
            HIDDEN_RELEVANCE_WEIGHT * relevance_score
            + HIDDEN_POPULARITY_WEIGHT * popularity_score
            + HIDDEN_RATING_COUNT_WEIGHT * review_volume_score
            + HIDDEN_RATING_WEIGHT * quality_score
            + HIDDEN_CONFIDENCE_WEIGHT * confidence_score
            + HIDDEN_GEM_BOOST * hidden_gem_flag
            + cohort_boost
        )
        ranking_profile = "hidden_gem"
        hidden_adjustment = HIDDEN_GEM_BOOST * hidden_gem_flag
    else:
        hidden_penalty = DEFAULT_HIDDEN_GEM_PENALTY * hidden_gem_flag
        final_score = (
            DEFAULT_RELEVANCE_WEIGHT * relevance_score
            + DEFAULT_POPULARITY_WEIGHT * popularity_score
            + DEFAULT_RATING_COUNT_WEIGHT * review_volume_score
            + DEFAULT_RATING_WEIGHT * quality_score
            + DEFAULT_CONFIDENCE_WEIGHT * confidence_score
            + cohort_boost
            - hidden_penalty
        )
        ranking_profile = "default_quality_popularity"
        hidden_adjustment = -hidden_penalty

    return {
        "ranking_profile": ranking_profile,
        "weighted_hybrid_score": weighted_hybrid,
        "relevance_score": relevance_score,
        "popularity_score": popularity_score,
        "rating_count_score": review_volume_score,
        "quality_score": quality_score,
        "metadata_confidence_score": confidence_score,
        "hidden_gem_adjustment": hidden_adjustment,
        "cohort_boost": cohort_boost,
        "primary_rank_score": final_score,
    }


def rank_candidates(
    candidates: list[dict[str, Any]],
    *,
    hidden_gem_mode: bool = False,
    graphics_preference: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not candidates:
        return []

    graphics_preference = graphics_preference or {}
    request_2d = bool(graphics_preference.get("request_2d", False))
    avoid_3d = bool(graphics_preference.get("avoid_3d", False))
    two_d_boost = safe_float(graphics_preference.get("two_d_boost", 1.5), 1.5)
    three_d_penalty = safe_float(graphics_preference.get("three_d_penalty", 0.1), 0.1)

    for candidate in candidates:
        scores = compute_ranking_scores(candidate, hidden_gem_mode=hidden_gem_mode)
        candidate.update(scores)

        multiplier = 1.0
        candidate["penalty_applied"] = False
        candidate["boost_applied"] = False
        if (request_2d or avoid_3d) and bool(candidate.get("is_3d_detected", False)):
            multiplier *= three_d_penalty
            candidate["penalty_applied"] = True
        if request_2d and bool(candidate.get("is_2d_detected", False)):
            multiplier *= two_d_boost
            candidate["boost_applied"] = True

        candidate["constraint_multiplier"] = multiplier
        candidate["primary_rank_score"] = safe_float(candidate.get("primary_rank_score"), 0.0) * multiplier

    return sorted(
        candidates,
        key=lambda item: (
            -safe_float(item.get("primary_rank_score", 0.0), 0.0),
            -safe_float(item.get("relevance_score", 0.0), 0.0),
            safe_float(item.get("distance", 1.0), 1.0),
        ),
    )
