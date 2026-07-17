import math
import sqlite3
from collections import Counter
from pathlib import Path

import pandas as pd


def _is_missing(value):
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    text = str(value).strip().lower()
    return text in {"", "nan", "none", "null"}


def _safe_float(value, default=0.0):
    try:
        if _is_missing(value):
            return default
        return float(value)
    except Exception:
        return default


def _parse_csv_values(value):
    if _is_missing(value):
        return []
    text = str(value).strip()
    return [part.strip().lower() for part in text.split(",") if part.strip()]


def _normalize_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(v) for v in value if not _is_missing(v)]


def _clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


class ContentBasedRecommender:
    """Decoupled recommender engine using cosine similarity on game metadata features."""

    def __init__(self, db_path=None):
        root_dir = Path(__file__).resolve().parent.parent
        self.db_path = Path(db_path) if db_path else root_dir / "data" / "database" / "igdb_games.db"
        self.catalog = self._load_catalog()
        self.genre_rarity, self.theme_rarity = self._build_rarity_maps()
        self.game_vectors, self.game_norms = self._build_game_vectors()

    def _load_catalog(self):
        query = """
        SELECT
            game_id,
            name,
            platforms,
            genres,
            themes,
            total_rating,
            playtime_normally,
            release_year
        FROM analytics_ready_games
        """
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(query, conn)
        finally:
            conn.close()

        if df.empty:
            return []

        records = []
        for _, row in df.iterrows():
            records.append(
                {
                    "game_id": str(row.get("game_id", "")),
                    "name": str(row.get("name", "") or "Unknown Game"),
                    "platforms": row.get("platforms"),
                    "genres": row.get("genres"),
                    "themes": row.get("themes"),
                    "total_rating": _safe_float(row.get("total_rating"), 0.0),
                    "playtime_normally": _safe_float(row.get("playtime_normally"), 0.0),
                    "release_year": int(_safe_float(row.get("release_year"), 0.0)),
                }
            )
        return records

    def _build_rarity_maps(self):
        genre_counts = Counter()
        theme_counts = Counter()
        total_games = max(len(self.catalog), 1)

        for row in self.catalog:
            unique_genres = set(_parse_csv_values(row.get("genres")))
            unique_themes = set(_parse_csv_values(row.get("themes")))
            genre_counts.update(unique_genres)
            theme_counts.update(unique_themes)

        def rarity(count):
            # Higher weight for less frequent values while staying numerically stable.
            return math.log(1.0 + (total_games / max(count, 1)))

        genre_rarity = {g: rarity(c) for g, c in genre_counts.items()}
        theme_rarity = {t: rarity(c) for t, c in theme_counts.items()}
        return genre_rarity, theme_rarity

    def _game_to_vector(self, game_row):
        vector = {}

        for platform in _parse_csv_values(game_row.get("platforms")):
            vector[f"platform::{platform}"] = 1.0
        for genre in _parse_csv_values(game_row.get("genres")):
            vector[f"genre::{genre}"] = 1.0
        for theme in _parse_csv_values(game_row.get("themes")):
            vector[f"theme::{theme}"] = 1.0

        rating_norm = min(max(_safe_float(game_row.get("total_rating"), 0.0) / 100.0, 0.0), 1.0)
        vector["numeric::rating"] = rating_norm
        return vector

    def _build_game_vectors(self):
        vectors = {}
        norms = {}
        for row in self.catalog:
            game_id = row.get("game_id")
            vector = self._game_to_vector(row)
            norm = math.sqrt(sum(v * v for v in vector.values()))
            vectors[game_id] = vector
            norms[game_id] = norm
        return vectors, norms

    def _build_user_vector(self, questionnaire, discovery_mode="balanced"):
        questionnaire = questionnaire or {}
        vector = {}

        platforms = _normalize_list(questionnaire.get("platforms", questionnaire.get("platform", [])))
        genres = _normalize_list(questionnaire.get("genres", questionnaire.get("genre", [])))
        themes = _normalize_list(questionnaire.get("themes", questionnaire.get("theme", [])))
        rating = questionnaire.get("rating", questionnaire.get("preferred_rating"))

        discovery_mode = str(discovery_mode or "balanced").strip().lower()
        niche_strength = _clamp(_safe_float(questionnaire.get("niche_strength", 0.6), 0.6), 0.0, 2.0)
        popular_strength = _clamp(_safe_float(questionnaire.get("popular_strength", 0.5), 0.5), 0.0, 2.0)

        for platform in platforms or []:
            if not _is_missing(platform):
                vector[f"platform::{str(platform).strip().lower()}"] = 1.0

        for genre in genres or []:
            if not _is_missing(genre):
                normalized_genre = str(genre).strip().lower()
                weight = 1.0
                if discovery_mode == "niche":
                    rarity_bonus = self.genre_rarity.get(normalized_genre, 1.0)
                    weight = 1.0 + (niche_strength * rarity_bonus)
                vector[f"genre::{normalized_genre}"] = weight

        for theme in themes or []:
            if not _is_missing(theme):
                normalized_theme = str(theme).strip().lower()
                weight = 1.0
                if discovery_mode == "niche":
                    rarity_bonus = self.theme_rarity.get(normalized_theme, 1.0)
                    weight = 1.0 + (niche_strength * rarity_bonus)
                vector[f"theme::{normalized_theme}"] = weight

        if rating is not None and not _is_missing(rating):
            rating_norm = min(max(_safe_float(rating, 0.0) / 100.0, 0.0), 1.0)
            rating_weight = 1.0 + popular_strength if discovery_mode == "popular" else 1.0
            vector["numeric::rating"] = rating_norm * rating_weight

        return vector

    def _playtime_match_multiplier(self, playtime_pref, game_playtime, playtime_weight):
        playtime_pref = str(playtime_pref or "").strip().lower()
        if not playtime_pref:
            return 1.0

        value = _safe_float(game_playtime, 0.0)
        if value <= 0:
            return 1.0

        if playtime_pref == "short":
            is_match = value <= 10.0
        elif playtime_pref == "medium":
            is_match = 10.0 < value <= 30.0
        elif playtime_pref == "long":
            is_match = value > 30.0
        else:
            return 1.0

        if is_match:
            return 1.0 + playtime_weight
        return max(0.0, 1.0 - playtime_weight)

    def _year_multiplier(self, release_year, years_mode, years_start, years_end, years_weight):
        if years_mode == "off":
            return 1.0

        year = int(_safe_float(release_year, 0.0))
        in_range = years_start <= year <= years_end

        if years_mode == "filter":
            return 1.0 if in_range else 0.0

        # boost mode
        if in_range:
            return 1.0 + years_weight
        return max(0.0, 1.0 - years_weight)

    def _quality_multiplier(self, game_rating, target_rating, quality_weight):
        if target_rating is None or _is_missing(target_rating):
            return 1.0

        game_rating_val = _safe_float(game_rating, 0.0)
        target = _safe_float(target_rating, game_rating_val)
        distance = abs(game_rating_val - target)
        closeness = 1.0 - _clamp(distance / 100.0, 0.0, 1.0)
        return max(0.0, (1.0 - quality_weight) + (quality_weight * closeness))

    def recommend(self, questionnaire, top_n=5):
        questionnaire = questionnaire or {}
        discovery_mode = str(questionnaire.get("discovery", "Balanced")).strip().lower()
        if discovery_mode not in {"balanced", "niche", "popular"}:
            discovery_mode = "balanced"

        target_rating = questionnaire.get("rating", questionnaire.get("preferred_rating"))
        quality_weight = _clamp(_safe_float(questionnaire.get("quality_weight", 0.5), 0.5), 0.0, 1.0)
        playtime_pref = questionnaire.get("playtime", questionnaire.get("playtime_category"))
        playtime_weight = _clamp(_safe_float(questionnaire.get("playtime_weight", 0.2), 0.2), 0.0, 1.0)

        years_mode = str(questionnaire.get("years_mode", "boost")).strip().lower()
        if years_mode not in {"boost", "filter", "off"}:
            years_mode = "boost"
        years_start = int(_safe_float(questionnaire.get("years_start", 2010), 2010))
        years_end = int(_safe_float(questionnaire.get("years_end", 2024), 2024))
        if years_start > years_end:
            years_start, years_end = years_end, years_start
        years_weight = _clamp(_safe_float(questionnaire.get("years_weight", 0.15), 0.15), 0.0, 1.0)

        user_vector = self._build_user_vector(questionnaire, discovery_mode=discovery_mode)
        user_norm = math.sqrt(sum(v * v for v in user_vector.values()))
        if user_norm == 0.0:
            return []

        scored = []
        for row in self.catalog:
            game_id = row.get("game_id")
            game_vector = self.game_vectors.get(game_id, {})
            game_norm = self.game_norms.get(game_id, 0.0)
            if game_norm == 0.0:
                continue

            dot = 0.0
            for feature, value in user_vector.items():
                dot += value * game_vector.get(feature, 0.0)

            cosine_similarity = dot / (user_norm * game_norm) if (user_norm > 0.0 and game_norm > 0.0) else 0.0
            quality_multiplier = self._quality_multiplier(
                game_rating=row.get("total_rating"),
                target_rating=target_rating,
                quality_weight=quality_weight,
            )
            playtime_multiplier = self._playtime_match_multiplier(
                playtime_pref=playtime_pref,
                game_playtime=row.get("playtime_normally"),
                playtime_weight=playtime_weight,
            )
            year_multiplier = self._year_multiplier(
                release_year=row.get("release_year"),
                years_mode=years_mode,
                years_start=years_start,
                years_end=years_end,
                years_weight=years_weight,
            )
            if years_mode == "filter" and year_multiplier == 0.0:
                continue

            final_score = cosine_similarity * quality_multiplier * playtime_multiplier * year_multiplier
            scored.append(
                {
                    "game_id": game_id,
                    "name": row.get("name", "Unknown Game"),
                    "platforms": row.get("platforms"),
                    "genres": row.get("genres"),
                    "themes": row.get("themes"),
                    "total_rating": _safe_float(row.get("total_rating"), 0.0),
                    "playtime_normally": _safe_float(row.get("playtime_normally"), 0.0),
                    "release_year": int(_safe_float(row.get("release_year"), 0.0)),
                    "cosine_similarity": cosine_similarity,
                    "quality_multiplier": quality_multiplier,
                    "playtime_multiplier": playtime_multiplier,
                    "year_multiplier": year_multiplier,
                    "final_score": final_score,
                }
            )

        scored.sort(
            key=lambda x: (
                -_safe_float(x.get("final_score"), 0.0),
                -_safe_float(x.get("cosine_similarity"), 0.0),
                -_safe_float(x.get("total_rating"), 0.0),
            )
        )
        return scored[:top_n]


if __name__ == "__main__":
    recommender = ContentBasedRecommender()
    sample_questionnaire = {
        "discovery": "Niche",
        "platforms": ["Nintendo Switch"],
        "genres": ["Role-playing (RPG)", "Adventure"],
        "themes": ["Fantasy"],
        "rating": 80,
        "quality_weight": 0.6,
        "playtime": "Medium",
        "playtime_weight": 0.2,
        "years_mode": "boost",
        "years_start": 2010,
        "years_end": 2024,
        "years_weight": 0.15,
    }
    recommendations = recommender.recommend(sample_questionnaire, top_n=5)
    for idx, game in enumerate(recommendations, start=1):
        print(
            f"{idx}. {game['name']} | final={game['final_score']:.4f} | "
            f"cosine={game['cosine_similarity']:.4f} | rating={game['total_rating']:.1f}"
        )
