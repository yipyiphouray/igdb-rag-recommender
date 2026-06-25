from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from src.app.constants import HIDDEN_GEM_VISIBILITY_PERCENTILE, MIN_RATING_COUNT, QUALITY_THRESHOLD
from src.app.filters import apply_catalog_filters


SENSITIVITY_RULES = {
    "Conservative": {"rating": 85, "visibility": 0.25},
    "Balanced": {"rating": QUALITY_THRESHOLD, "visibility": HIDDEN_GEM_VISIBILITY_PERCENTILE},
    "Broad": {"rating": 75, "visibility": 0.50},
}


def filter_hidden_gems(
    hidden_gems: pd.DataFrame,
    catalog: pd.DataFrame | None = None,
    sensitivity: str = "Balanced",
    release_year_range: tuple[int, int] | None = None,
    platforms: Iterable[str] | None = None,
    genres: Iterable[str] | None = None,
    themes: Iterable[str] | None = None,
    min_rating: float | None = None,
    min_rating_count: int | None = None,
) -> pd.DataFrame:
    rule = SENSITIVITY_RULES.get(sensitivity, SENSITIVITY_RULES["Balanced"])

    if sensitivity == "Balanced" or catalog is None:
        source = hidden_gems.copy()
    else:
        source = catalog[
            (catalog["extraction_cohort"] == "quality")
            & (catalog["main_game_flag"] == 1)
            & (catalog["popscore_available_flag"] == 1)
            & (catalog["rating_reliable_flag"] == 1)
            & (catalog["total_rating"].fillna(-1) >= rule["rating"])
            & (catalog["visibility_percentile_eligible_pool"].fillna(1) <= rule["visibility"])
        ].copy()
        source["hidden_gem_version"] = sensitivity
        source["hidden_gem_score"] = (
            (source["total_rating"].fillna(0) / 100.0) * 0.65
            + source["inverse_visibility_percentile"].fillna(0) * 0.35
        )
        source["candidate_explanation"] = source.apply(
            lambda row: (
                f"{row['name']} matches the {sensitivity.lower()} view with "
                f"a {row['total_rating']:.1f}/100 rating, {row['total_rating_count']:.0f} ratings, "
                f"and low known visibility in the current sample."
            ),
            axis=1,
        )

    source = apply_catalog_filters(
        source,
        release_year_range=release_year_range,
        platforms=platforms,
        genres=genres,
        themes=themes,
        min_rating=min_rating if min_rating is not None else rule["rating"],
        min_rating_count=min_rating_count if min_rating_count is not None else MIN_RATING_COUNT,
    )
    return source.sort_values(["hidden_gem_score", "total_rating"], ascending=False, na_position="last")


def hidden_gem_rule_text(sensitivity: str = "Balanced") -> str:
    rule = SENSITIVITY_RULES.get(sensitivity, SENSITIVITY_RULES["Balanced"])
    return (
        f"{sensitivity}: quality cohort, main game, reliable rating count >= {MIN_RATING_COUNT}, "
        f"total rating >= {rule['rating']}, PopScore-known, and visibility percentile <= {rule['visibility']:.0%}."
    )
