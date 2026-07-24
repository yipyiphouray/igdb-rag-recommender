from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from src.app import config
from src.app.embedding_text import build_embedding_text, normalize_embedding_catalog
from src.lightweight_rag_engine import (
    EMBEDDING_MODEL_NAME,
    LIGHTWEIGHT_EMBEDDINGS_PATH,
    LIGHTWEIGHT_GAME_IDS_PATH,
    LIGHTWEIGHT_MANIFEST_PATH,
    LIGHTWEIGHT_RAG_DIR,
)


CHROMA_COLLECTION_NAME = "igdb_game_profiles"
CHROMA_VECTOR_STORE_PATH = config.DATA_DIR / "vector_store"


def _atomic_write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=str(path.parent), suffix=".tmp") as file:
        json.dump(data, file, indent=2)
        temp_name = file.name
    os.replace(temp_name, path)


def _atomic_save_npy(path: Path, array: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=str(path.parent), suffix=".npy.tmp") as file:
        temp_name = file.name
    try:
        with open(temp_name, "wb") as file:
            np.save(file, array)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.remove(temp_name)


def _build_embedding_texts(df: pd.DataFrame) -> list[str]:
    return [build_embedding_text(row) for _, row in df.iterrows()]


def _convert_embedding_dtype(embeddings: np.ndarray, dtype: str) -> np.ndarray:
    if dtype == "float16":
        return embeddings.astype(np.float16)
    return embeddings.astype(np.float32)


def _load_from_chroma(
    *,
    batch_size: int,
    dtype: str,
    max_games: int | None = None,
) -> tuple[list[str], np.ndarray, dict]:
    import chromadb

    client = chromadb.PersistentClient(path=str(CHROMA_VECTOR_STORE_PATH))
    collection = client.get_collection(name=CHROMA_COLLECTION_NAME)
    collection_count = int(collection.count())
    target_count = min(collection_count, int(max_games)) if max_games is not None else collection_count

    game_ids: list[str] = []
    embedding_batches: list[np.ndarray] = []

    for offset in range(0, target_count, batch_size):
        limit = min(batch_size, target_count - offset)
        batch = collection.get(
            limit=limit,
            offset=offset,
            include=["embeddings"],
        )
        ids = [str(game_id) for game_id in batch.get("ids", [])]
        raw_embeddings = batch.get("embeddings")
        if raw_embeddings is None or len(ids) == 0:
            continue
        embeddings = np.asarray(raw_embeddings, dtype=np.float32)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-12
        embeddings = embeddings / norms
        game_ids.extend(ids)
        embedding_batches.append(embeddings)
        print(f"Exported Chroma embeddings: {len(game_ids):,}/{target_count:,}")

    if not embedding_batches:
        raise RuntimeError("No embeddings were exported from the Chroma collection.")

    embeddings = np.vstack(embedding_batches)
    embeddings = _convert_embedding_dtype(embeddings, dtype)
    source_metadata = {
        "source": "chroma",
        "source_collection": CHROMA_COLLECTION_NAME,
        "source_vector_store": str(CHROMA_VECTOR_STORE_PATH.as_posix()),
        "source_collection_count": collection_count,
    }
    return game_ids, embeddings, source_metadata


def _load_from_sentence_transformers(
    *,
    catalog_path: Path,
    model_name: str,
    batch_size: int,
    dtype: str,
    max_games: int | None = None,
) -> tuple[list[str], np.ndarray, dict]:
    from sentence_transformers import SentenceTransformer

    df = pd.read_parquet(catalog_path)
    safe_df = normalize_embedding_catalog(df)
    if max_games is not None:
        safe_df = safe_df.head(max(1, int(max_games))).copy()

    game_ids = safe_df["game_id"].astype(str).tolist()
    texts = _build_embedding_texts(safe_df)

    model = SentenceTransformer(model_name)
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    )
    embeddings = _convert_embedding_dtype(embeddings, dtype)
    source_metadata = {
        "source": "sentence-transformers",
        "source_collection": None,
        "source_vector_store": None,
        "source_collection_count": None,
    }
    return game_ids, embeddings, source_metadata


def build_lightweight_rag_index(
    *,
    catalog_path: Path = config.APP_CATALOG_PATH,
    output_dir: Path = LIGHTWEIGHT_RAG_DIR,
    model_name: str = EMBEDDING_MODEL_NAME,
    batch_size: int = 128,
    dtype: str = "float16",
    max_games: int | None = None,
    source: str = "sentence-transformers",
) -> dict:
    if dtype not in {"float16", "float32"}:
        raise ValueError("dtype must be either 'float16' or 'float32'")
    if source not in {"sentence-transformers", "chroma"}:
        raise ValueError("source must be either 'sentence-transformers' or 'chroma'")
    if not catalog_path.exists():
        raise FileNotFoundError(f"Missing app catalog: {catalog_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    embeddings_path = output_dir / LIGHTWEIGHT_EMBEDDINGS_PATH.name
    game_ids_path = output_dir / LIGHTWEIGHT_GAME_IDS_PATH.name
    manifest_path = output_dir / LIGHTWEIGHT_MANIFEST_PATH.name

    if source == "chroma":
        game_ids, embeddings, source_metadata = _load_from_chroma(
            batch_size=batch_size,
            dtype=dtype,
            max_games=max_games,
        )
    else:
        game_ids, embeddings, source_metadata = _load_from_sentence_transformers(
            catalog_path=catalog_path,
            model_name=model_name,
            batch_size=batch_size,
            dtype=dtype,
            max_games=max_games,
        )

    _atomic_save_npy(embeddings_path, embeddings)
    _atomic_write_json(game_ids_path, game_ids)

    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "catalog_path": str(catalog_path.as_posix()),
        "row_count": len(game_ids),
        "embedding_shape": list(embeddings.shape),
        "embedding_dtype": str(embeddings.dtype),
        "model_name": model_name,
        "embedding_text_profile": "src.app.embedding_text.build_embedding_text",
        "embeddings_path": str(embeddings_path.as_posix()),
        "game_ids_path": str(game_ids_path.as_posix()),
        **source_metadata,
    }
    _atomic_write_json(manifest_path, manifest)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Chroma-free lightweight RAG embedding index.")
    parser.add_argument("--catalog", type=Path, default=config.APP_CATALOG_PATH)
    parser.add_argument("--output-dir", type=Path, default=LIGHTWEIGHT_RAG_DIR)
    parser.add_argument("--model", default=EMBEDDING_MODEL_NAME)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--dtype", choices=["float16", "float32"], default="float16")
    parser.add_argument("--max-games", type=int, default=None)
    parser.add_argument("--source", choices=["sentence-transformers", "chroma"], default="sentence-transformers")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = build_lightweight_rag_index(
        catalog_path=args.catalog,
        output_dir=args.output_dir,
        model_name=args.model,
        batch_size=args.batch_size,
        dtype=args.dtype,
        max_games=args.max_games,
        source=args.source,
    )
    print(json.dumps(result, indent=2))
