import math
import re
import sqlite3
from collections import Counter
from pathlib import Path

import chromadb
import joblib
import pandas as pd
from chromadb.utils import embedding_functions

try:
    from rank_bm25 import BM25Okapi
except Exception:
    BM25Okapi = None


def _contains_any(text, options):
    text = (text or "").lower()
    return any(str(opt).lower() in text for opt in options)


def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _safe_int(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _tokenize_text(text):
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def _is_short_query(query, threshold=10):
    return len((query or "").strip()) < threshold


def _has_term(query, term):
    return term in (query or "").lower()


ROMAN_NUMERAL_MAP = {
    "1": "i",
    "2": "ii",
    "3": "iii",
    "4": "iv",
    "5": "v",
    "6": "vi",
    "7": "vii",
    "8": "viii",
    "9": "ix",
    "10": "x",
}


CONCRETE_ELEMENTS = {
    "mahjong",
    "tetris",
    "chess",
    "solitaire",
    "fps",
}

MANAGEMENT_DOMAINS = {
    "restaurant": ["restaurant", "cafe", "cooking", "diner", "kitchen"],
    "hotel": ["hotel", "inn", "resort", "lodging"],
    "store": ["store", "shop", "market", "retail"],
}


class SimpleBM25:
    """Fallback BM25 implementation when rank_bm25 is unavailable."""

    def __init__(self, tokenized_corpus, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.tokenized_corpus = tokenized_corpus
        self.doc_count = len(tokenized_corpus)
        self.doc_freq = {}
        self.doc_len = []
        self.term_freqs = []

        total_len = 0
        for doc in tokenized_corpus:
            tf = Counter(doc)
            self.term_freqs.append(tf)
            doc_len = len(doc)
            self.doc_len.append(doc_len)
            total_len += doc_len
            for term in tf:
                self.doc_freq[term] = self.doc_freq.get(term, 0) + 1

        self.avgdl = (total_len / self.doc_count) if self.doc_count > 0 else 0.0
        self.idf = {}
        for term, df in self.doc_freq.items():
            self.idf[term] = math.log(1 + (self.doc_count - df + 0.5) / (df + 0.5))

    def get_scores(self, query_tokens):
        scores = [0.0] * self.doc_count
        if not query_tokens:
            return scores

        for i, tf in enumerate(self.term_freqs):
            dl = self.doc_len[i]
            denom_norm = self.k1 * (1 - self.b + self.b * (dl / self.avgdl)) if self.avgdl > 0 else self.k1
            score = 0.0
            for term in query_tokens:
                if term not in tf:
                    continue
                term_tf = tf[term]
                idf = self.idf.get(term, 0.0)
                numerator = term_tf * (self.k1 + 1)
                denominator = term_tf + denom_norm
                score += idf * (numerator / denominator)
            scores[i] = score
        return scores


def build_model_feature_vector(candidate):
    platforms = candidate.get("platforms", "") or ""
    genres = candidate.get("genres", "") or ""
    themes = candidate.get("themes", "") or ""
    developers = candidate.get("developers", "") or ""
    publishers = candidate.get("publishers", "") or ""
    summary = candidate.get("summary", "") or ""
    storyline = candidate.get("storyline", "") or ""
    category_id = _safe_int(candidate.get("category_id", 0), 0)

    feature_map = {
        "release_year": _safe_float(candidate.get("release_year", 0), 0.0),
        "mp_campaign_coop": _safe_float(candidate.get("mp_campaign_coop", 0), 0.0),
        "mp_splitscreen": _safe_float(candidate.get("mp_splitscreen", 0), 0.0),
        "mp_online_coop": _safe_float(candidate.get("mp_online_coop", 0), 0.0),
        "mp_offline_coop": _safe_float(candidate.get("mp_offline_coop", 0), 0.0),
        "mp_max_online_players": _safe_float(candidate.get("mp_max_online_players", 0), 0.0),
        "summary_length": float(len(summary)),
        "storyline_length": float(len(storyline)),
        "category_is_main_game": 1.0 if category_id == 0 else 0.0,
        "category_is_variant_or_special": 0.0 if category_id == 0 else 1.0,
        "platform_pc": 1.0 if "pc" in platforms.lower() else 0.0,
        "platform_playstation_4": 1.0 if "playstation 4" in platforms.lower() else 0.0,
        "platform_playstation_5": 1.0 if "playstation 5" in platforms.lower() else 0.0,
        "platform_xbox_one": 1.0 if "xbox one" in platforms.lower() else 0.0,
        "platform_xbox_series_x_s": 1.0 if "xbox series x|s" in platforms.lower() else 0.0,
        "platform_nintendo_switch": 1.0 if "nintendo switch" in platforms.lower() else 0.0,
        "genre_action": 1.0 if "action" in themes.lower() else 0.0,
        "genre_adventure": 1.0 if "adventure" in genres.lower() else 0.0,
        "genre_role_playing_rpg": 1.0 if "role-playing (rpg)" in genres.lower() else 0.0,
        "genre_strategy": 1.0 if "strategy" in genres.lower() else 0.0,
        "genre_shooter": 1.0 if "shooter" in genres.lower() else 0.0,
        "genre_indie": 1.0 if "indie" in genres.lower() else 0.0,
        "genre_simulator": 1.0 if "simulator" in genres.lower() else 0.0,
        "genre_platform": 1.0 if "platform" in genres.lower() else 0.0,
        "dev_nintendo": 1.0 if "nintendo" in developers.lower() else 0.0,
        "dev_ubisoft": 1.0 if "ubisoft" in developers.lower() else 0.0,
        "dev_electronic_arts": 1.0 if ("electronic arts" in developers.lower() or "ea " in developers.lower()) else 0.0,
        "dev_sony": 1.0 if ("sony" in developers.lower() or "sony" in publishers.lower()) else 0.0,
        "dev_square_enix": 1.0 if "square enix" in developers.lower() else 0.0,
        "dev_capcom": 1.0 if "capcom" in developers.lower() else 0.0,
        "dev_valve": 1.0 if "valve" in developers.lower() else 0.0,
    }
    return feature_map


def rank_results(candidates, model_bundle=None):
    if not candidates:
        return []

    model = None
    feature_columns = []
    if model_bundle:
        model = model_bundle.get("model")
        feature_columns = model_bundle.get("feature_columns", [])

    # Step A: relevance score is retrieval relevance + metadata similarity boost.
    for candidate in candidates:
        metadata_boost = _safe_float(candidate.get("metadata_boost", 0.0), 0.0)
        hybrid_rrf = _safe_float(candidate.get("hybrid_score", 0.0), 0.0)
        candidate["relevance_score"] = metadata_boost + hybrid_rrf

    # Step B: rank all candidates by relevance first.
    relevance_sorted = sorted(
        candidates,
        key=lambda x: (
            -_safe_float(x.get("relevance_score", 0.0), 0.0),
            _safe_float(x.get("distance", 1.0), 1.0),
        ),
    )

    # Step C: apply predictive scoring only to top 20 relevance candidates.
    top_k = relevance_sorted[:20]
    remainder = relevance_sorted[20:]

    if model is not None and feature_columns and top_k:
        rows = []
        for candidate in top_k:
            feature_map = build_model_feature_vector(candidate)
            rows.append({col: feature_map.get(col, 0.0) for col in feature_columns})

        x = pd.DataFrame(rows, columns=feature_columns).fillna(0)
        preds = model.predict(x)
        for candidate, score in zip(top_k, preds):
            candidate["predicted_quality_score"] = _safe_float(score, 0.0)
            final_score = candidate["predicted_quality_score"]
            if _safe_float(candidate.get("metadata_boost", 0.0), 0.0) <= 0.0:
                final_score *= 0.5
            candidate["primary_rank_score"] = final_score
    else:
        for candidate in top_k:
            fallback = _safe_float(candidate.get("total_rating", 0.0), 0.0)
            candidate["predicted_quality_score"] = fallback
            final_score = fallback
            if _safe_float(candidate.get("metadata_boost", 0.0), 0.0) <= 0.0:
                final_score *= 0.5
            candidate["primary_rank_score"] = final_score

    # Keep remainder below top-20 ranked set.
    for candidate in remainder:
        fallback = _safe_float(candidate.get("total_rating", 0.0), 0.0)
        candidate["predicted_quality_score"] = fallback
        candidate["primary_rank_score"] = -1.0

    # Step D: final display order is predictive score on top-20 with relevance as tiebreak.
    top_k_sorted = sorted(
        top_k,
        key=lambda x: (
            -_safe_float(x.get("primary_rank_score", 0.0), 0.0),
            -_safe_float(x.get("relevance_score", 0.0), 0.0),
            _safe_float(x.get("distance", 1.0), 1.0),
        ),
    )
    return top_k_sorted + remainder


class RAGAgent:
    def __init__(self):
        self.root_dir = Path(__file__).resolve().parent.parent
        self.db_path = self.root_dir / "data" / "database" / "igdb_games.db"
        self.model_path = self.root_dir / "models" / "recommender_model.pkl"

        self.client = chromadb.PersistentClient(path=str(self.root_dir / "data" / "vector_store"))
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_collection(
            name="igdb_game_profiles",
            embedding_function=self.embedding_fn,
        )

        self.model_bundle = self._load_model_bundle()
        self.analytics_columns = self._get_analytics_columns()
        self.catalog_by_id = {}
        self.bm25_doc_ids = []
        self.bm25_index = None
        self._build_bm25_index_from_analytics_view()

    def _load_model_bundle(self):
        if not self.model_path.exists():
            print(f"[WARN] Model not found at {self.model_path}. Using heuristic ranking.")
            return None

        try:
            artifact = joblib.load(self.model_path)
            if isinstance(artifact, dict) and "model" in artifact and "feature_columns" in artifact:
                return artifact
            return {"model": artifact, "feature_columns": []}
        except Exception as exc:
            print(f"[WARN] Could not load model ({exc}). Using heuristic ranking.")
            return None

    def _get_analytics_columns(self):
        conn = sqlite3.connect(self.db_path)
        try:
            rows = pd.read_sql_query("PRAGMA table_info(analytics_ready_games)", conn)
        finally:
            conn.close()
        if rows.empty:
            return set()
        return set(rows["name"].astype(str).tolist())

    def _build_bm25_index_from_analytics_view(self):
        query = """
        SELECT
            game_id,
            name,
            release_year,
            platforms,
            summary,
            storyline,
            total_rating,
            genres,
            themes,
            developers,
            publishers,
            category_id,
            mp_campaign_coop,
            mp_splitscreen,
            mp_online_coop,
            mp_offline_coop,
            mp_max_online_players
        FROM analytics_ready_games
        """

        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(query, conn)
        finally:
            conn.close()

        self.catalog_by_id = {}
        tokenized_corpus = []
        self.bm25_doc_ids = []

        for _, row in df.iterrows():
            row_data = row.to_dict()
            game_id = str(row_data.get("game_id"))
            self.catalog_by_id[game_id] = row_data

            # Prioritize lexical matching in key textual fields.
            bm25_text = " ".join(
                [
                    str(row_data.get("name", "") or ""),
                    str(row_data.get("summary", "") or ""),
                    str(row_data.get("storyline", "") or ""),
                    str(row_data.get("genres", "") or ""),
                    str(row_data.get("themes", "") or ""),
                    str(row_data.get("platforms", "") or ""),
                ]
            )
            tokenized_corpus.append(_tokenize_text(bm25_text))
            self.bm25_doc_ids.append(game_id)

        if BM25Okapi is not None:
            self.bm25_index = BM25Okapi(tokenized_corpus)
            print(f"[INFO] BM25 index initialized with rank_bm25 for {len(tokenized_corpus)} games.")
        else:
            self.bm25_index = SimpleBM25(tokenized_corpus)
            print(f"[WARN] rank_bm25 not installed. Using SimpleBM25 fallback for {len(tokenized_corpus)} games.")

    def _passes_filters(self, row, min_year=None, platforms=None, multiplayer_mode=None):
        release_year = _safe_int(row.get("release_year"), 0)
        if min_year is not None and release_year < int(min_year):
            return False

        if platforms:
            db_platforms = row.get("platforms", "") or ""
            if not _contains_any(db_platforms, platforms):
                return False

        if multiplayer_mode:
            mode = str(multiplayer_mode).strip().lower()
            has_online = (
                _safe_int(row.get("mp_online_coop"), 0) == 1
                or _safe_int(row.get("mp_max_online_players"), 0) > 0
            )
            has_offline = (
                _safe_int(row.get("mp_offline_coop"), 0) == 1
                or _safe_int(row.get("mp_splitscreen"), 0) == 1
                or _safe_int(row.get("mp_campaign_coop"), 0) == 1
            )

            if mode == "online" and not has_online:
                return False
            if mode == "offline" and not has_offline:
                return False
            if mode == "both" and not (has_online and has_offline):
                return False

        return True

    def _extract_explicit_requirements(self, query):
        query_lower = (query or "").lower()
        return {
            "needs_fishing": _has_term(query_lower, "fishing"),
            "needs_switch": ("nintendo switch" in query_lower) or ("switch" in _tokenize_text(query_lower)),
            "needs_coop": any(phrase in query_lower for phrase in ["co-op", "coop", "co op", "multiplayer"]),
        }

    def _detect_platform_terms(self, query, platforms):
        query_lower = (query or "").lower()
        requested = []

        if "switch" in query_lower or "nintendo switch" in query_lower:
            requested.append(("platform_nintendo_switch", "nintendo switch"))
        if "steam" in query_lower or " pc " in f" {query_lower} ":
            requested.append(("platform_pc", "pc"))
        if "playstation 5" in query_lower or "ps5" in query_lower:
            requested.append(("platform_playstation_5", "playstation 5"))
        if "playstation 4" in query_lower or "ps4" in query_lower:
            requested.append(("platform_playstation_4", "playstation 4"))
        if "xbox one" in query_lower:
            requested.append(("platform_xbox_one", "xbox one"))
        if "xbox series" in query_lower:
            requested.append(("platform_xbox_series_x_s", "xbox series"))

        if platforms:
            for platform in platforms:
                p = str(platform).lower()
                if "switch" in p:
                    requested.append(("platform_nintendo_switch", "nintendo switch"))
                elif "steam" in p or p == "pc":
                    requested.append(("platform_pc", "pc"))
                elif "playstation 5" in p or "ps5" in p:
                    requested.append(("platform_playstation_5", "playstation 5"))
                elif "playstation 4" in p or "ps4" in p:
                    requested.append(("platform_playstation_4", "playstation 4"))
                elif "xbox one" in p:
                    requested.append(("platform_xbox_one", "xbox one"))
                elif "xbox series" in p:
                    requested.append(("platform_xbox_series_x_s", "xbox series"))
                else:
                    requested.append((None, p))

        deduped = []
        seen = set()
        for item in requested:
            if item in seen:
                continue
            seen.add(item)
            deduped.append(item)
        return deduped

    def _get_prefilter_ids(self, query, min_year=None, platforms=None, multiplayer_mode=None):
        req = self._extract_explicit_requirements(query)
        where_parts = []
        params = []

        platform_constraints = self._detect_platform_terms(query, platforms)
        if req["needs_switch"] and ("platform_nintendo_switch", "nintendo switch") not in platform_constraints:
            platform_constraints.append(("platform_nintendo_switch", "nintendo switch"))

        if platform_constraints:
            platform_clauses = []
            for col_name, fallback_term in platform_constraints:
                if col_name and col_name in self.analytics_columns:
                    platform_clauses.append(f"IFNULL({col_name}, 0) = 1")
                else:
                    platform_clauses.append("LOWER(platforms) LIKE ?")
                    params.append(f"%{fallback_term}%")
            where_parts.append("(" + " OR ".join(platform_clauses) + ")")

        if req["needs_coop"] or (
            multiplayer_mode and str(multiplayer_mode).strip().lower() in {"online", "offline", "both"}
        ):
            where_parts.append(
                "("
                "IFNULL(mp_online_coop, 0) = 1 "
                "OR IFNULL(mp_offline_coop, 0) = 1 "
                "OR IFNULL(mp_splitscreen, 0) = 1 "
                "OR IFNULL(mp_campaign_coop, 0) = 1"
                ")"
            )

        if req["needs_fishing"]:
            where_parts.append(
                "("
                "LOWER(genres) LIKE ? "
                "OR LOWER(themes) LIKE ? "
                "OR LOWER(name) LIKE ? "
                "OR LOWER(summary) LIKE ?"
                ")"
            )
            params.extend(["%fishing%", "%fishing%", "%fishing%", "%fishing%"])

        if min_year is not None:
            where_parts.append("IFNULL(release_year, 0) >= ?")
            params.append(int(min_year))

        if multiplayer_mode:
            mode = str(multiplayer_mode).strip().lower()
            if mode == "online":
                where_parts.append("(IFNULL(mp_online_coop, 0) = 1 OR IFNULL(mp_max_online_players, 0) > 0)")
            elif mode == "offline":
                where_parts.append(
                    "(IFNULL(mp_offline_coop, 0) = 1 OR IFNULL(mp_splitscreen, 0) = 1 OR IFNULL(mp_campaign_coop, 0) = 1)"
                )
            elif mode == "both":
                where_parts.append(
                    "("
                    "(IFNULL(mp_online_coop, 0) = 1 OR IFNULL(mp_max_online_players, 0) > 0) "
                    "AND "
                    "(IFNULL(mp_offline_coop, 0) = 1 OR IFNULL(mp_splitscreen, 0) = 1 OR IFNULL(mp_campaign_coop, 0) = 1)"
                    ")"
                )

        if not where_parts:
            return None, req

        sql = "SELECT game_id FROM analytics_ready_games WHERE " + " AND ".join(where_parts)
        conn = sqlite3.connect(self.db_path)
        try:
            rows = pd.read_sql_query(sql, conn, params=params)
        finally:
            conn.close()

        return set(rows["game_id"].astype(str).tolist()), req

    def _detect_concrete_keywords(self, query):
        query_lower = (query or "").lower()
        query_tokens = set(_tokenize_text(query_lower))
        matched = []
        for keyword in CONCRETE_ELEMENTS:
            if keyword in query_tokens or keyword in query_lower:
                matched.append(keyword)
        return matched

    def _detect_management_domain(self, query):
        query_lower = (query or "").lower()
        query_tokens = set(_tokenize_text(query_lower))
        has_management_intent = ("manage" in query_tokens) or ("management" in query_tokens)
        if not has_management_intent:
            return None, []

        for domain, keywords in MANAGEMENT_DOMAINS.items():
            if any(keyword in query_tokens or keyword in query_lower for keyword in keywords):
                return domain, keywords
        return None, []

    def _extract_similarity_seed_title(self, query):
        q = (query or "").strip()
        patterns = [
            r"similar to\s+(.+?)(?:\s+on\s+|\s+for\s+|$)",
            r"like\s+(.+?)(?:\s+on\s+|\s+for\s+|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, q, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip(" .,!?:;\"'")
        return None

    def _normalize_seed_key(self, text):
        parts = _tokenize_text(text)
        normalized = []
        for part in parts:
            if part in ROMAN_NUMERAL_MAP:
                normalized.append(ROMAN_NUMERAL_MAP[part])
                continue

            alnum_digit_match = re.fullmatch(r"([a-z]+)(\d+)", part)
            if alnum_digit_match:
                alpha = alnum_digit_match.group(1)
                digit = alnum_digit_match.group(2)
                normalized.append(alpha + ROMAN_NUMERAL_MAP.get(digit, digit))
                continue

            normalized.append(part)
        return "".join(normalized)

    def _acronym_key(self, text):
        parts = _tokenize_text(text)
        if not parts:
            return ""
        normalized_parts = []
        for part in parts:
            if part in ROMAN_NUMERAL_MAP:
                normalized_parts.append(ROMAN_NUMERAL_MAP[part])
            else:
                normalized_parts.append(part)
        return "".join(part[0] for part in normalized_parts if part)

    def _find_seed_game(self, seed_title):
        if not seed_title:
            return None

        conn = sqlite3.connect(self.db_path)
        try:
            sql = """
            SELECT
                game_id,
                name,
                platforms,
                genres,
                themes,
                developers
            FROM analytics_ready_games
            WHERE LOWER(name) LIKE ?
            LIMIT 1
            """
            df = pd.read_sql_query(sql, conn, params=[f"%{seed_title.lower()}%"])
        finally:
            conn.close()

        if not df.empty:
            return df.iloc[0].to_dict()

        # Fuzzy fallback for compact aliases like "gta5" -> "Grand Theft Auto V".
        conn = sqlite3.connect(self.db_path)
        try:
            all_games = pd.read_sql_query(
                """
                SELECT game_id, name, platforms, genres, themes, developers
                FROM analytics_ready_games
                """,
                conn,
            )
        finally:
            conn.close()

        if all_games.empty:
            return None

        seed_key = self._normalize_seed_key(seed_title)
        for _, row in all_games.iterrows():
            name = str(row.get("name", ""))
            name_key = self._normalize_seed_key(name)
            name_acronym = self._acronym_key(name)
            if seed_key and (seed_key == name_key or seed_key == name_acronym or seed_key in name_key):
                return row.to_dict()
        return None

    def _parse_csv_values(self, raw_value):
        if raw_value is None:
            return []
        text = str(raw_value).strip()
        if not text:
            return []
        return [part.strip() for part in text.split(",") if part.strip()]

    def _get_similar_by_seed_attributes(self, seed_game):
        seed_game_id = str(seed_game.get("game_id"))
        seed_platforms = self._parse_csv_values(seed_game.get("platforms"))
        seed_genres = self._parse_csv_values(seed_game.get("genres"))
        seed_themes = self._parse_csv_values(seed_game.get("themes"))
        seed_developers = self._parse_csv_values(seed_game.get("developers"))

        if not seed_platforms or len(seed_genres) < 2 or len(seed_themes) < 1:
            return None, {}

        platform_clause_parts = []
        platform_params = []
        for p in seed_platforms:
            platform_clause_parts.append("LOWER(platforms) LIKE ?")
            platform_params.append(f"%{p.lower()}%")
        platform_clause = "(" + " OR ".join(platform_clause_parts) + ")"

        genre_case_parts = []
        genre_params = []
        for g in seed_genres:
            genre_case_parts.append("CASE WHEN LOWER(genres) LIKE ? THEN 1 ELSE 0 END")
            genre_params.append(f"%{g.lower()}%")
        genre_match_expr = " + ".join(genre_case_parts)

        theme_case_parts = []
        theme_params = []
        for t in seed_themes:
            theme_case_parts.append("CASE WHEN LOWER(themes) LIKE ? THEN 1 ELSE 0 END")
            theme_params.append(f"%{t.lower()}%")
        theme_match_expr = " + ".join(theme_case_parts)

        sql = f"""
        SELECT
            game_id,
            genres,
            themes,
            developers,
            ({genre_match_expr}) AS genre_match_count,
            ({theme_match_expr}) AS theme_match_count
        FROM analytics_ready_games
        WHERE game_id != ? AND {platform_clause}
        """
        params = genre_params + theme_params + [seed_game_id] + platform_params

        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(sql, conn, params=params)
        finally:
            conn.close()

        if df.empty:
            return set(), {}

        filtered = df[(df["genre_match_count"] >= 2) & (df["theme_match_count"] >= 1)]
        if filtered.empty:
            return set(), {}

        seed_genres_set = {x.lower() for x in seed_genres}
        seed_themes_set = {x.lower() for x in seed_themes}
        seed_developers_set = {x.lower() for x in seed_developers}

        similarity_boosts = {}
        for _, row in filtered.iterrows():
            game_id = str(row["game_id"])
            candidate_genres = {x.lower() for x in self._parse_csv_values(row.get("genres"))}
            candidate_themes = {x.lower() for x in self._parse_csv_values(row.get("themes"))}
            candidate_developers = {x.lower() for x in self._parse_csv_values(row.get("developers"))}

            shared_genres = len(seed_genres_set.intersection(candidate_genres))
            shared_themes = len(seed_themes_set.intersection(candidate_themes))
            same_developer = len(seed_developers_set.intersection(candidate_developers)) > 0

            boost = float(shared_genres) + float(shared_themes) + (2.0 if same_developer else 0.0)
            similarity_boosts[game_id] = boost

        return set(filtered["game_id"].astype(str).tolist()), similarity_boosts

    def _get_management_filter_ids(self, domain_keywords):
        if not domain_keywords:
            return None

        clauses = []
        params = []
        for keyword in domain_keywords:
            clauses.append("LOWER(summary) LIKE ?")
            params.append(f"%{keyword.lower()}%")

        sql = (
            "SELECT game_id FROM analytics_ready_games WHERE "
            + "("
            + " OR ".join(clauses)
            + ")"
        )

        conn = sqlite3.connect(self.db_path)
        try:
            rows = pd.read_sql_query(sql, conn, params=params)
        finally:
            conn.close()

        return set(rows["game_id"].astype(str).tolist())

    def _vector_search(self, query, n_results=100, allowed_ids=None):
        requested = n_results
        if allowed_ids is not None and len(allowed_ids) > 0:
            requested = min(max(n_results * 5, 500), max(len(self.catalog_by_id), 500))
        results = self.collection.query(query_texts=[query], n_results=requested)
        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]
        if not distances:
            distances = [1.0] * len(ids)

        vector_hits = []
        for game_id, distance in zip(ids, distances):
            game_id = str(game_id)
            if allowed_ids is not None and game_id not in allowed_ids:
                continue
            vector_hits.append(
                {
                    "game_id": game_id,
                    "distance": _safe_float(distance, 1.0),
                    "similarity": 1.0 - _safe_float(distance, 1.0),
                    "vector_rank": len(vector_hits) + 1,
                }
            )
            if len(vector_hits) >= n_results:
                break
        return vector_hits

    def _bm25_search(self, query, n_results=100, allowed_ids=None):
        if not self.bm25_index or not self.bm25_doc_ids:
            return []

        query_tokens = _tokenize_text(query)
        if not query_tokens:
            return []

        scores = list(self.bm25_index.get_scores(query_tokens))
        max_score = max(scores) if scores else 0.0
        if max_score <= 0:
            return []

        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        bm25_hits = []
        for idx in ranked_indices:
            score = _safe_float(scores[idx], 0.0)
            if score <= 0:
                continue
            game_id = self.bm25_doc_ids[idx]
            if allowed_ids is not None and game_id not in allowed_ids:
                continue
            bm25_hits.append(
                {
                    "game_id": game_id,
                    "bm25_score": score,
                    "bm25_rank": len(bm25_hits) + 1,
                }
            )
            if len(bm25_hits) >= n_results:
                break
        return bm25_hits

    def _strict_keyword_search(self, query, matched_keywords, n_results=100):
        # Hard lexical filter on title + summary only (vector retrieval fully bypassed).
        filtered = []
        for game_id, row in self.catalog_by_id.items():
            name_text = (row.get("name", "") or "").lower()
            summary_text = (row.get("summary", "") or "").lower()
            if any(keyword in name_text or keyword in summary_text for keyword in matched_keywords):
                filtered.append((game_id, row))

        if not filtered:
            # If hard filter returns nothing, fallback to pure BM25 retrieval.
            bm25_hits = self._bm25_search(query=query, n_results=n_results)
            return [
                {
                    "game_id": hit["game_id"],
                    "hybrid_score": _safe_float(hit.get("bm25_score", 0.0), 0.0),
                    "distance": 1.0,
                    "vector_similarity": 0.0,
                    "bm25_score_raw": _safe_float(hit.get("bm25_score", 0.0), 0.0),
                    "keyword_boost_applied": False,
                }
                for hit in bm25_hits
            ]

        query_tokens = _tokenize_text(query)
        strict_hits = []
        for game_id, row in filtered:
            name_text = (row.get("name", "") or "").lower()
            summary_text = (row.get("summary", "") or "").lower()
            keyword_match_count = sum(1 for token in query_tokens if token in name_text or token in summary_text)

            strict_hits.append(
                {
                    "game_id": game_id,
                    "hybrid_score": float(keyword_match_count + 1.0),
                    "distance": 1.0,
                    "vector_similarity": 0.0,
                    "bm25_score_raw": float(keyword_match_count),
                    "keyword_boost_applied": True,
                }
            )

        strict_hits.sort(key=lambda x: _safe_float(x.get("hybrid_score", 0.0), 0.0), reverse=True)
        return strict_hits[:n_results]

    def _hybrid_fuse(self, query, vector_hits, bm25_hits, rrf_k=60, vector_weight=0.8, bm25_weight=0.2):
        merged = {}
        vector_rank_map = {h["game_id"]: h["vector_rank"] for h in vector_hits}
        bm25_rank_map = {h["game_id"]: h["bm25_rank"] for h in bm25_hits}
        vector_sim_map = {h["game_id"]: h.get("similarity", 0.0) for h in vector_hits}
        vector_distance_map = {h["game_id"]: h.get("distance", 1.0) for h in vector_hits}
        bm25_raw_map = {h["game_id"]: h.get("bm25_score", 0.0) for h in bm25_hits}
        query_tokens = _tokenize_text(query)

        for hit in vector_hits:
            game_id = hit["game_id"]
            merged[game_id] = {
                "game_id": game_id,
                "vector_similarity": hit.get("similarity", 0.0),
                "distance": hit.get("distance", 1.0),
                "bm25_score_raw": 0.0,
            }

        for hit in bm25_hits:
            game_id = hit["game_id"]
            if game_id not in merged:
                merged[game_id] = {
                    "game_id": game_id,
                    "vector_similarity": 0.0,
                    "distance": 1.0,
                    "bm25_score_raw": hit.get("bm25_score", 0.0),
                }
            else:
                merged[game_id]["bm25_score_raw"] = hit.get("bm25_score", 0.0)

        fused = []
        for game_id, item in merged.items():
            rank_vector = vector_rank_map.get(game_id)
            rank_bm25 = bm25_rank_map.get(game_id)
            vector_rrf = (vector_weight / (rrf_k + rank_vector)) if rank_vector is not None else 0.0
            bm25_rrf = (bm25_weight / (rrf_k + rank_bm25)) if rank_bm25 is not None else 0.0
            hybrid_score = vector_rrf + bm25_rrf

            row = self.catalog_by_id.get(game_id, {})
            name_text = (row.get("name", "") or "").lower()
            summary_text = (row.get("summary", "") or "").lower()
            if query_tokens and any(token in name_text or token in summary_text for token in query_tokens):
                hybrid_score *= 2.0
                item["keyword_boost_applied"] = True
            else:
                item["keyword_boost_applied"] = False

            hybrid_distance = 1.0 - min(1.0, max(0.0, hybrid_score * 10.0))
            item["hybrid_score"] = hybrid_score
            item["vector_rrf_score"] = vector_rrf
            item["bm25_rrf_score"] = bm25_rrf
            item["vector_similarity"] = vector_sim_map.get(game_id, 0.0)
            item["bm25_score_raw"] = bm25_raw_map.get(game_id, 0.0)
            item["distance"] = min(_safe_float(vector_distance_map.get(game_id, 1.0), 1.0), hybrid_distance)
            fused.append(item)

        fused.sort(key=lambda x: _safe_float(x.get("hybrid_score", 0.0), 0.0), reverse=True)
        return fused

    def _log_top_hybrid_scores(self, candidates, top_k=5):
        for i, row in enumerate(candidates[:top_k], start=1):
            print(
                f"[HybridDebug] {i}. {row.get('name', 'Unknown')} | "
                f"Vector Score={_safe_float(row.get('vector_similarity', 0.0), 0.0):.4f} | "
                f"BM25 Score={_safe_float(row.get('bm25_score_raw', 0.0), 0.0):.4f} | "
                f"Metadata Boost={_safe_float(row.get('metadata_boost', 0.0), 0.0):.4f} | "
                f"Hybrid RRF={_safe_float(row.get('hybrid_score', 0.0), 0.0):.6f} | "
                f"KeywordBoost={row.get('keyword_boost_applied', False)}"
            )

    def _format_storyline_output(self, summary, storyline, max_len=1000):
        summary_clean = (summary or "").strip()
        storyline_clean = (storyline or "").strip()
        combined = " ".join([part for part in [summary_clean, storyline_clean] if part]).strip()
        if len(combined) > max_len:
            return combined[:max_len].strip() + "..."
        return combined

    def _format_text_output(self, text, max_len=1000):
        cleaned = (text or "").strip()
        if len(cleaned) > max_len:
            return cleaned[:max_len].strip() + "..."
        return cleaned

    def search(
        self,
        query,
        top_n=5,
        min_year=None,
        platforms=None,
        multiplayer_mode=None,
        vector_k=100,
        bm25_k=100,
        debug_scores=False,
    ):
        allowed_ids, requirements = self._get_prefilter_ids(
            query=query,
            min_year=min_year,
            platforms=platforms,
            multiplayer_mode=multiplayer_mode,
        )
        seed_similarity_boosts = {}

        seed_title = self._extract_similarity_seed_title(query)
        if seed_title:
            seed_game = self._find_seed_game(seed_title)
            if seed_game:
                seed_ids, seed_similarity_boosts = self._get_similar_by_seed_attributes(seed_game)
                if seed_ids is not None:
                    seed_name = seed_game.get("name", seed_title)
                    seed_attrs = [
                        f"platforms={seed_game.get('platforms', '')}",
                        f"genres={seed_game.get('genres', '')}",
                        f"themes={seed_game.get('themes', '')}",
                        f"developers={seed_game.get('developers', '')}",
                    ]
                    print(
                        f"Retrieving games similar to {seed_name} using attributes: "
                        + "; ".join(seed_attrs)
                    )
                    if allowed_ids is None:
                        allowed_ids = seed_ids
                    else:
                        allowed_ids = allowed_ids.intersection(seed_ids)
            else:
                print(f"[INFO] Seed game '{seed_title}' not found. Falling back to Hybrid Vector+BM25.")

        management_domain, domain_keywords = self._detect_management_domain(query)
        if management_domain:
            print(f"Management Filter Active: {management_domain}")
            management_ids = self._get_management_filter_ids(domain_keywords)
            if not management_ids:
                return []
            if allowed_ids is None:
                allowed_ids = management_ids
            else:
                allowed_ids = allowed_ids.intersection(management_ids)
            if not allowed_ids:
                return []

        if allowed_ids is not None and not allowed_ids:
            if requirements.get("needs_fishing"):
                print("No matching fishing games found with these constraints")
            return []
        if allowed_ids is not None and len(allowed_ids) < 5:
            print("Constraint Over-constrained")
            return []

        print("Retrieval Mode: Semantic Theme")
        vector_hits = self._vector_search(query=query, n_results=vector_k, allowed_ids=allowed_ids)
        bm25_hits = self._bm25_search(query=query, n_results=bm25_k, allowed_ids=allowed_ids)
        fused_hits = self._hybrid_fuse(
            query=query,
            vector_hits=vector_hits,
            bm25_hits=bm25_hits,
            rrf_k=60,
            vector_weight=0.9,
            bm25_weight=0.1,
        )

        candidates = []
        for hit in fused_hits:
            game_id = hit["game_id"]
            row = self.catalog_by_id.get(game_id)
            if not row:
                continue
            if not self._passes_filters(row, min_year=min_year, platforms=platforms, multiplayer_mode=multiplayer_mode):
                continue

            summary = self._format_text_output(row.get("summary"), max_len=1000)
            storyline = self._format_text_output(row.get("storyline"), max_len=1000)
            combined_story = self._format_storyline_output(summary, storyline, max_len=1000)

            candidates.append(
                {
                    "name": row.get("name", "Not Listed"),
                    "release_year": _safe_int(row.get("release_year"), 0),
                    "platforms": row.get("platforms", "Not Listed"),
                    "summary": summary,
                    "storyline": storyline,
                    "storyline_summary": combined_story,
                    "total_rating": _safe_float(row.get("total_rating"), 0.0),
                    "distance": _safe_float(hit.get("distance"), 1.0),
                    "metadata_boost": _safe_float(seed_similarity_boosts.get(game_id), 0.0),
                    "hybrid_score": _safe_float(hit.get("hybrid_score"), 0.0),
                    "vector_similarity": _safe_float(hit.get("vector_similarity"), 0.0),
                    "bm25_score_raw": _safe_float(hit.get("bm25_score_raw"), 0.0),
                    "keyword_boost_applied": bool(hit.get("keyword_boost_applied", False)),
                    "genres": row.get("genres", ""),
                    "themes": row.get("themes", ""),
                    "developers": row.get("developers", ""),
                    "publishers": row.get("publishers", ""),
                    "category_id": _safe_int(row.get("category_id"), 0),
                    "mp_campaign_coop": _safe_int(row.get("mp_campaign_coop"), 0),
                    "mp_splitscreen": _safe_int(row.get("mp_splitscreen"), 0),
                    "mp_online_coop": _safe_int(row.get("mp_online_coop"), 0),
                    "mp_offline_coop": _safe_int(row.get("mp_offline_coop"), 0),
                    "mp_max_online_players": _safe_int(row.get("mp_max_online_players"), 0),
                }
            )

        if requirements.get("needs_fishing"):
            candidates = [
                c
                for c in candidates
                if (
                    "fishing" in (c.get("genres", "") or "").lower()
                    or "fishing" in (c.get("themes", "") or "").lower()
                    or "fishing" in (c.get("name", "") or "").lower()
                    or "fishing" in (c.get("summary", "") or "").lower()
                )
            ]
            if not candidates:
                print("No matching fishing games found with these constraints")
                return []

        if debug_scores:
            self._log_top_hybrid_scores(candidates, top_k=5)

        ranked = rank_results(candidates, model_bundle=self.model_bundle)
        return ranked[:top_n]


if __name__ == "__main__":
    agent = RAGAgent()
    print("Agent initialized. Testing hybrid query...")

    test_query = "i want a free-roam game on PC."
    results = agent.search(
        test_query,
        top_n=5,
        min_year=None,
        platforms=None,
        multiplayer_mode=None,
        debug_scores=True,
    )

    print(f"\nResults for: '{test_query}'")
    for i, match in enumerate(results, start=1):
        print(f"\n{i}. Name: {match.get('name', 'Not Listed')}")
        print(f"   Release Year: {match.get('release_year', 'Unknown')}")
        print(f"   Predicted Rating: {match.get('predicted_quality_score', 0.0):.2f}")
        print(f"   Platforms: {match.get('platforms', 'Not Listed')}")
        print(f"   Summary: {(match.get('summary', '') or '').strip()}")
