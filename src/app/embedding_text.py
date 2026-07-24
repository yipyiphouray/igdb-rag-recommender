from __future__ import annotations

import re
from typing import Any

import pandas as pd


EMBEDDING_COLUMN_MAP = {
    "platforms": "platforms_list",
    "genres": "genres_list",
    "playtime": "normal_playtime_hours",
    "developers": "developers_list",
    "themes": "themes_list",
    "keywords": "keywords_list",
    "game_modes": "game_modes_list",
    "player_perspectives": "player_perspectives_list",
    "publishers": "publishers_list",
}

EMBEDDING_METADATA_COLUMNS = [
    "name",
    "platforms",
    "developers",
    "genres",
    "themes",
    "total_rating",
    "is_high_rated",
    "release_year",
    "rating_band",
    "game_modes",
    "player_perspectives",
    "hidden_gem_balanced_flag",
    "rag_ready_flag",
]


def ensure_embedding_column(df: pd.DataFrame, canonical_name: str, default_value: Any = "") -> None:
    mapped_name = EMBEDDING_COLUMN_MAP.get(canonical_name)
    if canonical_name not in df.columns and mapped_name in df.columns:
        df[canonical_name] = df[mapped_name]
    if canonical_name not in df.columns:
        df[canonical_name] = default_value


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    try:
        missing = pd.isna(value)
    except (TypeError, ValueError):
        return False
    if isinstance(missing, bool):
        return missing
    return False


def _clean_text(value: object) -> str:
    if _is_missing(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"", "nan", "none", "<na>", "not listed"}:
        return ""
    return text


def _limited_text(value: object, max_chars: int = 700) -> str:
    text = _clean_text(value)
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0].strip()


def _split_values(value: object, limit: int = 14) -> list[str]:
    text = _clean_text(value)
    if not text:
        return []

    values = []
    seen = set()
    cleaned = str(text).replace("[", "").replace("]", "").replace("'", "")
    for part in re.split(r"\s*[,|;]\s*", cleaned):
        item = part.strip()
        if not item:
            continue
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        values.append(item)
        if len(values) >= limit:
            break
    return values


def _append_labeled(parts: list[str], label: str, value: object) -> None:
    text = _clean_text(value)
    if text:
        parts.append(f"{label}: {text}")


def _append_list(parts: list[str], label: str, value: object, limit: int = 14) -> None:
    values = _split_values(value, limit=limit)
    if values:
        parts.append(f"{label}: {', '.join(values)}")


def _truthy_int(value: object) -> bool:
    try:
        return int(float(value)) == 1
    except (TypeError, ValueError):
        return False


def _playtime_label(value: object) -> str:
    try:
        hours = float(value)
    except (TypeError, ValueError):
        return ""
    if hours <= 0:
        return ""
    if hours <= 8:
        return "short playtime"
    if hours <= 25:
        return "medium playtime"
    return "long playtime"


def normalize_embedding_catalog(df: pd.DataFrame) -> pd.DataFrame:
    ensure_embedding_column(df, "name", "Unknown")
    ensure_embedding_column(df, "game_id", "")
    ensure_embedding_column(df, "rag_text_profile", "")
    ensure_embedding_column(df, "summary", "")
    ensure_embedding_column(df, "storyline", "")
    ensure_embedding_column(df, "platforms", "Not Listed")
    ensure_embedding_column(df, "developers", "Not Listed")
    ensure_embedding_column(df, "publishers", "Not Listed")
    ensure_embedding_column(df, "genres", "")
    ensure_embedding_column(df, "themes", "")
    ensure_embedding_column(df, "keywords", "")
    ensure_embedding_column(df, "game_modes", "")
    ensure_embedding_column(df, "player_perspectives", "")
    ensure_embedding_column(df, "release_year", 0)
    ensure_embedding_column(df, "rating_band", "")
    ensure_embedding_column(df, "normal_playtime_hours", 0.0)
    ensure_embedding_column(df, "hidden_gem_balanced_flag", 0)
    ensure_embedding_column(df, "multiplayer_flag", 0)
    ensure_embedding_column(df, "rag_ready_flag", 0)
    ensure_embedding_column(df, "total_rating", 0.0)

    safe_df = df.copy()
    safe_df["name"] = safe_df["name"].fillna("Unknown").astype(str)
    safe_df["game_id"] = safe_df["game_id"].fillna("").astype(str)
    safe_df["rag_text_profile"] = safe_df["rag_text_profile"].fillna("").astype(str)
    safe_df["summary"] = safe_df["summary"].fillna("").astype(str)
    safe_df["storyline"] = safe_df["storyline"].fillna("").astype(str)
    safe_df["platforms"] = safe_df["platforms"].fillna("Not Listed").astype(str)
    safe_df["developers"] = safe_df["developers"].fillna("Not Listed").astype(str)
    safe_df["publishers"] = safe_df["publishers"].fillna("Not Listed").astype(str)
    safe_df["genres"] = safe_df["genres"].fillna("").astype(str)
    safe_df["themes"] = safe_df["themes"].fillna("").astype(str)
    safe_df["keywords"] = safe_df["keywords"].fillna("").astype(str)
    safe_df["game_modes"] = safe_df["game_modes"].fillna("").astype(str)
    safe_df["player_perspectives"] = safe_df["player_perspectives"].fillna("").astype(str)
    safe_df["release_year"] = pd.to_numeric(safe_df["release_year"], errors="coerce").fillna(0).astype(int)
    safe_df["rating_band"] = safe_df["rating_band"].fillna("").astype(str)
    safe_df["normal_playtime_hours"] = pd.to_numeric(
        safe_df["normal_playtime_hours"], errors="coerce"
    ).fillna(0.0)
    safe_df["hidden_gem_balanced_flag"] = pd.to_numeric(
        safe_df["hidden_gem_balanced_flag"], errors="coerce"
    ).fillna(0).astype(int)
    safe_df["multiplayer_flag"] = pd.to_numeric(safe_df["multiplayer_flag"], errors="coerce").fillna(0).astype(int)
    safe_df["rag_ready_flag"] = pd.to_numeric(safe_df["rag_ready_flag"], errors="coerce").fillna(0).astype(int)
    safe_df["total_rating"] = pd.to_numeric(safe_df["total_rating"], errors="coerce").fillna(0.0)
    safe_df["is_high_rated"] = (safe_df["total_rating"] >= 80).astype(int)

    safe_df = safe_df[safe_df["game_id"].str.strip() != ""].copy()
    safe_df = safe_df.drop_duplicates(subset=["game_id"], keep="first")
    return safe_df


def build_embedding_text(row: pd.Series | dict[str, Any]) -> str:
    parts = []

    _append_labeled(parts, "Title", row.get("name"))
    _append_list(parts, "Genres", row.get("genres_list", row.get("genres")), limit=8)
    _append_list(parts, "Themes", row.get("themes_list", row.get("themes")), limit=8)
    _append_list(parts, "Keywords", row.get("keywords_list", row.get("keywords")), limit=14)
    _append_list(parts, "Platforms", row.get("platforms_list", row.get("platforms")), limit=10)
    _append_list(parts, "Game modes", row.get("game_modes_list", row.get("game_modes")), limit=8)
    _append_list(
        parts,
        "Player perspectives",
        row.get("player_perspectives_list", row.get("player_perspectives")),
        limit=6,
    )
    _append_list(parts, "Developers", row.get("developers_list", row.get("developers")), limit=4)
    _append_labeled(parts, "Rating band", row.get("rating_band"))

    playtime = _playtime_label(row.get("normal_playtime_hours"))
    if playtime:
        parts.append(f"Playtime profile: {playtime}")
    if _truthy_int(row.get("multiplayer_flag")):
        parts.append("Multiplayer profile: multiplayer or co-op support")
    if _truthy_int(row.get("hidden_gem_balanced_flag")):
        parts.append("Discovery profile: hidden gem candidate")
    if _truthy_int(row.get("is_high_rated")):
        parts.append("Quality profile: highly rated")

    _append_labeled(parts, "Summary", _limited_text(row.get("summary"), max_chars=700))
    _append_labeled(parts, "Storyline", _limited_text(row.get("storyline"), max_chars=450))
    _append_labeled(parts, "Catalog profile", _limited_text(row.get("rag_text_profile"), max_chars=700))

    return " | ".join(parts).strip()
