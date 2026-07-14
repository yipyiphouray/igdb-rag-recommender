import math
import re
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import chromadb
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


def _contains_phrase(text, phrase):
    return f" {phrase} " in f" {(text or '').lower()} "


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

TWO_D_REGEX = re.compile(r"\b2(?:\.5)?d\b", flags=re.IGNORECASE)
THREE_D_REGEX = re.compile(r"\b3d\b", flags=re.IGNORECASE)


@dataclass
class UserInteraction:
    user_id: str
    game_id: str
    game_name: str
    time_played: float


def get_alpha(games_played):
    if games_played < 3:
        return 0.1
    elif games_played <= 10:
        return 0.4
    else:
        return 0.75


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


def rank_results(
    candidates,
    graphics_preference=None,
):
    if not candidates:
        return []

    request_2d = bool((graphics_preference or {}).get("request_2d", False))
    avoid_3d = bool((graphics_preference or {}).get("avoid_3d", False))
    two_d_boost = _safe_float((graphics_preference or {}).get("two_d_boost", 1.5), 1.5)
    three_d_penalty = _safe_float((graphics_preference or {}).get("three_d_penalty", 0.1), 0.1)

    # Step A: relevance score is retrieval relevance + metadata similarity boost.
    for candidate in candidates:
        candidate["total_rating"] = _safe_float(candidate.get("total_rating", 0.0), 0.0)
        metadata_boost = _safe_float(candidate.get("metadata_boost", 0.0), 0.0)
        hybrid_rrf = _safe_float(candidate.get("hybrid_score", 0.0), 0.0)
        candidate["relevance_score"] = metadata_boost + hybrid_rrf
        candidate["constraint_multiplier"] = 1.0
        candidate["penalty_applied"] = False
        candidate["boost_applied"] = False

        multiplier = 1.0
        if (request_2d or avoid_3d) and bool(candidate.get("is_3d_detected", False)):
            multiplier *= three_d_penalty
            candidate["penalty_applied"] = True
        if request_2d and bool(candidate.get("is_2d_detected", False)):
            multiplier *= two_d_boost
            candidate["boost_applied"] = True

        candidate["constraint_multiplier"] = multiplier
        candidate["relevance_score"] *= multiplier
        candidate["primary_rank_score"] = _safe_float(candidate.get("relevance_score", 0.0), 0.0)

    # Step B: rank by semantic + lexical relevance only (RAG is independent from recommendation scoring).
    return sorted(
        candidates,
        key=lambda x: (
            -_safe_float(x.get("primary_rank_score", 0.0), 0.0),
            _safe_float(x.get("distance", 1.0), 1.0),
        ),
    )


class RAGAgent:
    def __init__(self):
        self.root_dir = Path(__file__).resolve().parent.parent
        self.db_path = self.root_dir / "data" / "database" / "igdb_games.db"

        self.client = chromadb.PersistentClient(path=str(self.root_dir / "data" / "vector_store"))
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_collection(
            name="igdb_game_profiles",
            embedding_function=self.embedding_fn,
        )

        self.analytics_columns = self._get_analytics_columns()
        self.catalog_by_id = {}
        self.bm25_doc_ids = []
        self.bm25_index = None
        self.dimension_keyword_sets = self._load_dimension_keyword_sets()
        self._build_bm25_index_from_analytics_view()

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
            playtime_normally,
            genres,
            themes,
            developers,
            publishers,
            rag_text_profile,
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
                    str(row_data.get("rag_text_profile", "") or ""),
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

    def _load_dimension_keyword_sets(self):
        sql = """
        SELECT
            gk.game_id,
            LOWER(k.name) AS keyword_name
        FROM game_keywords gk
        JOIN keywords k ON gk.keyword_id = k.keyword_id
        WHERE LOWER(k.name) IN ('2d', '2.5d', '3d')
        """
        conn = sqlite3.connect(self.db_path)
        try:
            rows = pd.read_sql_query(sql, conn)
        finally:
            conn.close()

        two_d_ids = set()
        three_d_ids = set()
        for _, row in rows.iterrows():
            game_id = str(row.get("game_id"))
            keyword_name = str(row.get("keyword_name", "") or "")
            if keyword_name in {"2d", "2.5d"}:
                two_d_ids.add(game_id)
            if keyword_name == "3d":
                three_d_ids.add(game_id)

        return {"2d": two_d_ids, "3d": three_d_ids}

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

    def _extract_hard_constraints(self, query):
        q = (query or "").lower()
        two_d_only_patterns = [
            r"\b2d\s+only\b",
            r"\bonly\s+2d\b",
            r"\bstrictly\s+2d\b",
            r"\bpure\s+2d\b",
        ]
        no_three_d_patterns = [
            r"\bno\s+3d\b",
            r"\bwithout\s+3d\b",
            r"\bnon[-\s]?3d\b",
            r"\bavoid\s+3d\b",
            r"\bexclude\s+3d\b",
            r"\bnot\s+3d\b",
            r"\bno\s+3d\s+graphics\b",
        ]
        require_2d = any(re.search(p, q) for p in two_d_only_patterns)
        exclude_3d = require_2d or any(re.search(p, q) for p in no_three_d_patterns)

        # Handle compact phrasing such as "2d game, no 3d graphics please".
        if _contains_phrase(q, "2d game") and _contains_phrase(q, "no 3d"):
            require_2d = True
            exclude_3d = True

        return {
            "require_2d": require_2d,
            "exclude_3d": exclude_3d,
        }

    def _parse_year_constraint(self, query):
        q = (query or "").lower()

        # Explicit year constraints in the query always take priority.
        explicit_year_match = re.search(r"\b(19\d{2}|20\d{2}|21\d{2})\b", q)
        if explicit_year_match:
            return int(explicit_year_match.group(1))

        current_year = datetime.now().year

        # "latest" should be stricter than generic "new/recent".
        if re.search(r"\blatest\b", q):
            return current_year
        if re.search(r"\b(new|recent)\b", q):
            return current_year - 1

        return None

    def _extract_graphics_preference(self, query, hard_constraints=None):
        q = (query or "").lower()
        hard_constraints = hard_constraints or {}
        request_2d = bool(TWO_D_REGEX.search(q)) or bool(hard_constraints.get("require_2d"))
        avoid_3d = bool(hard_constraints.get("exclude_3d"))
        return {
            "request_2d": request_2d,
            "avoid_3d": avoid_3d,
            "two_d_boost": 1.5,
            "three_d_penalty": 0.1,
        }

    def _get_user_personalization_profile(self, user_id):
        normalized_user_id = str(user_id).strip() if user_id is not None else ""
        if not normalized_user_id:
            return 0, 0.0, {}, [], 1.0, "Balanced"

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='user_interactions'"
            )
            if cursor.fetchone() is None:
                print("[INFO] user_interactions table not found. Personalization disabled.")
                return 0, 0.0, {}, [], 1.0, "Balanced"

            games_played_sql = """
            SELECT COUNT(DISTINCT game_id)
            FROM user_interactions
            WHERE user_id = ?
            """
            cursor.execute(games_played_sql, [normalized_user_id])
            games_played = _safe_int((cursor.fetchone() or [0])[0], 0)
            if games_played <= 0:
                return 0, 0.0, {}, [], 1.0, "Balanced"

            schema_rows = pd.read_sql_query("PRAGMA table_info(user_interactions)", conn)
            available_columns = set(schema_rows["name"].astype(str).tolist()) if not schema_rows.empty else set()
            has_game_name = "game_name" in available_columns
            has_time_played = "time_played" in available_columns

            game_name_select = "COALESCE(MAX(game_name), '') AS game_name" if has_game_name else "'' AS game_name"
            time_played_expr = (
                "SUM(COALESCE(time_played, 0.0))"
                if has_time_played
                else "COUNT(*)"
            )

            interactions_sql = f"""
            SELECT
                CAST(user_id AS TEXT) AS user_id,
                CAST(game_id AS TEXT) AS game_id,
                {game_name_select},
                {time_played_expr} AS time_played
            FROM user_interactions
            WHERE user_id = ? AND game_id IS NOT NULL
            GROUP BY user_id, game_id
            """
            cursor.execute(interactions_sql, [normalized_user_id])
            raw_interactions = cursor.fetchall()

            interactions = []
            for row in raw_interactions:
                interactions.append(
                    UserInteraction(
                        user_id=str(row[0] or normalized_user_id),
                        game_id=str(row[1] or ""),
                        game_name=str(row[2] or ""),
                        time_played=_safe_float(row[3], 0.0),
                    )
                )

            if not interactions:
                return games_played, 0.0, {}, [], 1.0, "Balanced"

            max_time_played = max([_safe_float(i.time_played, 0.0) for i in interactions] + [1.0])
            preference_scores = {
                interaction.game_id: (_safe_float(interaction.time_played, 0.0) / max_time_played) * 100.0
                for interaction in interactions
                if interaction.game_id
            }

            user_pace_signature = 1.0
            pace_profile_label = "Balanced"
            if has_time_played:
                pace_sql = """
                SELECT
                    ui.time_played,
                    gtb.normally
                FROM user_interactions ui
                JOIN game_time_to_beats gtb ON CAST(ui.game_id AS TEXT) = CAST(gtb.game_id AS TEXT)
                WHERE ui.user_id = ?
                  AND ui.time_played IS NOT NULL
                  AND COALESCE(ui.time_played, 0) > 0
                  AND gtb.normally IS NOT NULL
                  AND COALESCE(gtb.normally, 0) > 0
                """
                pace_rows = pd.read_sql_query(pace_sql, conn, params=[normalized_user_id])
                if not pace_rows.empty:
                    pace_rows["time_played"] = pd.to_numeric(pace_rows["time_played"], errors="coerce")
                    pace_rows["normally"] = pd.to_numeric(pace_rows["normally"], errors="coerce")
                    pace_rows = pace_rows.dropna(subset=["time_played", "normally"])
                    pace_rows = pace_rows[(pace_rows["time_played"] > 0) & (pace_rows["normally"] > 0)]
                    if not pace_rows.empty:
                        pace_rows["rpi"] = pace_rows["time_played"] / pace_rows["normally"]
                        user_pace_signature = _safe_float(pace_rows["rpi"].median(), 1.0)

            if user_pace_signature > 1.2:
                pace_profile_label = "Deep/Extended"
            elif user_pace_signature < 0.8:
                pace_profile_label = "Snackable/Fast"

            alpha = get_alpha(games_played)
            return games_played, alpha, preference_scores, interactions, user_pace_signature, pace_profile_label
        except Exception as exc:
            print(f"[WARN] Could not load personalization profile for user_id={normalized_user_id}: {exc}")
            return 0, 0.0, {}, [], 1.0, "Balanced"
        finally:
            conn.close()

    def _detect_dimension_tags(self, game_id, row):
        two_d_keywords = self.dimension_keyword_sets.get("2d", set())
        three_d_keywords = self.dimension_keyword_sets.get("3d", set())
        has_2d_keyword = game_id in two_d_keywords
        has_3d_keyword = game_id in three_d_keywords
        haystack = " ".join(
            [
                str(row.get("name", "") or ""),
                str(row.get("summary", "") or ""),
                str(row.get("storyline", "") or ""),
                str(row.get("genres", "") or ""),
                str(row.get("themes", "") or ""),
                str(row.get("rag_text_profile", "") or ""),
            ]
        )
        has_2d_regex = bool(TWO_D_REGEX.search(haystack))
        has_3d_regex = bool(THREE_D_REGEX.search(haystack))
        return {
            "is_2d_detected": has_2d_keyword or has_2d_regex,
            "is_3d_detected": has_3d_keyword or has_3d_regex,
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
        min_year_value = None

        platform_constraints = self._detect_platform_terms(query, platforms)
        if req["needs_switch"] and ("platform_nintendo_switch", "nintendo switch") not in platform_constraints:
            platform_constraints.append(("platform_nintendo_switch", "nintendo switch"))

        platform_clauses = []
        platform_params = []
        if platform_constraints:
            for col_name, fallback_term in platform_constraints:
                if col_name and col_name in self.analytics_columns:
                    platform_clauses.append(f"IFNULL({col_name}, 0) = 1")
                else:
                    platform_clauses.append("LOWER(platforms) LIKE ?")
                    like_value = f"%{fallback_term}%"
                    params.append(like_value)
                    platform_params.append(like_value)
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
            min_year_value = _safe_int(min_year, 0)
            if min_year_value > 0:
                where_parts.append("IFNULL(release_year, 0) >= ?")
                params.append(min_year_value)

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
            cursor = conn.cursor()

            # Baseline table population checks.
            games_table_count = None
            games_count_sql = "SELECT COUNT(*) FROM games WHERE 1=1"
            try:
                cursor.execute(games_count_sql)
                games_table_count = _safe_int((cursor.fetchone() or [0])[0], 0)
                print(f"[PrefilterSQL] Baseline Count SQL: {games_count_sql}")
                print(f"[PrefilterSQL] Baseline Count Result (games): {games_table_count}")
            except Exception as exc:
                print(f"[PrefilterSQL] Baseline Count SQL Failed on games: {games_count_sql} | error={exc}")

            analytics_count_sql = "SELECT COUNT(*) FROM analytics_ready_games WHERE 1=1"
            cursor.execute(analytics_count_sql)
            analytics_total_count = _safe_int((cursor.fetchone() or [0])[0], 0)
            print(f"[PrefilterSQL] Baseline Count SQL: {analytics_count_sql}")
            print(f"[PrefilterSQL] Baseline Count Result (analytics_ready_games): {analytics_total_count}")

            # Count rows matching platform-only constraints.
            if platform_clauses:
                platform_only_sql = "SELECT COUNT(*) FROM analytics_ready_games WHERE " + "(" + " OR ".join(platform_clauses) + ")"
                print(f"[PrefilterSQL] Platform-Only Count SQL: {platform_only_sql}")
                print(f"[PrefilterSQL] Platform-Only Params: {platform_params}")
                cursor.execute(platform_only_sql, platform_params)
                platform_only_count = _safe_int((cursor.fetchone() or [0])[0], 0)
                print(f"[PrefilterSQL] Platform-Only Count Result: {platform_only_count}")

            # Count rows matching year-only constraints.
            if min_year_value and min_year_value > 0:
                year_only_sql = "SELECT COUNT(*) FROM analytics_ready_games WHERE IFNULL(release_year, 0) >= ?"
                year_only_params = [min_year_value]
                print(f"[PrefilterSQL] Year-Only Count SQL: {year_only_sql}")
                print(f"[PrefilterSQL] Year-Only Params: {year_only_params}")
                cursor.execute(year_only_sql, year_only_params)
                year_only_count = _safe_int((cursor.fetchone() or [0])[0], 0)
                print(f"[PrefilterSQL] Year-Only Count Result: {year_only_count}")

            # Platform value inspection for PC-style entries.
            platform_profile_sql = """
            SELECT
                COALESCE(platforms, '') AS platforms_value,
                COUNT(*) AS row_count
            FROM analytics_ready_games
            WHERE LOWER(COALESCE(platforms, '')) LIKE '%pc%'
               OR LOWER(COALESCE(platforms, '')) LIKE '%personal computer%'
               OR LOWER(COALESCE(platforms, '')) LIKE '%steam%'
            GROUP BY COALESCE(platforms, '')
            ORDER BY row_count DESC
            LIMIT 15
            """
            print("[PrefilterSQL] Platform Profile SQL:")
            print(platform_profile_sql.strip())
            cursor.execute(platform_profile_sql)
            platform_profile_rows = cursor.fetchall()
            if platform_profile_rows:
                print("[PrefilterSQL] Platform Profile Top Values (platforms, count):")
                for platform_value, row_count in platform_profile_rows:
                    print(f"  - {platform_value} | {row_count}")
            else:
                print("[PrefilterSQL] Platform Profile Top Values: none")

            params_dict = {f"p{i + 1}": value for i, value in enumerate(params)}
            print(f"[PrefilterSQL] Final Query SQL: {sql}")
            print(f"[PrefilterSQL] Final Query Params List: {params}")
            print(f"[PrefilterSQL] Final Query Params Dict: {params_dict}")
            cursor.execute(sql, params)
            result_rows = cursor.fetchall()
        finally:
            conn.close()

        return {str(row[0]) for row in result_rows if row and row[0] is not None}, req

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

    def _find_seed_game_by_id(self, seed_game_id):
        if seed_game_id is None:
            return None

        normalized_seed_id = str(seed_game_id).strip()
        if not normalized_seed_id:
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
            WHERE CAST(game_id AS TEXT) = ?
            LIMIT 1
            """
            df = pd.read_sql_query(sql, conn, params=[normalized_seed_id])
        finally:
            conn.close()

        if df.empty:
            return None
        return df.iloc[0].to_dict()

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

        if not seed_genres and not seed_themes:
            return set(), {}

        sql = """
        SELECT
            game_id,
            platforms,
            genres,
            themes,
            developers
        FROM analytics_ready_games
        WHERE CAST(game_id AS TEXT) != ?
        """
        params = [seed_game_id]

        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(sql, conn, params=params)
        finally:
            conn.close()

        if df.empty:
            return set(), {}

        seed_platforms_set = {x.lower() for x in seed_platforms}
        seed_genres_set = {x.lower() for x in seed_genres}
        seed_themes_set = {x.lower() for x in seed_themes}
        seed_developers_set = {x.lower() for x in seed_developers}

        similar_ids = set()
        similarity_boosts = {}
        for _, row in df.iterrows():
            game_id = str(row["game_id"])
            candidate_platforms = {x.lower() for x in self._parse_csv_values(row.get("platforms"))}
            candidate_genres = {x.lower() for x in self._parse_csv_values(row.get("genres"))}
            candidate_themes = {x.lower() for x in self._parse_csv_values(row.get("themes"))}
            candidate_developers = {x.lower() for x in self._parse_csv_values(row.get("developers"))}

            if seed_platforms_set and len(seed_platforms_set.intersection(candidate_platforms)) == 0:
                continue

            shared_genres = len(seed_genres_set.intersection(candidate_genres))
            shared_themes = len(seed_themes_set.intersection(candidate_themes))
            if seed_genres_set and shared_genres == 0:
                continue
            if seed_themes_set and shared_themes == 0:
                continue

            same_developer = len(seed_developers_set.intersection(candidate_developers)) > 0

            # Explicit developer overlap bonus to elevate seed-studio continuity in relevance scoring.
            developer_overlap_bonus = 3.0 if same_developer else 0.0
            boost = float(shared_genres) + float(shared_themes) + developer_overlap_bonus
            similar_ids.add(game_id)
            similarity_boosts[game_id] = boost

        return similar_ids, similarity_boosts

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

    def _hybrid_fuse(
        self,
        query,
        vector_hits,
        bm25_hits,
        rrf_k=60,
        vector_weight=0.8,
        bm25_weight=0.2,
    ):
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
                f"KeywordBoost={row.get('keyword_boost_applied', False)} | "
                f"PenaltyApplied={row.get('penalty_applied', False)}"
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
        user_id=None,
        seed_game_id=None,
    ):
        hard_constraints = self._extract_hard_constraints(query)
        graphics_preference = self._extract_graphics_preference(query, hard_constraints)
        parsed_min_year = self._parse_year_constraint(query)
        effective_min_year = min_year if min_year is not None else parsed_min_year
        seed_filter_ids = None
        management_filter_ids = None

        print(
            "[Trace] search:start | "
            f"query='{query}' | top_n={top_n} | min_year_input={min_year} | parsed_min_year={parsed_min_year} | "
            f"effective_min_year={effective_min_year} | platforms={platforms} | multiplayer_mode={multiplayer_mode} | "
            f"user_id={user_id} | seed_game_id={seed_game_id}"
        )

        allowed_ids, requirements = self._get_prefilter_ids(
            query=query,
            min_year=effective_min_year,
            platforms=platforms,
            multiplayer_mode=multiplayer_mode,
        )
        allowed_count = "ALL" if allowed_ids is None else len(allowed_ids)
        print(f"[Trace] prefilter:first_pass | allowed_ids={allowed_count}")

        seed_similarity_boosts = {}
        seed_game = None
        if seed_game_id is not None:
            seed_game = self._find_seed_game_by_id(seed_game_id)
            if not seed_game:
                print(f"[Trace] search:return [] | reason=seed_game_id_not_found | seed_game_id={seed_game_id}")
                return []
            seed_filter_ids, seed_similarity_boosts = self._get_similar_by_seed_attributes(seed_game)
            if not seed_filter_ids:
                print(
                    "[Trace] search:return [] | reason=seed_game_similarity_empty | "
                    f"seed_game_id={seed_game_id}"
                )
                return []

            seed_name = seed_game.get("name", str(seed_game_id))
            print(
                f"Seed Game Filter Active (ID={seed_game_id}): {seed_name} | "
                f"similar_candidates={len(seed_filter_ids)}"
            )
            if allowed_ids is None:
                allowed_ids = seed_filter_ids
            else:
                allowed_ids = allowed_ids.intersection(seed_filter_ids)
        else:
            seed_title = self._extract_similarity_seed_title(query)
            if seed_title:
                seed_game = self._find_seed_game(seed_title)
                if seed_game:
                    seed_filter_ids, seed_similarity_boosts = self._get_similar_by_seed_attributes(seed_game)
                    if seed_filter_ids is not None:
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
                            allowed_ids = seed_filter_ids
                        else:
                            allowed_ids = allowed_ids.intersection(seed_filter_ids)
                else:
                    print(f"[INFO] Seed game '{seed_title}' not found. Falling back to Hybrid Vector+BM25.")

        management_domain, domain_keywords = self._detect_management_domain(query)
        if management_domain:
            print(f"Management Filter Active: {management_domain}")
            management_filter_ids = self._get_management_filter_ids(domain_keywords)
            if not management_filter_ids:
                print("[Trace] search:return [] | reason=management_filter_empty")
                return []
            if allowed_ids is None:
                allowed_ids = management_filter_ids
            else:
                allowed_ids = allowed_ids.intersection(management_filter_ids)
            if not allowed_ids:
                print("[Trace] search:return [] | reason=management_intersection_empty")
                return []

        if allowed_ids is not None and not allowed_ids:
            if requirements.get("needs_fishing"):
                print("No matching fishing games found with these constraints")
            print("[Trace] search:return [] | reason=prefilter_empty")
            return []
        if allowed_ids is not None and len(allowed_ids) < 5 and effective_min_year is not None:
            print("[INFO] Constraint too tight, relaxing year filter...")
            relaxed_allowed_ids, requirements = self._get_prefilter_ids(
                query=query,
                min_year=None,
                platforms=platforms,
                multiplayer_mode=multiplayer_mode,
            )
            effective_min_year = None

            if seed_filter_ids is not None:
                if relaxed_allowed_ids is None:
                    relaxed_allowed_ids = set(seed_filter_ids)
                else:
                    relaxed_allowed_ids = relaxed_allowed_ids.intersection(seed_filter_ids)

            if management_filter_ids is not None:
                if relaxed_allowed_ids is None:
                    relaxed_allowed_ids = set(management_filter_ids)
                else:
                    relaxed_allowed_ids = relaxed_allowed_ids.intersection(management_filter_ids)

            allowed_ids = relaxed_allowed_ids
            relaxed_allowed_count = "ALL" if allowed_ids is None else len(allowed_ids)
            print(f"[Trace] prefilter:relaxed_pass | allowed_ids={relaxed_allowed_count}")
            if allowed_ids is not None and not allowed_ids:
                print("[Trace] search:return [] | reason=relaxed_prefilter_empty")
                return []

        print("Retrieval Mode: Semantic Theme")
        allowed_count_for_retrieval = "ALL" if allowed_ids is None else len(allowed_ids)
        print(f"[Trace] retrieval:starting | allowed_ids={allowed_count_for_retrieval}")
        vector_hits = self._vector_search(query=query, n_results=vector_k, allowed_ids=allowed_ids)
        bm25_hits = self._bm25_search(query=query, n_results=bm25_k, allowed_ids=allowed_ids)
        print(
            "[Trace] retrieval:fetched | "
            f"vector_hits={len(vector_hits)} | bm25_hits={len(bm25_hits)} | allowed_ids={allowed_count_for_retrieval}"
        )
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
            if not self._passes_filters(
                row,
                min_year=effective_min_year,
                platforms=platforms,
                multiplayer_mode=multiplayer_mode,
            ):
                continue

            summary = self._format_text_output(row.get("summary"), max_len=1000)
            storyline = self._format_text_output(row.get("storyline"), max_len=1000)
            combined_story = self._format_storyline_output(summary, storyline, max_len=1000)
            dimension_tags = self._detect_dimension_tags(game_id, row)

            candidates.append(
                {
                    "game_id": game_id,
                    "name": row.get("name", "Not Listed"),
                    "release_year": _safe_int(row.get("release_year"), 0),
                    "platforms": row.get("platforms", "Not Listed"),
                    "summary": summary,
                    "storyline": storyline,
                    "storyline_summary": combined_story,
                    "total_rating": _safe_float(row.get("total_rating"), 0.0),
                    "playtime_normally": _safe_float(row.get("playtime_normally"), 0.0),
                    "distance": _safe_float(hit.get("distance"), 1.0),
                    "metadata_boost": _safe_float(seed_similarity_boosts.get(game_id), 0.0),
                    "hybrid_score": _safe_float(hit.get("hybrid_score"), 0.0),
                    "vector_similarity": _safe_float(hit.get("vector_similarity"), 0.0),
                    "bm25_score_raw": _safe_float(hit.get("bm25_score_raw"), 0.0),
                    "keyword_boost_applied": bool(hit.get("keyword_boost_applied", False)),
                    "is_2d_detected": bool(dimension_tags.get("is_2d_detected", False)),
                    "is_3d_detected": bool(dimension_tags.get("is_3d_detected", False)),
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
                print("[Trace] search:return [] | reason=fishing_postfilter_empty")
                return []

        ranked = rank_results(
            candidates,
            graphics_preference=graphics_preference,
        )
        if debug_scores:
            self._log_top_hybrid_scores(ranked, top_k=5)
        print(f"[Trace] search:return results | count={min(len(ranked), top_n)}")
        return ranked[:top_n]


if __name__ == "__main__":
    agent = RAGAgent()
    print("Agent initialized. Testing hybrid query...")

    test_query = "i want a game similar to 'It takes two'."
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
        print(f"   Relevance Score: {match.get('primary_rank_score', 0.0):.4f}")
        print(f"   Platforms: {match.get('platforms', 'Not Listed')}")
        print(f"   Summary: {(match.get('summary', '') or '').strip()}")
