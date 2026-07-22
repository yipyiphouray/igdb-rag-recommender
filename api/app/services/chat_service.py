from __future__ import annotations

import importlib.util
import re
from typing import Any

from app.schemas.chat import ChatRequest
from src.app.chat_intelligence import (
    analyze_message,
    build_filter_overrides,
    enhance_answer_text,
    enrich_retrieved_games,
    filter_seed_games,
)
from src.app.rag_service import VECTOR_STORE_PATH, answer_game_query, get_rag_backend, rag_status


COLLECTION_NAME = "igdb_game_profiles"
FOLLOW_UP_TERMS = {
    "those",
    "these",
    "that",
    "them",
    "more",
    "similar",
    "another",
    "again",
    "instead",
    "shorter",
    "longer",
    "hidden",
    "pc",
    "switch",
    "xbox",
    "playstation",
    "ps5",
    "coop",
    "co-op",
}
PREDEFINED_RESPONSES = [
    {
        "intent": "greeting",
        "patterns": [
            r"^\s*(hi|hello|hey|yo|sup|good morning|good afternoon|good evening)\s*[!.]?\s*$",
        ],
        "answer": (
            "Hey. I am the project guide for game discovery. Tell me what kind of game you want, "
            "or ask me to narrow results by platform, mood, genre, playtime, or hidden-gem style."
        ),
        "prompts": [
            "Recommend story-rich RPGs on PC",
            "Find hidden gems with exploration",
            "Suggest shorter atmospheric games",
        ],
    },
    {
        "intent": "identity",
        "patterns": [
            r"\bwho are you\b",
            r"\bwhat are you\b",
            r"\bwhat is this\b",
            r"\bwhat is this project\b",
            r"\bwhat is the guide\b",
        ],
        "answer": (
            "This is a game-discovery project built around IGDB data. The guide helps users search "
            "the catalog conversationally, while the Recommend Me page supports structured preference "
            "matching. Both are designed to help users find games with more context than a basic filter."
        ),
        "prompts": [
            "How does the guide work?",
            "How do recommendations work?",
            "Find highly rated co-op games",
        ],
    },
    {
        "intent": "capabilities",
        "patterns": [
            r"^\s*help\s*[!.?]*\s*$",
            r"\bwhat can you do\b",
            r"\bhow can i use\b",
            r"\bwhat should i ask\b",
            r"\bgive me examples\b",
        ],
        "answer": (
            "You can ask for game discovery help in natural language. Good prompts mention a platform, "
            "genre, mood, playstyle, reference game, rating preference, or playtime. I can also continue "
            "from the previous turn when you ask for more, shorter, hidden-gem, or similar options."
        ),
        "prompts": [
            "Recommend atmospheric RPGs on PC",
            "Make these shorter to play",
            "Narrow these to hidden gems",
        ],
    },
    {
        "intent": "data_source",
        "patterns": [
            r"\bwhat data (do|are) you use\b",
            r"\bwhere (does|do) (the )?data come from\b",
            r"\bis this from igdb\b",
            r"\bwhat is igdb\b",
            r"\bare (the )?ratings from users\b",
            r"\bigdb\b.*\bsource\b",
            r"\bdata source\b",
        ],
        "answer": (
            "The project uses a local game catalog built from IGDB data. The catalog includes game "
            "metadata such as title, release year, genres, platforms, themes, ratings, rating counts, "
            "and summaries when available. The guide only uses the local project dataset, so answers "
            "depend on what was pulled, cleaned, and indexed."
        ),
        "prompts": [
            "Show me games with strong rating coverage",
            "Find recent RPGs in the catalog",
            "Recommend games with fantasy themes",
        ],
    },
    {
        "intent": "recommendation_help",
        "patterns": [
            r"^\s*(can you )?recommend (a |me a )?game\s*[?.!]*\s*$",
            r"\bwhat should i play\b",
            r"\bfind me something good\b",
        ],
        "answer": (
            "Yes. Give me a few clues: platform, genre, mood, recent games you liked, and whether "
            "you want popular games or hidden gems. The more specific your prompt is, the better "
            "the guide can search the catalog."
        ),
        "prompts": [
            "I played Hades and Dead Cells recently. Recommend similar games",
            "Recommend cozy farming games on Switch",
            "Find cinematic single-player games with strong ratings",
        ],
    },
    {
        "intent": "rag_methodology",
        "patterns": [
            r"\bhow (does|do) (this|you|the guide|the chatbot) (work|answer)\b",
            r"\bmethodology\b",
            r"\brag\b",
            r"\bretrieval\b",
            r"\bvector\b",
            r"\bbm25\b",
            r"\bdata source\b",
        ],
        "answer": (
            "The guide uses a hybrid retrieval workflow. Semantic vector search finds games with similar "
            "meaning, BM25 keyword search keeps exact terms precise, and metadata checks keep answers tied "
            "to the local IGDB project catalog. The response is deterministic and grounded in retrieved games."
        ),
        "prompts": [
            "Find games similar to Stardew Valley",
            "Recommend story-rich RPGs",
            "Show me hidden gems on PC",
        ],
    },
    {
        "intent": "cosine_similarity_methodology",
        "patterns": [
            r"\bcosine similarity\b",
            r"\bhow (does|do) (the )?recommend me (page )?work\b",
            r"\bhow (does|do) (the )?recommendation page work\b",
            r"\bhow are my answers used\b",
            r"\bwhy (do you|does it) ask.*recent games\b",
            r"\brecommend me\b.*\bask the guide\b",
            r"\bdifference between recommend me and ask the guide\b",
        ],
        "answer": (
            "The Recommend Me page uses structured preferences to build a user profile, then compares "
            "that profile against games in the catalog using cosine similarity. Recent games you played "
            "help describe your taste, while fields like genre, platform, theme, and playstyle help "
            "narrow the match."
        ),
        "prompts": [
            "Explain the difference between Recommend Me and Ask the Guide",
            "Help me choose recommendation preferences",
            "What details should I provide for better matches?",
        ],
    },
    {
        "intent": "refinement_help",
        "skip_when_history": True,
        "patterns": [
            r"\bhow can i refine\b",
            r"\bhow do i narrow\b",
            r"\bcan you narrow results\b",
            r"\bcan you refine results\b",
            r"\bwhat filters can i use\b",
        ],
        "answer": (
            "I can refine results by platform, genre, mood, popularity, rating strength, playtime, "
            "or hidden-gem focus. If we already have results, tell me which constraint matters most "
            "and I will search with that context."
        ),
        "prompts": [
            "Make these more hidden-gem focused",
            "Narrow to PC games only",
            "Show more story-heavy options",
        ],
    },
    {
        "intent": "hidden_gems_explanation",
        "patterns": [
            r"\bwhat is a hidden gem\b",
            r"\bwhat does hidden gem mean\b",
            r"\bdefine hidden gems?\b",
            r"\bhow do hidden gems work\b",
        ],
        "answer": (
            "In this project, a hidden gem means a game that looks promising but is less obvious than "
            "the most mainstream recommendations. The guide should balance quality signals, rating "
            "coverage, metadata richness, and popularity so the result is interesting without being random."
        ),
        "prompts": [
            "Find hidden gems with fantasy themes",
            "Show overlooked indie games",
            "Recommend lesser-known RPGs with strong ratings",
        ],
    },
    {
        "intent": "thanks",
        "patterns": [
            r"^\s*(thanks|thank you|thx|appreciate it)\s*[!.]?\s*$",
        ],
        "answer": (
            "You're welcome. If you want to continue, ask me to make the results more specific, broader, "
            "shorter, more popular, or more hidden-gem focused."
        ),
        "prompts": [
            "Show me more like the first result",
            "Make these more hidden-gem focused",
            "Find something with stronger ratings",
        ],
    },
    {
        "intent": "project_demo",
        "patterns": [
            r"\bhow should i explain this project\b",
            r"\bwhat is the goal of the website\b",
            r"\bwhat are the four analytics pillars\b",
            r"\bhow does this connect to (the )?class project\b",
            r"\bwhat should i say during (the )?demo\b",
        ],
        "answer": (
            "The project turns IGDB game data into a discovery system. Descriptive analytics explains "
            "what is in the catalog, diagnostic analytics investigates patterns behind game quality and "
            "visibility, the recommendation engine matches users to games, and the RAG guide lets users "
            "explore the catalog through natural language."
        ),
        "prompts": [
            "Explain the descriptive pillar",
            "Explain the diagnostic pillar",
            "Explain the difference between Recommend Me and Ask the Guide",
        ],
    },
    {
        "intent": "personality_surprise",
        "patterns": [
            r"^\s*surprise me\s*[!.?]*\s*$",
        ],
        "answer": (
            "I can do that. Give me one anchor first: cozy, chaotic, strategic, cinematic, spooky, "
            "or experimental. Then I will search the catalog instead of throwing a random game into "
            "the neon fog."
        ),
        "prompts": [
            "Find weird atmospheric games",
            "Recommend cozy games for a rainy night",
            "Give me chaotic roguelikes on PC",
        ],
    },
    {
        "intent": "personality_weird",
        "patterns": [
            r"^\s*(give me |i want )?something weird\s*[!.?]*\s*$",
            r"^\s*(give me |i want )?weird\s*[!.?]*\s*$",
        ],
        "answer": (
            "Weird is a valid search signal. Tell me if you want weird mechanics, weird story, "
            "weird atmosphere, or weird visuals, and I will look for matches in the catalog."
        ),
        "prompts": [
            "Find weird atmospheric games",
            "Recommend experimental story games",
            "Show me unusual puzzle games",
        ],
    },
    {
        "intent": "personality_cyberpunk",
        "patterns": [
            r"\bwhat would (the )?cyberpunk guide play\b",
            r"\bneon energy\b",
        ],
        "answer": (
            "Probably something atmospheric, stylish, and slightly suspicious. If you want that lane, "
            "ask me for neon, sci-fi, dystopian, or story-heavy games."
        ),
        "prompts": [
            "Find neon sci-fi games",
            "Recommend dystopian story games",
            "Show stylish atmospheric games",
        ],
    },
    {
        "intent": "personality_chaos",
        "patterns": [
            r"^\s*i want chaos\s*[!.?]*\s*$",
            r"\bfor my villain arc\b",
        ],
        "answer": (
            "Chaos detected. I can search for action-heavy, roguelike, fast-paced, or high-intensity "
            "games. Add a platform if you want cleaner results."
        ),
        "prompts": [
            "Give me chaotic roguelikes on PC",
            "Recommend fast-paced action games",
            "Find intense single-player games",
        ],
    },
    {
        "intent": "personality_rainy_night",
        "patterns": [
            r"\brainy night\b",
            r"\bfeels like 2\s*a\.?m\.?\b",
            r"\bdangerous but cozy\b",
        ],
        "answer": (
            "Rainy-night mode works best with mood clues. I can look for atmospheric, cozy, mysterious, "
            "narrative, or slow-burn games."
        ),
        "prompts": [
            "Recommend cozy games for a rainy night",
            "Find mysterious atmospheric games",
            "Suggest slow-burn narrative games",
        ],
    },
    {
        "intent": "personality_brain_fried",
        "patterns": [
            r"\bbrain is fried\b",
            r"\bbrain feels fried\b",
            r"\btoo tired to think\b",
        ],
        "answer": (
            "Then we should avoid spreadsheet-energy games. I can search for relaxing, cozy, short, "
            "simple, or low-pressure games."
        ),
        "prompts": [
            "Suggest low-pressure games after a long day",
            "Recommend relaxing cozy games",
            "Find short simple games",
        ],
    },
]
DEFAULT_RESPONSE = (
    "I can only help with game discovery questions for this project. Ask me for recommendations by "
    "platform, genre, mood, playstyle, playtime, rating quality, hidden-gem preference, or a game you liked."
)
DEFAULT_PROMPTS = [
    "Recommend story-rich RPGs on PC",
    "Find hidden gems with fantasy themes",
    "Suggest co-op games with strong ratings",
]
CLARIFICATION_RESPONSE = (
    "I can help, but I need one more clue. Are you asking how the project works, "
    "or are you looking for a game recommendation? If it is a recommendation, give me a platform, "
    "genre, mood, or a game you already liked."
)
CLARIFICATION_PROMPTS = [
    "Explain how the guide works",
    "Recommend story-rich RPGs on PC",
    "Help me choose recommendation preferences",
]
VAGUE_RECOMMENDATION_RESPONSE = (
    "Yes, I can recommend games. I need one useful clue first so I do not hand you a random catalog result. "
    "Tell me a platform, genre, mood, recent game you liked, or whether you want popular games or hidden gems."
)
VAGUE_RECOMMENDATION_PROMPTS = [
    "Recommend story-rich RPGs on PC",
    "I played Hades recently. Recommend similar games",
    "Find hidden gems with exploration",
]

QUESTION_TERMS = {
    "are",
    "can",
    "could",
    "describe",
    "do",
    "does",
    "explain",
    "how",
    "is",
    "should",
    "tell",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "would",
}
PURPOSE_TERMS = {
    "built",
    "created",
    "exist",
    "goal",
    "mission",
    "objective",
    "point",
    "purpose",
}
PROJECT_CONTEXT_TERMS = {
    "app",
    "chatbot",
    "guide",
    "project",
    "site",
    "system",
    "website",
    "you",
    "your",
    "yourself",
}
DATA_CONTEXT_TERMS = {
    "catalog",
    "data",
    "dataset",
    "igdb",
    "metadata",
    "rating",
    "ratings",
    "source",
    "sources",
}
METHODOLOGY_TERMS = {
    "bm25",
    "embedding",
    "embeddings",
    "hybrid",
    "keyword",
    "method",
    "methodology",
    "rag",
    "retrieval",
    "semantic",
    "vector",
}
COSINE_TERMS = {
    "answers",
    "cosine",
    "difference",
    "matching",
    "preferences",
    "profile",
    "recent",
    "similarity",
}
DEMO_TERMS = {
    "analytics",
    "class",
    "demo",
    "explain",
    "pillar",
    "pillars",
    "presentation",
    "professor",
}
HIDDEN_GEM_EXPLANATION_TERMS = {
    "define",
    "definition",
    "mean",
    "meaning",
}
GAME_SEARCH_ACTION_TERMS = {
    "discover",
    "find",
    "pick",
    "recommend",
    "search",
    "show",
    "suggest",
}
GAME_CONTEXT_TERMS = {
    "game",
    "games",
    "play",
    "played",
}
GAME_PREFERENCE_TERMS = {
    "action",
    "adventure",
    "atmospheric",
    "chaotic",
    "cinematic",
    "co-op",
    "coop",
    "cozy",
    "dystopian",
    "experimental",
    "fantasy",
    "farming",
    "fast",
    "hidden",
    "horror",
    "indie",
    "low-pressure",
    "multiplayer",
    "mysterious",
    "narrative",
    "neon",
    "pc",
    "platform",
    "playstation",
    "ps5",
    "puzzle",
    "rainy",
    "rating",
    "relaxing",
    "roguelike",
    "rpg",
    "sci-fi",
    "sci",
    "fi",
    "short",
    "single-player",
    "single",
    "solo",
    "spooky",
    "story",
    "strategy",
    "switch",
    "xbox",
}
def _dependency_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _collection_available() -> tuple[bool, str | None]:
    if not _dependency_available("chromadb"):
        return False, None

    try:
        import chromadb

        client = chromadb.PersistentClient(path=str(VECTOR_STORE_PATH))
        collection_names = [
            getattr(collection, "name", str(collection))
            for collection in client.list_collections()
        ]
    except Exception as error:
        return False, f"Could not inspect Chroma collection: {type(error).__name__}: {error}"

    if COLLECTION_NAME not in collection_names:
        return False, f"Missing Chroma collection: {COLLECTION_NAME}."

    return True, None


def get_chat_status() -> dict[str, Any]:
    artifacts = rag_status()
    backend = get_rag_backend()
    warnings: list[str] = []

    if not artifacts.get("app_catalog", False):
        warnings.append("Missing data/app/app_game_catalog.parquet.")

    collection_available = False
    retrieval_artifacts_available = False

    if backend == "lightweight":
        if not artifacts.get("lightweight_rag_dir", False):
            warnings.append("Missing data/rag/lightweight directory.")
        if not artifacts.get("lightweight_embeddings", False):
            warnings.append("Missing data/rag/lightweight/game_embeddings.npy.")
        if not artifacts.get("lightweight_game_ids", False):
            warnings.append("Missing data/rag/lightweight/game_ids.json.")
        if not artifacts.get("lightweight_manifest", False):
            warnings.append("Missing data/rag/lightweight/manifest.json.")
        retrieval_artifacts_available = bool(
            artifacts.get("lightweight_rag_dir", False)
            and artifacts.get("lightweight_embeddings", False)
            and artifacts.get("lightweight_game_ids", False)
            and artifacts.get("lightweight_manifest", False)
        )
    else:
        if not artifacts.get("vector_store", False):
            warnings.append("Missing data/vector_store directory.")
        if not artifacts.get("vector_store_sqlite", False):
            warnings.append("Missing data/vector_store/chroma.sqlite3.")
        if not _dependency_available("chromadb"):
            warnings.append("Missing Python dependency: chromadb.")
        if (
            artifacts.get("vector_store", False)
            and artifacts.get("vector_store_sqlite", False)
            and _dependency_available("chromadb")
        ):
            collection_available, collection_warning = _collection_available()
            if collection_warning:
                warnings.append(collection_warning)
        retrieval_artifacts_available = bool(
            artifacts.get("vector_store", False)
            and artifacts.get("vector_store_sqlite", False)
            and collection_available
        )

    if not _dependency_available("sentence_transformers"):
        warnings.append("Missing Python dependency: sentence-transformers.")

    status = "ready" if not warnings else "unavailable"

    return {
        "status": status,
        "backend": backend,
        "catalog_available": bool(artifacts.get("app_catalog", False)),
        "vector_store_available": bool(artifacts.get("vector_store", False)),
        "retrieval_artifacts_available": retrieval_artifacts_available,
        "collection_available": collection_available,
        "engine": "hybrid_numpy_bm25" if backend == "lightweight" else "hybrid_chroma_bm25",
        "warnings": warnings,
    }


def _request_filters(request: ChatRequest) -> dict[str, Any]:
    if request.filters is None:
        return {}
    filters = request.filters.model_dump(exclude_none=True)
    return {key: value for key, value in filters.items() if value not in (None, "", [])}


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9\-]+", text.lower())


def _normalized_message(text: str) -> str:
    return " ".join(str(text or "").lower().split())


def _has_any(tokens: set[str], terms: set[str]) -> bool:
    return bool(tokens.intersection(terms))


def _has_phrase(message: str, phrases: list[str]) -> bool:
    normalized = _normalized_message(message)
    return any(phrase in normalized for phrase in phrases)


def _looks_like_question(message: str) -> bool:
    stripped = message.strip()
    tokens = set(_tokenize(stripped))
    if stripped.endswith("?"):
        return True
    if _has_any(tokens, QUESTION_TERMS):
        return True
    return _has_phrase(
        stripped,
        [
            "tell me about",
            "talk about",
            "walk me through",
            "i want to know",
            "i am asking about",
        ],
    )


def _looks_like_follow_up(message: str) -> bool:
    tokens = set(_tokenize(message))
    if not tokens:
        return False
    return bool(tokens.intersection(FOLLOW_UP_TERMS)) or _has_phrase(
        message,
        [
            "same but",
            "more like",
            "less popular",
            "more popular",
            "make it",
            "keep it",
            "only show",
            "show more",
        ],
    )


def _build_chat_response(
    *,
    intent: str,
    answer: str,
    prompts: list[str],
    status: str = "success",
    caveats: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "answer": answer,
        "mode": f"predefined_{intent}",
        "status": status,
        "retrieved_games": [],
        "caveats": caveats or [],
        "applied_filters": {},
        "follow_up_prompts": prompts,
        "contextual_query": None,
    }


def _predefined_response(message: str, request: ChatRequest) -> dict[str, Any] | None:
    for response in PREDEFINED_RESPONSES:
        if response.get("skip_when_history") and request.history:
            continue
        if any(re.search(pattern, message, flags=re.IGNORECASE) for pattern in response["patterns"]):
            return _build_chat_response(
                intent=response["intent"],
                answer=response["answer"],
                prompts=response["prompts"],
            )
    return None


def _concept_response(message: str) -> dict[str, Any] | None:
    normalized = _normalized_message(message)
    tokens = set(_tokenize(message))
    question_like = _looks_like_question(message)

    if question_like and (
        _has_any(tokens, PURPOSE_TERMS)
        or _has_phrase(normalized, ["what are you here for", "why are you here", "what is your job"])
    ):
        return _build_chat_response(
            intent="identity_purpose",
            answer=(
                "My purpose is to help users explore the project game catalog in a more useful way than "
                "a plain search box. I can explain the project, answer methodology questions, and guide "
                "users toward catalog-backed game recommendations."
            ),
            prompts=[
                "What can you do?",
                "How does the guide work?",
                "Recommend story-rich RPGs on PC",
            ],
        )

    if (
        question_like
        and _has_any(tokens, DATA_CONTEXT_TERMS)
        and not _has_any(tokens, GAME_SEARCH_ACTION_TERMS)
        and not (
            _has_any(tokens, GAME_CONTEXT_TERMS)
            and _has_any(tokens, GAME_PREFERENCE_TERMS.union({"best", "good", "quality", "strong"}))
        )
    ):
        return _build_chat_response(
            intent="data_source",
            answer=(
                "The project uses a local game catalog built from IGDB data. The catalog includes game "
                "metadata such as title, release year, genres, platforms, themes, ratings, rating counts, "
                "and summaries when available. The guide only uses the local project dataset, so answers "
                "depend on what was pulled, cleaned, and indexed."
            ),
            prompts=[
                "Show me games with strong rating coverage",
                "Find recent RPGs in the catalog",
                "Recommend games with fantasy themes",
            ],
        )

    if (
        question_like
        and _has_any(tokens, {"recommendation", "recommendations", "recommender"})
        and _has_any(tokens, {"work", "works"})
    ):
        return _build_chat_response(
            intent="recommendation_methodology",
            answer=(
                "The project has two recommendation paths. Recommend Me uses structured answers and "
                "cosine similarity to match a user profile to catalog games. Ask the Guide uses hybrid "
                "RAG retrieval so users can search and refine recommendations conversationally."
            ),
            prompts=[
                "Explain cosine similarity",
                "Explain how the guide works",
                "Recommend atmospheric RPGs on PC",
            ],
        )

    if question_like and (
        _has_any(tokens, METHODOLOGY_TERMS)
        or _has_phrase(normalized, ["how does the guide work", "how does the chatbot work"])
    ):
        return _build_chat_response(
            intent="rag_methodology",
            answer=(
                "The guide uses a hybrid retrieval workflow. Semantic search finds games with similar "
                "meaning, keyword search keeps exact terms precise, and metadata checks keep answers tied "
                "to the local IGDB project catalog. The response is deterministic and grounded in retrieved games."
            ),
            prompts=[
                "Find games similar to Stardew Valley",
                "Recommend story-rich RPGs",
                "Show me hidden gems on PC",
            ],
        )

    if (
        _has_phrase(normalized, ["cosine similarity"])
        or (
            question_like
            and _has_phrase(normalized, ["recommend me", "recommendation page"])
            and _has_any(tokens, COSINE_TERMS.union({"work", "works", "page"}))
        )
    ):
        return _build_chat_response(
            intent="cosine_similarity_methodology",
            answer=(
                "The Recommend Me page uses structured preferences to build a user profile, then compares "
                "that profile against games in the catalog using cosine similarity. Recent games you played "
                "help describe your taste, while fields like genre, platform, theme, and playstyle help "
                "narrow the match."
            ),
            prompts=[
                "Explain the difference between Recommend Me and Ask the Guide",
                "Help me choose recommendation preferences",
                "What details should I provide for better matches?",
            ],
        )

    if (
        "hidden" in tokens
        and ("gem" in tokens or "gems" in tokens)
        and (question_like or _has_any(tokens, HIDDEN_GEM_EXPLANATION_TERMS))
        and not _has_any(tokens, GAME_SEARCH_ACTION_TERMS)
    ):
        return _build_chat_response(
            intent="hidden_gems_explanation",
            answer=(
                "In this project, a hidden gem means a game that looks promising but is less obvious than "
                "the most mainstream recommendations. The guide balances quality signals, rating coverage, "
                "metadata richness, and popularity so the result is interesting without being random."
            ),
            prompts=[
                "Find hidden gems with fantasy themes",
                "Show overlooked indie games",
                "Recommend lesser-known RPGs with strong ratings",
            ],
        )

    if question_like and _has_any(tokens, DEMO_TERMS):
        return _build_chat_response(
            intent="project_demo",
            answer=(
                "The project turns IGDB game data into a discovery system. Descriptive analytics explains "
                "what is in the catalog, diagnostic analytics investigates patterns behind game quality and "
                "visibility, the recommendation engine matches users to games, and the RAG guide lets users "
                "explore the catalog through natural language."
            ),
            prompts=[
                "Explain the descriptive pillar",
                "Explain the diagnostic pillar",
                "Explain the difference between Recommend Me and Ask the Guide",
            ],
        )

    if question_like and _has_any(tokens, PROJECT_CONTEXT_TERMS):
        return _build_chat_response(
            intent="project_context",
            answer=(
                "I am the project guide for the IGDB game-discovery system. I can explain the project, "
                "describe the data and methodology, or help you search the catalog for games."
            ),
            prompts=[
                "What is your purpose?",
                "How does the guide work?",
                "Recommend something atmospheric",
            ],
        )

    return None


def _clarification_response() -> dict[str, Any]:
    return _build_chat_response(
        intent="clarification",
        answer=CLARIFICATION_RESPONSE,
        prompts=CLARIFICATION_PROMPTS,
        status="needs_clarification",
    )


def _vague_recommendation_response() -> dict[str, Any]:
    return _build_chat_response(
        intent="recommendation_clarification",
        answer=VAGUE_RECOMMENDATION_RESPONSE,
        prompts=VAGUE_RECOMMENDATION_PROMPTS,
        status="needs_clarification",
    )


def _looks_ambiguous_supported_message(message: str) -> bool:
    tokens = set(_tokenize(message))
    if not tokens:
        return True
    if _looks_like_question(message) and _has_any(
        tokens,
        PROJECT_CONTEXT_TERMS.union(DATA_CONTEXT_TERMS).union(GAME_CONTEXT_TERMS),
    ):
        return True
    if len(tokens) <= 4 and _has_any(
        tokens,
        PURPOSE_TERMS.union(DATA_CONTEXT_TERMS).union(GAME_CONTEXT_TERMS).union(METHODOLOGY_TERMS),
    ):
        return True
    return False


def _clean_history_text(value: str, max_chars: int = 320) -> str:
    cleaned = " ".join(str(value or "").split())
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 1].rstrip() + "..."


def _build_contextual_query(request: ChatRequest) -> str:
    message = request.message.strip()
    if not request.history or not _looks_like_follow_up(message):
        return message

    recent_history = request.history[-6:]
    user_context: list[str] = []
    guide_context: list[str] = []

    for item in recent_history:
        if item.role == "user":
            user_context.append(_clean_history_text(item.content))
        elif item.role == "guide":
            guide_context.append(_clean_history_text(item.content))

    parts = [f"Current user request: {message}"]
    if user_context:
        parts.append("Earlier user preferences: " + " | ".join(user_context[-3:]))
    if guide_context:
        parts.append("Earlier guide results and context: " + " | ".join(guide_context[-2:]))

    return ". ".join(parts)


def _build_follow_up_prompts(games: list[dict[str, Any]]) -> list[str]:
    if not games:
        return [
            "Try a broader version of this search",
            "Search by genre and platform instead",
            "Show me highly rated options",
        ]

    first_game = games[0].get("name", "the first result")
    prompts = [
        f"Show me more games like {first_game}",
        "Narrow these to hidden gems",
        "Make these shorter to play",
    ]

    platforms = games[0].get("platforms") or []
    if platforms:
        prompts.append(f"Keep this on {platforms[0]}")

    return prompts[:4]


def _format_game_names(games: list[dict[str, Any]]) -> str:
    names = [str(game.get("name") or "").strip() for game in games[:3] if game.get("name")]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return f"{names[0]}, {names[1]}, and {names[2]}"


def _seed_filtered_answer_text(games: list[dict[str, Any]], excluded_seed_games: list[str]) -> str:
    names_text = _format_game_names(games)
    excluded_text = ", ".join(excluded_seed_games)
    pronoun = "them" if len(excluded_seed_games) > 1 else "it"
    if names_text:
        return (
            f"I found catalog-backed alternatives: {names_text}. "
            f"I excluded {excluded_text} because you already mentioned playing {pronoun}."
        )
    return (
        "I found retrieval matches, but they were mostly games you already mentioned. "
        "Try adding a genre, mood, platform, or hidden-gem preference so I can broaden the search."
    )


def _chat_intelligence_payload(intelligence: Any) -> dict[str, Any]:
    return {
        "interpreted_preferences": intelligence.slots.to_dict(),
        "chat_intent": intelligence.intent,
        "intent_confidence": intelligence.confidence,
        "route_source": intelligence.route_source,
        "matched_intent_example": intelligence.matched_example,
    }


def answer_chat_request(request: ChatRequest) -> dict[str, Any]:
    intelligence = analyze_message(request.message, has_history=bool(request.history))
    intelligence_payload = _chat_intelligence_payload(intelligence)

    if intelligence.should_clarify:
        return {
            **_build_chat_response(
                intent="recommendation_clarification",
                answer=intelligence.clarification_question or VAGUE_RECOMMENDATION_RESPONSE,
                prompts=list(intelligence.clarification_prompts) or VAGUE_RECOMMENDATION_PROMPTS,
                status="needs_clarification",
            ),
            "conversation_id": request.conversation_id,
            **intelligence_payload,
        }

    is_game_discovery_query = (
        intelligence.intent
        in {
            "game_recommendation",
            "seed_game_recommendation",
            "recommendation_follow_up",
        }
        and not intelligence.should_clarify
    )

    predefined = _predefined_response(request.message, request)
    if predefined is not None and not is_game_discovery_query:
        return {
            **predefined,
            "conversation_id": request.conversation_id,
            **intelligence_payload,
        }

    if not is_game_discovery_query:
        concept = _concept_response(request.message)
        if concept is not None:
            return {
                **concept,
                "conversation_id": request.conversation_id,
                **intelligence_payload,
            }

    if not is_game_discovery_query:
        if _looks_ambiguous_supported_message(request.message):
            return {
                **_clarification_response(),
                "conversation_id": request.conversation_id,
                **intelligence_payload,
            }

        return {
            "answer": DEFAULT_RESPONSE,
            "mode": "predefined_default",
            "status": "unsupported_question",
            "conversation_id": request.conversation_id,
            "retrieved_games": [],
            "caveats": [
                "The guide is intentionally scoped to catalog-backed game discovery."
            ],
            "applied_filters": {},
            "follow_up_prompts": DEFAULT_PROMPTS,
            "contextual_query": None,
            **intelligence_payload,
        }

    contextual_query = _build_contextual_query(request)
    request_filters = _request_filters(request)
    retrieval_filters = build_filter_overrides(intelligence.slots, request_filters)
    retrieval_top_k = request.max_results
    if intelligence.slots.recent_games:
        retrieval_top_k = min(10, request.max_results + len(intelligence.slots.recent_games))

    try:
        rag_response = answer_game_query(
            query=contextual_query,
            filters=retrieval_filters,
            top_k=retrieval_top_k,
        )
    except Exception as error:
        return {
            "answer": "The guide could not run the retrieval engine in the current environment.",
            "mode": "rag_unavailable",
            "status": "error",
            "conversation_id": request.conversation_id,
            "retrieved_games": [],
            "caveats": [f"{type(error).__name__}: {error}"],
            "applied_filters": retrieval_filters,
            "follow_up_prompts": [],
            "contextual_query": contextual_query,
            **intelligence_payload,
        }

    filtered_games, excluded_seed_games = filter_seed_games(
        rag_response.get("retrieved_games", []),
        intelligence.slots,
        top_k=request.max_results,
    )
    retrieved_games = enrich_retrieved_games(
        filtered_games,
        intelligence.slots,
    )
    base_answer = (
        _seed_filtered_answer_text(retrieved_games, excluded_seed_games)
        if excluded_seed_games
        else rag_response.get("answer_text", "")
    )
    answer_text = enhance_answer_text(
        base_answer,
        intelligence.slots,
        retrieved_games,
    )
    caveats = rag_response.get("warnings", [])
    if excluded_seed_games:
        caveats = [
            *caveats,
            "Recent games mentioned by the user were excluded from the displayed recommendations.",
        ]

    return {
        "answer": answer_text,
        "mode": "rag_hybrid_conversation"
        if request.history
        else rag_response.get("mode", "rag_hybrid_retrieval"),
        "status": rag_response.get("status", "success"),
        "conversation_id": request.conversation_id,
        "retrieved_games": retrieved_games,
        "caveats": caveats,
        "applied_filters": rag_response.get("applied_filters", {}),
        "follow_up_prompts": _build_follow_up_prompts(retrieved_games),
        "contextual_query": contextual_query if contextual_query != request.message else None,
        **intelligence_payload,
    }
