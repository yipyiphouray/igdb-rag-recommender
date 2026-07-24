from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from src.app import config
from src.app.formatting import split_list


@dataclass(frozen=True)
class CatalogFactAnswer:
    intent: str
    answer: str
    prompts: list[str]
    status: str = "success"
    caveats: list[str] = field(default_factory=list)
    source_files: list[str] = field(default_factory=list)
    interpreted_filters: dict[str, Any] = field(default_factory=dict)
    game_id: int | None = None
    game_ids: list[int] = field(default_factory=list)


DIMENSIONS = {
    "genre": {
        "option_key": "genres",
        "column": "genres_list",
        "terms": {"genre", "genres"},
        "label": "genre",
    },
    "platform": {
        "option_key": "platforms",
        "column": "platforms_list",
        "terms": {"platform", "platforms", "console", "consoles", "on"},
        "label": "platform",
    },
    "theme": {
        "option_key": "themes",
        "column": "themes_list",
        "terms": {"theme", "themes", "about", "with"},
        "label": "theme",
    },
    "game_mode": {
        "option_key": "game_modes",
        "column": "game_modes_list",
        "terms": {"mode", "modes", "multiplayer", "singleplayer", "co-op", "coop"},
        "label": "game mode",
    },
}

VALUE_ALIASES = {
    "rpg": "Role-playing (RPG)",
    "role playing": "Role-playing (RPG)",
    "role-playing": "Role-playing (RPG)",
    "switch": "Nintendo Switch",
    "pc": "PC (Microsoft Windows)",
    "windows": "PC (Microsoft Windows)",
    "ps5": "PlayStation 5",
    "ps4": "PlayStation 4",
    "xbox series": "Xbox Series X|S",
    "coop": "Co-operative",
    "co op": "Co-operative",
    "co-op": "Co-operative",
    "singleplayer": "Single player",
}

COUNT_TERMS = {
    "amount",
    "count",
    "counts",
    "many",
    "number",
    "total",
}

GAME_LOOKUP_STOP_PHRASES = (
    "is",
    "are",
    "was",
    "were",
    "what",
    "which",
    "when",
    "where",
    "who",
    "does",
    "do",
    "tell",
    "show",
    "about",
    "game",
    "in",
    "the",
    "dataset",
    "catalog",
    "project",
)


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", str(text or "").lower())


def _normalized(text: str) -> str:
    return " ".join(_tokenize(text))


def _source(path: Path) -> str:
    try:
        return path.relative_to(config.ROOT_DIR).as_posix()
    except ValueError:
        return path.as_posix()


@lru_cache(maxsize=1)
def _load_catalog() -> pd.DataFrame | None:
    if not config.APP_CATALOG_PATH.exists():
        return None
    try:
        return pd.read_parquet(config.APP_CATALOG_PATH)
    except Exception:
        return None


@lru_cache(maxsize=1)
def _load_filter_options() -> dict[str, Any]:
    if not config.APP_FILTER_OPTIONS_PATH.exists():
        return {}
    try:
        return json.loads(config.APP_FILTER_OPTIONS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _safe_filter_options() -> dict[str, Any]:
    options = _load_filter_options()
    return options if isinstance(options, dict) else {}


def get_catalog_filter_options() -> dict[str, Any]:
    return _safe_filter_options()


def _format_count(value: int) -> str:
    return f"{int(value):,}"


def _format_pct(part: int, total: int) -> str:
    if total <= 0:
        return "0.00%"
    return f"{(part / total) * 100:.2f}%"


def _safe_str(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    text = str(value).strip()
    return text or None


def _safe_int(value: object) -> int | None:
    try:
        if value is None:
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _safe_float(value: object) -> float | None:
    try:
        if value is None:
            return None
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(parsed) or math.isinf(parsed):
        return None
    return parsed


def _format_rating(value: object) -> str:
    rating = _safe_float(value)
    return "unknown" if rating is None else f"{rating:.1f}/100"


def _format_optional_count(value: object) -> str:
    count = _safe_int(value)
    return "unknown" if count is None else _format_count(count)


def _looks_like_catalog_count_question(message: str) -> bool:
    tokens = set(_tokenize(message))
    if not tokens.intersection(COUNT_TERMS):
        return False
    if not tokens.intersection({"game", "games", "title", "titles"}):
        return False

    dimension_terms = set()
    for metadata in DIMENSIONS.values():
        dimension_terms.update(metadata["terms"])
    if tokens.intersection(dimension_terms):
        return True

    normalized = _normalized(message)
    options = _safe_filter_options()
    for key in ("genres", "platforms", "themes", "game_modes"):
        for option in options.get(key, []) or []:
            if _normalized(option) and _normalized(option) in normalized:
                return True

    return any(alias in normalized for alias in VALUE_ALIASES)


def _guess_dimensions(message: str) -> list[str]:
    tokens = set(_tokenize(message))
    dimensions = [
        dimension
        for dimension, metadata in DIMENSIONS.items()
        if tokens.intersection(metadata["terms"])
    ]
    if dimensions:
        return dimensions

    normalized = _normalized(message)
    options = _safe_filter_options()
    guessed: list[str] = []
    for dimension, metadata in DIMENSIONS.items():
        for option in options.get(metadata["option_key"], []) or []:
            option_text = _normalized(option)
            if option_text and option_text in normalized:
                guessed.append(dimension)
                break
    return guessed


def _match_option(message: str, dimension: str) -> str | None:
    normalized_message = _normalized(message)

    for alias, canonical in VALUE_ALIASES.items():
        if alias in normalized_message:
            options = _safe_filter_options().get(DIMENSIONS[dimension]["option_key"], []) or []
            if canonical in options:
                return canonical

    options = _safe_filter_options().get(DIMENSIONS[dimension]["option_key"], []) or []
    scored: list[tuple[int, str]] = []
    message_tokens = set(_tokenize(message))

    for option in options:
        option_text = _normalized(option)
        if not option_text:
            continue
        option_tokens = set(_tokenize(option))
        if option_text in normalized_message:
            scored.append((100 + len(option_tokens), option))
            continue
        overlap = len(message_tokens.intersection(option_tokens))
        if overlap > 0:
            scored.append((overlap, option))

    if not scored:
        return None

    scored.sort(key=lambda item: item[0], reverse=True)
    best_score, best_option = scored[0]
    return best_option if best_score >= 1 else None


def _canonical_option(value: object, dimension: str) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None

    normalized_text = _normalized(text)
    options = _safe_filter_options().get(DIMENSIONS[dimension]["option_key"], []) or []

    for alias, canonical in VALUE_ALIASES.items():
        if normalized_text == _normalized(alias) and canonical in options:
            return canonical

    for option in options:
        if normalized_text == _normalized(option):
            return option

    scored: list[tuple[int, str]] = []
    value_tokens = set(_tokenize(text))
    for option in options:
        option_tokens = set(_tokenize(option))
        overlap = len(value_tokens.intersection(option_tokens))
        if overlap > 0:
            scored.append((overlap, option))

    if not scored:
        return None
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[0][1]


def _contains_value(value: object, target: str) -> bool:
    target_lower = target.strip().lower()
    return any(item.strip().lower() == target_lower for item in split_list(value))


def _safe_bool(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, float) and math.isnan(value):
        return False
    try:
        return bool(int(value))
    except (TypeError, ValueError):
        return bool(value)


def _normalize_filter_values(raw_filters: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    key_map = {
        "genre": "genres",
        "genres": "genres",
        "platform": "platforms",
        "platforms": "platforms",
        "theme": "themes",
        "themes": "themes",
        "mode": "game_modes",
        "modes": "game_modes",
        "game_mode": "game_modes",
        "game_modes": "game_modes",
        "perspective": "player_perspectives",
        "perspectives": "player_perspectives",
        "player_perspectives": "player_perspectives",
    }
    dimension_by_key = {
        "genres": "genre",
        "platforms": "platform",
        "themes": "theme",
        "game_modes": "game_mode",
    }

    for raw_key, raw_value in (raw_filters or {}).items():
        key = key_map.get(str(raw_key).strip().lower(), str(raw_key).strip().lower())
        if key in {"release_year_min", "release_year_max"}:
            try:
                normalized[key] = int(raw_value)
            except (TypeError, ValueError):
                continue
        elif key == "hidden_gems_only":
            normalized[key] = _safe_bool(raw_value)
        elif key in dimension_by_key:
            values = raw_value if isinstance(raw_value, list) else [raw_value]
            canonical_values = [
                canonical
                for value in values
                if (canonical := _canonical_option(value, dimension_by_key[key]))
            ]
            if canonical_values:
                normalized[key] = sorted(set(canonical_values))

    return normalized


def _apply_filters(catalog: pd.DataFrame, filters: dict[str, Any]) -> pd.Series:
    mask = pd.Series(True, index=catalog.index)
    column_map = {
        "genres": "genres_list",
        "platforms": "platforms_list",
        "themes": "themes_list",
        "game_modes": "game_modes_list",
        "player_perspectives": "player_perspectives_list",
    }
    for key, column in column_map.items():
        selected = filters.get(key) or []
        if selected and column in catalog.columns:
            mask = mask & catalog[column].apply(
                lambda value: any(_contains_value(value, option) for option in selected)
            )

    if filters.get("hidden_gems_only") and "hidden_gem_balanced_flag" in catalog.columns:
        mask = mask & catalog["hidden_gem_balanced_flag"].apply(_safe_bool)

    min_year = filters.get("release_year_min")
    max_year = filters.get("release_year_max")
    if min_year is not None and "release_year" in catalog.columns:
        mask = mask & (catalog["release_year"] >= int(min_year))
    if max_year is not None and "release_year" in catalog.columns:
        mask = mask & (catalog["release_year"] <= int(max_year))

    return mask


def _filter_label(filters: dict[str, Any]) -> str:
    parts: list[str] = []
    labels = {
        "genres": "genre",
        "platforms": "platform",
        "themes": "theme",
        "game_modes": "game mode",
        "player_perspectives": "player perspective",
    }
    for key, label in labels.items():
        values = filters.get(key) or []
        if values:
            parts.append(f"{label} = {', '.join(values)}")
    if filters.get("hidden_gems_only"):
        parts.append("hidden gem = yes")
    if filters.get("release_year_min") is not None or filters.get("release_year_max") is not None:
        start = filters.get("release_year_min", "any")
        end = filters.get("release_year_max", "any")
        parts.append(f"release year = {start} to {end}")
    return "; ".join(parts) if parts else "the selected filters"


def answer_catalog_count_with_filters(raw_filters: dict[str, Any]) -> CatalogFactAnswer | None:
    filters = _normalize_filter_values(raw_filters)
    if not filters:
        return None

    catalog = _load_catalog()
    if catalog is None:
        return CatalogFactAnswer(
            intent="catalog_count_unavailable",
            answer="I cannot verify that catalog count because the app catalog artifact is missing or unreadable.",
            prompts=[
                "How many games are in the dataset?",
                "What is the top genre?",
                "Where can I explore games?",
            ],
            status="unavailable",
            caveats=["Catalog count questions require data/app/app_game_catalog.parquet."],
            source_files=[_source(config.APP_CATALOG_PATH)],
            interpreted_filters=filters,
        )

    mask = _apply_filters(catalog, filters)
    count = int(mask.sum())
    total = int(len(catalog))
    count_scope = "hidden-gem games" if filters.get("hidden_gems_only") else "games"

    return CatalogFactAnswer(
        intent="catalog_filtered_count",
        answer=(
            f"The current app catalog contains {_format_count(count)} {count_scope} matching "
            f"{_filter_label(filters)}. That is {_format_pct(count, total)} of the "
            f"{_format_count(total)} games in the curated app dataset."
        ),
        prompts=[
            "What genre has the most games?",
            "How many games are in the dataset?",
            "Where can I explore games?",
        ],
        caveats=[
            "This count is based on the curated app catalog, not the full IGDB database.",
            "Games can match multiple metadata values, so filtered counts can overlap across categories.",
        ],
        source_files=[_source(config.APP_CATALOG_PATH)],
        interpreted_filters=filters,
    )


def answer_catalog_distribution(field: str | None, *, limit: int = 5) -> CatalogFactAnswer | None:
    field_map = {
        "genre": ("genres", "genres_list", "genres"),
        "genres": ("genres", "genres_list", "genres"),
        "platform": ("platforms", "platforms_list", "platforms"),
        "platforms": ("platforms", "platforms_list", "platforms"),
        "theme": ("themes", "themes_list", "themes"),
        "themes": ("themes", "themes_list", "themes"),
        "game_mode": ("game modes", "game_modes_list", "game_modes"),
        "game_modes": ("game modes", "game_modes_list", "game_modes"),
        "player_perspectives": ("player perspectives", "player_perspectives_list", "player_perspectives"),
    }
    field_key = str(field or "").strip().lower()
    if field_key not in field_map:
        return None

    label, column, intent_suffix = field_map[field_key]
    catalog = _load_catalog()
    if catalog is None or column not in catalog.columns:
        return None

    counts: dict[str, int] = {}
    for value in catalog[column]:
        for item in split_list(value):
            counts[item] = counts.get(item, 0) + 1

    if not counts:
        return None

    total = int(len(catalog))
    top_items = sorted(counts.items(), key=lambda item: item[1], reverse=True)[: max(1, min(limit, 10))]
    top_text = "; ".join(
        f"{name}: {_format_count(count)} games ({_format_pct(count, total)})"
        for name, count in top_items
    )

    return CatalogFactAnswer(
        intent=f"catalog_top_{intent_suffix}",
        answer=(
            f"The most common {label} in the current app catalog are: {top_text}. "
            "These counts are based on metadata tags in the curated dataset."
        ),
        prompts=[
            "How many games are in the top genre?",
            "Where can I see insights?",
            "How many games are in the dataset?",
        ],
        caveats=[
            "Games can have multiple metadata tags, so category totals can overlap.",
            "This reflects the curated app catalog, not full IGDB market prevalence.",
        ],
        source_files=[_source(config.APP_CATALOG_PATH)],
    )


def _clean_game_title_candidate(value: object) -> str:
    text = str(value or "").strip()
    text = re.sub(r"^['\"]|['\"]$", "", text).strip()
    text = re.sub(
        r"\b(is|are|was|were|what|which|when|where|who|does|do|tell me about|show me|about|in the dataset|in my dataset|in the catalog|in this project|game)\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )
    return re.sub(r"\s+", " ", text).strip(" ?!.,")


def _title_similarity(query: str, name: str) -> float:
    query_norm = _normalized(query)
    name_norm = _normalized(name)
    if not query_norm or not name_norm:
        return 0.0
    if query_norm == name_norm:
        return 1.0
    if query_norm in name_norm or name_norm in query_norm:
        return 0.88
    query_tokens = set(_tokenize(query))
    name_tokens = set(_tokenize(name))
    if not query_tokens or not name_tokens:
        return 0.0
    overlap = len(query_tokens.intersection(name_tokens))
    union = len(query_tokens.union(name_tokens))
    return overlap / union


def find_game_by_title(title: str) -> dict[str, Any] | None:
    cleaned_title = _clean_game_title_candidate(title)
    if not cleaned_title:
        return None

    catalog = _load_catalog()
    if catalog is None or "name" not in catalog.columns:
        return None

    best_row = None
    best_score = 0.0
    for _, row in catalog.iterrows():
        score = _title_similarity(cleaned_title, str(row.get("name", "")))
        if score > best_score:
            best_score = score
            best_row = row

    if best_row is None or best_score < 0.55:
        return None

    return best_row.to_dict()


def _infer_title_from_message(message: str) -> str:
    text = str(message or "").strip()
    quoted = re.search(r"['\"]([^'\"]+)['\"]", text)
    if quoted:
        return quoted.group(1).strip()

    patterns = [
        r"(?:about|for|called|named)\s+(.+?)(?:\?|$)",
        r"(?:is|was)\s+(.+?)\s+(?:in|part of|inside)\s+(?:the\s+)?(?:dataset|catalog|project)",
        r"(?:what|which)\s+(?:genre|genres|platform|platforms|rating|year|summary|theme|themes).+?\s+(?:for|of|does|is)\s+(.+?)(?:\?|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return _clean_game_title_candidate(match.group(1))

    tokens = [
        token
        for token in re.split(r"\s+", text)
        if _normalized(token) not in GAME_LOOKUP_STOP_PHRASES
    ]
    return _clean_game_title_candidate(" ".join(tokens))


def _looks_like_game_lookup_question(message: str) -> bool:
    normalized = _normalized(message)
    tokens = set(_tokenize(message))

    if any(phrase in normalized for phrase in ("your purpose", "what can you do", "who are you")):
        return False

    lookup_terms = {
        "genre",
        "genres",
        "platform",
        "platforms",
        "rating",
        "ratings",
        "year",
        "released",
        "release",
        "summary",
        "summarize",
        "theme",
        "themes",
        "hidden",
        "gem",
    }
    if tokens.intersection(lookup_terms):
        return True

    return any(
        phrase in normalized
        for phrase in (
            "in the dataset",
            "in my dataset",
            "in the catalog",
            "in this project",
            "tell me about",
            "show me",
        )
    )


def answer_game_lookup_question(message: str, *, game_title: str | None = None) -> CatalogFactAnswer | None:
    if game_title is None and not _looks_like_game_lookup_question(message):
        return None

    title = game_title or _infer_title_from_message(message)
    row = find_game_by_title(title)
    if row is None:
        return None

    game_id = _safe_int(row.get("game_id"))
    name = _safe_str(row.get("name")) or "Unknown title"
    release_year = _safe_int(row.get("release_year"))
    genres = split_list(row.get("genres_list"))
    platforms = split_list(row.get("platforms_list"))
    themes = split_list(row.get("themes_list"))
    summary = _safe_str(row.get("summary"))
    hidden_gem = _safe_bool(row.get("hidden_gem_balanced_flag"))
    rag_ready = _safe_bool(row.get("rag_ready_flag"))

    answer_parts = [
        f"{name} is in the current app catalog"
        + (f" with game_id {game_id}" if game_id is not None else "")
        + "."
    ]
    if release_year is not None:
        answer_parts.append(f"It has release year {release_year}.")
    if genres:
        answer_parts.append(f"Genres: {', '.join(genres[:5])}.")
    if platforms:
        answer_parts.append(f"Platforms include: {', '.join(platforms[:6])}.")
    if themes:
        answer_parts.append(f"Themes include: {', '.join(themes[:5])}.")
    answer_parts.append(
        f"Total rating is {_format_rating(row.get('total_rating'))} with "
        f"{_format_optional_count(row.get('total_rating_count'))} rating records."
    )
    answer_parts.append(f"Hidden-gem flag: {'yes' if hidden_gem else 'no'}.")
    answer_parts.append(f"RAG-ready flag: {'yes' if rag_ready else 'no'}.")
    if summary:
        answer_parts.append(f"Summary: {summary[:320].rstrip()}{'...' if len(summary) > 320 else ''}")

    caveats: list[str] = [
        "This answer is based on the local app catalog, not a live IGDB lookup.",
    ]
    if _safe_float(row.get("total_rating")) is None:
        caveats.append("This game does not have a usable total rating in the app catalog.")
    if not summary:
        caveats.append("This game does not have summary text in the app catalog.")

    return CatalogFactAnswer(
        intent="game_lookup",
        answer=" ".join(answer_parts),
        prompts=[
            "Where can I explore this game?",
            "How does Recommend Me use recent games?",
            "What data fields are available for games?",
        ],
        caveats=caveats,
        source_files=[_source(config.APP_CATALOG_PATH)],
        interpreted_filters={"game_title": name},
        game_id=game_id,
        game_ids=[game_id] if game_id is not None else [],
    )


def _game_compare_line(row: dict[str, Any]) -> str:
    name = _safe_str(row.get("name")) or "Unknown title"
    year = _safe_int(row.get("release_year"))
    genres = split_list(row.get("genres_list"))
    platforms = split_list(row.get("platforms_list"))
    themes = split_list(row.get("themes_list"))
    hidden_gem = _safe_bool(row.get("hidden_gem_balanced_flag"))
    return (
        f"{name}: release year {year if year is not None else 'unknown'}; "
        f"genres {', '.join(genres[:4]) if genres else 'unknown'}; "
        f"platforms {', '.join(platforms[:5]) if platforms else 'unknown'}; "
        f"themes {', '.join(themes[:4]) if themes else 'unknown'}; "
        f"rating {_format_rating(row.get('total_rating'))}; "
        f"rating count {_format_optional_count(row.get('total_rating_count'))}; "
        f"hidden gem {'yes' if hidden_gem else 'no'}."
    )


def _infer_compare_titles(message: str) -> list[str]:
    text = str(message or "").strip().strip("?")
    patterns = [
        r"compare\s+(.+?)\s+(?:and|vs\.?|versus)\s+(.+)$",
        r"(.+?)\s+(?:vs\.?|versus)\s+(.+)$",
        r"which\s+(?:is|has|one).+?,?\s+(.+?)\s+or\s+(.+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return [
                _clean_game_title_candidate(match.group(1)),
                _clean_game_title_candidate(match.group(2)),
            ]
    return []


def answer_game_compare_question(
    message: str,
    *,
    game_titles: list[str] | None = None,
) -> CatalogFactAnswer | None:
    titles = [title for title in (game_titles or []) if str(title).strip()]
    if len(titles) < 2:
        titles = _infer_compare_titles(message)
    if len(titles) < 2:
        return None

    matched_rows: list[dict[str, Any]] = []
    missing_titles: list[str] = []
    for title in titles[:2]:
        row = find_game_by_title(title)
        if row is None:
            missing_titles.append(title)
        else:
            matched_rows.append(row)

    if len(matched_rows) < 2:
        return CatalogFactAnswer(
            intent="game_compare_no_match",
            answer=(
                "I understood this as a game comparison, but I could not match both titles "
                "to the current app catalog. Try using exact game titles or search them on Explore Games_."
            ),
            prompts=[
                "Is Hades in the dataset?",
                "What platforms is Celeste on?",
                "Where can I explore games?",
            ],
            status="no_results",
            caveats=[
                "Game comparisons require both games to exist in the local app catalog.",
            ],
            source_files=[_source(config.APP_CATALOG_PATH)],
            interpreted_filters={"requested_titles": titles[:2], "missing_titles": missing_titles},
        )

    first, second = matched_rows
    first_name = _safe_str(first.get("name")) or "First game"
    second_name = _safe_str(second.get("name")) or "Second game"
    first_rating = _safe_float(first.get("total_rating"))
    second_rating = _safe_float(second.get("total_rating"))

    rating_note = "Rating comparison is unavailable because one or both games are missing total ratings."
    if first_rating is not None and second_rating is not None:
        if first_rating > second_rating:
            rating_note = f"{first_name} has the higher total rating in the app catalog."
        elif second_rating > first_rating:
            rating_note = f"{second_name} has the higher total rating in the app catalog."
        else:
            rating_note = "Both games have the same total rating in the app catalog."

    game_ids = [
        game_id
        for row in matched_rows
        if (game_id := _safe_int(row.get("game_id"))) is not None
    ]
    answer = (
        f"Here is the catalog-backed comparison. {_game_compare_line(first)} "
        f"{_game_compare_line(second)} {rating_note} This comparison uses project metadata only; "
        "it should not be read as an objective judgment of which game is better."
    )

    return CatalogFactAnswer(
        intent="game_compare",
        answer=answer,
        prompts=[
            "How does Recommend Me use recent games?",
            "What data fields are available for games?",
            "Where can I explore these games?",
        ],
        caveats=[
            "This comparison is based on the local app catalog, not live IGDB data.",
            "Missing ratings, summaries, or metadata can affect the comparison quality.",
        ],
        source_files=[_source(config.APP_CATALOG_PATH)],
        interpreted_filters={
            "game_titles": [first_name, second_name],
            "game_ids": game_ids,
        },
        game_id=game_ids[0] if game_ids else None,
        game_ids=game_ids,
    )


def answer_catalog_count_question(message: str) -> CatalogFactAnswer | None:
    cleaned = str(message or "").strip()
    if not cleaned or not _looks_like_catalog_count_question(cleaned):
        return None

    catalog = _load_catalog()
    if catalog is None:
        return CatalogFactAnswer(
            intent="catalog_count_unavailable",
            answer="I cannot verify that catalog count because the app catalog artifact is missing or unreadable.",
            prompts=[
                "How many games are in the dataset?",
                "What is the top genre?",
                "Where can I explore games?",
            ],
            status="unavailable",
            caveats=["Catalog count questions require data/app/app_game_catalog.parquet."],
            source_files=[_source(config.APP_CATALOG_PATH)],
        )

    dimensions = _guess_dimensions(cleaned)
    if not dimensions:
        return None

    for dimension in dimensions:
        metadata = DIMENSIONS[dimension]
        option = _match_option(cleaned, dimension)
        column = metadata["column"]
        if option is None or column not in catalog.columns:
            continue

        mask = catalog[column].apply(lambda value: _contains_value(value, option))
        hidden_gem_only = "hidden" in _tokenize(cleaned) and "gem" in _tokenize(cleaned)
        if hidden_gem_only and "hidden_gem_balanced_flag" in catalog.columns:
            mask = mask & catalog["hidden_gem_balanced_flag"].apply(_safe_bool)

        count = int(mask.sum())
        total = int(len(catalog))
        count_scope = "hidden-gem games" if hidden_gem_only else "games"
        label = metadata["label"]

        return CatalogFactAnswer(
            intent=f"catalog_{dimension}_count",
            answer=(
                f"The current app catalog contains {_format_count(count)} {count_scope} "
                f"with {option} as a {label}. That is {_format_pct(count, total)} of the "
                f"{_format_count(total)} games in the curated app dataset."
            ),
            prompts=[
                "How many games are in the dataset?",
                "What is the top genre?",
                "Where can I explore games?",
            ],
            caveats=[
                "This count is based on the curated app catalog, not the full IGDB database.",
                "Games can belong to multiple genres, platforms, themes, or modes, so category counts can overlap.",
            ],
            source_files=[_source(config.APP_CATALOG_PATH)],
        )

    return None
