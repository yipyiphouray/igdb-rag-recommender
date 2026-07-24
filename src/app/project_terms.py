from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProjectToolAnswer:
    intent: str
    answer: str
    prompts: list[str]
    status: str = "success"
    caveats: list[str] = field(default_factory=list)
    source_files: list[str] = field(default_factory=list)
    interpreted_preferences: dict[str, Any] = field(default_factory=dict)


TERM_DEFINITIONS = {
    "hidden gem": (
        "A hidden gem is a game with enough quality or metadata signal to be worth surfacing, "
        "but with lower visibility than the most obvious popular games. In this project, hidden-gem "
        "logic balances rating quality, rating evidence, metadata richness, and lower popularity/visibility."
    ),
    "popscore": (
        "PopScore is treated as a visibility or interest signal from IGDB where available. The project uses it "
        "carefully because PopScore coverage is incomplete, so missing PopScore does not automatically mean a game is unpopular."
    ),
    "total_rating": (
        "total_rating is IGDB's combined rating signal when available. In this project it is useful for quality analysis, "
        "but it is not a perfect ground truth because many games have sparse or missing ratings."
    ),
    "total_rating_count": (
        "total_rating_count is the amount of rating evidence attached to a game's total_rating. A higher count usually means "
        "the rating is more reliable than a rating based on very little activity."
    ),
    "rating coverage": (
        "Rating coverage is the share of games in the app catalog that have usable rating data. It matters because rating-based "
        "analysis only applies to games where IGDB provides enough rating information."
    ),
    "reliable rating": (
        "Reliable rating means a game has enough rating evidence to treat its rating as more stable. The project uses a minimum "
        "rating-count threshold for stronger rating evidence."
    ),
    "cosine similarity": (
        "Cosine similarity compares the user's preference profile with each game's metadata profile. Recommend Me_ uses it to rank "
        "games based on structured inputs such as recent games, genres, themes, platform, mood, and playstyle."
    ),
    "rag": (
        "RAG means retrieval-augmented generation. In this project, the chatbot retrieves project or catalog context first, then "
        "uses an LLM to phrase the answer while staying grounded in the retrieved evidence."
    ),
    "rag ready": (
        "RAG-ready means the game has enough text or metadata to be useful for retrieval-style explanation. Games with weak text "
        "coverage may be harder for retrieval systems to describe accurately."
    ),
    "curated dataset": (
        "A curated dataset means the app catalog is a selected analytical sample built for this project, not a full copy of every "
        "game in IGDB or a full-market prevalence estimate."
    ),
    "metadata richness": (
        "Metadata richness describes how complete a game's project fields are, such as genres, themes, platforms, summaries, "
        "ratings, playtime, and other descriptive fields."
    ),
}

TERM_ALIASES = {
    "pop score": "popscore",
    "total rating": "total_rating",
    "rating count": "total_rating_count",
    "total rating count": "total_rating_count",
    "cosine": "cosine similarity",
    "retrieval augmented generation": "rag",
    "rag-ready": "rag ready",
    "curated analytical sample": "curated dataset",
}

PAGE_GUIDANCE = {
    "home": {
        "href": "/",
        "label": "Home_",
        "use": "Use Home_ for the project overview, main value proposition, and entry points into the website.",
    },
    "explore": {
        "href": "/explore",
        "label": "Explore Games_",
        "use": "Use Explore Games_ to browse, search, filter, and inspect the curated game catalog directly.",
    },
    "recommend": {
        "href": "/recommendations",
        "label": "Recommend Me_",
        "use": "Use Recommend Me_ when you want ranked cosine-similarity game recommendations from structured preferences.",
    },
    "hidden_gems": {
        "href": "/hidden-gems",
        "label": "Hidden Gems_",
        "use": "Use Hidden Gems_ to focus on overlooked games with enough quality or metadata signal to be worth surfacing.",
    },
    "insights": {
        "href": "/insights",
        "label": "Insights_",
        "use": "Use Insights_ to review descriptive and diagnostic findings such as top genres, platforms, coverage, and rating patterns.",
    },
    "methodology": {
        "href": "/methodology",
        "label": "Methodology_",
        "use": "Use Methodology_ to understand the data pipeline, curation logic, analytics approach, recommendation method, and RAG design.",
    },
    "guide": {
        "href": "/guide",
        "label": "Ask the Guide_",
        "use": "Use Ask the Guide_ for scoped project, catalog, methodology, and website questions.",
    },
}

PAGE_ALIASES = {
    "browse": "explore",
    "catalog": "explore",
    "search": "explore",
    "filter": "explore",
    "recommendation": "recommend",
    "recommendations": "recommend",
    "similar games": "recommend",
    "match": "recommend",
    "matches": "recommend",
    "hidden gem": "hidden_gems",
    "hidden gems": "hidden_gems",
    "overlooked": "hidden_gems",
    "analytics": "insights",
    "findings": "insights",
    "charts": "insights",
    "top genres": "insights",
    "top platforms": "insights",
    "method": "methodology",
    "pipeline": "methodology",
    "data pull": "methodology",
    "how it works": "methodology",
    "rag": "methodology",
    "chatbot": "guide",
    "guide": "guide",
}


def _normalized(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9_]+", str(text or "").lower()))


def _canonical_term(term: str | None, message: str = "") -> str | None:
    candidates = []
    if term:
        candidates.append(str(term))
    candidates.append(str(message or ""))
    for candidate in candidates:
        normalized = _normalized(candidate)
        for alias, canonical in TERM_ALIASES.items():
            if _normalized(alias) in normalized:
                return canonical
        for known_term in TERM_DEFINITIONS:
            if _normalized(known_term) in normalized:
                return known_term
    return None


def answer_term_definition_question(message: str, *, term: str | None = None) -> ProjectToolAnswer | None:
    canonical = _canonical_term(term, message)
    if canonical is None:
        return None

    return ProjectToolAnswer(
        intent="term_definition",
        answer=TERM_DEFINITIONS[canonical],
        prompts=[
            "How does Recommend Me work?",
            "What is a hidden gem?",
            "What does RAG do here?",
        ],
        caveats=[
            "This is the project-specific meaning of the term, not a universal industry definition."
        ],
        source_files=[],
        interpreted_preferences={"term": canonical},
    )


def answer_recommendation_input_helper(
    message: str,
    *,
    filters: dict[str, Any] | None = None,
    game_titles: list[str] | None = None,
) -> ProjectToolAnswer:
    filters = filters or {}
    game_titles = [str(title).strip() for title in (game_titles or []) if str(title).strip()]

    genres = filters.get("genres") or []
    platforms = filters.get("platforms") or []
    themes = filters.get("themes") or []
    game_modes = filters.get("game_modes") or []
    hidden_gems_only = bool(filters.get("hidden_gems_only"))

    lines = [
        "I use Recommend Me_ for ranked results. Enter structured inputs so I can build a clear preference profile.",
    ]
    lines.append(f"- Recent games: {', '.join(game_titles) if game_titles else 'add 1-3 games you recently enjoyed'}")
    lines.append(f"- Platforms: {', '.join(platforms) if platforms else 'choose where you want to play'}")
    lines.append(f"- Genres: {', '.join(genres) if genres else 'choose the closest genre preferences'}")
    lines.append(f"- Themes or mood: {', '.join(themes) if themes else 'add mood/theme words such as cozy, horror, fantasy, story-rich, or atmospheric'}")
    lines.append(f"- Playstyle: {', '.join(game_modes) if game_modes else 'single-player, multiplayer, co-op, exploration, challenge, or story focus'}")
    lines.append(
        f"- Discovery preference: {'hidden gems' if hidden_gems_only else 'popular, balanced, or hidden gems depending on what you want'}"
    )
    lines.append(
        "Specific inputs usually give me stronger cosine-similarity matches than vague inputs."
    )

    return ProjectToolAnswer(
        intent="recommendation_input_helper",
        answer="\n".join(lines),
        prompts=[
            "How does Recommend Me work?",
            "Why do recent games help?",
            "What is cosine similarity?",
        ],
        caveats=[
            "This helper prepares inputs. It does not run the ranked recommendation engine inside the chatbot."
        ],
        source_files=[],
        interpreted_preferences={
            "filters": filters,
            "game_titles": game_titles,
            "raw_message": message,
        },
    )


def _infer_page_topic(message: str) -> str | None:
    normalized = _normalized(message)
    for alias, page_key in PAGE_ALIASES.items():
        if _normalized(alias) in normalized:
            return page_key
    for page_key in PAGE_GUIDANCE:
        if _normalized(page_key) in normalized:
            return page_key
    return None


def answer_website_navigation_question(
    message: str,
    *,
    page_topic: str | None = None,
) -> ProjectToolAnswer:
    selected_key = page_topic if page_topic in PAGE_GUIDANCE else _infer_page_topic(message)

    if selected_key and selected_key in PAGE_GUIDANCE:
        page = PAGE_GUIDANCE[selected_key]
        answer = f"I would use {page['label']} for that. {page['use']}"
        interpreted = {"page": selected_key, "href": page["href"], "label": page["label"]}
    else:
        page_lines = [page["use"] for page in PAGE_GUIDANCE.values()]
        answer = "Here is the website page map. " + " ".join(page_lines)
        interpreted = {"page": "all"}

    return ProjectToolAnswer(
        intent="website_navigation",
        answer=answer,
        prompts=[
            "Where should I get recommendations?",
            "Where can I browse games?",
            "Where can I see methodology?",
        ],
        source_files=[],
        interpreted_preferences=interpreted,
    )
