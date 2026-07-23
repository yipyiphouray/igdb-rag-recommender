from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from src.app import config


METHODOLOGY_METRICS_PATH = config.APP_METHODOLOGY_METRICS_PATH
INSIGHT_SUMMARY_PATH = config.APP_INSIGHT_SUMMARY_PATH
LIGHTWEIGHT_RAG_MANIFEST_PATH = config.RAG_DIR / "lightweight" / "manifest.json"


@dataclass(frozen=True)
class ProjectFactAnswer:
    intent: str
    answer: str
    prompts: list[str]
    status: str = "success"
    caveats: list[str] = field(default_factory=list)
    source_files: list[str] = field(default_factory=list)


FACT_FOLLOW_UP_PROMPTS = [
    "What years does the dataset cover?",
    "What is rating coverage?",
    "How does Recommend Me work?",
]


COUNT_TERMS = {
    "amount",
    "count",
    "counts",
    "many",
    "much",
    "number",
    "size",
    "total",
}
DATASET_TERMS = {
    "catalog",
    "data",
    "dataset",
    "project",
    "sample",
}
GAME_TERMS = {
    "game",
    "games",
    "title",
    "titles",
}
YEAR_TERMS = {
    "range",
    "release",
    "span",
    "time",
    "year",
    "years",
}
HIDDEN_GEM_TERMS = {
    "gem",
    "gems",
    "hidden",
    "hidden-gem",
    "hiddengem",
}
COVERAGE_TERMS = {
    "coverage",
    "covered",
    "available",
    "availability",
    "missing",
    "have",
    "has",
}
RAG_INDEX_TERMS = {
    "embedding",
    "embeddings",
    "index",
    "rag",
    "retrieval",
    "vector",
    "vectors",
}
RATING_TERMS = {
    "rating",
    "ratings",
    "rated",
}


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9\-]+", str(text or "").lower())


def _tokens(text: str) -> set[str]:
    return set(_tokenize(text))


def _normalized(text: str) -> str:
    return " ".join(str(text or "").lower().split())


def _has_any(tokens: set[str], options: set[str]) -> bool:
    return bool(tokens.intersection(options))


def _has_phrase(text: str, phrases: list[str]) -> bool:
    normalized = _normalized(text)
    return any(phrase in normalized for phrase in phrases)


@lru_cache(maxsize=8)
def _load_json_file(path: str) -> dict[str, Any] | None:
    source_path = Path(path)
    if not source_path.exists():
        return None
    try:
        return json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _load_metrics() -> dict[str, Any] | None:
    return _load_json_file(str(METHODOLOGY_METRICS_PATH))


def _load_insight_summary() -> dict[str, Any] | None:
    return _load_json_file(str(INSIGHT_SUMMARY_PATH))


def _load_rag_manifest() -> dict[str, Any] | None:
    return _load_json_file(str(LIGHTWEIGHT_RAG_MANIFEST_PATH))


def _source(path: Path) -> str:
    try:
        return str(path.relative_to(config.ROOT_DIR).as_posix())
    except ValueError:
        return str(path.as_posix())


def _is_number(value: object) -> bool:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return False
    return not math.isnan(parsed) and not math.isinf(parsed)


def _as_int(value: object) -> int | None:
    if not _is_number(value):
        return None
    return int(round(float(value)))


def _as_float(value: object) -> float | None:
    if not _is_number(value):
        return None
    return float(value)


def _format_count(value: object) -> str:
    parsed = _as_int(value)
    if parsed is None:
        return "unknown"
    return f"{parsed:,}"


def _format_year(value: object) -> str:
    parsed = _as_int(value)
    if parsed is None:
        return "unknown"
    return str(parsed)


def _format_percent(value: object) -> str:
    parsed = _as_float(value)
    if parsed is None:
        return "unknown"
    if parsed <= 1:
        parsed *= 100
    return f"{parsed:.2f}%"


def _estimated_count(total: object, ratio: object) -> int | None:
    total_count = _as_int(total)
    coverage_ratio = _as_float(ratio)
    if total_count is None or coverage_ratio is None:
        return None
    if coverage_ratio > 1:
        coverage_ratio /= 100
    return int(round(total_count * coverage_ratio))


def _unavailable_answer(intent: str, missing_source: Path) -> ProjectFactAnswer:
    source_name = _source(missing_source)
    return ProjectFactAnswer(
        intent=intent,
        answer=(
            f"I cannot verify that project fact because `{source_name}` is missing or unreadable."
        ),
        status="unavailable",
        caveats=[
            "Exact chatbot facts must come from structured project artifacts."
        ],
        prompts=FACT_FOLLOW_UP_PROMPTS,
        source_files=[source_name],
    )


def _metrics_answer(
    *,
    intent: str,
    answer: str,
    prompts: list[str] | None = None,
    caveats: list[str] | None = None,
) -> ProjectFactAnswer:
    return ProjectFactAnswer(
        intent=intent,
        answer=answer,
        prompts=prompts or FACT_FOLLOW_UP_PROMPTS,
        caveats=caveats or [
            "This answer comes from the current app methodology metrics artifact."
        ],
        source_files=[_source(METHODOLOGY_METRICS_PATH)],
    )


def _insight_answer(
    *,
    intent: str,
    answer: str,
    prompts: list[str] | None = None,
    caveats: list[str] | None = None,
) -> ProjectFactAnswer:
    return ProjectFactAnswer(
        intent=intent,
        answer=answer,
        prompts=prompts or FACT_FOLLOW_UP_PROMPTS,
        caveats=caveats or [
            "This answer comes from the current website insight summary artifact."
        ],
        source_files=[_source(INSIGHT_SUMMARY_PATH)],
    )


def _rag_manifest_answer(
    *,
    intent: str,
    answer: str,
    prompts: list[str] | None = None,
    caveats: list[str] | None = None,
) -> ProjectFactAnswer:
    return ProjectFactAnswer(
        intent=intent,
        answer=answer,
        prompts=prompts or [
            "What does RAG do here?",
            "Why is the guide not the main recommender?",
            "What data does the guide use?",
        ],
        caveats=caveats or [
            "This answer comes from the current lightweight RAG manifest artifact."
        ],
        source_files=[_source(LIGHTWEIGHT_RAG_MANIFEST_PATH)],
    )


def _answer_total_games(metrics: dict[str, Any]) -> ProjectFactAnswer:
    total_games = metrics.get("total_games")
    start_year = metrics.get("release_year_start")
    end_year = metrics.get("release_year_end")
    return _metrics_answer(
        intent="dataset_total_games",
        answer=(
            f"The current app dataset contains {_format_count(total_games)} games, "
            f"covering release years {_format_year(start_year)} through {_format_year(end_year)}."
        ),
        prompts=[
            "What years does the dataset cover?",
            "How many hidden gems are there?",
            "What is rating coverage?",
        ],
    )


def _answer_year_range(metrics: dict[str, Any]) -> ProjectFactAnswer:
    start_year = metrics.get("release_year_start")
    end_year = metrics.get("release_year_end")
    games_per_year = metrics.get("games_per_year")
    return _metrics_answer(
        intent="dataset_release_year_range",
        answer=(
            f"The current app dataset covers games released from {_format_year(start_year)} "
            f"through {_format_year(end_year)}. The extraction target was about "
            f"{_format_count(games_per_year)} games per release year."
        ),
        prompts=[
            "How many games are in the dataset?",
            "Why is this a curated sample?",
            "What is PopScore coverage?",
        ],
    )


def _answer_games_per_year(metrics: dict[str, Any]) -> ProjectFactAnswer:
    games_per_year = metrics.get("games_per_year")
    start_year = metrics.get("release_year_start")
    end_year = metrics.get("release_year_end")
    return _metrics_answer(
        intent="dataset_games_per_year",
        answer=(
            f"The current extraction target was about {_format_count(games_per_year)} games per release year "
            f"from {_format_year(start_year)} through {_format_year(end_year)}."
        ),
        caveats=[
            "This describes the curated app dataset target, not a full-market count of every game released each year."
        ],
    )


def _answer_hidden_gems(metrics: dict[str, Any]) -> ProjectFactAnswer:
    return _metrics_answer(
        intent="dataset_hidden_gem_count",
        answer=(
            f"The current app dataset identifies {_format_count(metrics.get('hidden_gem_count'))} hidden-gem games. "
            f"The project uses a quality threshold of {_format_count(metrics.get('quality_threshold'))}, "
            f"a minimum rating count of {_format_count(metrics.get('min_rating_count'))}, and lower visibility "
            f"around the {_format_percent(metrics.get('hidden_gem_visibility_percentile'))} visibility cutoff."
        ),
        prompts=[
            "What is a hidden gem?",
            "What is PopScore coverage?",
            "How does hidden-gem preference affect Recommend Me?",
        ],
    )


def _answer_rating_coverage(metrics: dict[str, Any]) -> ProjectFactAnswer:
    total_games = metrics.get("total_games")
    rating_coverage = metrics.get("rating_coverage")
    rating_count = _estimated_count(total_games, rating_coverage)
    count_text = f", which is about {_format_count(rating_count)} games," if rating_count is not None else ""
    return _metrics_answer(
        intent="dataset_rating_coverage",
        answer=(
            f"The current rating coverage is {_format_percent(rating_coverage)}{count_text} "
            "based on the current app dataset. Rating coverage means the share of games that have "
            "a usable rating value in the project catalog."
        ),
        caveats=[
            "IGDB rating coverage is incomplete, so rating-based analysis only applies to games with available ratings."
        ],
        prompts=[
            "What is reliable rating coverage?",
            "How many games are in the dataset?",
            "Why are some ratings missing?",
        ],
    )


def _answer_reliable_rating_coverage(metrics: dict[str, Any]) -> ProjectFactAnswer:
    total_games = metrics.get("total_games")
    reliable_coverage = metrics.get("reliable_rating_coverage")
    reliable_count = _estimated_count(total_games, reliable_coverage)
    count_text = f", or about {_format_count(reliable_count)} games," if reliable_count is not None else ""
    return _metrics_answer(
        intent="dataset_reliable_rating_coverage",
        answer=(
            f"The current reliable rating coverage is {_format_percent(reliable_coverage)}{count_text}. "
            f"In this project, reliable rating coverage focuses on games with enough rating activity, using "
            f"a minimum rating count of {_format_count(metrics.get('min_rating_count'))}."
        ),
        caveats=[
            "Reliable rating coverage is much smaller than basic rating coverage because many games have sparse rating activity."
        ],
        prompts=[
            "What is rating coverage?",
            "What does total_rating_count mean?",
            "How are hidden gems defined?",
        ],
    )


def _answer_popscore_coverage(metrics: dict[str, Any]) -> ProjectFactAnswer:
    total_games = metrics.get("total_games")
    popscore_coverage = metrics.get("popscore_coverage")
    popscore_count = _estimated_count(total_games, popscore_coverage)
    count_text = f", about {_format_count(popscore_count)} games," if popscore_count is not None else ""
    return _metrics_answer(
        intent="dataset_popscore_coverage",
        answer=(
            f"The current PopScore coverage is {_format_percent(popscore_coverage)}{count_text} "
            "in the app dataset. The project uses PopScore as a visibility or interest signal where IGDB provides it."
        ),
        caveats=[
            "PopScore coverage is incomplete, so visibility analysis must be interpreted only among games with available popularity signals."
        ],
        prompts=[
            "What is a hidden gem?",
            "How many hidden gems are there?",
            "Why does visibility matter?",
        ],
    )


def _answer_summary_coverage(metrics: dict[str, Any]) -> ProjectFactAnswer:
    total_games = metrics.get("total_games")
    summary_coverage = metrics.get("summary_coverage")
    summary_count = _estimated_count(total_games, summary_coverage)
    count_text = f", or about {_format_count(summary_count)} games," if summary_count is not None else ""
    return _metrics_answer(
        intent="dataset_summary_coverage",
        answer=(
            f"The current summary coverage is {_format_percent(summary_coverage)}{count_text}. "
            "Summary coverage matters because text metadata helps users understand games and supports retrieval-style explanations."
        ),
        prompts=[
            "What data does this project use?",
            "What does RAG retrieve?",
            "How many games are in the dataset?",
        ],
    )


def _answer_quality_threshold(metrics: dict[str, Any]) -> ProjectFactAnswer:
    return _metrics_answer(
        intent="dataset_quality_threshold",
        answer=(
            f"The project uses {_format_count(metrics.get('quality_threshold'))} as the high-quality rating threshold "
            f"and {_format_count(metrics.get('min_rating_count'))} as the minimum rating-count threshold for stronger "
            "rating evidence."
        ),
        caveats=[
            "These thresholds are project rules for analysis and recommendation interpretation, not universal definitions of game quality."
        ],
        prompts=[
            "What is a hidden gem?",
            "What is reliable rating coverage?",
            "How does Recommend Me use ratings?",
        ],
    )


def _answer_cohort_count(metrics: dict[str, Any], cohort_key: str, label: str) -> ProjectFactAnswer:
    return _metrics_answer(
        intent=f"dataset_{cohort_key}",
        answer=(
            f"The current app dataset has {_format_count(metrics.get(cohort_key))} games in the {label} cohort."
        ),
        caveats=[
            "Cohort counts describe the curated analytical sample and should not be interpreted as full-market prevalence."
        ],
        prompts=[
            "How many games are in the dataset?",
            "What years does the dataset cover?",
            "What is a hidden gem?",
        ],
    )


def _answer_top_genre(insight_summary: dict[str, Any]) -> ProjectFactAnswer:
    descriptive = insight_summary.get("descriptive", {}) or {}
    top_genre = descriptive.get("top_genre", "unknown")
    return _insight_answer(
        intent="dataset_top_genre",
        answer=(
            f"The top genre in the current app summary is {top_genre}. This reflects the curated project catalog, "
            "not necessarily the entire game market."
        ),
        prompts=[
            "What is the top platform?",
            "How many games are in the dataset?",
            "Where can I see insights?",
        ],
    )


def _answer_top_platform(insight_summary: dict[str, Any]) -> ProjectFactAnswer:
    descriptive = insight_summary.get("descriptive", {}) or {}
    top_platform = descriptive.get("top_platform", "unknown")
    return _insight_answer(
        intent="dataset_top_platform",
        answer=(
            f"The top platform in the current app summary is {top_platform}. This reflects platform coverage "
            "inside the curated project catalog."
        ),
        prompts=[
            "What is the top genre?",
            "Where can I explore games?",
            "What years does the dataset cover?",
        ],
    )


def _answer_rag_index_size(manifest: dict[str, Any]) -> ProjectFactAnswer:
    row_count = manifest.get("row_count")
    embedding_shape = manifest.get("embedding_shape", [])
    model_name = manifest.get("model_name", "unknown embedding model")
    dimensions = embedding_shape[1] if isinstance(embedding_shape, list) and len(embedding_shape) > 1 else None
    dimension_text = f" with {dimensions} embedding dimensions" if dimensions else ""
    return _rag_manifest_answer(
        intent="rag_index_size",
        answer=(
            f"The current lightweight RAG index contains {_format_count(row_count)} embedded game records"
            f"{dimension_text}. It was built with `{model_name}`."
        ),
        caveats=[
            "The current lightweight index is game-profile oriented. The project guide still needs a project-document retrieval layer for stronger methodology and dataset-fact answers."
        ],
    )


def _looks_like_total_games_question(message: str, tokens: set[str]) -> bool:
    if _has_phrase(
        message,
        [
            "how many games",
            "number of games",
            "total games",
            "dataset size",
            "catalog size",
            "how big is the dataset",
            "how many titles",
            "number of titles",
        ],
    ):
        return True
    return (
        _has_any(tokens, COUNT_TERMS)
        and _has_any(tokens, GAME_TERMS)
        and _has_any(tokens, DATASET_TERMS)
    )


def _looks_like_year_range_question(message: str, tokens: set[str]) -> bool:
    if _has_phrase(
        message,
        [
            "what years",
            "which years",
            "year range",
            "release years",
            "years does the dataset cover",
            "years are covered",
            "time span",
        ],
    ):
        return True
    return _has_any(tokens, YEAR_TERMS) and _has_any(tokens, {"cover", "covers", "covered", "span", "range"})


def _looks_like_hidden_gem_count_question(message: str, tokens: set[str]) -> bool:
    return _has_any(tokens, HIDDEN_GEM_TERMS) and (
        _has_any(tokens, COUNT_TERMS)
        or _has_phrase(message, ["how many hidden gems", "hidden gem count", "hidden gems are there"])
    )


def _looks_like_rag_index_question(message: str, tokens: set[str]) -> bool:
    return _has_any(tokens, RAG_INDEX_TERMS) and (
        _has_any(tokens, COUNT_TERMS)
        or _has_phrase(message, ["how many embeddings", "index size", "vector database size", "rag index size"])
    )


def answer_project_fact_question(message: str) -> ProjectFactAnswer | None:
    cleaned = str(message or "").strip()
    if not cleaned:
        return None

    tokens = _tokens(cleaned)

    if _looks_like_rag_index_question(cleaned, tokens):
        manifest = _load_rag_manifest()
        if manifest is None:
            return _unavailable_answer("rag_index_size", LIGHTWEIGHT_RAG_MANIFEST_PATH)
        return _answer_rag_index_size(manifest)

    metrics_required = (
        _looks_like_total_games_question(cleaned, tokens)
        or _looks_like_year_range_question(cleaned, tokens)
        or _looks_like_hidden_gem_count_question(cleaned, tokens)
        or _has_phrase(cleaned, ["games per year", "per release year"])
        or (_has_any(tokens, RATING_TERMS) and _has_any(tokens, COVERAGE_TERMS.union(COUNT_TERMS)))
        or ("popscore" in tokens or _has_phrase(cleaned, ["pop score"]))
        or ("summary" in tokens or "summaries" in tokens or "description" in tokens or "descriptions" in tokens)
        or ("threshold" in tokens and ("quality" in tokens or _has_any(tokens, RATING_TERMS)))
        or ("cohort" in tokens and _has_any(tokens, COUNT_TERMS))
        or _has_phrase(
            cleaned,
            [
                "quality cohort",
                "lower-rated cohort",
                "lower rated cohort",
                "popularity cohort",
                "low-visibility cohort",
                "low visibility cohort",
                "comparison cohort",
            ],
        )
    )

    if metrics_required:
        metrics = _load_metrics()
        if metrics is None:
            return _unavailable_answer("dataset_fact", METHODOLOGY_METRICS_PATH)

        if _looks_like_hidden_gem_count_question(cleaned, tokens):
            return _answer_hidden_gems(metrics)
        if _has_phrase(cleaned, ["games per year", "per release year"]):
            return _answer_games_per_year(metrics)
        if _looks_like_year_range_question(cleaned, tokens):
            return _answer_year_range(metrics)
        if "summary" in tokens or "summaries" in tokens or "description" in tokens or "descriptions" in tokens:
            return _answer_summary_coverage(metrics)
        if "reliable" in tokens and _has_any(tokens, RATING_TERMS):
            return _answer_reliable_rating_coverage(metrics)
        if _has_any(tokens, RATING_TERMS) and _has_any(tokens, COVERAGE_TERMS.union(COUNT_TERMS)):
            return _answer_rating_coverage(metrics)
        if "popscore" in tokens or _has_phrase(cleaned, ["pop score"]):
            return _answer_popscore_coverage(metrics)
        if "threshold" in tokens and ("quality" in tokens or _has_any(tokens, RATING_TERMS)):
            return _answer_quality_threshold(metrics)
        if _looks_like_total_games_question(cleaned, tokens):
            return _answer_total_games(metrics)

        if _has_phrase(cleaned, ["quality cohort"]):
            return _answer_cohort_count(metrics, "quality_cohort_count", "quality")
        if _has_phrase(cleaned, ["lower-rated cohort", "lower rated cohort"]):
            return _answer_cohort_count(metrics, "lower_rated_cohort_count", "lower-rated")
        if _has_phrase(cleaned, ["popularity cohort"]):
            return _answer_cohort_count(metrics, "popularity_cohort_count", "popularity")
        if _has_phrase(cleaned, ["low-visibility cohort", "low visibility cohort"]):
            return _answer_cohort_count(metrics, "low_visibility_cohort_count", "low-visibility")
        if _has_phrase(cleaned, ["comparison cohort"]):
            return _answer_cohort_count(metrics, "comparison_cohort_count", "comparison")

    if _has_phrase(cleaned, ["top genre", "most common genre", "biggest genre"]):
        insight_summary = _load_insight_summary()
        if insight_summary is None:
            return _unavailable_answer("dataset_top_genre", INSIGHT_SUMMARY_PATH)
        return _answer_top_genre(insight_summary)

    if _has_phrase(cleaned, ["top platform", "most common platform", "biggest platform"]):
        insight_summary = _load_insight_summary()
        if insight_summary is None:
            return _unavailable_answer("dataset_top_platform", INSIGHT_SUMMARY_PATH)
        return _answer_top_platform(insight_summary)

    return None
