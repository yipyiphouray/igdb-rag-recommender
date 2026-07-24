from __future__ import annotations

import json
import math
from collections.abc import Iterable
from functools import lru_cache
from typing import Any

import pandas as pd

from app import config
from src.app.filters import apply_catalog_filters, sort_catalog
from src.app.formatting import compact_text, split_list


SORT_OPTIONS = {
    "name": "name",
    "highest_rating": "Highest rating",
    "most_rating_evidence": "Most rating evidence",
    "highest_visibility": "Highest visibility",
    "newest_release": "Newest release",
    "lowest_visibility": "Lowest visibility among reliable high-rated games",
}


@lru_cache(maxsize=1)
def load_catalog() -> pd.DataFrame:
    if not config.APP_CATALOG_PATH.exists():
        raise FileNotFoundError(f"Missing app catalog artifact: {config.APP_CATALOG_PATH}")
    return pd.read_parquet(config.APP_CATALOG_PATH)


@lru_cache(maxsize=1)
def load_filter_options() -> dict[str, Any]:
    if not config.APP_FILTER_OPTIONS_PATH.exists():
        return {}
    with config.APP_FILTER_OPTIONS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    try:
        result = pd.isna(value)
    except (TypeError, ValueError):
        return False
    if isinstance(result, bool):
        return result
    return False


def _safe_str(value: object) -> str | None:
    if _is_missing(value):
        return None
    text = str(value).strip()
    return text or None


def _safe_int(value: object) -> int | None:
    if _is_missing(value):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_float(value: object) -> float | None:
    if _is_missing(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_bool(value: object) -> bool:
    if _is_missing(value):
        return False
    try:
        return bool(int(value))
    except (TypeError, ValueError):
        return bool(value)


def _row_value(row: pd.Series | dict[str, Any], key: str, default: Any = None) -> Any:
    if isinstance(row, pd.Series):
        return row.get(key, default)
    return row.get(key, default)


def serialize_game(row: pd.Series | dict[str, Any], *, detail: bool = False) -> dict[str, Any]:
    summary = _safe_str(_row_value(row, "summary")) if detail else compact_text(_row_value(row, "summary"), max_chars=280)

    game: dict[str, Any] = {
        "game_id": int(_row_value(row, "game_id")),
        "name": _safe_str(_row_value(row, "name")) or "Unknown title",
        "slug": _safe_str(_row_value(row, "slug")),
        "release_year": _safe_int(_row_value(row, "release_year")),
        "cover_url": _safe_str(_row_value(row, "cover_url")),
        "screenshot_url": _safe_str(_row_value(row, "screenshot_url")),
        "summary": summary or None,
        "total_rating": _safe_float(_row_value(row, "total_rating")),
        "total_rating_count": _safe_int(_row_value(row, "total_rating_count")),
        "custom_interest_score": _safe_float(_row_value(row, "custom_interest_score")),
        "custom_interest_percentile": _safe_float(_row_value(row, "custom_interest_percentile")),
        "extraction_cohort": _safe_str(_row_value(row, "extraction_cohort")),
        "platforms": split_list(_row_value(row, "platforms_list")),
        "genres": split_list(_row_value(row, "genres_list")),
        "themes": split_list(_row_value(row, "themes_list")),
        "game_modes": split_list(_row_value(row, "game_modes_list")),
        "player_perspectives": split_list(_row_value(row, "player_perspectives_list")),
        "normal_playtime_hours": _safe_float(_row_value(row, "normal_playtime_hours")),
        "hidden_gem_balanced_flag": _safe_bool(_row_value(row, "hidden_gem_balanced_flag")),
        "rag_ready_flag": _safe_bool(_row_value(row, "rag_ready_flag")),
    }

    if detail:
        caveats: list[str] = []
        if game["total_rating"] is None:
            caveats.append("Total rating is missing in the project data.")
        if game["custom_interest_score"] is None:
            caveats.append("PopScore interest is missing, so visibility should be treated as unknown.")
        if not game["summary"]:
            caveats.append("Summary text is missing, so this game may be less useful for RAG retrieval.")

        game.update(
            {
                "storyline": _safe_str(_row_value(row, "storyline")),
                "keywords": split_list(_row_value(row, "keywords_list")),
                "developers": split_list(_row_value(row, "developers_list")),
                "publishers": split_list(_row_value(row, "publishers_list")),
                "rating_band": _safe_str(_row_value(row, "rating_band")),
                "rating_reliable_flag": _safe_bool(_row_value(row, "rating_reliable_flag")),
                "main_game_flag": _safe_bool(_row_value(row, "main_game_flag")),
                "data_caveats": caveats,
            }
        )

    return game


def list_games(
    *,
    search: str = "",
    platform: Iterable[str] | None = None,
    genre: Iterable[str] | None = None,
    theme: Iterable[str] | None = None,
    release_year_min: int | None = None,
    release_year_max: int | None = None,
    min_rating: float | None = None,
    min_reviews: int | None = None,
    hidden_gems_only: bool = False,
    sort: str = "highest_rating",
    page: int = 1,
    page_size: int = 24,
) -> dict[str, Any]:
    catalog = load_catalog()
    release_year_range = None
    if release_year_min is not None and release_year_max is not None:
        release_year_range = (release_year_min, release_year_max)

    filtered = apply_catalog_filters(
        catalog,
        search_text=search,
        release_year_range=release_year_range,
        platforms=platform,
        genres=genre,
        themes=theme,
        min_rating=min_rating,
        min_rating_count=min_reviews,
        hidden_gems_only=hidden_gems_only,
    )

    sorted_games = sort_catalog(filtered, SORT_OPTIONS.get(sort, sort))
    total_items = int(len(sorted_games))
    total_pages = max(math.ceil(total_items / page_size), 1)
    safe_page = min(max(page, 1), total_pages)
    start = (safe_page - 1) * page_size
    end = start + page_size

    items = [serialize_game(row) for _, row in sorted_games.iloc[start:end].iterrows()]

    return {
        "items": items,
        "page": safe_page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
    }


def get_game(game_id: int) -> dict[str, Any] | None:
    catalog = load_catalog()
    matches = catalog[catalog["game_id"] == game_id]
    if matches.empty:
        return None
    return serialize_game(matches.iloc[0], detail=True)
