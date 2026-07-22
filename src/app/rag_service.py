from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from src.app import config
from src.app.formatting import compact_text, split_list


VECTOR_STORE_PATH = config.DATA_DIR / "vector_store"
VECTOR_STORE_SQLITE_PATH = VECTOR_STORE_PATH / "chroma.sqlite3"

RAG_ARTIFACTS = {
    "app_catalog": config.APP_CATALOG_PATH,
    "vector_store": VECTOR_STORE_PATH,
    "vector_store_sqlite": VECTOR_STORE_SQLITE_PATH,
}


def rag_status() -> dict[str, bool]:
    return {name: path.exists() for name, path in RAG_ARTIFACTS.items()}


def rag_ready() -> bool:
    status = rag_status()
    return bool(
        status.get("app_catalog")
        and status.get("vector_store")
        and status.get("vector_store_sqlite")
    )


@lru_cache(maxsize=1)
def _get_rag_agent():
    from src.rag_engine import RAGAgent

    return RAGAgent()


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    try:
        missing = pd.isna(value)
    except (TypeError, ValueError):
        return False
    if isinstance(missing, bool):
        return missing
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
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(parsed) or math.isinf(parsed):
        return None
    return parsed


def _safe_bool(value: object) -> bool:
    if _is_missing(value):
        return False
    try:
        return bool(int(value))
    except (TypeError, ValueError):
        return bool(value)


def _row_value(row: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        value = row.get(key)
        if not _is_missing(value) and value not in ("", "Not Listed"):
            return value
    return default


def _normalize_score(value: object) -> float | None:
    parsed = _safe_float(value)
    if parsed is None:
        return None
    return max(0.0, min(parsed, 1.0))


def _result_caveats(row: dict[str, Any]) -> list[str]:
    caveats: list[str] = []
    if _safe_float(_row_value(row, "total_rating")) is None:
        caveats.append("Rating is missing in the project catalog.")
    if not _safe_str(_row_value(row, "summary")):
        caveats.append("Summary text is missing, so explanation quality may be limited.")
    return caveats


def _build_evidence(result: dict[str, Any], row: dict[str, Any]) -> str:
    evidence_parts: list[str] = []

    genres = split_list(_row_value(row, "genres_list", "genres", default=""))
    themes = split_list(_row_value(row, "themes_list", "themes", default=""))
    platforms = split_list(_row_value(row, "platforms_list", "platforms", default=""))

    if genres:
        evidence_parts.append(f"genre match context: {', '.join(genres[:3])}")
    if themes:
        evidence_parts.append(f"theme context: {', '.join(themes[:3])}")
    if platforms:
        evidence_parts.append(f"available platform context: {', '.join(platforms[:3])}")

    semantic_score = _normalize_score(result.get("normalized_vec", result.get("vector_similarity")))
    lexical_score = _normalize_score(result.get("normalized_bm25"))

    if semantic_score is not None:
        evidence_parts.append(f"semantic retrieval score {semantic_score:.2f}")
    if lexical_score is not None and lexical_score > 0:
        evidence_parts.append(f"keyword retrieval score {lexical_score:.2f}")

    if not evidence_parts:
        return "Retrieved from the project catalog as a relevant match for the question."

    return "Matched through " + "; ".join(evidence_parts) + "."


def _normalize_game_result(result: dict[str, Any], source_row: dict[str, Any], rank: int) -> dict[str, Any]:
    row = {**result, **source_row}
    game_id = _safe_int(_row_value(row, "game_id"))

    return {
        "rank": rank,
        "game_id": game_id,
        "name": _safe_str(_row_value(row, "name")) or "Unknown title",
        "slug": _safe_str(_row_value(row, "slug")),
        "release_year": _safe_int(_row_value(row, "release_year")),
        "cover_url": _safe_str(_row_value(row, "cover_url")),
        "screenshot_url": _safe_str(_row_value(row, "screenshot_url")),
        "summary": compact_text(_row_value(row, "summary"), max_chars=360) or None,
        "total_rating": _safe_float(_row_value(row, "total_rating")),
        "total_rating_count": _safe_int(_row_value(row, "total_rating_count")),
        "custom_interest_score": _safe_float(_row_value(row, "custom_interest_score")),
        "custom_interest_percentile": _safe_float(_row_value(row, "custom_interest_percentile")),
        "extraction_cohort": _safe_str(_row_value(row, "extraction_cohort")),
        "platforms": split_list(_row_value(row, "platforms_list", "platforms", default="")),
        "genres": split_list(_row_value(row, "genres_list", "genres", default="")),
        "themes": split_list(_row_value(row, "themes_list", "themes", default="")),
        "game_modes": split_list(_row_value(row, "game_modes_list", default="")),
        "player_perspectives": split_list(_row_value(row, "player_perspectives_list", default="")),
        "normal_playtime_hours": _safe_float(_row_value(row, "normal_playtime_hours", "playtime_normally")),
        "hidden_gem_balanced_flag": _safe_bool(_row_value(row, "hidden_gem_balanced_flag")),
        "rag_ready_flag": _safe_bool(_row_value(row, "rag_ready_flag")),
        "retrieval_score": _normalize_score(_row_value(row, "primary_rank_score", "relevance_score", "hybrid_score")),
        "semantic_score": _normalize_score(_row_value(row, "normalized_vec", "vector_similarity")),
        "lexical_score": _normalize_score(_row_value(row, "normalized_bm25")),
        "evidence": _build_evidence(result, row),
        "caveats": _result_caveats(row),
    }


def _build_answer_text(query: str, games: list[dict[str, Any]]) -> str:
    if not games:
        return (
            "I could not find strong catalog-backed matches for that question. "
            "Try adding a platform, genre, theme, or a reference game."
        )

    names = [game["name"] for game in games[:3] if game.get("name")]
    if not names:
        return "I found catalog-backed matches, but their titles could not be formatted cleanly."

    if len(names) == 1:
        title_text = names[0]
    elif len(names) == 2:
        title_text = f"{names[0]} and {names[1]}"
    else:
        title_text = f"{names[0]}, {names[1]}, and {names[2]}"

    return (
        f"For your question, the strongest catalog-backed matches are {title_text}. "
        "These results come from hybrid retrieval over game summaries, genres, themes, "
        "platforms, and related metadata."
    )


def _clean_filters(filters: dict | None) -> dict[str, Any]:
    filters = filters or {}
    cleaned: dict[str, Any] = {}

    platforms = filters.get("platforms") or filters.get("platform")
    if isinstance(platforms, str):
        platforms = [platforms]
    if platforms:
        cleaned["platforms"] = [str(platform).strip() for platform in platforms if str(platform).strip()]

    min_year = filters.get("release_year_min") or filters.get("min_year")
    max_year = filters.get("release_year_max") or filters.get("max_year")
    multiplayer_mode = filters.get("multiplayer_mode")

    if min_year is not None:
        cleaned["release_year_min"] = _safe_int(min_year)
    if max_year is not None:
        cleaned["release_year_max"] = _safe_int(max_year)
    if multiplayer_mode:
        cleaned["multiplayer_mode"] = str(multiplayer_mode).strip()

    return {key: value for key, value in cleaned.items() if value not in (None, "", [])}


def answer_game_query(query: str, filters: dict | None = None, top_k: int = 5) -> dict:
    status = rag_status()
    cleaned_query = str(query or "").strip()
    cleaned_filters = _clean_filters(filters)
    top_k = max(1, min(int(top_k or 5), 10))

    if not cleaned_query:
        return {
            "answer_text": "Ask a game discovery question to start the guide.",
            "retrieved_game_ids": [],
            "retrieved_games": [],
            "applied_filters": cleaned_filters,
            "retrieval_scores": [],
            "warnings": ["The question was empty."],
            "mode": "rag_unavailable",
            "status": "empty_query",
        }

    if not rag_ready():
        return {
            "answer_text": (
                "RAG retrieval is unavailable because one or more required local artifacts "
                "are missing."
            ),
            "retrieved_game_ids": [],
            "retrieved_games": [],
            "applied_filters": cleaned_filters,
            "retrieval_scores": [],
            "warnings": [
                "Required artifacts: data/app/app_game_catalog.parquet and data/vector_store/chroma.sqlite3."
            ],
            "artifact_status": status,
            "mode": "rag_unavailable",
            "status": "unavailable",
        }

    try:
        agent = _get_rag_agent()
        search_top_n = max(top_k * 4, top_k)
        raw_results = agent.search(
            cleaned_query,
            top_n=search_top_n,
            min_year=cleaned_filters.get("release_year_min"),
            platforms=cleaned_filters.get("platforms"),
            multiplayer_mode=cleaned_filters.get("multiplayer_mode"),
            debug_scores=False,
        )
    except Exception as error:
        return {
            "answer_text": "RAG retrieval could not run cleanly in the current environment.",
            "retrieved_game_ids": [],
            "retrieved_games": [],
            "applied_filters": cleaned_filters,
            "retrieval_scores": [],
            "warnings": [f"{type(error).__name__}: {error}"],
            "artifact_status": status,
            "mode": "rag_unavailable",
            "status": "error",
        }

    release_year_max = cleaned_filters.get("release_year_max")
    normalized_games: list[dict[str, Any]] = []
    for result in raw_results:
        game_id = str(result.get("game_id"))
        source_row = getattr(agent, "catalog_by_id", {}).get(game_id, {})
        normalized = _normalize_game_result(result, source_row, rank=len(normalized_games) + 1)
        if normalized["game_id"] is None:
            continue
        if release_year_max is not None and normalized.get("release_year") is not None:
            if int(normalized["release_year"]) > int(release_year_max):
                continue
        normalized_games.append(normalized)
        if len(normalized_games) >= top_k:
            break

    retrieval_scores = [
        game["retrieval_score"]
        for game in normalized_games
        if game.get("retrieval_score") is not None
    ]
    warnings = [
        "Ratings, platform coverage, and text metadata depend on IGDB catalog completeness."
    ]

    if not normalized_games:
        warnings.append("Hybrid retrieval returned no displayable game matches.")

    return {
        "answer_text": _build_answer_text(cleaned_query, normalized_games),
        "retrieved_game_ids": [game["game_id"] for game in normalized_games],
        "retrieved_games": normalized_games,
        "applied_filters": cleaned_filters,
        "retrieval_scores": retrieval_scores,
        "warnings": warnings,
        "artifact_status": status,
        "mode": "rag_hybrid_retrieval",
        "status": "success" if normalized_games else "no_results",
    }


def artifact_path(name: str) -> Path:
    return RAG_ARTIFACTS[name]
