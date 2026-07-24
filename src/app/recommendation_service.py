from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from src.app.constants import MVP_RECOMMENDATION_WEIGHTS, RATING_LEVELS
from src.app.filters import apply_catalog_filters
from src.app.formatting import overlap_count


def _selected(values: Iterable[str] | None) -> list[str]:
    if values is None:
        return []
    return [str(value) for value in values if str(value)]


def _component_overlap_score(list_text: object, selected: list[str], weight: float) -> float:
    if not selected:
        return 0.0
    overlap = overlap_count(list_text, selected)
    return weight * min(overlap / max(len(selected), 1), 1.0)


def _quality_score(total_rating: object) -> float:
    if pd.isna(total_rating):
        return 0.0
    return MVP_RECOMMENDATION_WEIGHTS["quality"] * max(min(float(total_rating) / 100.0, 1.0), 0.0)


def _rating_evidence_score(total_rating_count: object, max_log_count: float) -> float:
    if pd.isna(total_rating_count) or float(total_rating_count) <= 0 or max_log_count <= 0:
        return 0.0
    return MVP_RECOMMENDATION_WEIGHTS["rating_evidence"] * (
        np.log1p(float(total_rating_count)) / max_log_count
    )


def _playtime_score(normal_playtime_hours: object, desired_playtime: str) -> float:
    if desired_playtime == "Any length" or pd.isna(normal_playtime_hours):
        return 0.0

    hours = float(normal_playtime_hours)
    if desired_playtime == "Shorter games" and hours <= 10:
        return MVP_RECOMMENDATION_WEIGHTS["playtime"]
    if desired_playtime == "Medium games" and 10 < hours <= 30:
        return MVP_RECOMMENDATION_WEIGHTS["playtime"]
    if desired_playtime == "Longer games" and hours > 30:
        return MVP_RECOMMENDATION_WEIGHTS["playtime"]
    return 0.0


def _explain(row: pd.Series, preferences: dict[str, object]) -> str:
    reasons: list[str] = []
    platform = preferences.get("platform")
    if platform:
        reasons.append(f"available on {platform}")

    genre_overlap = overlap_count(row.get("genres_list", ""), _selected(preferences.get("genres")))
    if genre_overlap:
        reasons.append("matches preferred genre(s)")

    theme_overlap = overlap_count(row.get("themes_list", ""), _selected(preferences.get("themes")))
    if theme_overlap:
        reasons.append("matches preferred theme/mood")

    if row.get("total_rating") == row.get("total_rating"):
        reasons.append(f"has a {row['total_rating']:.1f}/100 total rating")

    if row.get("total_rating_count") == row.get("total_rating_count"):
        reasons.append(f"has {row['total_rating_count']:.0f} rating-count evidence")

    if int(row.get("hidden_gem_balanced_flag", 0)) == 1:
        reasons.append("is a documented hidden-gem candidate")

    playtime_preference = preferences.get("desired_playtime")
    if playtime_preference and playtime_preference != "Any length" and row.get("normal_playtime_hours") == row.get("normal_playtime_hours"):
        reasons.append(f"has a normal playtime estimate near your {str(playtime_preference).lower()} preference")

    if not reasons:
        return "Recommended because it satisfies the current hard filters."
    return "Recommended because it " + ", ".join(reasons) + "."


def recommend_games(
    catalog: pd.DataFrame,
    platform: str | None = None,
    genres: Iterable[str] | None = None,
    themes: Iterable[str] | None = None,
    release_year_range: tuple[int, int] | None = None,
    rating_level: str = "Any rating",
    prefer_hidden_gems: bool = False,
    discovery_preference: str = "Balanced",
    desired_playtime: str = "Any length",
    top_n: int = 10,
) -> pd.DataFrame:
    selected_genres = _selected(genres)
    selected_themes = _selected(themes)
    min_rating = RATING_LEVELS.get(rating_level)

    filtered = apply_catalog_filters(
        catalog,
        release_year_range=release_year_range,
        platforms=[platform] if platform else None,
        min_rating=min_rating,
    ).copy()

    if filtered.empty:
        return filtered

    max_log_count = float(np.log1p(filtered["total_rating_count"].fillna(0).max()))
    filtered["genre_score"] = filtered["genres_list"].apply(
        lambda value: _component_overlap_score(value, selected_genres, MVP_RECOMMENDATION_WEIGHTS["genre"])
    )
    filtered["theme_score"] = filtered["themes_list"].apply(
        lambda value: _component_overlap_score(value, selected_themes, MVP_RECOMMENDATION_WEIGHTS["theme"])
    )
    filtered["quality_score_component"] = filtered["total_rating"].apply(_quality_score)
    filtered["rating_evidence_score"] = filtered["total_rating_count"].apply(
        lambda value: _rating_evidence_score(value, max_log_count)
    )
    hidden_preference = prefer_hidden_gems or discovery_preference == "Hidden gems"
    filtered["hidden_gem_score_component"] = np.where(
        hidden_preference,
        filtered["hidden_gem_balanced_flag"].fillna(0).astype(int)
        * MVP_RECOMMENDATION_WEIGHTS["hidden_gem"],
        0,
    )
    filtered["visibility_score_component"] = np.where(
        discovery_preference == "Popular / visible games",
        filtered["custom_interest_percentile"].fillna(0) * MVP_RECOMMENDATION_WEIGHTS["visibility"],
        0,
    )
    filtered["playtime_score_component"] = filtered["normal_playtime_hours"].apply(
        lambda value: _playtime_score(value, desired_playtime)
    )
    filtered["recommendation_score"] = (
        filtered["genre_score"]
        + filtered["theme_score"]
        + filtered["quality_score_component"]
        + filtered["rating_evidence_score"]
        + filtered["hidden_gem_score_component"]
        + filtered["visibility_score_component"]
        + filtered["playtime_score_component"]
    ).round(3)

    preferences = {
        "platform": platform,
        "genres": selected_genres,
        "themes": selected_themes,
        "rating_level": rating_level,
        "prefer_hidden_gems": hidden_preference,
        "discovery_preference": discovery_preference,
        "desired_playtime": desired_playtime,
    }
    filtered["recommendation_explanation"] = filtered.apply(lambda row: _explain(row, preferences), axis=1)
    return filtered.sort_values(
        ["recommendation_score", "total_rating", "total_rating_count"],
        ascending=False,
        na_position="last",
    ).head(top_n)

