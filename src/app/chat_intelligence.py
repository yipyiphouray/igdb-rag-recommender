from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from typing import Any


TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+#.'-]*")


PLATFORM_ALIASES: dict[str, tuple[str, ...]] = {
    "PC": ("pc", "steam", "windows", "computer"),
    "Nintendo Switch": ("switch", "nintendo switch"),
    "PlayStation 5": ("ps5", "playstation 5", "playstation5"),
    "PlayStation 4": ("ps4", "playstation 4", "playstation4"),
    "Xbox Series": ("xbox series", "series x", "series s"),
    "Xbox One": ("xbox one",),
    "Xbox": ("xbox",),
}


GENRE_ALIASES: dict[str, tuple[str, ...]] = {
    "RPG": ("rpg", "rpgs", "role playing", "role-playing", "jrpg", "jrpgs"),
    "Adventure": ("adventure", "exploration", "explore"),
    "Action": ("action", "combat", "fast paced", "fast-paced"),
    "Shooter": ("shooter", "shooters", "fps", "first person shooter", "third person shooter"),
    "Strategy": ("strategy", "tactics", "tactical"),
    "Puzzle": ("puzzle", "puzzles", "brain teaser"),
    "Simulation": ("simulation", "simulations", "simulator", "simulators", "sim"),
    "Platformer": ("platformer", "platforming"),
    "Roguelike": ("roguelike", "roguelikes", "rogue-like", "roguelite", "roguelites", "rogue-lite"),
    "Racing": ("racing", "driving"),
    "Sports": ("sports", "sport"),
    "Visual Novel": ("visual novel",),
    "Indie": ("indie",),
}


THEME_ALIASES: dict[str, tuple[str, ...]] = {
    "Fantasy": ("fantasy", "magic", "medieval"),
    "Science fiction": ("sci-fi", "scifi", "science fiction", "cyberpunk", "space"),
    "Horror": ("horror", "scary", "spooky"),
    "Mystery": ("mystery", "detective", "investigation"),
    "Survival": ("survival",),
    "Open world": ("open world", "open-world", "sandbox"),
    "Narrative": ("story", "story-rich", "story rich", "narrative", "cinematic"),
}


MOOD_ALIASES: dict[str, tuple[str, ...]] = {
    "Cozy": ("cozy", "comfort", "comforting", "wholesome"),
    "Relaxing": ("relaxing", "chill", "calm", "low pressure", "low-pressure"),
    "Atmospheric": ("atmospheric", "moody", "vibes", "vibey", "immersive"),
    "Dark": ("dark", "grim", "bleak"),
    "Chaotic": ("chaotic", "chaos", "intense", "high intensity", "high-intensity"),
    "Experimental": ("experimental", "weird", "unusual", "strange"),
    "Rainy night": ("rainy night", "2am", "2 a.m.", "late night"),
}


RECOMMENDATION_ACTION_TERMS = {
    "discover",
    "find",
    "pick",
    "recommend",
    "search",
    "show",
    "suggest",
}
GAME_CONTEXT_TERMS = {"game", "games", "play", "played", "playing"}
FOLLOW_UP_TERMS = {
    "again",
    "another",
    "instead",
    "less",
    "more",
    "shorter",
    "longer",
    "similar",
    "these",
    "those",
    "them",
}
PROJECT_TERMS = {
    "app",
    "chatbot",
    "cosine",
    "data",
    "dataset",
    "guide",
    "igdb",
    "methodology",
    "project",
    "rag",
    "recommendation",
    "retrieval",
    "website",
}
OFF_TOPIC_RECOMMENDATION_TERMS = {
    "book",
    "books",
    "movie",
    "movies",
    "music",
    "restaurant",
    "restaurants",
    "song",
    "songs",
    "tv",
}
GENERIC_TITLE_TOKENS = {
    "action",
    "adventure",
    "atmospheric",
    "cozy",
    "fantasy",
    "farming",
    "game",
    "games",
    "horror",
    "indie",
    "multiplayer",
    "pc",
    "platform",
    "play",
    "played",
    "playstation",
    "puzzle",
    "recommend",
    "rpg",
    "rpgs",
    "sci",
    "similar",
    "story",
    "strategy",
    "switch",
    "xbox",
}

ROUTABLE_RECOMMENDATION_INTENTS = {
    "game_recommendation",
    "seed_game_recommendation",
    "recommendation_follow_up",
}

INTENT_EXAMPLES: dict[str, tuple[str, ...]] = {
    "vague_recommendation": (
        "recommend a game",
        "recommend me something",
        "what should i play",
        "find me something good",
        "pick a game for me",
        "suggest anything fun",
    ),
    "game_recommendation": (
        "recommend cozy RPGs on Switch",
        "find atmospheric story games on PC",
        "show me hidden gems with exploration",
        "suggest short relaxing games",
        "i want a strategy game with strong ratings",
        "looking for a single player fantasy game",
    ),
    "seed_game_recommendation": (
        "i played Hades recently recommend similar games",
        "i loved Stardew Valley what should i play next",
        "find games like League of Legends",
        "recommend something similar to Baldur's Gate",
        "my recent game was Dead Cells recommend alternatives",
        "i enjoyed Hollow Knight give me similar games",
    ),
    "recommendation_follow_up": (
        "make them shorter",
        "show me more like these",
        "keep it on Switch",
        "make those more hidden gem focused",
        "yes my recent game was Hades",
        "that sounds good but more relaxing",
    ),
    "project_question": (
        "how does the guide work",
        "what is this project",
        "what data do you use",
        "where do your answers come from",
        "explain the RAG methodology",
        "how does cosine similarity work",
        "what is your purpose",
    ),
    "unsupported": (
        "recommend a movie",
        "suggest a restaurant",
        "what song should i play",
        "find me a book",
    ),
}


@dataclass(frozen=True)
class SemanticRoute:
    intent: str
    confidence: float
    matched_example: str | None = None


@dataclass(frozen=True)
class RecommendationSlots:
    platforms: tuple[str, ...] = ()
    genres: tuple[str, ...] = ()
    themes: tuple[str, ...] = ()
    moods: tuple[str, ...] = ()
    recent_games: tuple[str, ...] = ()
    avoid_terms: tuple[str, ...] = ()
    playtime_preference: str | None = None
    multiplayer_preference: str | None = None
    discovery_preference: str | None = None
    rating_preference: str | None = None
    raw_terms: tuple[str, ...] = ()

    def has_retrieval_signal(self) -> bool:
        return bool(
            self.platforms
            or self.genres
            or self.themes
            or self.moods
            or self.recent_games
            or self.avoid_terms
            or self.playtime_preference
            or self.multiplayer_preference
            or self.discovery_preference
            or self.rating_preference
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "platforms": list(self.platforms),
            "genres": list(self.genres),
            "themes": list(self.themes),
            "moods": list(self.moods),
            "recent_games": list(self.recent_games),
            "avoid_terms": list(self.avoid_terms),
            "playtime_preference": self.playtime_preference,
            "multiplayer_preference": self.multiplayer_preference,
            "discovery_preference": self.discovery_preference,
            "rating_preference": self.rating_preference,
            "raw_terms": list(self.raw_terms),
        }


@dataclass(frozen=True)
class ChatIntelligenceResult:
    normalized_message: str
    tokens: tuple[str, ...]
    intent: str
    confidence: float
    slots: RecommendationSlots
    recommendation_intent: bool
    project_intent: bool
    follow_up_intent: bool
    should_clarify: bool
    route_source: str = "semantic_router"
    matched_example: str | None = None
    clarification_question: str | None = None
    clarification_prompts: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent,
            "confidence": self.confidence,
            "recommendation_intent": self.recommendation_intent,
            "project_intent": self.project_intent,
            "follow_up_intent": self.follow_up_intent,
            "should_clarify": self.should_clarify,
            "route_source": self.route_source,
            "matched_example": self.matched_example,
            "slots": self.slots.to_dict(),
        }


def normalize_message(text: str) -> str:
    value = str(text or "").lower()
    value = value.replace("’", "'").replace("–", "-").replace("—", "-")
    return " ".join(value.split())


def tokenize_message(text: str) -> tuple[str, ...]:
    return tuple(TOKEN_RE.findall(normalize_message(text)))


def _dedupe(values: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        cleaned = " ".join(str(value or "").strip().split())
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(cleaned)
    return tuple(output)


def _feature_vector(text: str) -> Counter[str]:
    normalized = normalize_message(text)
    tokens = list(tokenize_message(normalized))
    features: Counter[str] = Counter()

    for token in tokens:
        features[f"tok:{token}"] += 1.0

    for size in (2, 3):
        for idx in range(0, max(0, len(tokens) - size + 1)):
            features[f"ng:{' '.join(tokens[idx: idx + size])}"] += 1.4

    compact = re.sub(r"[^a-z0-9]+", " ", normalized).strip()
    for size in (4, 5):
        for idx in range(0, max(0, len(compact) - size + 1)):
            gram = compact[idx : idx + size]
            if " " in gram.strip():
                continue
            features[f"ch:{gram}"] += 0.35

    return features


def _cosine_similarity(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    shared = set(left).intersection(right)
    dot = sum(left[key] * right[key] for key in shared)
    left_norm = sum(value * value for value in left.values()) ** 0.5
    right_norm = sum(value * value for value in right.values()) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


@lru_cache(maxsize=1)
def _intent_example_vectors() -> tuple[tuple[str, str, Counter[str]], ...]:
    vectors: list[tuple[str, str, Counter[str]]] = []
    for intent, examples in INTENT_EXAMPLES.items():
        for example in examples:
            vectors.append((intent, example, _feature_vector(example)))
    return tuple(vectors)


def semantic_route_message(message: str, *, has_history: bool = False) -> SemanticRoute:
    message_vector = _feature_vector(message)
    best_intent = "unknown"
    best_example: str | None = None
    best_score = 0.0

    for intent, example, example_vector in _intent_example_vectors():
        score = _cosine_similarity(message_vector, example_vector)
        if score > best_score:
            best_intent = intent
            best_example = example
            best_score = score

    normalized = normalize_message(message)
    tokens = set(tokenize_message(normalized))

    if tokens.intersection(OFF_TOPIC_RECOMMENDATION_TERMS) and tokens.intersection(
        RECOMMENDATION_ACTION_TERMS
    ):
        return SemanticRoute("unsupported", max(best_score, 0.75), best_example)

    seed_context = any(
        _has_phrase(normalized, phrase)
        for phrase in (
            "i played",
            "i liked",
            "i loved",
            "i enjoyed",
            "recent game",
            "favorite game",
            "favourite game",
            "similar to",
            "more like",
            "games like",
        )
    )
    recommendation_context = tokens.intersection(RECOMMENDATION_ACTION_TERMS) or any(
        _has_phrase(normalized, phrase)
        for phrase in ("what should", "what next", "try next", "play next")
    )
    if seed_context and recommendation_context:
        return SemanticRoute("seed_game_recommendation", max(best_score, 0.78), best_example)

    threshold = 0.18 if has_history else 0.22
    if best_score < threshold:
        return SemanticRoute("unknown", best_score, best_example)

    return SemanticRoute(best_intent, best_score, best_example)


def _title_search_key(value: object) -> str:
    normalized = normalize_message(str(value or ""))
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return " ".join(normalized.split())


@lru_cache(maxsize=1)
def _catalog_titles() -> tuple[str, ...]:
    try:
        import pandas as pd

        from src.app import config
    except Exception:
        return ()

    catalog_path = getattr(config, "APP_CATALOG_PATH", None)
    if catalog_path is None or not catalog_path.exists():
        return ()

    try:
        catalog = pd.read_parquet(catalog_path, columns=["name"])
    except Exception:
        return ()

    titles = [
        str(name).strip()
        for name in catalog["name"].dropna().tolist()
        if str(name).strip()
    ]
    return _dedupe(titles)


def extract_catalog_game_titles(
    message: str,
    *,
    catalog_titles: tuple[str, ...] | list[str] | None = None,
    max_titles: int = 5,
) -> tuple[str, ...]:
    titles = tuple(catalog_titles) if catalog_titles is not None else _catalog_titles()
    if not titles:
        return ()

    message_key = f" {_title_search_key(message)} "
    matches: list[tuple[int, int, str]] = []

    for title in titles:
        title_key = _title_search_key(title)
        if len(title_key) < 3:
            continue
        title_tokens = set(title_key.split())
        if title_tokens and title_tokens.issubset(GENERIC_TITLE_TOKENS):
            continue
        position = message_key.find(f" {title_key} ")
        if position >= 0:
            matches.append((position, -len(title_key), str(title).strip()))

    ordered_matches = [title for _, _, title in sorted(matches)]
    return _dedupe(ordered_matches[:max_titles])


def _has_token(tokens: set[str], alias: str) -> bool:
    return alias in tokens


def _has_phrase(normalized: str, phrase: str) -> bool:
    phrase = phrase.strip().lower()
    if not phrase:
        return False
    if " " not in phrase and "-" not in phrase:
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])", normalized))
    return phrase in normalized


def _extract_alias_matches(
    normalized: str,
    tokens: set[str],
    aliases_by_canonical: dict[str, tuple[str, ...]],
) -> tuple[str, ...]:
    matches: list[str] = []
    for canonical, aliases in aliases_by_canonical.items():
        for alias in aliases:
            if _has_phrase(normalized, alias) or _has_token(tokens, alias):
                matches.append(canonical)
                break
    return _dedupe(matches)


def _extract_playtime_preference(normalized: str) -> str | None:
    if any(
        _has_phrase(normalized, phrase)
        for phrase in ("short", "quick", "one sitting", "few hours", "not too long")
    ):
        return "short"
    if any(
        _has_phrase(normalized, phrase)
        for phrase in ("long", "deep", "hundreds of hours", "long-term", "big game")
    ):
        return "long"
    return None


def _extract_multiplayer_preference(normalized: str) -> str | None:
    if any(
        _has_phrase(normalized, phrase)
        for phrase in ("single player", "single-player", "solo", "by myself")
    ):
        return "single_player"
    if any(
        _has_phrase(normalized, phrase)
        for phrase in ("online co-op", "online coop", "online multiplayer")
    ):
        return "online"
    if any(
        _has_phrase(normalized, phrase)
        for phrase in ("couch co-op", "couch coop", "local co-op", "local coop", "split screen")
    ):
        return "offline"
    if any(_has_phrase(normalized, phrase) for phrase in ("co-op", "coop", "co op", "multiplayer")):
        return "both"
    return None


def _extract_discovery_preference(normalized: str) -> str | None:
    if any(
        _has_phrase(normalized, phrase)
        for phrase in ("hidden gem", "hidden gems", "underrated", "overlooked", "less known", "lesser known")
    ):
        return "hidden_gems"
    if any(
        _has_phrase(normalized, phrase)
        for phrase in ("popular", "mainstream", "well known", "famous")
    ):
        return "popular"
    return None


def _extract_rating_preference(normalized: str) -> str | None:
    if any(
        _has_phrase(normalized, phrase)
        for phrase in (
            "highly rated",
            "strong ratings",
            "best rated",
            "good rating",
            "good reviews",
            "reviewed well",
        )
    ):
        return "strong_rating_evidence"
    return None


def _extract_avoid_terms(normalized: str) -> tuple[str, ...]:
    avoid_terms: list[str] = []
    for pattern in (
        r"\b(?:no|avoid|without|not)\s+([a-z0-9][a-z0-9 +#.'-]{1,40})",
        r"\bi do not want\s+([a-z0-9][a-z0-9 +#.'-]{1,40})",
        r"\bi don't want\s+([a-z0-9][a-z0-9 +#.'-]{1,40})",
    ):
        for match in re.finditer(pattern, normalized):
            candidate = match.group(1)
            candidate = re.split(r"\b(?:but|and|or|with|on|for|please)\b", candidate)[0]
            candidate = candidate.strip(" .,!?:;")
            if candidate:
                avoid_terms.append(candidate)
    return _dedupe(avoid_terms[:5])


def _clean_game_title_fragment(fragment: str) -> str | None:
    cleaned = str(fragment or "").strip(" .,!?:;\"'")
    cleaned = re.sub(
        r"\b(?:recently|before|lately|please|can you|could you|recommend|suggest|find|games?|similar|more like|on|for|with)\b.*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip(" .,!?:;\"'")
    if not cleaned:
        return None
    if len(cleaned) < 2:
        return None
    if cleaned.lower() in {
        "a",
        "an",
        "anything",
        "game",
        "games",
        "it",
        "me",
        "one",
        "something",
        "that",
        "them",
        "these",
        "the",
        "this",
        "those",
    }:
        return None
    return cleaned


def _split_title_candidates(value: str) -> list[str]:
    return [
        candidate
        for candidate in re.split(r"\s*,\s*|\s+and\s+|\s*&\s*|\s+plus\s+", value)
        if candidate.strip()
    ]


def _extract_seed_title_from_context(message: str, *, max_titles: int = 5) -> tuple[str, ...]:
    normalized_original = " ".join(str(message or "").split())
    cue_patterns = (
        r"\b(?:played|liked|loved|enjoyed)\b",
        r"\b(?:similar to|more like|games? like)\b",
        r"\b(?:recent|favorite|favourite)\s+games?\b",
    )
    titles: list[str] = []

    for sentence in re.split(r"[.!?]+", normalized_original):
        sentence = sentence.strip()
        if not sentence:
            continue
        cue_match = None
        for cue_pattern in cue_patterns:
            cue_match = re.search(cue_pattern, sentence, flags=re.IGNORECASE)
            if cue_match:
                break
        if cue_match is None:
            continue

        candidate = sentence[cue_match.end() :].strip()
        if re.match(r"^(was|is|are|were)\b", candidate, flags=re.IGNORECASE):
            candidate = re.sub(r"^(was|is|are|were)\b", "", candidate, flags=re.IGNORECASE).strip()
        for piece in _split_title_candidates(candidate):
            cleaned = _clean_game_title_fragment(piece)
            if cleaned:
                titles.append(cleaned)

    return _dedupe(titles[:max_titles])


def extract_recent_game_titles(
    message: str,
    *,
    catalog_titles: tuple[str, ...] | list[str] | None = None,
) -> tuple[str, ...]:
    catalog_matches = extract_catalog_game_titles(message, catalog_titles=catalog_titles)
    contextual_matches = _extract_seed_title_from_context(message)
    return _dedupe(list(catalog_matches) + list(contextual_matches))[:5]


def extract_recommendation_slots(
    message: str,
    *,
    catalog_titles: tuple[str, ...] | list[str] | None = None,
) -> RecommendationSlots:
    normalized = normalize_message(message)
    tokens = set(tokenize_message(normalized))

    platforms = _extract_alias_matches(normalized, tokens, PLATFORM_ALIASES)
    genres = _extract_alias_matches(normalized, tokens, GENRE_ALIASES)
    themes = _extract_alias_matches(normalized, tokens, THEME_ALIASES)
    moods = _extract_alias_matches(normalized, tokens, MOOD_ALIASES)
    recent_games = extract_recent_game_titles(message, catalog_titles=catalog_titles)
    avoid_terms = _extract_avoid_terms(normalized)
    playtime = _extract_playtime_preference(normalized)
    multiplayer = _extract_multiplayer_preference(normalized)
    discovery = _extract_discovery_preference(normalized)
    rating = _extract_rating_preference(normalized)

    raw_terms = _dedupe(
        list(platforms)
        + list(genres)
        + list(themes)
        + list(moods)
        + list(recent_games)
        + list(avoid_terms)
        + [value for value in (playtime, multiplayer, discovery, rating) if value]
    )

    return RecommendationSlots(
        platforms=platforms,
        genres=genres,
        themes=themes,
        moods=moods,
        recent_games=recent_games,
        avoid_terms=avoid_terms,
        playtime_preference=playtime,
        multiplayer_preference=multiplayer,
        discovery_preference=discovery,
        rating_preference=rating,
        raw_terms=raw_terms,
    )


def has_recommendation_intent(message: str) -> bool:
    normalized = normalize_message(message)
    tokens = set(tokenize_message(normalized))
    if not tokens or tokens.intersection(OFF_TOPIC_RECOMMENDATION_TERMS):
        return False
    if tokens.intersection(RECOMMENDATION_ACTION_TERMS):
        return True
    return any(
        _has_phrase(normalized, phrase)
        for phrase in (
            "what should i play",
            "what game should i play",
            "i want to play",
            "i feel like playing",
            "looking for",
            "similar to",
            "more like",
            "games like",
            "i played",
            "i liked",
            "i loved",
            "i enjoyed",
        )
    )


def has_project_intent(message: str) -> bool:
    normalized = normalize_message(message)
    tokens = set(tokenize_message(normalized))
    question_like = normalized.endswith("?") or tokens.intersection(
        {"what", "why", "how", "who", "where", "explain", "describe", "tell"}
    )
    return bool(question_like and tokens.intersection(PROJECT_TERMS))


def has_follow_up_intent(message: str) -> bool:
    normalized = normalize_message(message)
    tokens = set(tokenize_message(normalized))
    return bool(tokens.intersection(FOLLOW_UP_TERMS)) or any(
        _has_phrase(normalized, phrase)
        for phrase in ("same but", "make it", "keep it", "only show", "show more")
    )


def build_clarification_prompts() -> tuple[str, ...]:
    return (
        "Recommend cozy games on Switch",
        "I played Hades and Dead Cells recently. Recommend similar games",
        "Find hidden gems with strong story and atmosphere",
    )


def analyze_message(
    message: str,
    *,
    has_history: bool = False,
    catalog_titles: tuple[str, ...] | list[str] | None = None,
) -> ChatIntelligenceResult:
    normalized = normalize_message(message)
    tokens = tokenize_message(normalized)
    slots = extract_recommendation_slots(message, catalog_titles=catalog_titles)
    route = semantic_route_message(message, has_history=has_history)

    route_recommendation_intent = route.intent in ROUTABLE_RECOMMENDATION_INTENTS
    route_project_intent = route.intent == "project_question"
    route_follow_up_intent = route.intent == "recommendation_follow_up"

    recommendation_intent = bool(
        route_recommendation_intent
        or has_recommendation_intent(message)
        or (has_history and slots.has_retrieval_signal())
    )
    project_intent = bool(route_project_intent or has_project_intent(message))
    follow_up_intent = bool(route_follow_up_intent or has_follow_up_intent(message))

    should_clarify = bool(
        (route.intent == "vague_recommendation" or recommendation_intent)
        and not project_intent
        and not slots.has_retrieval_signal()
        and not (has_history and follow_up_intent)
    )

    if has_history and slots.has_retrieval_signal() and not recommendation_intent:
        recommendation_intent = True
        follow_up_intent = True

    if route.intent == "unsupported":
        intent = "unsupported"
    elif project_intent and not recommendation_intent:
        intent = "project_question"
    elif should_clarify:
        intent = "recommendation_clarification"
    elif recommendation_intent and follow_up_intent and has_history:
        intent = "recommendation_follow_up"
    elif slots.recent_games and recommendation_intent:
        intent = "seed_game_recommendation"
    elif route.intent == "seed_game_recommendation":
        intent = "seed_game_recommendation"
    elif recommendation_intent:
        intent = "game_recommendation"
    elif follow_up_intent and has_history:
        intent = "recommendation_follow_up"
    else:
        intent = "unknown"

    confidence = max(route.confidence, 0.35)
    if slots.has_retrieval_signal():
        confidence = max(confidence, 0.82)
    elif should_clarify:
        confidence = max(confidence, 0.62)
    elif project_intent:
        confidence = max(confidence, 0.72)
    elif recommendation_intent:
        confidence = max(confidence, 0.55)

    clarification_question = None
    clarification_prompts: tuple[str, ...] = ()
    if should_clarify:
        clarification_question = (
            "I can recommend games, but I need one concrete signal first so the result is not random. "
            "Tell me a platform, genre, mood, recent game you liked, playtime preference, or whether "
            "you want popular games or hidden gems."
        )
        clarification_prompts = build_clarification_prompts()

    return ChatIntelligenceResult(
        normalized_message=normalized,
        tokens=tokens,
        intent=intent,
        confidence=confidence,
        slots=slots,
        recommendation_intent=recommendation_intent,
        project_intent=project_intent,
        follow_up_intent=follow_up_intent,
        should_clarify=should_clarify,
        route_source="semantic_router",
        matched_example=route.matched_example,
        clarification_question=clarification_question,
        clarification_prompts=clarification_prompts,
    )
