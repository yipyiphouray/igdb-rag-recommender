from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import List, Tuple

import chromadb
import numpy as np
import pandas as pd
from chromadb.utils import embedding_functions


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.app.embedding_text import build_embedding_text

PARQUET_PATH = ROOT_DIR / "data" / "app" / "app_game_catalog.parquet"
VECTOR_DB_DIR = ROOT_DIR / "data" / "vector_store"
COLLECTION_NAME = "igdb_game_profiles"
MODEL_NAME = "all-MiniLM-L6-v2"


@dataclass
class AuditConfig:
    sample_rows: int = 5
    stats_sample_size: int = 100
    seed: int = 42


def _prepare_text_for_embedding(row: pd.Series) -> str:
    return build_embedding_text(row)


def _load_catalog() -> pd.DataFrame:
    df = pd.read_parquet(PARQUET_PATH)
    if "game_id" not in df.columns:
        raise ValueError("Parquet catalog missing required column: game_id")
    df = df.copy()
    df["game_id"] = df["game_id"].astype(str)
    return df


def _load_collection() -> tuple[chromadb.Collection, embedding_functions.SentenceTransformerEmbeddingFunction]:
    client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)
    return collection, embedding_fn


def _similarity_from_distance(distance: float) -> float:
    return 1.0 - float(distance)


def data_content_sampling(df: pd.DataFrame, collection: chromadb.Collection, cfg: AuditConfig) -> None:
    print("\n=== Data Content Sampling ===")
    sampled = df.sample(n=min(cfg.sample_rows, len(df)), random_state=cfg.seed)

    vectors = []
    for idx, (_, row) in enumerate(sampled.iterrows(), start=1):
        game_id = str(row["game_id"])
        text = _prepare_text_for_embedding(row)
        print(f"\n[{idx}] game_id={game_id}")
        print(f"Text: {text[:300]}")

        res = collection.get(ids=[game_id], include=["embeddings", "documents", "metadatas"])
        embeddings = res.get("embeddings")
        emb = None
        if embeddings is not None and len(embeddings) > 0:
            emb = embeddings[0]
        if emb is None:
            raise ValueError(f"Missing embedding in vector store for game_id={game_id}")

        emb_arr = np.array(emb, dtype=float)
        first_five = emb_arr[:5].tolist()
        print(f"Embedding[:5]: {first_five}")

        if np.allclose(emb_arr, 0.0):
            raise ValueError(f"Zero vector detected for game_id={game_id}")

        vectors.append(emb_arr)

    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            if np.allclose(vectors[i], vectors[j]):
                raise ValueError("Duplicate/identical vectors detected across different sampled rows")

    print("[OK] Sampled vectors are non-zero and not identical.")


def semantic_diversity_test(collection: chromadb.Collection) -> None:
    print("\n=== Semantic Diversity Test ===")
    queries = ["horror game", "racing game", "open world RPG"]

    top_game_sets = []
    top_score_sets = []

    for query in queries:
        result = collection.query(query_texts=[query], n_results=3, include=["distances", "metadatas", "documents"])
        ids = result.get("ids", [[]])[0]
        distances = result.get("distances", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0] if result.get("metadatas") else [{} for _ in ids]

        print(f"\nQuery: {query}")
        top_ids = []
        top_scores = []
        for rank, (gid, dist, meta) in enumerate(zip(ids, distances, metadatas), start=1):
            name = (meta or {}).get("name", "Unknown")
            similarity = _similarity_from_distance(dist)
            top_ids.append(str(gid))
            top_scores.append(round(similarity, 6))
            print(f"  {rank}. game_id={gid} | name={name} | similarity={similarity:.4f}")

        top_game_sets.append(tuple(top_ids))
        top_score_sets.append(tuple(top_scores))

    all_same_games = len(set(top_game_sets)) == 1
    all_same_scores = len(set(top_score_sets)) == 1
    if all_same_games or all_same_scores:
        raise ValueError("Vector collapse detected")

    print("[OK] Semantic diversity check passed.")


def self_similarity_check(df: pd.DataFrame, collection: chromadb.Collection, embedding_fn) -> None:
    print("\n=== Self-Similarity Check ===")
    target_name = "It Takes Two"
    matches = df[df["name"].astype(str).str.lower() == target_name.lower()]
    if matches.empty:
        raise ValueError(f"Target game not found in catalog: {target_name}")

    row = matches.iloc[0]
    target_id = str(row["game_id"])
    text = _prepare_text_for_embedding(row)
    if not text:
        raise ValueError(f"Target game has empty embedding text: {target_name}")

    query_embedding = embedding_fn([text])[0]
    result = collection.query(query_embeddings=[query_embedding], n_results=5, include=["distances", "metadatas"])

    ids = result.get("ids", [[]])[0]
    distances = result.get("distances", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0] if result.get("metadatas") else [{} for _ in ids]

    print(f"Target: {target_name} (game_id={target_id})")
    for rank, (gid, dist, meta) in enumerate(zip(ids, distances, metadatas), start=1):
        sim = _similarity_from_distance(dist)
        print(f"  {rank}. game_id={gid} | name={(meta or {}).get('name', 'Unknown')} | similarity={sim:.4f}")

    if not ids:
        raise ValueError("Self-similarity query returned no results")

    top_id = str(ids[0])
    top_similarity = _similarity_from_distance(distances[0])

    if top_id != target_id or top_similarity <= 0.95:
        raise ValueError(
            f"Self-similarity failed: expected #1={target_id} with similarity>0.95, "
            f"got #1={top_id} similarity={top_similarity:.4f}"
        )

    print("[OK] Self-similarity check passed.")


def statistical_check(collection: chromadb.Collection, cfg: AuditConfig) -> None:
    print("\n=== Statistical Check ===")
    total = collection.count()
    sample_size = min(cfg.stats_sample_size, total)
    if sample_size == 0:
        raise ValueError("Collection is empty")

    # Grab a deterministic prefix sample from collection IDs
    ids_page = collection.get(limit=sample_size, include=[])
    ids = ids_page.get("ids", [])
    if not ids:
        raise ValueError("Could not fetch IDs from collection for statistical check")

    vectors = collection.get(ids=ids, include=["embeddings"]).get("embeddings", None)
    if vectors is None or len(vectors) == 0:
        raise ValueError("No embeddings returned for statistical check")

    arr = np.array(vectors, dtype=float)
    mean_val = float(arr.mean())
    std_val = float(arr.std())

    print(f"Sample size: {arr.shape[0]} vectors")
    print(f"Mean: {mean_val:.6f}")
    print(f"Std:  {std_val:.6f}")

    if std_val < 1e-6:
        raise ValueError("Embedding collapse detected: std is near zero")

    print("[OK] Statistical variance check passed.")


def run_audit() -> None:
    cfg = AuditConfig()
    print("--- Vector Health Audit ---")
    print(f"Catalog path: {PARQUET_PATH}")
    print(f"Vector DB path: {VECTOR_DB_DIR}")

    df = _load_catalog()
    collection, embedding_fn = _load_collection()

    print(f"Catalog rows: {len(df)}")
    print(f"Collection rows: {collection.count()}")

    data_content_sampling(df, collection, cfg)
    semantic_diversity_test(collection)
    self_similarity_check(df, collection, embedding_fn)
    statistical_check(collection, cfg)

    print("\n[SUCCESS] Vector health audit passed.")


if __name__ == "__main__":
    run_audit()
