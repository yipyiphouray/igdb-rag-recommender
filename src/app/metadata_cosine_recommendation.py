from __future__ import annotations

import math
import re
from dataclasses import dataclass
from difflib import get_close_matches
from typing import Any, Iterable

import pandas as pd

from src.app.filters import apply_catalog_filters
from src.app.formatting import split_list


Vector = dict[str, float]

VECTOR_COLUMN_WEIGHTS = {
    "platforms_list": ("platform", 0.85),
    "genres_list": ("genre", 1.45),
    "themes_list": ("theme", 1.2),
    "game_modes_list": ("game_mode", 0.75),
    "player_perspectives_list": ("perspective", 0.65),
    "keywords_list": ("keyword", 0.35),
    "developers_list": ("developer", 0.25),
    "publishers_list": ("publisher", 0.2),
}

USER_FIELD_WEIGHTS = {
    "platform": 0.9,
    "genre": 1.7,
    "theme": 1.45,
    "mood": 0.8,
    "playstyle": 0.8,
    "seed": 0.75,
    "playtime": 0.65,
}

RANKING_WEIGHTS = {
    "similarity": 0.65,
    "quality": 0.15,
    "evidence": 0.10,
    "discovery": 0.05,
    "playtime": 0.05,
}

FUZZY_TITLE_THRESHOLD = 0.82
MAX_RECENT_GAME_SEEDS = 5

TOKEN_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "game",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
    "your",
}


@dataclass(frozen=True)
class VectorizedGame:
    row_index: int
    game_id: int
    name: str
    normalized_name: str
    vector: Vector
    norm: float


@dataclass
class SeedMatch:
    query: str
    game_id: int
    name: str
    match_type: str
    score: float
    vector: Vector


@dataclass
class MetadataCosineRecommendationOutput:
    recommendations: pd.DataFrame
    matched_seed_games: list[str]
    unmatched_seed_games: list[str]
    profile_terms: list[str]


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    try:
        result = pd.isna(value)
    except (TypeError, ValueError):
        return False
    if isinstance(result, bool):
        return result
    return False


def _safe_float(value: object, default: float = 0.0) -> float:
    if _is_missing(value):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: object, default: int = 0) -> int:
    if _is_missing(value):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _clean_text(value: object) -> str:
    if _is_missing(value):
        return ""
    return str(value).strip()


def _normalize_term(value: object) -> str:
    text = _clean_text(value).lower()
    text = re.sub(r"[’']", "", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _normalize_title(value: object) -> str:
    return _normalize_term(value)


def _tokenize(value: object, *, max_tokens: int = 80) -> list[str]:
    text = _normalize_term(value)
    if not text:
        return []
    tokens = []
    seen = set()
    for token in text.split():
        if len(token) < 3 or token in TOKEN_STOPWORDS or token in seen:
            continue
        seen.add(token)
        tokens.append(token)
        if len(tokens) >= max_tokens:
            break
    return tokens


def _selected(values: Iterable[str] | None) -> list[str]:
    if values is None:
        return []
    cleaned = []
    for value in values:
        text = _clean_text(value)
        if text:
            cleaned.append(text)
    return cleaned


def _add_feature(vector: Vector, feature: str, weight: float) -> None:
    if not feature or weight <= 0:
        return
    vector[feature] = vector.get(feature, 0.0) + float(weight)


def _norm(vector: Vector) -> float:
    return math.sqrt(sum(value * value for value in vector.values()))


def _cosine(left: Vector, left_norm: float, right: Vector, right_norm: float) -> float:
    if left_norm <= 0 or right_norm <= 0:
        return 0.0
    if len(left) > len(right):
        left, right = right, left
    dot = sum(value * right.get(feature, 0.0) for feature, value in left.items())
    return max(min(dot / (left_norm * right_norm), 1.0), 0.0)


def _playtime_band(hours: object) -> str | None:
    value = _safe_float(hours, -1.0)
    if value < 0:
        return None
    if value <= 10:
        return "shorter"
    if value <= 30:
        return "medium"
    return "longer"


def _desired_playtime_band(desired_playtime: str) -> str | None:
    normalized = desired_playtime.strip().lower()
    if "short" in normalized:
        return "shorter"
    if "medium" in normalized:
        return "medium"
    if "long" in normalized:
        return "longer"
    return None


def _quality_score(total_rating: object) -> float:
    if _is_missing(total_rating):
        return 0.0
    return max(min(_safe_float(total_rating) / 100.0, 1.0), 0.0)


def _rating_evidence_score(total_rating_count: object, max_log_count: float) -> float:
    if max_log_count <= 0:
        return 0.0
    count = max(_safe_float(total_rating_count), 0.0)
    return max(min(math.log1p(count) / max_log_count, 1.0), 0.0)


def _discovery_score(row: pd.Series, discovery_preference: str) -> float:
    normalized = discovery_preference.strip().lower()
    if "hidden" in normalized:
        return 1.0 if _safe_int(row.get("hidden_gem_balanced_flag")) == 1 else 0.0
    if "popular" in normalized or "visible" in normalized:
        return max(min(_safe_float(row.get("custom_interest_percentile")), 1.0), 0.0)
    return 0.0


def _playtime_score(row: pd.Series, desired_playtime: str) -> float:
    desired_band = _desired_playtime_band(desired_playtime)
    if desired_band is None:
        return 0.0
    return 1.0 if _playtime_band(row.get("normal_playtime_hours")) == desired_band else 0.0


def _overlap_values(row: pd.Series, column: str, selected_values: Iterable[str]) -> list[str]:
    selected_normalized = {_normalize_term(value) for value in selected_values if _normalize_term(value)}
    if not selected_normalized:
        return []
    matches = []
    for value in split_list(row.get(column)):
        if _normalize_term(value) in selected_normalized:
            matches.append(value)
    return matches


def _format_names(values: Iterable[str], limit: int = 3) -> str:
    cleaned = [value for value in values if value]
    if not cleaned:
        return ""
    shown = cleaned[:limit]
    if len(cleaned) > limit:
        shown.append(f"+{len(cleaned) - limit} more")
    return ", ".join(shown)


class MetadataCosineRecommender:
    """Metadata-based cosine recommender built from the app catalog parquet schema."""

    def __init__(self, catalog: pd.DataFrame):
        self.catalog = catalog.reset_index(drop=True).copy()
        self.games = self._build_games()
        self.title_index = self._build_title_index()
        self.title_choices = sorted(self.title_index)

    def _build_games(self) -> list[VectorizedGame]:
        games: list[VectorizedGame] = []
        for row_index, row in self.catalog.iterrows():
            vector = self._game_to_vector(row)
            norm = _norm(vector)
            if norm <= 0:
                continue
            games.append(
                VectorizedGame(
                    row_index=int(row_index),
                    game_id=_safe_int(row.get("game_id")),
                    name=_clean_text(row.get("name")) or "Unknown title",
                    normalized_name=_normalize_title(row.get("name")),
                    vector=vector,
                    norm=norm,
                )
            )
        return games

    def _build_title_index(self) -> dict[str, VectorizedGame]:
        title_index: dict[str, VectorizedGame] = {}
        for game in self.games:
            if not game.normalized_name:
                continue
            existing = title_index.get(game.normalized_name)
            if existing is None or self._seed_quality(game) > self._seed_quality(existing):
                title_index[game.normalized_name] = game
        return title_index

    def _seed_quality(self, game: VectorizedGame) -> tuple[float, float]:
        row = self.catalog.iloc[game.row_index]
        return (
            _safe_float(row.get("total_rating_count")),
            _safe_float(row.get("total_rating")),
        )

    def _game_to_vector(self, row: pd.Series) -> Vector:
        vector: Vector = {}
        for column, (prefix, weight) in VECTOR_COLUMN_WEIGHTS.items():
            if column not in row.index:
                continue
            for value in split_list(row.get(column)):
                normalized = _normalize_term(value)
                if normalized:
                    _add_feature(vector, f"{prefix}::{normalized}", weight)

        playtime_band = _playtime_band(row.get("normal_playtime_hours"))
        if playtime_band:
            _add_feature(vector, f"playtime::{playtime_band}", 0.55)

        for token in _tokenize(row.get("name"), max_tokens=10):
            _add_feature(vector, f"text::{token}", 0.35)
        for token in _tokenize(row.get("summary"), max_tokens=80):
            _add_feature(vector, f"text::{token}", 0.08)

        return vector

    def _match_seed_games(self, seed_titles: Iterable[str]) -> tuple[list[SeedMatch], list[str]]:
        matched: list[SeedMatch] = []
        unmatched: list[str] = []
        seen_game_ids: set[int] = set()

        for raw_title in _selected(seed_titles)[:MAX_RECENT_GAME_SEEDS]:
            normalized = _normalize_title(raw_title)
            if not normalized:
                continue

            game = self.title_index.get(normalized)
            match_type = "exact"
            score = 1.0

            if game is None:
                close_matches = get_close_matches(
                    normalized,
                    self.title_choices,
                    n=1,
                    cutoff=FUZZY_TITLE_THRESHOLD,
                )
                if close_matches:
                    game = self.title_index[close_matches[0]]
                    match_type = "fuzzy"
                    score = 0.0

            if game is None:
                unmatched.append(raw_title)
                continue

            if game.game_id in seen_game_ids:
                continue
            seen_game_ids.add(game.game_id)
            matched.append(
                SeedMatch(
                    query=raw_title,
                    game_id=game.game_id,
                    name=game.name,
                    match_type=match_type,
                    score=score,
                    vector=game.vector,
                )
            )

        return matched, unmatched

    def _build_user_vector(
        self,
        *,
        platforms: Iterable[str] | None,
        genres: Iterable[str] | None,
        themes: Iterable[str] | None,
        mood_words: Iterable[str] | None,
        playstyle_preferences: Iterable[str] | None,
        desired_playtime: str,
        seed_matches: list[SeedMatch],
    ) -> tuple[Vector, list[str]]:
        vector: Vector = {}
        profile_terms: list[str] = []

        for value in _selected(platforms):
            normalized = _normalize_term(value)
            if normalized:
                _add_feature(vector, f"platform::{normalized}", USER_FIELD_WEIGHTS["platform"])
                profile_terms.append(value)

        for value in _selected(genres):
            normalized = _normalize_term(value)
            if normalized:
                _add_feature(vector, f"genre::{normalized}", USER_FIELD_WEIGHTS["genre"])
                profile_terms.append(value)

        for value in _selected(themes):
            normalized = _normalize_term(value)
            if normalized:
                _add_feature(vector, f"theme::{normalized}", USER_FIELD_WEIGHTS["theme"])
                profile_terms.append(value)

        for value in _selected(mood_words):
            profile_terms.append(value)
            for token in _tokenize(value, max_tokens=8):
                _add_feature(vector, f"text::{token}", USER_FIELD_WEIGHTS["mood"])

        for value in _selected(playstyle_preferences):
            profile_terms.append(value)
            normalized = _normalize_term(value)
            if normalized:
                _add_feature(vector, f"game_mode::{normalized}", USER_FIELD_WEIGHTS["playstyle"])
                _add_feature(vector, f"perspective::{normalized}", USER_FIELD_WEIGHTS["playstyle"] * 0.8)
            for token in _tokenize(value, max_tokens=8):
                _add_feature(vector, f"text::{token}", USER_FIELD_WEIGHTS["playstyle"] * 0.5)

        playtime_band = _desired_playtime_band(desired_playtime)
        if playtime_band:
            _add_feature(vector, f"playtime::{playtime_band}", USER_FIELD_WEIGHTS["playtime"])
            profile_terms.append(desired_playtime)

        if seed_matches:
            seed_weight = USER_FIELD_WEIGHTS["seed"] / max(len(seed_matches), 1)
            for seed in seed_matches:
                profile_terms.append(seed.name)
                for feature, value in seed.vector.items():
                    _add_feature(vector, feature, value * seed_weight)

        return vector, profile_terms

    def recommend(
        self,
        *,
        platform: str | None = None,
        platforms: Iterable[str] | None = None,
        genres: Iterable[str] | None = None,
        themes: Iterable[str] | None = None,
        mood_words: Iterable[str] | None = None,
        favorite_games: Iterable[str] | None = None,
        playstyle_preferences: Iterable[str] | None = None,
        release_year_range: tuple[int, int] | None = None,
        discovery_preference: str = "Balanced",
        desired_playtime: str = "Any length",
        top_n: int = 10,
    ) -> MetadataCosineRecommendationOutput:
        selected_platforms = _selected(platforms)
        if platform:
            selected_platforms = [platform, *selected_platforms]
        selected_platforms = list(dict.fromkeys(selected_platforms))

        seed_matches, unmatched_seed_games = self._match_seed_games(favorite_games or [])
        user_vector, profile_terms = self._build_user_vector(
            platforms=selected_platforms,
            genres=genres,
            themes=themes,
            mood_words=mood_words,
            playstyle_preferences=playstyle_preferences,
            desired_playtime=desired_playtime,
            seed_matches=seed_matches,
        )
        user_norm = _norm(user_vector)
        if user_norm <= 0:
            return MetadataCosineRecommendationOutput(
                recommendations=pd.DataFrame(),
                matched_seed_games=[seed.name for seed in seed_matches],
                unmatched_seed_games=unmatched_seed_games,
                profile_terms=profile_terms,
            )

        filtered = apply_catalog_filters(
            self.catalog,
            release_year_range=release_year_range,
            platforms=selected_platforms,
        )
        if filtered.empty:
            return MetadataCosineRecommendationOutput(
                recommendations=filtered,
                matched_seed_games=[seed.name for seed in seed_matches],
                unmatched_seed_games=unmatched_seed_games,
                profile_terms=profile_terms,
            )

        seed_game_ids = {seed.game_id for seed in seed_matches}
        candidate_positions = set(filtered.index.tolist())
        candidate_games = [
            game
            for game in self.games
            if game.row_index in candidate_positions and game.game_id not in seed_game_ids
        ]
        if not candidate_games:
            return MetadataCosineRecommendationOutput(
                recommendations=pd.DataFrame(),
                matched_seed_games=[seed.name for seed in seed_matches],
                unmatched_seed_games=unmatched_seed_games,
                profile_terms=profile_terms,
            )

        max_log_count = max(
            math.log1p(_safe_float(self.catalog.iloc[game.row_index].get("total_rating_count")))
            for game in candidate_games
        )

        scored_rows: list[pd.Series] = []
        for game in candidate_games:
            row = self.catalog.iloc[game.row_index].copy()
            similarity_score = _cosine(user_vector, user_norm, game.vector, game.norm)
            quality_score = _quality_score(row.get("total_rating"))
            evidence_score = _rating_evidence_score(row.get("total_rating_count"), max_log_count)
            discovery_score = _discovery_score(row, discovery_preference)
            playtime_score = _playtime_score(row, desired_playtime)

            final_score = (
                RANKING_WEIGHTS["similarity"] * similarity_score
                + RANKING_WEIGHTS["quality"] * quality_score
                + RANKING_WEIGHTS["evidence"] * evidence_score
                + RANKING_WEIGHTS["discovery"] * discovery_score
                + RANKING_WEIGHTS["playtime"] * playtime_score
            )

            row["similarity_score_component"] = round(similarity_score, 6)
            row["quality_score_component"] = round(quality_score, 6)
            row["rating_evidence_score"] = round(evidence_score, 6)
            row["discovery_score_component"] = round(discovery_score, 6)
            row["playtime_score_component"] = round(playtime_score, 6)
            row["recommendation_score"] = round(final_score, 6)
            row["recommendation_explanation"] = self._explain(
                row=row,
                selected_platforms=selected_platforms,
                selected_genres=_selected(genres),
                selected_themes=_selected(themes),
                seed_matches=seed_matches,
                discovery_preference=discovery_preference,
                desired_playtime=desired_playtime,
            )
            row["recommendation_caveats"] = self._caveats(row, unmatched_seed_games)
            scored_rows.append(row)

        recommendations = pd.DataFrame(scored_rows)
        recommendations = recommendations.sort_values(
            ["recommendation_score", "similarity_score_component", "total_rating", "total_rating_count"],
            ascending=False,
            na_position="last",
        ).head(top_n)

        return MetadataCosineRecommendationOutput(
            recommendations=recommendations,
            matched_seed_games=[seed.name for seed in seed_matches],
            unmatched_seed_games=unmatched_seed_games,
            profile_terms=list(dict.fromkeys(profile_terms)),
        )

    def _explain(
        self,
        *,
        row: pd.Series,
        selected_platforms: list[str],
        selected_genres: list[str],
        selected_themes: list[str],
        seed_matches: list[SeedMatch],
        discovery_preference: str,
        desired_playtime: str,
    ) -> str:
        reasons: list[str] = []

        platform_matches = _overlap_values(row, "platforms_list", selected_platforms)
        if platform_matches:
            reasons.append(f"available on {_format_names(platform_matches)}")

        genre_matches = _overlap_values(row, "genres_list", selected_genres)
        if genre_matches:
            reasons.append(f"matches your {_format_names(genre_matches)} genre preference")

        theme_matches = _overlap_values(row, "themes_list", selected_themes)
        if theme_matches:
            reasons.append(f"matches your {_format_names(theme_matches)} theme preference")

        if seed_matches:
            reasons.append(
                f"shares metadata similarity with recently played game(s): {_format_names([seed.name for seed in seed_matches])}"
            )

        if "hidden" in discovery_preference.lower() and _safe_int(row.get("hidden_gem_balanced_flag")) == 1:
            reasons.append("is a documented hidden-gem candidate")
        elif ("popular" in discovery_preference.lower() or "visible" in discovery_preference.lower()) and _safe_float(row.get("custom_interest_percentile")) > 0:
            reasons.append("has a stronger known visibility signal")

        desired_band = _desired_playtime_band(desired_playtime)
        if desired_band and _playtime_band(row.get("normal_playtime_hours")) == desired_band:
            reasons.append(f"fits your {desired_playtime.lower()} playtime preference")

        if not _is_missing(row.get("total_rating")):
            reasons.append(f"has a {float(row['total_rating']):.1f}/100 total rating")

        if not reasons:
            return "Recommended because it is one of the closest metadata matches in the current catalog."
        return "Recommended because it " + ", ".join(reasons) + "."

    def _caveats(self, row: pd.Series, unmatched_seed_games: list[str]) -> list[str]:
        caveats: list[str] = []
        if unmatched_seed_games:
            caveats.append(
                "Some recent games could not be matched in the catalog: "
                + _format_names(unmatched_seed_games, limit=5)
                + "."
            )
        if _is_missing(row.get("total_rating")):
            caveats.append("This game is missing total rating data, so quality scoring is limited.")
        if _is_missing(row.get("custom_interest_percentile")):
            caveats.append("This game is missing PopScore visibility data, so visibility should be treated as unknown.")
        return caveats
