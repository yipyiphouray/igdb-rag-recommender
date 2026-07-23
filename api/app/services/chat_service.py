from __future__ import annotations

from typing import Any

from app.schemas.chat import ChatRequest
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


def get_chat_status() -> dict[str, Any]:
    artifacts = rag_status()
    warnings: list[str] = []

    if not artifacts.get("app_catalog", False):
        warnings.append("Missing data/app/app_game_catalog.parquet.")

    return {
        "status": "ready" if not warnings else "unavailable",
        "backend": get_rag_backend(),
        "catalog_available": bool(artifacts.get("app_catalog", False)),
        "vector_store_available": bool(artifacts.get("vector_store", False)),
        "retrieval_artifacts_available": bool(
            artifacts.get("lightweight_embeddings", False)
            and artifacts.get("lightweight_game_ids", False)
            and artifacts.get("lightweight_manifest", False)
        ),
        "collection_available": False,
        "engine": "condition_based_project_guide",
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
        "interpreted_preferences": {},
        "chat_intent": intent,
        "intent_confidence": 1.0,
        "route_source": "selected_route_mode",
        "matched_intent_example": None,
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
    )


def _unsupported_route_response() -> dict[str, Any]:
    return _build_chat_response(
        intent="unsupported_instruction",
        answer=(
            "Ask the Guide_ is now condition-based. Choose one of the predefined "
            "guide instructions instead of typing a free-form question."
        ),
        prompts=DEFAULT_PROMPTS,
        status="unsupported_question",
        caveats=[
            "The Guide is intentionally limited to predefined project instructions for reliability."
        ],
        mode="condition_unsupported_instruction",
    )


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
                "RAG is treated as a project explanation and grounding concept, not as the main game "
                "recommendation engine. In this simplified Guide design, the user chooses predefined project "
                "instructions and the backend returns controlled answers. This keeps the website reliable, "
                "easy to test, and easier to deploy."
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

    if route_mode in FACT_ROUTE_QUESTIONS:
        fact = answer_project_fact_question(FACT_ROUTE_QUESTIONS[route_mode])
        if fact is not None:
            response = _project_fact_chat_response(fact)
            return {
                **response,
                "route_mode": route_mode,
                "conversation_id": request.conversation_id,
            }

    topic_response = _guide_topic_response(route_mode or "")
    if topic_response is not None:
        return {
            **topic_response,
            "route_mode": route_mode,
            "conversation_id": request.conversation_id,
        }

    return {
        **_unsupported_route_response(),
        "route_mode": route_mode,
        "conversation_id": request.conversation_id,
    }
