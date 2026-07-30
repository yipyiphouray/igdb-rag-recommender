from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from src.app import config


PROJECT_CONTEXT_SOURCES: tuple[Path, ...] = (
    config.ROOT_DIR / "docs" / "project_source_of_truth" / "final_product_current_state.md",
    config.ROOT_DIR / "docs" / "project_source_of_truth" / "ask_the_guide_knowledge_base.md",
    config.ROOT_DIR / "docs" / "project_source_of_truth" / "ask_the_guide_current_state.md",
    config.ROOT_DIR / "docs" / "project_source_of_truth" / "IGDB_ERD_BusinessRules.md",
    config.ROOT_DIR / "docs" / "project_source_of_truth" / "IGDB_ERD_Data_Dictionary.md",
    config.ROOT_DIR / "docs" / "project_source_of_truth" / "website_visual_style_guide.md",
    config.ROOT_DIR / "docs" / "report" / "descriptive_pillar_findings.md",
    config.ROOT_DIR / "docs" / "report" / "diagnostic_pillar_findings.md",
    config.APP_METHODOLOGY_METRICS_PATH,
    config.APP_INSIGHT_SUMMARY_PATH,
)

SUPPORTED_SCOPE_TERMS = {
    "analytics",
    "catalog",
    "chatbot",
    "cosine",
    "data",
    "dataset",
    "descriptive",
    "diagnostic",
    "discover",
    "discovery",
    "explore",
    "game",
    "games",
    "gem",
    "gems",
    "guide",
    "hidden",
    "igdb",
    "insight",
    "insights",
    "methodology",
    "platform",
    "project",
    "rag",
    "rating",
    "recommend",
    "recommendation",
    "recommender",
    "retrieval",
    "similarity",
    "website",
}

RECOMMENDATION_TERMS = {
    "recommend",
    "recommendation",
    "recommendations",
    "similar",
    "like",
    "match",
    "matches",
    "play",
    "played",
}


@dataclass(frozen=True)
class ProjectContextChunk:
    title: str
    path: str
    section: str
    text: str
    score: float = 0.0


def _relative_path(path: Path) -> str:
    try:
        return path.relative_to(config.ROOT_DIR).as_posix()
    except ValueError:
        return path.as_posix()


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_]+", str(text or "").lower())


def _title_from_path(path: Path) -> str:
    stem = path.stem.replace("_", " ").replace("-", " ").strip()
    return " ".join(part.capitalize() for part in stem.split()) or path.name


def _compact_text(text: str, max_chars: int = 1800) -> str:
    compacted = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(compacted) <= max_chars:
        return compacted
    return compacted[: max_chars - 1].rstrip() + "…"


def _markdown_chunks(path: Path, text: str) -> list[ProjectContextChunk]:
    chunks: list[ProjectContextChunk] = []
    current_heading = _title_from_path(path)
    current_lines: list[str] = []

    for line in text.splitlines():
        heading_match = re.match(r"^(#{1,4})\s+(.+?)\s*$", line)
        if heading_match and current_lines:
            body = "\n".join(current_lines).strip()
            if body:
                chunks.append(
                    ProjectContextChunk(
                        title=_title_from_path(path),
                        path=_relative_path(path),
                        section=current_heading,
                        text=_compact_text(body),
                    )
                )
            current_lines = []
            current_heading = heading_match.group(2).strip()
        elif heading_match:
            current_heading = heading_match.group(2).strip()
        else:
            current_lines.append(line)

    body = "\n".join(current_lines).strip()
    if body:
        chunks.append(
            ProjectContextChunk(
                title=_title_from_path(path),
                path=_relative_path(path),
                section=current_heading,
                text=_compact_text(body),
            )
        )

    return chunks


def _flatten_json(data: Any, prefix: str = "") -> list[str]:
    rows: list[str] = []
    if isinstance(data, dict):
        for key, value in data.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(_flatten_json(value, next_prefix))
    elif isinstance(data, list):
        for index, value in enumerate(data[:30]):
            next_prefix = f"{prefix}[{index}]"
            rows.extend(_flatten_json(value, next_prefix))
    else:
        rows.append(f"{prefix}: {data}")
    return rows


def _json_chunks(path: Path, text: str) -> list[ProjectContextChunk]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []

    lines = _flatten_json(data)
    body = "\n".join(lines)
    return [
        ProjectContextChunk(
            title=_title_from_path(path),
            path=_relative_path(path),
            section="Structured metrics",
            text=_compact_text(body, max_chars=2200),
        )
    ]


@lru_cache(maxsize=1)
def load_project_context_chunks() -> tuple[ProjectContextChunk, ...]:
    chunks: list[ProjectContextChunk] = []
    for path in PROJECT_CONTEXT_SOURCES:
        if not path.exists() or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if not text.strip():
            continue

        if path.suffix.lower() == ".json":
            chunks.extend(_json_chunks(path, text))
        else:
            chunks.extend(_markdown_chunks(path, text))

    return tuple(chunk for chunk in chunks if chunk.text.strip())


def project_retrieval_status() -> dict[str, Any]:
    available_sources = [
        _relative_path(path)
        for path in PROJECT_CONTEXT_SOURCES
        if path.exists() and path.is_file()
    ]
    return {
        "source_count": len(available_sources),
        "chunk_count": len(load_project_context_chunks()),
        "sources": available_sources,
    }


def is_supported_project_scope(message: str) -> bool:
    tokens = set(_tokenize(message))
    if tokens.intersection(SUPPORTED_SCOPE_TERMS):
        return True

    normalized = " ".join(str(message or "").lower().split())
    supported_phrases = (
        "what is your purpose",
        "how does this work",
        "what can you do",
        "where should i go",
        "what page",
        "how many",
    )
    return any(phrase in normalized for phrase in supported_phrases)


def has_recommendation_intent(message: str) -> bool:
    tokens = set(_tokenize(message))
    return bool(tokens.intersection(RECOMMENDATION_TERMS)) and bool(
        tokens.intersection({"game", "games", "play", "played", "recommend", "similar", "like"})
    )


def retrieve_project_context(message: str, *, top_k: int = 5) -> list[ProjectContextChunk]:
    query_tokens = _tokenize(message)
    if not query_tokens:
        return []

    query_counts: dict[str, int] = {}
    for token in query_tokens:
        query_counts[token] = query_counts.get(token, 0) + 1

    chunks = load_project_context_chunks()
    document_frequency: dict[str, int] = {}
    chunk_tokens: list[list[str]] = []
    for chunk in chunks:
        tokens = _tokenize(f"{chunk.title} {chunk.section} {chunk.text}")
        chunk_tokens.append(tokens)
        for token in set(tokens):
            document_frequency[token] = document_frequency.get(token, 0) + 1

    scored: list[ProjectContextChunk] = []
    total_chunks = max(1, len(chunks))
    normalized_query = " ".join(query_tokens)

    for chunk, tokens in zip(chunks, chunk_tokens):
        if not tokens:
            continue
        token_counts: dict[str, int] = {}
        for token in tokens:
            token_counts[token] = token_counts.get(token, 0) + 1

        score = 0.0
        for token, query_count in query_counts.items():
            term_frequency = token_counts.get(token, 0)
            if term_frequency <= 0:
                continue
            inverse_document_frequency = math.log(
                1 + (total_chunks + 1) / (document_frequency.get(token, 0) + 1)
            )
            score += query_count * (1 + math.log(term_frequency)) * inverse_document_frequency

        section_text = f"{chunk.section} {chunk.title}".lower()
        if any(token in section_text for token in query_counts):
            score *= 1.25

        if normalized_query and normalized_query in chunk.text.lower():
            score += 5.0

        if score > 0:
            scored.append(
                ProjectContextChunk(
                    title=chunk.title,
                    path=chunk.path,
                    section=chunk.section,
                    text=chunk.text,
                    score=round(score, 4),
                )
            )

    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[: max(1, min(top_k, 8))]
