import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import chromadb
import numpy as np
import pandas as pd
from chromadb.utils import embedding_functions

try:
    from rank_bm25 import BM25Okapi
except Exception:
    BM25Okapi = None



SEMANTIC_WEIGHT = 0.9
LEXICAL_WEIGHT = 0.1


PLATFORM_MATCH_ALIASES = {
    "nintendo switch": ("nintendo switch", "switch"),
    "switch": ("nintendo switch", "switch"),
    "pc": ("pc", "windows", "microsoft windows", "steam"),
    "windows": ("pc", "windows", "microsoft windows", "steam"),
    "steam": ("pc", "windows", "microsoft windows", "steam"),
    "playstation 5": ("playstation 5", "ps5"),
    "ps5": ("playstation 5", "ps5"),
    "playstation 4": ("playstation 4", "ps4"),
    "ps4": ("playstation 4", "ps4"),
    "xbox series": ("xbox series", "series x", "series s"),
    "xbox one": ("xbox one",),
    "xbox": ("xbox",),
}


def _contains_any(text, options):
    text = (text or "").lower()
    expanded_options = []
    for option in options:
        normalized_option = str(option or "").lower().strip()
        if not normalized_option:
            continue
        expanded_options.append(normalized_option)
        for alias_key, aliases in PLATFORM_MATCH_ALIASES.items():
            if normalized_option == alias_key or normalized_option in aliases:
                expanded_options.extend(aliases)
                break
    return any(option and option in text for option in expanded_options)


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

GENERIC_SEED_TITLE_TOKENS = {
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
    "sci",
    "similar",
    "story",
    "strategy",
    "switch",
    "xbox",
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
    """Apply final ranking with metadata-aware adjustments.

    Fallback and prefilter order across the retrieval pipeline:
    1) Metadata/DataFrame prefilter constraints
    2) Semantic vector retrieval
    3) BM25 lexical retrieval (or SimpleBM25 fallback)
    4) Fusion scoring (weighted normalized vector/BM25 + metadata boosts)
    5) Post-fusion multipliers/penalties (e.g., 2D preference, 3D avoidance)

    Note: upstream fusion may use RRF-style candidate blending; the weighted
    semantic/lexical score is preserved as an interpretable secondary signal.
    """
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
        normalized_vec = _safe_float(candidate.get("normalized_vec", candidate.get("semantic_score", 0.0)), 0.0)
        normalized_bm25 = _safe_float(candidate.get("normalized_bm25", candidate.get("bm25_score_norm", 0.0)), 0.0)

        semantic_weight = _safe_float(candidate.get("vector_weight", SEMANTIC_WEIGHT), SEMANTIC_WEIGHT)
        lexical_weight = _safe_float(candidate.get("bm25_weight", LEXICAL_WEIGHT), LEXICAL_WEIGHT)
        weighted_hybrid = (semantic_weight * normalized_vec) + (lexical_weight * normalized_bm25)

        hybrid_rrf = _safe_float(candidate.get("hybrid_score", 0.0), 0.0)
        candidate["weighted_hybrid_score"] = weighted_hybrid
        candidate["relevance_score"] = metadata_boost + max(hybrid_rrf, weighted_hybrid)
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
        self.catalog_path = self.root_dir / "data" / "app" / "app_game_catalog.parquet"
        self.COLUMN_MAP = {
            "platforms": "platforms_list",
            "genres": "genres_list",
            "playtime": "normal_playtime_hours",
        }

        self.client = chromadb.PersistentClient(path=str(self.root_dir / "data" / "vector_store"))
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_collection(
            name="igdb_game_profiles",
            embedding_function=self.embedding_fn,
        )

        self.catalog_df = self._load_catalog_df()
        self._warn_if_index_mismatch()

        self.analytics_columns = self._get_analytics_columns()
        self.catalog_by_id = {}
        self.bm25_doc_ids = []
        self.bm25_index = None
        self.dimension_keyword_sets = self._load_dimension_keyword_sets()
        self._build_bm25_index_from_analytics_view()

    def _get_analytics_columns(self):
        if self.catalog_df is None or self.catalog_df.empty:
            return set()
        return set(self.catalog_df.columns.astype(str).tolist())

    def _load_catalog_df(self):
        df = pd.read_parquet(self.catalog_path)
        for canonical_col, mapped_col in self.COLUMN_MAP.items():
            if canonical_col not in df.columns and mapped_col in df.columns:
                df[canonical_col] = df[mapped_col]
        return df

    def _warn_if_index_mismatch(self):
        catalog_count = len(self.catalog_df)
        index_count = self.collection.count()
        if catalog_count != index_count:
            print(
                "[WARN] Catalog and vector index size mismatch "
                f"(catalog={catalog_count}, index={index_count}). "
                "Run src/initialize_vector_db.py to rebuild the vector index."
            )

    def _build_bm25_index_from_analytics_view(self):
        df = self.catalog_df.copy()

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
        two_d_ids = set()
        three_d_ids = set()

        if self.catalog_df is None or self.catalog_df.empty:
            return {"2d": two_d_ids, "3d": three_d_ids}

        # Build text from fields that may contain dimension clues.
        text_columns = ["keywords", "genres", "themes", "summary", "storyline", "rag_text_profile"]

        for _, row in self.catalog_df.iterrows():
            game_id = str(row.get("game_id", "")).strip()
            if not game_id:
                continue

            haystack_parts = []
            for col in text_columns:
                value = row.get(col, "")
                if value is None:
                    continue
                haystack_parts.append(str(value).lower())

            haystack = " ".join(haystack_parts)

            # 2D detection
            if ("2d" in haystack) or ("2.5d" in haystack):
                two_d_ids.add(game_id)

            # 3D detection
            if "3d" in haystack:
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

        interactions_df = self.catalog_df.copy()
        if interactions_df.empty or "user_id" not in interactions_df.columns:
            return 0, 0.0, {}, [], 1.0, "Balanced"

        user_rows = interactions_df[
            interactions_df["user_id"].astype(str).str.strip() == normalized_user_id
        ].copy()
        if user_rows.empty:
            return 0, 0.0, {}, [], 1.0, "Balanced"

        games_played = int(user_rows["game_id"].astype(str).nunique()) if "game_id" in user_rows.columns else len(user_rows)

        has_time_played = "time_played" in user_rows.columns
        interactions = []
        for _, row in user_rows.iterrows():
            interactions.append(
                UserInteraction(
                    user_id=str(row.get("user_id", normalized_user_id) or normalized_user_id),
                    game_id=str(row.get("game_id", "") or ""),
                    game_name=str(row.get("game_name", row.get("name", "")) or ""),
                    time_played=_safe_float(row.get("time_played", 1.0 if not has_time_played else 0.0), 0.0),
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
        if has_time_played and "normally" in user_rows.columns:
            pace_rows = user_rows[["time_played", "normally"]].copy()
            pace_rows = pace_rows.dropna(subset=["time_played", "normally"])
            pace_rows = pace_rows[(pd.to_numeric(pace_rows["time_played"], errors="coerce") > 0)]
            pace_rows = pace_rows[(pd.to_numeric(pace_rows["normally"], errors="coerce") > 0)]
            if not pace_rows.empty:
                pace_rows["rpi"] = pd.to_numeric(pace_rows["time_played"], errors="coerce") / pd.to_numeric(
                    pace_rows["normally"], errors="coerce"
                )
                user_pace_signature = _safe_float(pace_rows["rpi"].median(), 1.0)

        if user_pace_signature > 1.2:
            pace_profile_label = "Deep/Extended"
        elif user_pace_signature < 0.8:
            pace_profile_label = "Snackable/Fast"

        alpha = get_alpha(games_played)
        return games_played, alpha, preference_scores, interactions, user_pace_signature, pace_profile_label

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

    def _get_series(self, column_name, default_value=0):
        df = self.catalog_df
        if df is None or df.empty:
            return pd.Series(dtype="object")

        candidates = [column_name]

        mapped = self.COLUMN_MAP.get(column_name)
        if mapped and mapped not in candidates:
            candidates.append(mapped)

        reverse_mapped = None
        for canonical, mapped_name in self.COLUMN_MAP.items():
            if mapped_name == column_name:
                reverse_mapped = canonical
                break
        if reverse_mapped and reverse_mapped not in candidates:
            candidates.append(reverse_mapped)

        for candidate in candidates:
            if candidate in df.columns:
                return df[candidate]

        return pd.Series(default_value, index=df.index)


    def _get_prefilter_ids(self, query, min_year=None, platforms=None, multiplayer_mode=None):
        req = self._extract_explicit_requirements(query)
        df = self.catalog_df.copy()
        if df.empty:
            return set(), req

        mask = pd.Series(True, index=df.index)

        platform_constraints = self._detect_platform_terms(query, platforms)
        if req.get("needs_switch") and ("platform_nintendo_switch", "nintendo switch") not in platform_constraints:
            platform_constraints.append(("platform_nintendo_switch", "nintendo switch"))

        if platform_constraints:
            platform_mask = pd.Series(False, index=df.index)
            platforms_text = self._get_series("platforms", "").astype(str).str.lower()
            for col_name, fallback_term in platform_constraints:
                term = str(fallback_term or "").lower().strip()
                candidate_mask = pd.Series(False, index=df.index)
                if col_name and col_name in df.columns:
                    col_series = pd.to_numeric(self._get_series(col_name, 0), errors="coerce").fillna(0).astype(int)
                    candidate_mask = candidate_mask | (col_series == 1)
                if term:
                    candidate_mask = candidate_mask | platforms_text.str.contains(term, na=False, regex=False)
                platform_mask = platform_mask | candidate_mask
            mask = mask & platform_mask

        mode = str(multiplayer_mode).strip().lower() if multiplayer_mode else ""
        needs_multiplayer_filter = req.get("needs_coop") or mode in {"online", "offline", "both"}

        if needs_multiplayer_filter:
            mp_online_coop = pd.to_numeric(self._get_series("mp_online_coop", 0), errors="coerce").fillna(0).astype(int)
            mp_max_online_players = pd.to_numeric(self._get_series("mp_max_online_players", 0), errors="coerce").fillna(0)
            mp_offline_coop = pd.to_numeric(self._get_series("mp_offline_coop", 0), errors="coerce").fillna(0).astype(int)
            mp_splitscreen = pd.to_numeric(self._get_series("mp_splitscreen", 0), errors="coerce").fillna(0).astype(int)
            mp_campaign_coop = pd.to_numeric(self._get_series("mp_campaign_coop", 0), errors="coerce").fillna(0).astype(int)

            online = (mp_online_coop == 1) | (mp_max_online_players > 0)
            offline = (mp_offline_coop == 1) | (mp_splitscreen == 1) | (mp_campaign_coop == 1)

            if req.get("needs_coop") and not mode:
                mask = mask & (online | offline)
            elif mode == "online":
                mask = mask & online
            elif mode == "offline":
                mask = mask & offline
            elif mode == "both":
                mask = mask & (online & offline)

        if req.get("needs_fishing"):
            fishing_mask = pd.Series(False, index=df.index)
            for col in ["genres", "themes", "name", "summary"]:
                col_text = self._get_series(col, "").astype(str).str.lower()
                fishing_mask = fishing_mask | col_text.str.contains("fishing", na=False)
            mask = mask & fishing_mask

        if min_year is not None:
            min_year_value = _safe_int(min_year, 0)
            if min_year_value > 0:
                release_years = pd.to_numeric(self._get_series("release_year", 0), errors="coerce").fillna(0).astype(int)
                mask = mask & (release_years >= min_year_value)

        filtered = df[mask]
        if filtered.empty:
            print(
                "[WARN] Prefilter constraints were too strict (0 matches). "
                "Falling back to broad catalog search."
            )
            broad_mask = pd.Series(True, index=df.index)
            if min_year is not None:
                min_year_value = _safe_int(min_year, 0)
                if min_year_value > 0:
                    release_years = pd.to_numeric(self._get_series("release_year", 0), errors="coerce").fillna(0).astype(int)
                    broad_mask = broad_mask & (release_years >= min_year_value)
            filtered = df[broad_mask]
            if filtered.empty:
                filtered = df

        game_id_series = self._get_series("game_id", "").astype(str).str.strip()
        fallback_mask = filtered.index
        return set(game_id_series.loc[fallback_mask][game_id_series.loc[fallback_mask] != ""].tolist()), req

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
        if not q:
            return None

        patterns = [
            r"similar to\s+(.+?)(?:\s+with\b|\s+that\b|\s+having\b|\s+on\s+|\s+for\s+|\s+but\b|$)",
            r"more like\s+(.+?)(?:\s+with\b|\s+that\b|\s+having\b|\s+on\s+|\s+for\s+|\s+but\b|$)",
            r"games?\s+like\s+(.+?)(?:\s+with\b|\s+that\b|\s+having\b|\s+on\s+|\s+for\s+|\s+but\b|$)",
            r"like\s+(.+?)(?:\s+with\b|\s+that\b|\s+having\b|\s+on\s+|\s+for\s+|\s+but\b|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, q, flags=re.IGNORECASE)
            if not match:
                continue
            raw = match.group(1).strip(" .,!?:;\"'")
            raw = re.split(
                r"\b(with|and|plus|featuring|including|multiplayer|co-?op|farming|elements?)\b",
                raw,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0].strip(" .,!?:;\"'")
            if raw:
                return raw
        return None

    def _has_seed_reference_intent(self, query):
        q = (query or "").lower()
        if not q:
            return False

        seed_intent_patterns = [
            r"\bsimilar to\b",
            r"\bmore like\b",
            r"\bgames?\s+like\b",
            r"\bi\s+(recently\s+)?played\b",
            r"\brecently\s+played\b",
            r"\bafter\s+playing\b",
            r"\bi\s+(liked|loved|enjoyed)\b",
            r"\bbased on\b",
        ]
        return any(re.search(pattern, q, flags=re.IGNORECASE) for pattern in seed_intent_patterns)

    def _is_specific_seed_title(self, title_tokens):
        if not title_tokens:
            return False
        if len(title_tokens) >= 2:
            return len("".join(title_tokens)) >= 5

        token = title_tokens[0]
        return len(token) >= 5 and token not in GENERIC_SEED_TITLE_TOKENS

    def _find_seed_games_mentioned_in_query(self, query, max_matches=5):
        if not self._has_seed_reference_intent(query):
            return []

        query_tokens = _tokenize_text(query)
        if not query_tokens:
            return []

        max_window = min(8, len(query_tokens))
        query_ngrams = set()
        for size in range(1, max_window + 1):
            for idx in range(0, len(query_tokens) - size + 1):
                query_ngrams.add(tuple(query_tokens[idx : idx + size]))

        matches = []
        for _, row in self.catalog_df.iterrows():
            name = str(row.get("name", "") or "").strip()
            game_id = str(row.get("game_id", "") or "").strip()
            if not name or not game_id:
                continue

            title_tokens = tuple(_tokenize_text(name))
            if len(title_tokens) > max_window or not self._is_specific_seed_title(title_tokens):
                continue
            if title_tokens not in query_ngrams:
                continue

            matches.append(
                (
                    len(title_tokens),
                    len(name),
                    _safe_float(row.get("total_rating_count"), 0.0),
                    row.to_dict(),
                )
            )

        matches.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)

        selected = []
        seen_game_ids = set()
        for _, _, _, row in matches:
            game_id = str(row.get("game_id", "") or "").strip()
            if not game_id or game_id in seen_game_ids:
                continue
            seen_game_ids.add(game_id)
            selected.append(row)
            if len(selected) >= max_matches:
                break

        return selected

    def _append_seed_game(self, seed_games, seen_seed_ids, seed_game):
        if not seed_game:
            return

        game_id = str(seed_game.get("game_id", "") or "").strip()
        if not game_id or game_id in seen_seed_ids:
            return

        seen_seed_ids.add(game_id)
        seed_games.append(seed_game)

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

        df = self.catalog_df.copy()
        if df.empty or "name" not in df.columns:
            return None

        seed_title_lower = str(seed_title).strip().lower()
        direct = df[df["name"].astype(str).str.lower().str.contains(seed_title_lower, na=False)]
        if not direct.empty:
            return direct.iloc[0].to_dict()

        seed_key = self._normalize_seed_key(seed_title)
        for _, row in df.iterrows():
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

        df = self.catalog_df.copy()
        if df.empty or "game_id" not in df.columns:
            return None

        matches = df[df["game_id"].astype(str) == normalized_seed_id]
        if matches.empty:
            return None
        return matches.iloc[0].to_dict()

    def _parse_csv_values(self, raw_value):
        if raw_value is None:
            return []
        text = str(raw_value).strip()
        if not text:
            return []
        return [part.strip() for part in text.split(",") if part.strip()]

    def _get_similar_by_seed_attributes(self, seed_game):
        seed_game_id = str(seed_game.get("game_id"))
        seed_platforms = self._parse_csv_values(seed_game.get("platforms_list", seed_game.get("platforms")))
        seed_genres = self._parse_csv_values(seed_game.get("genres_list", seed_game.get("genres")))
        seed_themes = self._parse_csv_values(seed_game.get("themes_list", seed_game.get("themes")))
        seed_developers = self._parse_csv_values(seed_game.get("developers_list", seed_game.get("developers")))

        df = self.catalog_df.copy()
        if df.empty:
            return set(), {}
        if "game_id" in df.columns:
            df = df[df["game_id"].astype(str) != seed_game_id]

        if df.empty:
            return set(), {}

        seed_platforms_set = {x.lower() for x in seed_platforms if str(x).strip()}
        seed_genres_set = {x.lower() for x in seed_genres if str(x).strip()}
        seed_themes_set = {x.lower() for x in seed_themes if str(x).strip()}
        seed_developers_set = {x.lower() for x in seed_developers if str(x).strip()}

        def _jaccard(a, b):
            if not a or not b:
                return 0.0
            inter = len(a.intersection(b))
            union = len(a.union(b))
            if union == 0:
                return 0.0
            return inter / union

        similar_ids = set()
        similarity_boosts = {}
        for _, row in df.iterrows():
            game_id = str(row.get("game_id", ""))
            candidate_platforms = {x.lower() for x in self._parse_csv_values(row.get("platforms_list", row.get("platforms"))) if str(x).strip()}
            candidate_genres = {x.lower() for x in self._parse_csv_values(row.get("genres_list", row.get("genres"))) if str(x).strip()}
            candidate_themes = {x.lower() for x in self._parse_csv_values(row.get("themes_list", row.get("themes"))) if str(x).strip()}
            candidate_developers = {x.lower() for x in self._parse_csv_values(row.get("developers_list", row.get("developers"))) if str(x).strip()}

            genre_j = _jaccard(seed_genres_set, candidate_genres)
            theme_j = _jaccard(seed_themes_set, candidate_themes)
            developer_j = _jaccard(seed_developers_set, candidate_developers)
            platform_j = _jaccard(seed_platforms_set, candidate_platforms)

            # Weighted metadata similarity score for soft boosting only.
            boost = (1.4 * genre_j) + (0.8 * theme_j) + (0.5 * developer_j) + (0.3 * platform_j)

            # Keep candidate ids for optional soft overlap telemetry, but avoid hard gating.
            if boost > 0.0:
                similar_ids.add(game_id)
                similarity_boosts[game_id] = boost

        return similar_ids, similarity_boosts

    def _get_management_filter_ids(self, domain_keywords):
        if not domain_keywords:
            return None

        df = self.catalog_df.copy()
        if df.empty or "summary" not in df.columns or "game_id" not in df.columns:
            return set()

        summary = df["summary"].astype(str).str.lower()
        mask = pd.Series(False, index=df.index)
        for keyword in domain_keywords:
            kw = str(keyword).strip().lower()
            if kw:
                mask = mask | summary.str.contains(kw, na=False)

        rows = df[mask]
        return set(rows["game_id"].astype(str).tolist())

    def _vector_search(self, query, n_results=100, allowed_ids=None):
        requested = n_results
        if allowed_ids is not None:
            allowed_size = len(allowed_ids)
            if allowed_size == 0:
                return []
            requested = max(
                n_results * 20,
                min(max(allowed_size * 10, 1000), max(len(self.catalog_by_id), 1000)),
            )
        requested = min(requested, 2000)
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

        if allowed_ids is not None and not vector_hits:
            sample_ids = list(allowed_ids)[: min(len(allowed_ids), 5000)]
            direct = self.collection.get(ids=sample_ids, include=["embeddings"])
            emb_list = direct.get("embeddings") if direct.get("embeddings") is not None else []
            id_list = direct.get("ids") if direct.get("ids") is not None else []
            if len(emb_list) > 0 and len(id_list) > 0:
                q_emb = self.embedding_fn([query])[0]
                q = np.array(q_emb, dtype=float)
                q_norm = np.linalg.norm(q) + 1e-12

                scored = []
                for gid, emb in zip(id_list, emb_list):
                    v = np.array(emb, dtype=float)
                    sim = float(np.dot(q, v) / (q_norm * (np.linalg.norm(v) + 1e-12)))
                    scored.append((str(gid), sim))

                scored.sort(key=lambda x: x[1], reverse=True)
                vector_hits = [
                    {
                        "game_id": gid,
                        "distance": 1.0 - sim,
                        "similarity": sim,
                        "vector_rank": idx + 1,
                    }
                    for idx, (gid, sim) in enumerate(scored[:n_results])
                ]
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
        vector_weight=0.9,
        bm25_weight=0.1,
    ):
        merged = {}
        vector_rank_map = {h["game_id"]: h["vector_rank"] for h in vector_hits}
        bm25_rank_map = {h["game_id"]: h["bm25_rank"] for h in bm25_hits}
        vector_sim_map = {h["game_id"]: _safe_float(h.get("similarity", 0.0), 0.0) for h in vector_hits}
        bm25_raw_map = {h["game_id"]: _safe_float(h.get("bm25_score", 0.0), 0.0) for h in bm25_hits}
        query_tokens = _tokenize_text(query)

        bm25_vals = list(bm25_raw_map.values())
        if bm25_vals:
            bmin, bmax = min(bm25_vals), max(bm25_vals)
            denom = (bmax - bmin) if (bmax - bmin) > 1e-12 else 1.0
            bm25_norm_map = {gid: (score - bmin) / denom for gid, score in bm25_raw_map.items()}
        else:
            bm25_norm_map = {}

        vector_norm_map = {gid: max(0.0, min(1.0, sim)) for gid, sim in vector_sim_map.items()}
        all_ids = set(vector_norm_map.keys()) | set(bm25_norm_map.keys())

        for game_id in all_ids:
            v = vector_norm_map.get(game_id, 0.0)
            b = bm25_norm_map.get(game_id, 0.0)
            v_rrf = 1.0 / (rrf_k + vector_rank_map[game_id]) if game_id in vector_rank_map else 0.0
            b_rrf = 1.0 / (rrf_k + bm25_rank_map[game_id]) if game_id in bm25_rank_map else 0.0
            fused_score = (vector_weight * v) + (bm25_weight * b) + 0.05 * (v_rrf + b_rrf)

            row = self.catalog_by_id.get(game_id, {})
            lexical_bonus = 0.0
            searchable_blob = " ".join(
                [
                    str(row.get("name", "") or "").lower(),
                    str(row.get("summary", "") or "").lower(),
                    str(row.get("storyline", "") or "").lower(),
                ]
            )
            for token in query_tokens:
                if token and token in searchable_blob:
                    lexical_bonus += 0.01

            weighted_component = (vector_weight * v) + (bm25_weight * b)
            rrf_component = 0.05 * (v_rrf + b_rrf)
            final_score = weighted_component + rrf_component + lexical_bonus

            merged[game_id] = {
                "game_id": game_id,
                "hybrid_score": final_score,
                "distance": 1.0 - v,
                "vector_similarity": v,
                "normalized_vec": v,
                "normalized_bm25": b,
                "weighted_component": weighted_component,
                "rrf_component": rrf_component,
                "lexical_bonus": lexical_bonus,
                "vector_rrf": v_rrf,
                "bm25_rrf": b_rrf,
                "vector_weight": vector_weight,
                "bm25_weight": bm25_weight,
                "bm25_score_raw": _safe_float(bm25_raw_map.get(game_id, 0.0), 0.0),
                "keyword_boost_applied": lexical_bonus > 0.0,
            }

        return sorted(merged.values(), key=lambda x: x["hybrid_score"], reverse=True)

    def _format_text_output(self, text, max_len=1000):
        cleaned = (text or "").strip()
        if len(cleaned) > max_len:
            return cleaned[:max_len].strip() + "..."
        return cleaned

    def _format_storyline_output(self, summary, storyline, max_len=1000):
        summary_text = (summary or "").strip()
        storyline_text = (storyline or "").strip()
        if summary_text and storyline_text:
            combined = f"{summary_text}\n\n{storyline_text}"
        else:
            combined = summary_text or storyline_text
        if len(combined) > max_len:
            return combined[:max_len].strip() + "..."
        return combined

    def _log_top_hybrid_scores(self, ranked, top_k=5):
        for idx, item in enumerate(ranked[:top_k], start=1):
            print(
                "[HybridDebug] "
                f"{idx}. {item.get('name', 'Unknown')} | "
                f"RawVec={_safe_float(item.get('vector_similarity', 0.0), 0.0):.4f} | "
                f"RawBM25={_safe_float(item.get('bm25_score_raw', 0.0), 0.0):.4f} | "
                f"NormVec={_safe_float(item.get('normalized_vec', item.get('vector_similarity', 0.0)), 0.0):.4f} | "
                f"NormBM25={_safe_float(item.get('normalized_bm25', 0.0), 0.0):.4f} | "
                f"Weights=({_safe_float(item.get('vector_weight', SEMANTIC_WEIGHT), SEMANTIC_WEIGHT):.2f},"
                f"{_safe_float(item.get('bm25_weight', LEXICAL_WEIGHT), LEXICAL_WEIGHT):.2f}) | "
                f"Weighted={_safe_float(item.get('weighted_component', 0.0), 0.0):.4f} | "
                f"RRF={_safe_float(item.get('rrf_component', 0.0), 0.0):.4f} | "
                f"LexicalBonus={_safe_float(item.get('lexical_bonus', 0.0), 0.0):.4f} | "
                f"MetadataBoost={_safe_float(item.get('metadata_boost', 0.0), 0.0):.4f} | "
                f"Final={_safe_float(item.get('hybrid_score', 0.0), 0.0):.4f} | "
                f"KeywordBoost={bool(item.get('keyword_boost_applied', False))}"
            )

    def search(
        self,
        query,
        top_n=5,
        min_year=None,
        platforms=None,
        multiplayer_mode=None,
        vector_k=100,
        bm25_k=100,
        semantic_weight=SEMANTIC_WEIGHT,
        lexical_weight=LEXICAL_WEIGHT,
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
        print(f"Prefilter found {len(allowed_ids) if allowed_ids is not None else len(self.catalog_df)} games.")

        seed_similarity_boosts = {}
        seed_filter_ids = None
        seed_exclusion_ids = set()
        seed_games = []
        seen_seed_ids = set()

        if seed_game_id is not None:
            seed_game = self._find_seed_game_by_id(seed_game_id)
            if not seed_game:
                print(f"[Trace] search:return [] | reason=seed_game_id_not_found | seed_game_id={seed_game_id}")
                return []
            self._append_seed_game(seed_games, seen_seed_ids, seed_game)
        else:
            seed_title = self._extract_similarity_seed_title(query)
            if seed_title:
                seed_game = self._find_seed_game(seed_title)
                if seed_game:
                    self._append_seed_game(seed_games, seen_seed_ids, seed_game)
                else:
                    print(f"[INFO] Seed game '{seed_title}' not found. Falling back to Hybrid Vector+BM25.")

        for seed_game in self._find_seed_games_mentioned_in_query(query):
            self._append_seed_game(seed_games, seen_seed_ids, seed_game)

        if seed_games:
            seed_filter_ids = set()
            seed_names = []
            for seed_game in seed_games:
                seed_id = str(seed_game.get("game_id", "") or "").strip()
                seed_name = str(seed_game.get("name", seed_id) or seed_id).strip()
                if seed_id:
                    seed_exclusion_ids.add(seed_id)
                if seed_name:
                    seed_names.append(seed_name)

                current_seed_ids, current_boosts = self._get_similar_by_seed_attributes(seed_game)
                seed_filter_ids.update(current_seed_ids)
                for game_id, boost in current_boosts.items():
                    seed_similarity_boosts[game_id] = max(
                        _safe_float(seed_similarity_boosts.get(game_id), 0.0),
                        _safe_float(boost, 0.0),
                    )

            if seed_game_id is not None and not seed_similarity_boosts:
                print(
                    "[Trace] search:return [] | reason=seed_game_similarity_empty | "
                    f"seed_game_id={seed_game_id}"
                )
                return []

            if seed_exclusion_ids and allowed_ids is not None:
                allowed_ids = allowed_ids.difference(seed_exclusion_ids)

            seed_overlap = allowed_ids.intersection(seed_filter_ids) if allowed_ids is not None else set(seed_filter_ids)
            print(
                "[Trace] seed_context:active | "
                f"seed_titles={seed_names} | excluded_seed_ids={len(seed_exclusion_ids)} | "
                f"similar_candidates={len(seed_filter_ids)}"
            )
            if seed_overlap:
                print(f"[Trace] seed_filter:soft_overlap | overlap_candidates={len(seed_overlap)}")
            else:
                print("[Trace] seed_filter:soft_only | overlap_candidates=0 | using metadata boost without hard filter")

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
            print("[WARN] Prefilter empty after strict constraints; auto-relaxing to broad retrieval.")
            allowed_ids = set(self.catalog_by_id.keys()).difference(seed_exclusion_ids)
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
                print("[WARN] Relaxed prefilter still empty; falling back to full catalog for retrieval.")
                allowed_ids = set(self.catalog_by_id.keys()).difference(seed_exclusion_ids)

        print("Retrieval Mode: Semantic Theme")
        if allowed_ids is not None and not allowed_ids:
            print("[WARN] Prefilter produced empty set; falling back to full catalog for retrieval.")
            allowed_ids = set(self.catalog_by_id.keys()).difference(seed_exclusion_ids)
        allowed_count_for_retrieval = "ALL" if allowed_ids is None else len(allowed_ids)
        print(f"[Trace] retrieval:starting | allowed_ids={allowed_count_for_retrieval}")
        print("Searching with vector index...")
        vector_hits = self._vector_search(query=query, n_results=vector_k, allowed_ids=allowed_ids)
        if not vector_hits and allowed_ids is not None and len(allowed_ids) > 0:
            print("[WARN] vector_hits=0 with constrained allowed_ids; retrying vector search without allowed_ids then filtering.")
            broad_vector_hits = self._vector_search(query=query, n_results=max(vector_k * 10, 500), allowed_ids=None)
            vector_hits = [h for h in broad_vector_hits if h["game_id"] in allowed_ids][:vector_k]
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
            vector_weight=semantic_weight,
            bm25_weight=lexical_weight,
        )

        candidates = []
        for hit in fused_hits:
            game_id = hit["game_id"]
            if game_id in seed_exclusion_ids:
                continue
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
                    "normalized_vec": _safe_float(hit.get("normalized_vec"), 0.0),
                    "normalized_bm25": _safe_float(hit.get("normalized_bm25"), 0.0),
                    "weighted_component": _safe_float(hit.get("weighted_component"), 0.0),
                    "rrf_component": _safe_float(hit.get("rrf_component"), 0.0),
                    "lexical_bonus": _safe_float(hit.get("lexical_bonus"), 0.0),
                    "vector_rrf": _safe_float(hit.get("vector_rrf"), 0.0),
                    "bm25_rrf": _safe_float(hit.get("bm25_rrf"), 0.0),
                    "vector_weight": _safe_float(hit.get("vector_weight"), SEMANTIC_WEIGHT),
                    "bm25_weight": _safe_float(hit.get("bm25_weight"), LEXICAL_WEIGHT),
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
        top3_names = [c.get("name", "Not Listed") for c in ranked[:3]]
        print(f"Top 3 matches found: {top3_names}")
        if debug_scores:
            self._log_top_hybrid_scores(ranked, top_k=5)
        print(f"[Trace] search:return results | count={min(len(ranked), top_n)}")
        return ranked[:top_n]


if __name__ == "__main__":
    agent = RAGAgent()
    print("Agent initialized. Running sanity checks...")
    print(f"Catalog rows: {len(agent.catalog_df)}")
    print(f"Current year: {datetime.now().year}")
    print("Catalog columns:", sorted(agent.catalog_df.columns.tolist()))

    test_query = "I want a game similar to Stardew Valley with multiplayer co-op and farming elements."
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
