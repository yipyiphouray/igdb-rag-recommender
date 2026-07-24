from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from src.app.formatting import contains_any


def _as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Iterable):
        return [str(item) for item in value if str(item)]
    return []


def apply_catalog_filters(
    catalog: pd.DataFrame,
    search_text: str = "",
    release_year_range: tuple[int, int] | None = None,
    platforms: Iterable[str] | None = None,
    genres: Iterable[str] | None = None,
    themes: Iterable[str] | None = None,
    game_modes: Iterable[str] | None = None,
    perspectives: Iterable[str] | None = None,
    cohorts: Iterable[str] | None = None,
    min_rating: float | None = None,
    min_rating_count: int | None = None,
    hidden_gems_only: bool = False,
) -> pd.DataFrame:
    filtered = catalog

    if search_text:
        query = search_text.strip().lower()
        if query:
            name_match = filtered["name"].fillna("").str.lower().str.contains(query, regex=False)
            summary_match = filtered["summary"].fillna("").str.lower().str.contains(query, regex=False)
            filtered = filtered[name_match | summary_match]

    if release_year_range and "release_year" in filtered:
        start_year, end_year = release_year_range
        filtered = filtered[
            filtered["release_year"].between(start_year, end_year, inclusive="both")
        ]

    list_filters = {
        "platforms_list": _as_list(platforms),
        "genres_list": _as_list(genres),
        "themes_list": _as_list(themes),
        "game_modes_list": _as_list(game_modes),
        "player_perspectives_list": _as_list(perspectives),
    }
    for column, selected in list_filters.items():
        if selected and column in filtered:
            filtered = filtered[filtered[column].apply(lambda value: contains_any(value, selected))]

    selected_cohorts = _as_list(cohorts)
    if selected_cohorts and "extraction_cohort" in filtered:
        filtered = filtered[filtered["extraction_cohort"].isin(selected_cohorts)]

    if min_rating is not None and "total_rating" in filtered:
        filtered = filtered[filtered["total_rating"].fillna(-1) >= min_rating]

    if min_rating_count is not None and "total_rating_count" in filtered:
        filtered = filtered[filtered["total_rating_count"].fillna(0) >= min_rating_count]

    if hidden_gems_only and "hidden_gem_balanced_flag" in filtered:
        filtered = filtered[filtered["hidden_gem_balanced_flag"] == 1]

    if "game_id" in filtered.columns and filtered["game_id"].duplicated().any():
        return filtered.drop_duplicates(subset=["game_id"])
    return filtered


def sort_catalog(catalog: pd.DataFrame, sort_option: str) -> pd.DataFrame:
    if catalog.empty:
        return catalog

    sort_map = {
        "Highest rating": ("total_rating", False),
        "Most rating evidence": ("total_rating_count", False),
        "Highest visibility": ("custom_interest_percentile", False),
        "Newest release": ("release_year", False),
        "Lowest visibility among reliable high-rated games": ("custom_interest_percentile", True),
        "Best recommendation score": ("recommendation_score", False),
    }
    column, ascending = sort_map.get(sort_option, ("name", True))
    if column not in catalog.columns:
        column, ascending = "name", True
    return catalog.sort_values(column, ascending=ascending, na_position="last")

