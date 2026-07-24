from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

import requests


DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"
GEMINI_ENDPOINT_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)


@dataclass(frozen=True)
class LLMResult:
    answer: str
    provider: str
    model: str
    status: str
    error: str | None = None


@dataclass(frozen=True)
class LLMToolPlan:
    tool: str
    intent: str
    confidence: float
    filters: dict[str, Any]
    metric_name: str | None = None
    distribution_field: str | None = None
    game_title: str | None = None
    game_titles: list[str] | None = None
    term: str | None = None
    project_question: str | None = None
    reason: str | None = None
    provider: str = "none"
    model: str = "none"
    status: str = "unavailable"
    error: str | None = None


def get_llm_provider_status() -> dict[str, object]:
    provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
    model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL
    api_key_available = bool(os.getenv("GEMINI_API_KEY", "").strip())
    return {
        "provider": provider,
        "model": model,
        "api_key_available": api_key_available,
    }


def llm_available() -> bool:
    status = get_llm_provider_status()
    return status["provider"] == "gemini" and bool(status["api_key_available"])


def generate_grounded_answer(
    *,
    question: str,
    context: str,
    history: list[dict[str, str]] | None = None,
    timeout_seconds: int = 18,
) -> LLMResult:
    status = get_llm_provider_status()
    provider = str(status["provider"])
    model = str(status["model"])
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if provider != "gemini":
        return LLMResult(
            answer="",
            provider=provider,
            model=model,
            status="unavailable",
            error=f"Unsupported LLM_PROVIDER: {provider}",
        )

    if not api_key:
        return LLMResult(
            answer="",
            provider=provider,
            model=model,
            status="unavailable",
            error="Missing GEMINI_API_KEY.",
        )

    prompt = _build_grounded_prompt(question=question, context=context, history=history or [])
    url = GEMINI_ENDPOINT_TEMPLATE.format(model=model)

    try:
        response = requests.post(
            url,
            params={"key": api_key},
            json={
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}],
                    }
                ]
            },
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as error:
        status_code = None
        response_text = ""
        if getattr(error, "response", None) is not None:
            status_code = error.response.status_code
            response_text = str(error.response.text or "")[:500]
        return LLMResult(
            answer="",
            provider=provider,
            model=model,
            status="error",
            error=(
                f"{type(error).__name__}"
                + (f" status={status_code}" if status_code else "")
                + (f" response={response_text}" if response_text else "")
            ),
        )

    answer = _extract_gemini_text(payload)
    if not answer:
        return LLMResult(
            answer="",
            provider=provider,
            model=model,
            status="error",
            error="Gemini returned no answer text.",
        )

    return LLMResult(
        answer=answer.strip(),
        provider=provider,
        model=model,
        status="success",
    )


def plan_chat_tool(
    *,
    question: str,
    filter_options: dict[str, Any] | None,
    history: list[dict[str, str]] | None = None,
    timeout_seconds: int = 12,
) -> LLMToolPlan:
    status = get_llm_provider_status()
    provider = str(status["provider"])
    model = str(status["model"])
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if provider != "gemini":
        return LLMToolPlan(
            tool="fallback",
            intent="planner_unavailable",
            confidence=0.0,
            filters={},
            provider=provider,
            model=model,
            error=f"Unsupported LLM_PROVIDER: {provider}",
        )

    if not api_key:
        return LLMToolPlan(
            tool="fallback",
            intent="planner_unavailable",
            confidence=0.0,
            filters={},
            provider=provider,
            model=model,
            error="Missing GEMINI_API_KEY.",
        )

    prompt = _build_tool_planning_prompt(
        question=question,
        filter_options=filter_options or {},
        history=history or [],
    )
    url = GEMINI_ENDPOINT_TEMPLATE.format(model=model)

    try:
        response = requests.post(
            url,
            params={"key": api_key},
            json={
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}],
                    }
                ],
                "generationConfig": {
                    "temperature": 0.0,
                    "responseMimeType": "application/json",
                },
            },
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as error:
        status_code = None
        response_text = ""
        if getattr(error, "response", None) is not None:
            status_code = error.response.status_code
            response_text = str(error.response.text or "")[:500]
        return LLMToolPlan(
            tool="fallback",
            intent="planner_error",
            confidence=0.0,
            filters={},
            provider=provider,
            model=model,
            status="error",
            error=(
                f"{type(error).__name__}"
                + (f" status={status_code}" if status_code else "")
                + (f" response={response_text}" if response_text else "")
            ),
        )

    raw_text = _extract_gemini_text(payload)
    parsed = _parse_json_object(raw_text)
    if not parsed:
        return LLMToolPlan(
            tool="fallback",
            intent="planner_parse_error",
            confidence=0.0,
            filters={},
            provider=provider,
            model=model,
            status="error",
            error="Planner returned invalid JSON.",
        )

    return _normalize_tool_plan(parsed, provider=provider, model=model)


def _build_grounded_prompt(
    *,
    question: str,
    context: str,
    history: list[dict[str, str]],
) -> str:
    trimmed_history = history[-6:]
    history_lines = []
    for item in trimmed_history:
        role = str(item.get("role", "")).strip().lower()
        content = str(item.get("content", "")).strip()
        if role and content:
            history_lines.append(f"{role}: {content[:900]}")

    history_text = "\n".join(history_lines) if history_lines else "No prior context."

    return f"""You are Ask the Guide_, a scoped AI guide for an IGDB game-discovery analytics website.

Answer only questions related to this project, IGDB/game catalog data, game discovery, recommendations, hidden gems, methodology, RAG, analytics findings, or website navigation.

Voice:
- Speak as Ask the Guide_ in first person.
- Sound like a focused system intelligence inside this IGDB project.
- Be analytical, precise, direct, and intuitive for a normal website user.
- Use "I" naturally: "I can check...", "I use...", "I do not have enough evidence..."
- Avoid warmth, casual pleasantries, jokes, apologies, encouragement, or filler.
- Prefer short declarative sentences.
- Do not use artificial labels such as "Assessment:", "Evidence:", "Constraint:", or "Directive:" in the answer.
- Do not call the user "Subject."
- Do not claim actual consciousness, emotions, personal memory, or human experience.
- Do not sound like a general assistant or friendly chatbot.

Rules:
- Use only the retrieved project context below.
- Do not invent dataset counts, metrics, methods, or unsupported facts.
- If the context is not enough, say the project context does not provide enough evidence.
- If the user asks for ranked game recommendations, explain that Recommend Me_ is the main ranked recommender and tell them what inputs to provide there.
- Do not reveal internal storage details, material names, source names, paths, formats, filenames, retrieval IDs, retrieval scores, or retrieval metadata.
- Do not mention documents, files, artifacts, markdown, parquet, JSON, databases, paths, chunks, or storage formats.
- If the user asks where your information comes from or asks about sources or files, answer exactly: "I strictly use the context available within this website to answer."
- Do not say "according to the document", "the source says", or similar source-revealing phrasing.
- Keep the answer concise and operational.
- Do not claim live IGDB access.

Conversation context:
{history_text}

Retrieved project context:
{context}

User question:
{question}

Answer:"""


def _build_tool_planning_prompt(
    *,
    question: str,
    filter_options: dict[str, Any] | None,
    history: list[dict[str, str]],
) -> str:
    filter_options = filter_options or {}
    allowed_options = {
        "genres": filter_options.get("genres", []),
        "platforms": filter_options.get("platforms", []),
        "themes": filter_options.get("themes", []),
        "game_modes": filter_options.get("game_modes", []),
        "player_perspectives": filter_options.get("player_perspectives", []),
        "release_years": filter_options.get("release_years", []),
    }
    trimmed_history = history[-4:]

    return f"""You are a strict routing planner for the Ask the Guide_ chatbot in an IGDB game-discovery analytics project.

Return exactly one JSON object. Do not answer the user.

Allowed tools:
- project_fact: exact project metrics such as total games, year range, rating coverage, hidden-gem count, PopScore coverage, summary coverage, top genre, top platform, RAG index size.
- catalog_count: count games in the app catalog using filters.
- catalog_distribution: summarize top categories in the app catalog.
- game_lookup: answer factual questions about one specific game in the app catalog.
- game_compare: compare two specific games using app catalog metadata.
- recommendation_input_helper: translate vague user preferences into suggested Recommend Me_ inputs.
- term_definition: define project-specific terms such as PopScore, hidden gem, total_rating_count, RAG, cosine similarity, or rating coverage.
- website_navigation: route users to the correct website page for browsing, recommendations, hidden gems, insights, methodology, or guide questions.
- recommendation_redirect: user wants ranked/similar game recommendations; route them to Recommend Me_.
- project_context: project, methodology, website, data, hidden gem, RAG, analytics explanation question.
- unsupported: unrelated to this IGDB project or game discovery.

Use catalog_count for questions like:
- how many indie games are there
- count RPGs on Switch
- how many hidden gems are on PC
- how many horror games with multiplayer

Use catalog_distribution for questions like:
- what genre has the most games
- top platforms
- most common themes

Use game_lookup for questions like:
- is Baldur's Gate 3 in the dataset
- what platforms is Hades on
- what genre is Celeste
- what is the rating for League of Legends
- summarize Hollow Knight

Use game_compare for questions like:
- compare Hades and Dead Cells
- which has a higher rating, Celeste or Hollow Knight
- how are Stardew Valley and Animal Crossing different

Use recommendation_input_helper for questions like:
- I want cozy games on Switch, what should I put in Recommend Me
- I like Elden Ring, how should I answer the wizard
- how do I get better recommendations

Use term_definition for questions like:
- what is PopScore
- define total_rating_count
- what does RAG-ready mean
- what is a curated dataset

Use website_navigation for questions like:
- where should I go to browse games
- where can I see insights
- what page explains the methodology
- where do I get recommendations

Use project_fact for exact global metrics with no category filter.

Allowed filter keys:
- genres
- platforms
- themes
- game_modes
- player_perspectives
- hidden_gems_only
- release_year_min
- release_year_max

Allowed distribution_field values:
- genres
- platforms
- themes
- game_modes
- player_perspectives

Known catalog values:
{json.dumps(allowed_options, ensure_ascii=False)}

Recent conversation:
{json.dumps(trimmed_history, ensure_ascii=False)}

User question:
{question}

Required JSON shape:
{{
  "tool": "project_fact | catalog_count | catalog_distribution | game_lookup | game_compare | recommendation_input_helper | term_definition | website_navigation | recommendation_redirect | project_context | unsupported",
  "intent": "short_snake_case_intent",
  "confidence": 0.0,
  "filters": {{}},
  "metric_name": null,
  "distribution_field": null,
  "game_title": null,
  "game_titles": [],
  "term": null,
  "project_question": null,
  "reason": "short reason"
}}"""


def _parse_json_object(text: str) -> dict[str, Any] | None:
    cleaned = str(text or "").strip()
    if not cleaned:
        return None

    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, flags=re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1)
    else:
        object_match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if object_match:
            cleaned = object_match.group(0)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _normalize_tool_plan(parsed: dict[str, Any], *, provider: str, model: str) -> LLMToolPlan:
    allowed_tools = {
        "project_fact",
        "catalog_count",
        "catalog_distribution",
        "game_lookup",
        "game_compare",
        "recommendation_input_helper",
        "term_definition",
        "website_navigation",
        "recommendation_redirect",
        "project_context",
        "unsupported",
    }
    tool = str(parsed.get("tool") or "project_context").strip().lower()
    if tool not in allowed_tools:
        tool = "project_context"

    try:
        confidence = float(parsed.get("confidence", 0.5))
    except (TypeError, ValueError):
        confidence = 0.5
    confidence = max(0.0, min(confidence, 1.0))

    filters = parsed.get("filters")
    if not isinstance(filters, dict):
        filters = {}
    game_titles = parsed.get("game_titles")
    if isinstance(game_titles, list):
        normalized_game_titles = [str(title).strip() for title in game_titles if str(title).strip()]
    else:
        normalized_game_titles = []

    return LLMToolPlan(
        tool=tool,
        intent=str(parsed.get("intent") or tool).strip().lower()[:80],
        confidence=confidence,
        filters=filters,
        metric_name=(
            str(parsed.get("metric_name")).strip()
            if parsed.get("metric_name") is not None
            else None
        ),
        distribution_field=(
            str(parsed.get("distribution_field")).strip()
            if parsed.get("distribution_field") is not None
            else None
        ),
        game_title=(
            str(parsed.get("game_title")).strip()
            if parsed.get("game_title") is not None
            else None
        ),
        game_titles=normalized_game_titles,
        term=(
            str(parsed.get("term")).strip()
            if parsed.get("term") is not None
            else None
        ),
        project_question=(
            str(parsed.get("project_question")).strip()
            if parsed.get("project_question") is not None
            else None
        ),
        reason=(
            str(parsed.get("reason")).strip()
            if parsed.get("reason") is not None
            else None
        ),
        provider=provider,
        model=model,
        status="success",
    )


def _extract_gemini_text(payload: dict) -> str:
    candidates = payload.get("candidates") or []
    if not candidates:
        return ""

    parts = (
        candidates[0]
        .get("content", {})
        .get("parts", [])
    )
    text_parts = [str(part.get("text", "")).strip() for part in parts if part.get("text")]
    return "\n".join(part for part in text_parts if part)
