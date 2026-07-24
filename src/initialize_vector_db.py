from pathlib import Path
import shutil
import sys

import chromadb
import pandas as pd
from chromadb.utils import embedding_functions

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.app.embedding_text import (
    EMBEDDING_METADATA_COLUMNS,
    build_embedding_text,
    normalize_embedding_catalog,
)


def initialize_intelligence_layer():
    print("--- Initializing RAG Intelligence Layer ---")

    parquet_path = ROOT_DIR / "data" / "app" / "app_game_catalog.parquet"
    vector_db_dir = ROOT_DIR / "data" / "vector_store"

    print(f"-> Loading catalog from: {parquet_path}")
    df = pd.read_parquet(parquet_path)
    safe_df = normalize_embedding_catalog(df)

    if vector_db_dir.exists():
        print(f"-> Clearing existing vector store directory: {vector_db_dir}")
        shutil.rmtree(vector_db_dir)
    vector_db_dir.mkdir(parents=True, exist_ok=True)

    chroma_client = chromadb.PersistentClient(path=str(vector_db_dir))
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    collection = chroma_client.create_collection(
        name="igdb_game_profiles",
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )

    metadata_cols = [column for column in EMBEDDING_METADATA_COLUMNS if column in safe_df.columns]

    filtered_rows = []
    skipped_empty = 0
    for _, row in safe_df.iterrows():
        text_for_embedding = build_embedding_text(row)
        if not text_for_embedding:
            skipped_empty += 1
            print(f"[WARN] Skipping empty embedding text for game_id={row.get('game_id', '')}")
            continue
        row_dict = row.to_dict()
        row_dict["embedding_text"] = text_for_embedding
        filtered_rows.append(row_dict)

    prepared_df = pd.DataFrame(filtered_rows)
    docs = prepared_df["embedding_text"].tolist() if not prepared_df.empty else []
    ids = prepared_df["game_id"].astype(str).tolist() if not prepared_df.empty else []
    metadatas = prepared_df[metadata_cols].to_dict(orient="records") if not prepared_df.empty else []

    batch_size = 4000
    total = len(docs)
    print(f"-> Indexing full catalog: {total} games in batches of {batch_size}...")
    if skipped_empty > 0:
        print(f"[WARN] Skipped {skipped_empty} rows due to empty embedding text")

    debug_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    debug_printed = 0

    for i in range(0, total, batch_size):
        end = min(i + batch_size, total)
        if debug_printed < 3:
            for j in range(i, min(end, i + (3 - debug_printed))):
                sample_text = docs[j]
                print(f"[DEBUG] text sample ({debug_printed + 1}): {sample_text[:50]}")
                sample_embedding = debug_embedding_fn([sample_text])[0]
                first_five = [float(x) for x in sample_embedding[:5]]
                print(f"[DEBUG] embedding[:5] ({debug_printed + 1}): {first_five}")
                if all(v == 0.0 for v in first_five):
                    print(f"[WARN] Zero embedding prefix detected for sample {debug_printed + 1}")
                debug_printed += 1

        collection.upsert(
            documents=docs[i:end],
            ids=ids[i:end],
            metadatas=metadatas[i:end],
        )
        print(f"   Indexed batch {i} to {end}")

    final_count = collection.count()
    print(f"[SUCCESS] Vector store updated. Final collection count: {final_count}")
    print(f"[VALIDATION] Catalog rows: {total} | Collection rows: {final_count}")


if __name__ == "__main__":
    initialize_intelligence_layer()
