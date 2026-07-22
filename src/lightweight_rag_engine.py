from __future__ import annotations

import json
import math
import re
from collections import Counter
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.app import config
from src.app.embedding_text import normalize_embedding_catalog

try:
    from rank_bm25 import BM25Okapi
except Exception:
    BM25Okapi = None


SEMANTIC_WEIGHT = 0.8
LEXICAL_WEIGHT = 0.2
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

LIGHTWEIGHT_RAG_DIR = config.RAG_DIR / "lightweight"
LIGHTWEIGHT_EMBEDDINGS_PATH = LIGHTWEIGHT_RAG_DIR / "game_embeddings.npy"
LIGHTWEIGHT_GAME_IDS_PATH = LIGHTWEIGHT_RAG_DIR / "game_ids.json"
LIGHTWEIGHT_MANIFEST_PATH = LIGHTWEIGHT_RAG_DIR / "manifest.json"

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

TWO_D_REGEX = re.compile(r"\b2(?:\.5)?d\b", flags=re.IGNORECASE)
THREE_D_REGEX = re.compile(r"\b3d\b", flags=re.IGNORECASE)


def lightweight_rag_artifacts() -> dict[str, Path]:
    return {
        "lightweight_rag_dir": LIGHTWEIGHT_RAG_DIR,
        "lightweight_embeddings": LIGHTWEIGHT_EMBEDDINGS_PATH,
        "lightweight_game_ids": LIGHTWEIGHT_GAME_IDS_PATH,
        "lightweight_manifest": LIGHTWEIGHT_MANIFEST_PATH,
    }


def lightweight_rag_ready() -> bool:
    return all(path.exists() for path in lightweight_rag_artifacts().values())


def _contains_any(text: object, options: list[str] | tuple[str, ...]) -> bool:
    text = str(text or "").lower()
    expanded_options: list[str] = []
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


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        parsed = float(value)
    except Exception:
        return default
    if math.isnan(parsed) or math.isinf(parsed):
        return default
    return parsed


def _safe_int(value: object, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(float(value))
    except Exception:
        return default


def _tokenize_text(text: object) -> list[str]:
    return re.findall(r"[a-z0-9]+", str(text or "").lower())


def _has_term(query: str, term: str) -> bool:
    return term in str(query or "").lower()


def _contains_phrase(text: str, phrase: str) -> bool:
    return f" {phrase} " in f" {str(text or '').lower()} "


class SimpleBM25:
    """Small BM25 fallback used when rank_bm25 is unavailable."""

    def __init__(self, tokenized_corpus: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_count = len(tokenized_corpus)
        self.doc_freq: dict[str, int] = {}
        self.doc_len: list[int] = []
        self.term_freqs: list[Counter] = []

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
        self.idf = {
            term: math.log(1 + (self.doc_count - df + 0.5) / (df + 0.5))
            for term, df in self.doc_freq.items()
        }

    def get_scores(self, query_tokens: list[str]) -> list[float]:
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


@lru_cache(maxsize=1)
def _get_embedding_model(model_name: str):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def rank_results(candidates: list[dict[str, Any]], graphics_preference: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    if not candidates:
        return []

    graphics_preference = graphics_preference or {}
    request_2d = bool(graphics_preference.get("request_2d", False))
    avoid_3d = bool(graphics_preference.get("avoid_3d", False))
    two_d_boost = _safe_float(graphics_preference.get("two_d_boost", 1.5), 1.5)
    three_d_penalty = _safe_float(graphics_preference.get("three_d_penalty", 0.1), 0.1)

    for candidate in candidates:
        metadata_boost = _safe_float(candidate.get("metadata_boost", 0.0), 0.0)
        normalized_vec = _safe_float(candidate.get("normalized_vec", candidate.get("semantic_score", 0.0)), 0.0)
        normalized_bm25 = _safe_float(candidate.get("normalized_bm25", candidate.get("bm25_score_norm", 0.0)), 0.0)
        semantic_weight = _safe_float(candidate.get("vector_weight", SEMANTIC_WEIGHT), SEMANTIC_WEIGHT)
        lexical_weight = _safe_float(candidate.get("bm25_weight", LEXICAL_WEIGHT), LEXICAL_WEIGHT)
        weighted_hybrid = (semantic_weight * normalized_vec) + (lexical_weight * normalized_bm25)

        hybrid_rrf = _safe_float(candidate.get("hybrid_score", 0.0), 0.0)
        candidate["weighted_hybrid_score"] = weighted_hybrid
        candidate["relevance_score"] = metadata_boost + max(hybrid_rrf, weighted_hybrid)

        multiplier = 1.0
        if (request_2d or avoid_3d) and bool(candidate.get("is_3d_detected", False)):
            multiplier *= three_d_penalty
        if request_2d and bool(candidate.get("is_2d_detected", False)):
            multiplier *= two_d_boost

        candidate["constraint_multiplier"] = multiplier
        candidate["primary_rank_score"] = candidate["relevance_score"] * multiplier

    return sorted(
        candidates,
        key=lambda item: (
            -_safe_float(item.get("primary_rank_score", 0.0), 0.0),
            _safe_float(item.get("distance", 1.0), 1.0),
        ),
    )


class LightweightRAGAgent:
    """Chroma-free RAG retrieval using NumPy cosine similarity plus BM25 fusion."""

    backend_name = "lightweight_numpy_bm25"

    def __init__(
        self,
        embeddings_path: Path | None = None,
        game_ids_path: Path | None = None,
        manifest_path: Path | None = None,
    ):
        self.root_dir = config.ROOT_DIR
        self.catalog_path = config.APP_CATALOG_PATH
        self.embeddings_path = embeddings_path or LIGHTWEIGHT_EMBEDDINGS_PATH
        self.game_ids_path = game_ids_path or LIGHTWEIGHT_GAME_IDS_PATH
        self.manifest_path = manifest_path or LIGHTWEIGHT_MANIFEST_PATH
        self.COLUMN_MAP = {
            "platforms": "platforms_list",
            "genres": "genres_list",
            "playtime": "normal_playtime_hours",
        }

        self.manifest = self._load_manifest()
        self.embedding_model_name = self.manifest.get("model_name", EMBEDDING_MODEL_NAME)
        self.catalog_df = self._load_catalog_df()
        self.catalog_by_id: dict[str, dict[str, Any]] = {}
        self.bm25_doc_ids: list[str] = []
        self.bm25_index = None
        self.game_ids = self._load_game_ids()
        self.game_id_to_position = {game_id: idx for idx, game_id in enumerate(self.game_ids)}
        self.embeddings = self._load_embeddings()
        self._validate_index_alignment()
        self._build_bm25_index()

    def _load_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            raise FileNotFoundError(
                f"Missing lightweight RAG manifest: {self.manifest_path}. "
                "Run `python -m src.build_lightweight_rag_index` first."
            )
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def _load_game_ids(self) -> list[str]:
        if not self.game_ids_path.exists():
            raise FileNotFoundError(
                f"Missing lightweight RAG game IDs: {self.game_ids_path}. "
                "Run `python -m src.build_lightweight_rag_index` first."
            )
        data = json.loads(self.game_ids_path.read_text(encoding="utf-8"))
        return [str(game_id) for game_id in data]

    def _load_embeddings(self) -> np.ndarray:
        if not self.embeddings_path.exists():
            raise FileNotFoundError(
                f"Missing lightweight RAG embeddings: {self.embeddings_path}. "
                "Run `python -m src.build_lightweight_rag_index` first."
            )
        return np.load(self.embeddings_path, mmap_mode="r")

    def _validate_index_alignment(self) -> None:
        if len(self.game_ids) != int(self.embeddings.shape[0]):
            raise ValueError(
                "Lightweight RAG index mismatch: "
                f"game_ids={len(self.game_ids)}, embeddings={self.embeddings.shape[0]}"
            )

    def _load_catalog_df(self) -> pd.DataFrame:
        df = pd.read_parquet(self.catalog_path)
        df = normalize_embedding_catalog(df)
        for canonical_col, mapped_col in self.COLUMN_MAP.items():
            if canonical_col not in df.columns and mapped_col in df.columns:
                df[canonical_col] = df[mapped_col]
        return df

    def _build_bm25_index(self) -> None:
        tokenized_corpus = []
        self.catalog_by_id = {}
        self.bm25_doc_ids = []

        for _, row in self.catalog_df.iterrows():
            row_data = row.to_dict()
            game_id = str(row_data.get("game_id", "")).strip()
            if not game_id:
                continue
            self.catalog_by_id[game_id] = row_data
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

    def _get_series(self, column_name: str, default_value: object = 0) -> pd.Series:
        df = self.catalog_df
        if df is None or df.empty:
            return pd.Series(dtype="object")

        candidates = [column_name]
        mapped = self.COLUMN_MAP.get(column_name)
        if mapped and mapped not in candidates:
            candidates.append(mapped)
        for canonical, mapped_name in self.COLUMN_MAP.items():
            if mapped_name == column_name and canonical not in candidates:
                candidates.append(canonical)

        for candidate in candidates:
            if candidate in df.columns:
                return df[candidate]
        return pd.Series(default_value, index=df.index)

    def _embed_query(self, query: str) -> np.ndarray:
        model = _get_embedding_model(self.embedding_model_name)
        embedding = model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )[0]
        return np.asarray(embedding, dtype=np.float32)

    def _score_positions(self, query_embedding: np.ndarray, positions: list[int], chunk_size: int = 8192) -> np.ndarray:
        scores = np.empty(len(positions), dtype=np.float32)
        for start in range(0, len(positions), chunk_size):
            end = min(start + chunk_size, len(positions))
            position_chunk = positions[start:end]
            embedding_chunk = np.asarray(self.embeddings[position_chunk], dtype=np.float32)
            scores[start:end] = embedding_chunk @ query_embedding
        return scores

    def _vector_search(self, query: str, n_results: int = 100, allowed_ids: set[str] | None = None) -> list[dict[str, Any]]:
        if not query:
            return []

        if allowed_ids is None:
            positions = list(range(len(self.game_ids)))
        else:
            positions = [
                self.game_id_to_position[game_id]
                for game_id in allowed_ids
                if game_id in self.game_id_to_position
            ]

        if not positions:
            return []

        query_embedding = self._embed_query(query)
        scores = self._score_positions(query_embedding, positions)
        top_n = min(int(n_results), len(positions))
        top_local_indices = np.argsort(scores)[::-1][:top_n]

        hits = []
        for local_idx in top_local_indices:
            position = positions[int(local_idx)]
            game_id = self.game_ids[position]
            similarity = float(scores[int(local_idx)])
            hits.append(
                {
                    "game_id": game_id,
                    "distance": 1.0 - similarity,
                    "similarity": similarity,
                    "vector_rank": len(hits) + 1,
                }
            )
        return hits

    def _bm25_search(self, query: str, n_results: int = 100, allowed_ids: set[str] | None = None) -> list[dict[str, Any]]:
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
        hits = []
        for idx in ranked_indices:
            score = _safe_float(scores[idx], 0.0)
            if score <= 0:
                continue
            game_id = self.bm25_doc_ids[idx]
            if allowed_ids is not None and game_id not in allowed_ids:
                continue
            hits.append({"game_id": game_id, "bm25_score": score, "bm25_rank": len(hits) + 1})
            if len(hits) >= n_results:
                break
        return hits

    def _hybrid_fuse(
        self,
        query: str,
        vector_hits: list[dict[str, Any]],
        bm25_hits: list[dict[str, Any]],
        rrf_k: int = 60,
        vector_weight: float = SEMANTIC_WEIGHT,
        bm25_weight: float = LEXICAL_WEIGHT,
    ) -> list[dict[str, Any]]:
        merged = {}
        vector_rank_map = {hit["game_id"]: hit["vector_rank"] for hit in vector_hits}
        bm25_rank_map = {hit["game_id"]: hit["bm25_rank"] for hit in bm25_hits}
        vector_sim_map = {hit["game_id"]: _safe_float(hit.get("similarity", 0.0), 0.0) for hit in vector_hits}
        bm25_raw_map = {hit["game_id"]: _safe_float(hit.get("bm25_score", 0.0), 0.0) for hit in bm25_hits}
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

        return sorted(merged.values(), key=lambda item: item["hybrid_score"], reverse=True)

    def _parse_csv_values(self, raw_value: object) -> list[str]:
        if raw_value is None:
            return []
        text = str(raw_value).strip()
        if not text:
            return []
        return [part.strip() for part in text.split(",") if part.strip()]

    def _normalize_seed_key(self, text: object) -> str:
        normalized = []
        for part in _tokenize_text(text):
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

    def _acronym_key(self, text: object) -> str:
        parts = _tokenize_text(text)
        if not parts:
            return ""
        normalized_parts = [ROMAN_NUMERAL_MAP.get(part, part) for part in parts]
        return "".join(part[0] for part in normalized_parts if part)

    def _extract_similarity_seed_title(self, query: str) -> str | None:
        q = str(query or "").strip()
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

    def _has_seed_reference_intent(self, query: str) -> bool:
        q = str(query or "").lower()
        if not q:
            return False
        patterns = [
            r"\bsimilar to\b",
            r"\bmore like\b",
            r"\bgames?\s+like\b",
            r"\bi\s+(recently\s+)?played\b",
            r"\brecently\s+played\b",
            r"\bafter\s+playing\b",
            r"\bi\s+(liked|loved|enjoyed)\b",
            r"\bbased on\b",
        ]
        return any(re.search(pattern, q, flags=re.IGNORECASE) for pattern in patterns)

    def _is_specific_seed_title(self, title_tokens: tuple[str, ...]) -> bool:
        if not title_tokens:
            return False
        if len(title_tokens) >= 2:
            return len("".join(title_tokens)) >= 5
        token = title_tokens[0]
        return len(token) >= 5 and token not in GENERIC_SEED_TITLE_TOKENS

    def _find_seed_game(self, seed_title: str | None) -> dict[str, Any] | None:
        if not seed_title:
            return None
        df = self.catalog_df
        if df.empty or "name" not in df.columns:
            return None

        seed_title_lower = str(seed_title).strip().lower()
        direct = df[df["name"].astype(str).str.lower().str.contains(seed_title_lower, na=False, regex=False)]
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

    def _find_seed_game_by_id(self, seed_game_id: object) -> dict[str, Any] | None:
        normalized_seed_id = str(seed_game_id or "").strip()
        if not normalized_seed_id:
            return None
        return self.catalog_by_id.get(normalized_seed_id)

    def _find_seed_games_mentioned_in_query(self, query: str, max_matches: int = 5) -> list[dict[str, Any]]:
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
            matches.append((len(title_tokens), len(name), _safe_float(row.get("total_rating_count"), 0.0), row.to_dict()))

        matches.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
        selected = []
        seen = set()
        for _, _, _, row in matches:
            game_id = str(row.get("game_id", "") or "").strip()
            if not game_id or game_id in seen:
                continue
            seen.add(game_id)
            selected.append(row)
            if len(selected) >= max_matches:
                break
        return selected

    def _append_seed_game(self, seed_games: list[dict[str, Any]], seen_seed_ids: set[str], seed_game: dict[str, Any] | None) -> None:
        if not seed_game:
            return
        game_id = str(seed_game.get("game_id", "") or "").strip()
        if not game_id or game_id in seen_seed_ids:
            return
        seen_seed_ids.add(game_id)
        seed_games.append(seed_game)

    def _get_similar_by_seed_attributes(self, seed_game: dict[str, Any]) -> tuple[set[str], dict[str, float]]:
        seed_game_id = str(seed_game.get("game_id"))
        seed_platforms = self._parse_csv_values(seed_game.get("platforms_list", seed_game.get("platforms")))
        seed_genres = self._parse_csv_values(seed_game.get("genres_list", seed_game.get("genres")))
        seed_themes = self._parse_csv_values(seed_game.get("themes_list", seed_game.get("themes")))
        seed_developers = self._parse_csv_values(seed_game.get("developers_list", seed_game.get("developers")))

        seed_platforms_set = {value.lower() for value in seed_platforms if value}
        seed_genres_set = {value.lower() for value in seed_genres if value}
        seed_themes_set = {value.lower() for value in seed_themes if value}
        seed_developers_set = {value.lower() for value in seed_developers if value}

        def _jaccard(a: set[str], b: set[str]) -> float:
            if not a or not b:
                return 0.0
            union = len(a.union(b))
            return len(a.intersection(b)) / union if union else 0.0

        similar_ids = set()
        boosts = {}
        for game_id, row in self.catalog_by_id.items():
            if str(game_id) == seed_game_id:
                continue
            candidate_platforms = {value.lower() for value in self._parse_csv_values(row.get("platforms_list", row.get("platforms"))) if value}
            candidate_genres = {value.lower() for value in self._parse_csv_values(row.get("genres_list", row.get("genres"))) if value}
            candidate_themes = {value.lower() for value in self._parse_csv_values(row.get("themes_list", row.get("themes"))) if value}
            candidate_developers = {value.lower() for value in self._parse_csv_values(row.get("developers_list", row.get("developers"))) if value}

            genre_j = _jaccard(seed_genres_set, candidate_genres)
            theme_j = _jaccard(seed_themes_set, candidate_themes)
            developer_j = _jaccard(seed_developers_set, candidate_developers)
            platform_j = _jaccard(seed_platforms_set, candidate_platforms)
            boost = (1.4 * genre_j) + (0.8 * theme_j) + (0.5 * developer_j) + (0.3 * platform_j)
            if boost > 0.0:
                similar_ids.add(game_id)
                boosts[game_id] = boost

        return similar_ids, boosts

    def _extract_explicit_requirements(self, query: str) -> dict[str, bool]:
        query_lower = str(query or "").lower()
        return {
            "needs_fishing": _has_term(query_lower, "fishing"),
            "needs_switch": ("nintendo switch" in query_lower) or ("switch" in _tokenize_text(query_lower)),
            "needs_coop": any(phrase in query_lower for phrase in ["co-op", "coop", "co op", "multiplayer"]),
        }

    def _parse_year_constraint(self, query: str) -> int | None:
        q = str(query or "").lower()
        explicit_year_match = re.search(r"\b(19\d{2}|20\d{2}|21\d{2})\b", q)
        if explicit_year_match:
            return int(explicit_year_match.group(1))
        current_year = datetime.now().year
        if re.search(r"\blatest\b", q):
            return current_year
        if re.search(r"\b(new|recent)\b", q):
            return current_year - 1
        return None

    def _extract_hard_constraints(self, query: str) -> dict[str, bool]:
        q = str(query or "").lower()
        require_2d = any(re.search(pattern, q) for pattern in [r"\b2d\s+only\b", r"\bonly\s+2d\b", r"\bstrictly\s+2d\b"])
        exclude_3d = require_2d or any(
            re.search(pattern, q)
            for pattern in [r"\bno\s+3d\b", r"\bwithout\s+3d\b", r"\bavoid\s+3d\b", r"\bexclude\s+3d\b"]
        )
        if _contains_phrase(q, "2d game") and _contains_phrase(q, "no 3d"):
            require_2d = True
            exclude_3d = True
        return {"require_2d": require_2d, "exclude_3d": exclude_3d}

    def _extract_graphics_preference(self, query: str, hard_constraints: dict[str, bool] | None = None) -> dict[str, Any]:
        q = str(query or "").lower()
        hard_constraints = hard_constraints or {}
        return {
            "request_2d": bool(TWO_D_REGEX.search(q)) or bool(hard_constraints.get("require_2d")),
            "avoid_3d": bool(hard_constraints.get("exclude_3d")),
            "two_d_boost": 1.5,
            "three_d_penalty": 0.1,
        }

    def _detect_platform_terms(self, query: str, platforms: list[str] | None) -> list[tuple[str | None, str]]:
        query_lower = str(query or "").lower()
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

        for platform in platforms or []:
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
            elif p.strip():
                requested.append((None, p.strip()))

        deduped = []
        seen = set()
        for item in requested:
            if item in seen:
                continue
            seen.add(item)
            deduped.append(item)
        return deduped

    def _get_prefilter_ids(
        self,
        query: str,
        min_year: int | None = None,
        platforms: list[str] | None = None,
        multiplayer_mode: str | None = None,
    ) -> tuple[set[str], dict[str, bool]]:
        req = self._extract_explicit_requirements(query)
        df = self.catalog_df
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
            broad_mask = pd.Series(True, index=df.index)
            if min_year is not None:
                min_year_value = _safe_int(min_year, 0)
                if min_year_value > 0:
                    release_years = pd.to_numeric(self._get_series("release_year", 0), errors="coerce").fillna(0).astype(int)
                    broad_mask = broad_mask & (release_years >= min_year_value)
            filtered = df[broad_mask]
            if filtered.empty:
                filtered = df

        return set(filtered["game_id"].astype(str).str.strip().tolist()), req

    def _detect_management_domain(self, query: str) -> tuple[str | None, list[str]]:
        query_lower = str(query or "").lower()
        query_tokens = set(_tokenize_text(query_lower))
        has_management_intent = ("manage" in query_tokens) or ("management" in query_tokens)
        if not has_management_intent:
            return None, []
        for domain, keywords in MANAGEMENT_DOMAINS.items():
            if any(keyword in query_tokens or keyword in query_lower for keyword in keywords):
                return domain, keywords
        return None, []

    def _get_management_filter_ids(self, domain_keywords: list[str]) -> set[str] | None:
        if not domain_keywords:
            return None
        summary = self._get_series("summary", "").astype(str).str.lower()
        mask = pd.Series(False, index=self.catalog_df.index)
        for keyword in domain_keywords:
            kw = str(keyword).strip().lower()
            if kw:
                mask = mask | summary.str.contains(kw, na=False)
        return set(self.catalog_df.loc[mask, "game_id"].astype(str).tolist())

    def _passes_filters(
        self,
        row: dict[str, Any],
        min_year: int | None = None,
        platforms: list[str] | None = None,
        multiplayer_mode: str | None = None,
    ) -> bool:
        release_year = _safe_int(row.get("release_year"), 0)
        if min_year is not None and release_year < int(min_year):
            return False
        if platforms:
            db_platforms = row.get("platforms", "") or ""
            if not _contains_any(db_platforms, platforms):
                return False
        if multiplayer_mode:
            mode = str(multiplayer_mode).strip().lower()
            has_online = _safe_int(row.get("mp_online_coop"), 0) == 1 or _safe_int(row.get("mp_max_online_players"), 0) > 0
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

    def _detect_dimension_tags(self, row: dict[str, Any]) -> dict[str, bool]:
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
        return {
            "is_2d_detected": bool(TWO_D_REGEX.search(haystack)),
            "is_3d_detected": bool(THREE_D_REGEX.search(haystack)),
        }

    def _format_text_output(self, text: object, max_len: int = 1000) -> str:
        cleaned = str(text or "").strip()
        if len(cleaned) > max_len:
            return cleaned[:max_len].strip() + "..."
        return cleaned

    def _format_storyline_output(self, summary: str, storyline: str, max_len: int = 1000) -> str:
        summary_text = str(summary or "").strip()
        storyline_text = str(storyline or "").strip()
        combined = f"{summary_text}\n\n{storyline_text}" if summary_text and storyline_text else summary_text or storyline_text
        if len(combined) > max_len:
            return combined[:max_len].strip() + "..."
        return combined

    def search(
        self,
        query: str,
        top_n: int = 5,
        min_year: int | None = None,
        platforms: list[str] | None = None,
        multiplayer_mode: str | None = None,
        vector_k: int = 100,
        bm25_k: int = 100,
        semantic_weight: float = SEMANTIC_WEIGHT,
        lexical_weight: float = LEXICAL_WEIGHT,
        debug_scores: bool = False,
        user_id: str | None = None,
        seed_game_id: str | None = None,
    ) -> list[dict[str, Any]]:
        hard_constraints = self._extract_hard_constraints(query)
        graphics_preference = self._extract_graphics_preference(query, hard_constraints)
        parsed_min_year = self._parse_year_constraint(query)
        effective_min_year = min_year if min_year is not None else parsed_min_year

        allowed_ids, requirements = self._get_prefilter_ids(
            query=query,
            min_year=effective_min_year,
            platforms=platforms,
            multiplayer_mode=multiplayer_mode,
        )

        seed_similarity_boosts: dict[str, float] = {}
        seed_filter_ids: set[str] = set()
        seed_exclusion_ids: set[str] = set()
        seed_games: list[dict[str, Any]] = []
        seen_seed_ids: set[str] = set()

        if seed_game_id is not None:
            self._append_seed_game(seed_games, seen_seed_ids, self._find_seed_game_by_id(seed_game_id))
        else:
            seed_title = self._extract_similarity_seed_title(query)
            if seed_title:
                self._append_seed_game(seed_games, seen_seed_ids, self._find_seed_game(seed_title))

        for seed_game in self._find_seed_games_mentioned_in_query(query):
            self._append_seed_game(seed_games, seen_seed_ids, seed_game)

        for seed_game in seed_games:
            seed_id = str(seed_game.get("game_id", "") or "").strip()
            if seed_id:
                seed_exclusion_ids.add(seed_id)
            current_seed_ids, current_boosts = self._get_similar_by_seed_attributes(seed_game)
            seed_filter_ids.update(current_seed_ids)
            for game_id, boost in current_boosts.items():
                seed_similarity_boosts[game_id] = max(
                    _safe_float(seed_similarity_boosts.get(game_id), 0.0),
                    _safe_float(boost, 0.0),
                )

        if seed_exclusion_ids:
            allowed_ids = allowed_ids.difference(seed_exclusion_ids)

        management_domain, domain_keywords = self._detect_management_domain(query)
        if management_domain:
            management_filter_ids = self._get_management_filter_ids(domain_keywords)
            if not management_filter_ids:
                return []
            allowed_ids = allowed_ids.intersection(management_filter_ids)
            if not allowed_ids:
                return []

        if not allowed_ids:
            allowed_ids = set(self.catalog_by_id.keys()).difference(seed_exclusion_ids)

        vector_hits = self._vector_search(query=query, n_results=vector_k, allowed_ids=allowed_ids)
        bm25_hits = self._bm25_search(query=query, n_results=bm25_k, allowed_ids=allowed_ids)
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
            game_id = str(hit["game_id"])
            if game_id in seed_exclusion_ids:
                continue
            row = self.catalog_by_id.get(game_id)
            if not row:
                continue
            if not self._passes_filters(row, min_year=effective_min_year, platforms=platforms, multiplayer_mode=multiplayer_mode):
                continue

            summary = self._format_text_output(row.get("summary"), max_len=1000)
            storyline = self._format_text_output(row.get("storyline"), max_len=1000)
            dimension_tags = self._detect_dimension_tags(row)
            candidates.append(
                {
                    "game_id": game_id,
                    "name": row.get("name", "Not Listed"),
                    "release_year": _safe_int(row.get("release_year"), 0),
                    "platforms": row.get("platforms", "Not Listed"),
                    "summary": summary,
                    "storyline": storyline,
                    "storyline_summary": self._format_storyline_output(summary, storyline, max_len=1000),
                    "total_rating": _safe_float(row.get("total_rating"), 0.0),
                    "playtime_normally": _safe_float(row.get("playtime_normally", row.get("normal_playtime_hours")), 0.0),
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
                candidate
                for candidate in candidates
                if (
                    "fishing" in str(candidate.get("genres", "") or "").lower()
                    or "fishing" in str(candidate.get("themes", "") or "").lower()
                    or "fishing" in str(candidate.get("name", "") or "").lower()
                    or "fishing" in str(candidate.get("summary", "") or "").lower()
                )
            ]
            if not candidates:
                return []

        ranked = rank_results(candidates, graphics_preference=graphics_preference)
        if debug_scores:
            for idx, item in enumerate(ranked[:5], start=1):
                print(
                    "[LightweightHybridDebug] "
                    f"{idx}. {item.get('name', 'Unknown')} | "
                    f"NormVec={_safe_float(item.get('normalized_vec'), 0.0):.4f} | "
                    f"NormBM25={_safe_float(item.get('normalized_bm25'), 0.0):.4f} | "
                    f"Final={_safe_float(item.get('primary_rank_score'), 0.0):.4f}"
                )
        return ranked[:top_n]


if __name__ == "__main__":
    agent = LightweightRAGAgent()
    results = agent.search("I played Hades and Dead Cells recently. Recommend similar games.", top_n=5, debug_scores=True)
    for idx, result in enumerate(results, start=1):
        print(f"{idx}. {result.get('name')} ({result.get('release_year')})")
