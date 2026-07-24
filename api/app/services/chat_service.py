from __future__ import annotations

from typing import Any

from app.schemas.chat import ChatRequest
from src.app.llm_provider import (
    generate_grounded_answer,
    get_llm_provider_status,
    llm_available,
    plan_chat_tool,
)
from src.app.catalog_facts import (
    CatalogFactAnswer,
    answer_catalog_count_question,
    answer_catalog_count_with_filters,
    answer_catalog_distribution,
    answer_game_compare_question,
    answer_game_lookup_question,
    get_catalog_filter_options,
)
from src.app.project_terms import (
    ProjectToolAnswer,
    answer_recommendation_input_helper,
    answer_term_definition_question,
    answer_website_navigation_question,
)
from src.app.project_context_retrieval import (
    has_recommendation_intent,
    is_supported_project_scope,
    project_retrieval_status,
    retrieve_project_context,
)
from src.app.project_facts import ProjectFactAnswer, answer_project_fact_question
from src.app.rag_service import get_rag_backend, rag_status


GUIDED_ROUTE_MODES = {
    "custom_question",
    "dataset_size",
    "dataset_year_range",
    "explain_data",
    "explain_hidden_gems",
    "explain_limitations",
    "explain_project",
    "explain_rag",
    "explain_recommendation",
    "recommend_games",
    "recommend_me_guidance",
    "rating_coverage",
    "search_catalog",
    "website_navigation",
}

FACT_ROUTE_QUESTIONS = {
    "dataset_size": "How many games does the dataset have?",
    "dataset_year_range": "What years does the dataset cover?",
    "rating_coverage": "What is rating coverage?",
}

DEFAULT_PROMPTS = [
    "Explain this project",
    "Explain the data",
    "Help me use Recommend Me",
]

RAG_FOLLOW_UP_PROMPTS = [
    "How does Recommend Me work?",
    "What is a hidden gem?",
    "What does RAG do here?",
]

DEFAULT_NEXT_ACTIONS = [
    {"label": "Explore Games_", "href": "/explore"},
    {"label": "Open Recommend Me_", "href": "/recommendations"},
    {"label": "View Methodology_", "href": "/methodology"},
]


def get_chat_status() -> dict[str, Any]:
    artifacts = rag_status()
    project_context = project_retrieval_status()
    llm_status = get_llm_provider_status()
    warnings: list[str] = []

    if not artifacts.get("app_catalog", False):
        warnings.append("Missing data/app/app_game_catalog.parquet.")
    if not project_context["chunk_count"]:
        warnings.append("No project context chunks are available for chatbot retrieval.")
    if not llm_status["api_key_available"]:
        warnings.append("Missing GEMINI_API_KEY. Chat will use extractive fallback answers.")

    return {
        "status": "ready" if project_context["chunk_count"] else "unavailable",
        "backend": get_rag_backend(),
        "catalog_available": bool(artifacts.get("app_catalog", False)),
        "vector_store_available": bool(artifacts.get("vector_store", False)),
        "retrieval_artifacts_available": bool(
            artifacts.get("lightweight_embeddings", False)
            and artifacts.get("lightweight_game_ids", False)
            and artifacts.get("lightweight_manifest", False)
        ),
        "collection_available": False,
        "project_context_available": bool(project_context["chunk_count"]),
        "project_context_chunk_count": int(project_context["chunk_count"]),
        "engine": "scoped_rag_llm_project_guide",
        "llm_provider": str(llm_status["provider"]),
        "llm_model": str(llm_status["model"]),
        "llm_available": llm_available(),
        "warnings": warnings,
    }


def _build_chat_response(
    *,
    intent: str,
    answer: str,
    prompts: list[str],
    status: str = "success",
    caveats: list[str] | None = None,
    mode: str | None = None,
    sources: list[dict[str, Any]] | None = None,
    next_actions: list[dict[str, str]] | None = None,
    llm_provider: str | None = None,
    llm_model: str | None = None,
    confidence: float = 1.0,
    route_source: str = "selected_route_mode",
    interpreted_preferences: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "answer": answer,
        "mode": mode or f"condition_{intent}",
        "status": status,
        "retrieved_games": [],
        "caveats": caveats or [],
        "applied_filters": {},
        "follow_up_prompts": prompts,
        "contextual_query": None,
        "interpreted_preferences": interpreted_preferences or {},
        "chat_intent": intent,
        "intent_confidence": confidence,
        "route_source": route_source,
        "matched_intent_example": None,
        "sources": sources or [],
        "next_actions": next_actions or [],
        "llm_provider": llm_provider,
        "llm_model": llm_model,
    }


def _project_fact_chat_response(fact: ProjectFactAnswer) -> dict[str, Any]:
    caveats = list(fact.caveats)
    if fact.source_files:
        caveats.append(f"Source artifact: {', '.join(fact.source_files)}.")

    return _build_chat_response(
        intent=fact.intent,
        answer=fact.answer,
        prompts=fact.prompts,
        status=fact.status,
        caveats=caveats,
        mode=f"project_fact_{fact.intent}",
        sources=[
            {
                "title": "Structured project fact",
                "path": source_file,
                "section": fact.intent,
                "score": None,
            }
            for source_file in fact.source_files
        ],
        next_actions=_next_actions_for_intent(fact.intent),
    )


def _catalog_fact_chat_response(fact: CatalogFactAnswer) -> dict[str, Any]:
    caveats = list(fact.caveats)
    if fact.source_files:
        caveats.append(f"Source artifact: {', '.join(fact.source_files)}.")

    next_actions = _next_actions_for_intent(fact.intent)
    if fact.game_ids:
        game_actions = [
            {"label": f"Open game file {index}_", "href": f"/explore/{game_id}"}
            for index, game_id in enumerate(fact.game_ids[:2], start=1)
        ]
        next_actions = [*game_actions, *next_actions]
    elif fact.game_id is not None:
        next_actions = [{"label": "Open game file_", "href": f"/explore/{fact.game_id}"}, *next_actions]

    return _build_chat_response(
        intent=fact.intent,
        answer=fact.answer,
        prompts=fact.prompts,
        status=fact.status,
        caveats=caveats,
        mode=f"catalog_fact_{fact.intent}",
        sources=[
            {
                "title": "App catalog",
                "path": source_file,
                "section": fact.intent,
                "score": None,
            }
            for source_file in fact.source_files
        ],
        next_actions=next_actions,
        interpreted_preferences=fact.interpreted_filters,
    )


def _project_tool_chat_response(answer: ProjectToolAnswer) -> dict[str, Any]:
    caveats = list(answer.caveats)
    if answer.source_files:
        caveats.append(f"Source artifact: {', '.join(answer.source_files)}.")

    next_actions = _next_actions_for_intent(answer.intent)
    if answer.intent == "website_navigation" and answer.interpreted_preferences.get("href"):
        next_actions = [
            {
                "label": str(answer.interpreted_preferences.get("label") or "Open page_"),
                "href": str(answer.interpreted_preferences["href"]),
            }
        ]

    return _build_chat_response(
        intent=answer.intent,
        answer=answer.answer,
        prompts=answer.prompts,
        status=answer.status,
        caveats=caveats,
        mode=f"project_tool_{answer.intent}",
        sources=[
            {
                "title": "Project source",
                "path": source_file,
                "section": answer.intent,
                "score": None,
            }
            for source_file in answer.source_files
        ],
        next_actions=next_actions,
        interpreted_preferences=answer.interpreted_preferences,
    )


def _unsupported_route_response() -> dict[str, Any]:
    return _build_chat_response(
        intent="unsupported_question",
        answer=(
            "Assessment: Unsupported. Scope: IGDB project, game catalog, methodology, recommendations, "
            "hidden gems, RAG, analytics findings, and website navigation. Directive: Subject must ask a "
            "project or catalog question."
        ),
        prompts=DEFAULT_PROMPTS,
        status="unsupported_question",
        caveats=[
            "The Guide is intentionally scoped so it does not drift into unrelated chatbot behavior."
        ],
        mode="scoped_refusal",
        next_actions=DEFAULT_NEXT_ACTIONS,
    )


def _next_actions_for_intent(intent: str) -> list[dict[str, str]]:
    if "game_compare" in intent:
        return [{"label": "Explore Games_", "href": "/explore"}]
    if "term_definition" in intent:
        return [{"label": "View Methodology_", "href": "/methodology"}]
    if "recommendation_input_helper" in intent:
        return [{"label": "Open Recommend Me_", "href": "/recommendations"}]
    if "recommend" in intent:
        return [{"label": "Open Recommend Me_", "href": "/recommendations"}]
    if "hidden" in intent:
        return [{"label": "Open Hidden Gems_", "href": "/hidden-gems"}]
    if "navigation" in intent:
        return DEFAULT_NEXT_ACTIONS
    if "game_lookup" in intent:
        return [{"label": "Explore Games_", "href": "/explore"}]
    if "data" in intent or "dataset" in intent or "rating" in intent:
        return [
            {"label": "Explore Games_", "href": "/explore"},
            {"label": "View Insights_", "href": "/insights"},
        ]
    if "methodology" in intent or "rag" in intent:
        return [{"label": "View Methodology_", "href": "/methodology"}]
    return DEFAULT_NEXT_ACTIONS


def _sources_from_chunks(chunks) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    sources: list[dict[str, Any]] = []
    for chunk in chunks:
        key = (chunk.path, chunk.section)
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            {
                "title": chunk.title,
                "path": chunk.path,
                "section": chunk.section,
                "score": chunk.score,
            }
        )
    return sources


def _context_from_chunks(chunks) -> str:
    context_parts = []
    for index, chunk in enumerate(chunks, start=1):
        context_parts.append(
            f"[{index}] {chunk.title} | {chunk.section} | {chunk.path}\n{chunk.text}"
        )
    return "\n\n".join(context_parts)


def _fallback_answer_from_chunks(message: str, chunks) -> str:
    if not chunks:
        return (
            "Assessment: No evidence. Constraint: Project context does not provide enough information "
            "for this question. Directive: Subject should ask about the dataset, methodology, "
            "Recommend Me_, hidden gems, or website navigation."
        )

    lead = chunks[0]
    answer = (
        f"Evidence: {lead.text[:700].strip()}"
    )
    if len(lead.text) > 700:
        answer = answer.rstrip() + "…"

    if has_recommendation_intent(message):
        answer += (
            "\n\nDirective: Subject should use Recommend Me_ for ranked game matches. Rationale: "
            "Recommend Me_ applies the cosine-similarity workflow to structured preferences."
        )

    return answer


def _history_for_llm(request: ChatRequest) -> list[dict[str, str]]:
    return [
        {"role": item.role, "content": item.content}
        for item in (request.history or [])[-6:]
    ]


def _answer_scoped_rag_question(request: ChatRequest) -> dict[str, Any]:
    message = request.message.strip()

    tool_response = _answer_with_tool_planner(request)
    if tool_response is not None:
        return tool_response

    return _answer_with_fallback_routing(request)


def _answer_with_tool_planner(request: ChatRequest) -> dict[str, Any] | None:
    message = request.message.strip()
    llm_status = get_llm_provider_status()
    plan = plan_chat_tool(
        question=message,
        filter_options=get_catalog_filter_options(),
        history=_history_for_llm(request),
    )

    if plan.status != "success" or plan.tool == "fallback" or plan.confidence < 0.45:
        return None

    if plan.tool == "unsupported":
        response = _unsupported_route_response()
        return {
            **response,
            "llm_provider": plan.provider,
            "llm_model": plan.model,
            "route_source": "llm_tool_planner",
            "intent_confidence": plan.confidence,
            "interpreted_preferences": {
                "tool": plan.tool,
                "planner_reason": plan.reason,
            },
        }

    if plan.tool == "recommendation_redirect":
        return _build_chat_response(
            intent=plan.intent or "recommend_me_guidance",
            answer=(
                "Assessment: Recommendation request detected. Directive: Subject should use Recommend Me_ "
                "for ranked game matches. Rationale: Recommend Me_ runs the cosine-similarity engine "
                "against catalog games. "
                "Input fields: recent games, platform, genre, mood, playstyle, rating-quality preference, "
                "and hidden-gem preference."
            ),
            prompts=[
                "How does Recommend Me work?",
                "Why do recent games help?",
                "What is a hidden gem?",
            ],
            mode="tool_recommendation_redirect",
            next_actions=[{"label": "Open Recommend Me_", "href": "/recommendations"}],
            llm_provider=plan.provider,
            llm_model=plan.model,
            confidence=plan.confidence,
            route_source="llm_tool_planner",
            interpreted_preferences={
                "tool": plan.tool,
                "planner_reason": plan.reason,
            },
        )

    if plan.tool == "catalog_count":
        catalog_fact = answer_catalog_count_with_filters(plan.filters)
        if catalog_fact is not None:
            response = _catalog_fact_chat_response(catalog_fact)
            return {
                **response,
                "llm_provider": plan.provider,
                "llm_model": plan.model,
                "route_source": "llm_tool_planner",
                "intent_confidence": plan.confidence,
                "interpreted_preferences": {
                    **response.get("interpreted_preferences", {}),
                    "tool": plan.tool,
                    "planner_reason": plan.reason,
                },
            }
        return _build_chat_response(
            intent="catalog_count_needs_clarification",
            answer=(
                "Assessment: Needs clarification. Intent: catalog count. Issue: filters did not map to "
                "known catalog metadata. Directive: Subject must specify genre, platform, theme, "
                "game mode, or hidden-gem condition."
            ),
            prompts=[
                "How many Indie games are there?",
                "How many games are on Nintendo Switch?",
                "What genre has the most games?",
            ],
            status="needs_clarification",
            mode="tool_catalog_count_needs_clarification",
            next_actions=[{"label": "Explore Games_", "href": "/explore"}],
            llm_provider=plan.provider,
            llm_model=plan.model,
            confidence=plan.confidence,
            route_source="llm_tool_planner",
            interpreted_preferences={
                "tool": plan.tool,
                "raw_filters": plan.filters,
                "planner_reason": plan.reason,
            },
        )

    if plan.tool == "catalog_distribution":
        catalog_fact = answer_catalog_distribution(plan.distribution_field)
        if catalog_fact is not None:
            response = _catalog_fact_chat_response(catalog_fact)
            return {
                **response,
                "llm_provider": plan.provider,
                "llm_model": plan.model,
                "route_source": "llm_tool_planner",
                "intent_confidence": plan.confidence,
                "interpreted_preferences": {
                    "tool": plan.tool,
                    "distribution_field": plan.distribution_field,
                    "planner_reason": plan.reason,
                },
            }

    if plan.tool == "game_lookup":
        catalog_fact = answer_game_lookup_question(message, game_title=plan.game_title)
        if catalog_fact is not None:
            response = _catalog_fact_chat_response(catalog_fact)
            return {
                **response,
                "llm_provider": plan.provider,
                "llm_model": plan.model,
                "route_source": "llm_tool_planner",
                "intent_confidence": plan.confidence,
                "interpreted_preferences": {
                    **response.get("interpreted_preferences", {}),
                    "tool": plan.tool,
                    "game_title": plan.game_title,
                    "planner_reason": plan.reason,
                },
            }
        return _build_chat_response(
            intent="game_lookup_no_match",
            answer=(
                "Assessment: No match. Intent: game lookup. Issue: title not found in the current app "
                "catalog. Directive: Subject should use the exact title or search on Explore Games_."
            ),
            prompts=[
                "Is Hades in the dataset?",
                "What platforms is Celeste on?",
                "Where can I explore games?",
            ],
            status="no_results",
            mode="tool_game_lookup_no_match",
            next_actions=[{"label": "Explore Games_", "href": "/explore"}],
            llm_provider=plan.provider,
            llm_model=plan.model,
            confidence=plan.confidence,
            route_source="llm_tool_planner",
            interpreted_preferences={
                "tool": plan.tool,
                "game_title": plan.game_title,
                "planner_reason": plan.reason,
                },
            )

    if plan.tool == "game_compare":
        catalog_fact = answer_game_compare_question(message, game_titles=plan.game_titles)
        if catalog_fact is not None:
            response = _catalog_fact_chat_response(catalog_fact)
            return {
                **response,
                "llm_provider": plan.provider,
                "llm_model": plan.model,
                "route_source": "llm_tool_planner",
                "intent_confidence": plan.confidence,
                "interpreted_preferences": {
                    **response.get("interpreted_preferences", {}),
                    "tool": plan.tool,
                    "game_titles": plan.game_titles or [],
                    "planner_reason": plan.reason,
                },
            }
        return _build_chat_response(
            intent="game_compare_needs_clarification",
            answer=(
                "Assessment: Needs clarification. Intent: game comparison. Required input: two exact "
                "game titles. Example: Compare Hades and Celeste."
            ),
            prompts=[
                "Compare Hades and Celeste",
                "Is Hades in the dataset?",
                "Where can I explore games?",
            ],
            status="needs_clarification",
            mode="tool_game_compare_needs_clarification",
            next_actions=[{"label": "Explore Games_", "href": "/explore"}],
            llm_provider=plan.provider,
            llm_model=plan.model,
            confidence=plan.confidence,
            route_source="llm_tool_planner",
            interpreted_preferences={
                "tool": plan.tool,
                "game_titles": plan.game_titles or [],
                "planner_reason": plan.reason,
            },
        )

    if plan.tool == "recommendation_input_helper":
        game_titles = list(plan.game_titles or [])
        if plan.game_title and plan.game_title not in game_titles:
            game_titles.append(plan.game_title)
        helper_answer = answer_recommendation_input_helper(
            message,
            filters=plan.filters,
            game_titles=game_titles,
        )
        response = _project_tool_chat_response(helper_answer)
        return {
            **response,
            "llm_provider": plan.provider,
            "llm_model": plan.model,
            "route_source": "llm_tool_planner",
            "intent_confidence": plan.confidence,
            "interpreted_preferences": {
                **response.get("interpreted_preferences", {}),
                "tool": plan.tool,
                "planner_reason": plan.reason,
            },
        }

    if plan.tool == "term_definition":
        term_answer = answer_term_definition_question(message, term=plan.term)
        if term_answer is not None:
            response = _project_tool_chat_response(term_answer)
            return {
                **response,
                "llm_provider": plan.provider,
                "llm_model": plan.model,
                "route_source": "llm_tool_planner",
                "intent_confidence": plan.confidence,
                "interpreted_preferences": {
                    **response.get("interpreted_preferences", {}),
                    "tool": plan.tool,
                    "planner_reason": plan.reason,
                },
            }
        return _build_chat_response(
            intent="term_definition_needs_clarification",
            answer=(
                "Assessment: Needs clarification. Intent: term definition. Required input: one project "
                "term. Examples: PopScore, hidden gem, total_rating_count, RAG, cosine similarity."
            ),
            prompts=[
                "What is PopScore?",
                "What is a hidden gem?",
                "What is cosine similarity?",
            ],
            status="needs_clarification",
            mode="tool_term_definition_needs_clarification",
            next_actions=[{"label": "View Methodology_", "href": "/methodology"}],
            llm_provider=plan.provider,
            llm_model=plan.model,
            confidence=plan.confidence,
            route_source="llm_tool_planner",
            interpreted_preferences={
                "tool": plan.tool,
                "term": plan.term,
                "planner_reason": plan.reason,
            },
        )

    if plan.tool == "website_navigation":
        navigation_answer = answer_website_navigation_question(message)
        response = _project_tool_chat_response(navigation_answer)
        return {
            **response,
            "llm_provider": plan.provider,
            "llm_model": plan.model,
            "route_source": "llm_tool_planner",
            "intent_confidence": plan.confidence,
            "interpreted_preferences": {
                **response.get("interpreted_preferences", {}),
                "tool": plan.tool,
                "planner_reason": plan.reason,
            },
        }

    if plan.tool == "project_fact":
        fact = answer_project_fact_question(plan.project_question or message)
        if fact is not None:
            response = _project_fact_chat_response(fact)
            return {
                **response,
                "llm_provider": plan.provider,
                "llm_model": plan.model,
                "route_source": "llm_tool_planner",
                "intent_confidence": plan.confidence,
                "interpreted_preferences": {
                    "tool": plan.tool,
                    "metric_name": plan.metric_name,
                    "planner_reason": plan.reason,
                },
            }

    if plan.tool == "project_context":
        return _answer_project_context_question(
            request,
            route_source="llm_tool_planner",
            planner_metadata={
                "tool": plan.tool,
                "planner_reason": plan.reason,
                "planner_intent": plan.intent,
            },
            confidence=plan.confidence,
        )

    return None


def _answer_with_fallback_routing(request: ChatRequest) -> dict[str, Any]:
    message = request.message.strip()

    catalog_fact = answer_catalog_count_question(message)
    if catalog_fact is not None:
        return _catalog_fact_chat_response(catalog_fact)

    game_compare = answer_game_compare_question(message)
    if game_compare is not None:
        return _catalog_fact_chat_response(game_compare)

    game_lookup = answer_game_lookup_question(message)
    if game_lookup is not None:
        return _catalog_fact_chat_response(game_lookup)

    term_answer = answer_term_definition_question(message)
    if term_answer is not None:
        return _project_tool_chat_response(term_answer)

    fact = answer_project_fact_question(message)
    if fact is not None:
        return _project_fact_chat_response(fact)

    if _looks_like_recommendation_input_help(message):
        return _project_tool_chat_response(answer_recommendation_input_helper(message))

    if _looks_like_website_navigation_question(message):
        return _project_tool_chat_response(answer_website_navigation_question(message))

    if not is_supported_project_scope(message):
        return _unsupported_route_response()

    if has_recommendation_intent(message):
        return _build_chat_response(
            intent="recommend_me_guidance",
            answer=(
                "Assessment: Recommendation request detected. Directive: Subject should use Recommend Me_ "
                "for ranked matches. "
                "Required inputs: recent games, platform, genre, mood, playstyle, rating-quality preference, "
                "and popular versus hidden-gem preference."
            ),
            prompts=[
                "How does Recommend Me work?",
                "Why do recent games help?",
                "What is a hidden gem?",
            ],
            mode="rag_guided_recommendation_redirect",
            next_actions=[{"label": "Open Recommend Me_", "href": "/recommendations"}],
            route_source="natural_language_scope",
            confidence=0.86,
        )

    return _answer_project_context_question(
        request,
        route_source="natural_language_rag",
        planner_metadata={},
        confidence=0.74,
    )


def _answer_project_context_question(
    request: ChatRequest,
    *,
    route_source: str,
    planner_metadata: dict[str, Any],
    confidence: float,
) -> dict[str, Any]:
    message = request.message.strip()
    chunks = retrieve_project_context(message, top_k=request.max_results)
    sources = _sources_from_chunks(chunks)
    llm_status = get_llm_provider_status()
    context = _context_from_chunks(chunks)

    llm_result = generate_grounded_answer(
        question=message,
        context=context,
        history=_history_for_llm(request),
    )

    caveats: list[str] = []
    if llm_result.status != "success":
        caveats.append(
            "LLM generation was unavailable, so this answer uses the retrieved project context directly."
        )
        if llm_result.error:
            caveats.append(llm_result.error)

    return _build_chat_response(
        intent="project_rag_answer",
        answer=llm_result.answer or _fallback_answer_from_chunks(message, chunks),
        prompts=RAG_FOLLOW_UP_PROMPTS,
        status="success" if chunks else "no_results",
        caveats=caveats,
        mode="scoped_rag_llm_project_guide"
        if llm_result.status == "success"
        else "scoped_rag_extractive_fallback",
        sources=sources,
        next_actions=_next_actions_for_intent("project_rag_answer"),
        llm_provider=str(llm_status["provider"]),
        llm_model=str(llm_status["model"]),
        route_source=route_source,
        confidence=confidence if chunks else 0.25,
        interpreted_preferences=planner_metadata,
    )


def _looks_like_recommendation_input_help(message: str) -> bool:
    normalized = str(message or "").lower()
    helper_phrases = (
        "what should i put",
        "how should i answer",
        "how do i get better recommendation",
        "help me use recommend",
        "better recommend me",
        "improve my recommendation",
        "recommendation input",
        "recommend me input",
    )
    return any(phrase in normalized for phrase in helper_phrases)


def _looks_like_website_navigation_question(message: str) -> bool:
    normalized = str(message or "").lower()
    navigation_phrases = (
        "where should i go",
        "where do i go",
        "where can i",
        "what page",
        "which page",
        "how do i find",
        "how do i browse",
        "where is",
        "navigate",
    )
    return any(phrase in normalized for phrase in navigation_phrases)


def _guide_topic_response(route_mode: str) -> dict[str, Any] | None:
    if route_mode == "explain_project":
        return _build_chat_response(
            intent="project_overview",
            answer=(
                "This project is an IGDB-powered game-discovery analytics website. It uses a curated "
                "game catalog to support descriptive analytics, diagnostic analytics, hidden-gem discovery, "
                "the Recommend Me_ cosine-similarity workflow, and a guided explanation layer. The goal is "
                "to help users understand the catalog and discover games through structured, evidence-backed "
                "tools."
            ),
            prompts=[
                "Explain the data",
                "Explain recommendations",
                "Explain RAG",
            ],
        )

    if route_mode == "explain_data":
        return _build_chat_response(
            intent="data_source",
            answer=(
                "The project uses a local app catalog built from IGDB data. The catalog contains game-level "
                "metadata such as title, release year, genres, themes, platforms, summaries, ratings, rating "
                "counts, playtime where available, and derived project fields such as hidden-gem indicators. "
                "The dataset is curated for analysis and the website experience; it is not a complete copy of "
                "every game in IGDB."
            ),
            prompts=[
                "How many games are in the dataset?",
                "What years does the dataset cover?",
                "Explain limitations",
            ],
        )

    if route_mode == "explain_recommendation":
        return _build_chat_response(
            intent="recommendation_methodology",
            answer=(
                "Recommend Me_ is the main recommendation workflow. It collects structured user inputs, such "
                "as recent games, platform, genre, theme, mood, playstyle, playtime, rating preference, and "
                "hidden-gem preference. Those inputs are converted into a preference profile and compared "
                "against games in the catalog using cosine similarity."
            ),
            prompts=[
                "Help me use Recommend Me",
                "Explain hidden gems",
                "Explain limitations",
            ],
        )

    if route_mode == "recommend_me_guidance" or route_mode == "recommend_games":
        return _build_chat_response(
            intent="recommend_me_guidance",
            answer=(
                "Use Recommend Me_ when you want actual game matches. Start by entering recent games you liked, "
                "then add platform, genre, theme, mood, playstyle, playtime, rating-quality preference, and "
                "whether you prefer popular games or hidden gems. This is more reliable than asking the Guide "
                "for open-ended recommendations because the recommender gets structured inputs."
            ),
            prompts=[
                "Explain recommendations",
                "Explain hidden gems",
                "Explain limitations",
            ],
            mode="recommend_me_guidance",
        )

    if route_mode == "explain_rag":
        return _build_chat_response(
            intent="rag_methodology",
            answer=(
                "RAG is the grounding layer for Ask the Guide_. The chatbot retrieves relevant project "
                "context first, then uses an external free-tier LLM only to phrase the answer. This keeps "
                "the Guide grounded while reducing drift away from the IGDB project, dataset, "
                "methodology, and website scope."
            ),
            prompts=[
                "Explain this project",
                "Explain recommendations",
                "Explain limitations",
            ],
        )

    if route_mode == "explain_hidden_gems":
        return _build_chat_response(
            intent="hidden_gems_explanation",
            answer=(
                "A hidden gem in this project means a game that has enough quality or metadata signal to be "
                "worth surfacing, but is less obvious than the most popular catalog entries. The goal is not "
                "to recommend random obscure games; it is to balance quality evidence, metadata richness, and "
                "lower visibility."
            ),
            prompts=[
                "How many hidden gems are there?",
                "Explain recommendations",
                "Explain limitations",
            ],
        )

    if route_mode == "search_catalog":
        return _build_chat_response(
            intent="catalog_navigation_guidance",
            answer=(
                "Use Explore Games_ when you want to browse, search, and filter the catalog directly. It is "
                "the best page for inspecting games by platform, genre, release year, rating, metadata, and "
                "hidden-gem status."
            ),
            prompts=[
                "Explain the data",
                "Explain hidden gems",
                "Website navigation",
            ],
            mode="catalog_navigation_guidance",
        )

    if route_mode == "website_navigation":
        return _build_chat_response(
            intent="website_navigation",
            answer=(
                "Use Home_ for the project overview, Explore Games_ for catalog browsing, Recommend Me_ for "
                "personalized cosine-similarity recommendations, Hidden Gems_ for overlooked games, Insights_ "
                "for analytical findings, Methodology_ for how the system was built, and Ask the Guide_ for "
                "controlled project explanations."
            ),
            prompts=[
                "Help me use Recommend Me",
                "Explain the data",
                "Explain this project",
            ],
        )

    if route_mode == "explain_limitations":
        return _build_chat_response(
            intent="project_limitations",
            answer=(
                "The main limitations are metadata coverage, rating sparsity, incomplete PopScore availability, "
                "and the fact that the app catalog is a curated analytical sample rather than a full-market "
                "dataset. Recommendation quality also depends on how specific the user's structured inputs are."
            ),
            prompts=[
                "What is rating coverage?",
                "Explain the data",
                "Explain recommendations",
            ],
        )

    return None


def answer_chat_request(request: ChatRequest) -> dict[str, Any]:
    route_mode = request.route_mode if request.route_mode in GUIDED_ROUTE_MODES else None

    if route_mode and route_mode != "custom_question" and route_mode in FACT_ROUTE_QUESTIONS:
        fact = answer_project_fact_question(FACT_ROUTE_QUESTIONS[route_mode])
        if fact is not None:
            response = _project_fact_chat_response(fact)
            return {
                **response,
                "route_mode": route_mode,
                "conversation_id": request.conversation_id,
            }

    if route_mode and route_mode != "custom_question":
        topic_response = _guide_topic_response(route_mode or "")
        if topic_response is not None:
            return {
                **topic_response,
                "route_mode": route_mode,
                "conversation_id": request.conversation_id,
            }

    scoped_response = _answer_scoped_rag_question(request)
    if scoped_response is not None:
        return {
            **scoped_response,
            "route_mode": route_mode,
            "conversation_id": request.conversation_id,
        }

    return {
        **_unsupported_route_response(),
        "route_mode": route_mode,
        "conversation_id": request.conversation_id,
    }
