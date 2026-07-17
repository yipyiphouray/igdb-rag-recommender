from pathlib import Path
import shutil

import chromadb
import pandas as pd
from chromadb.utils import embedding_functions


COLUMN_MAP = {
    "platforms": "platforms_list",
    "genres": "genres_list",
    "playtime": "normal_playtime_hours",
    "developers": "developers_list",
    "themes": "themes_list",
}


def _ensure_column(df, canonical_name, default_value=""):
    mapped_name = COLUMN_MAP.get(canonical_name)
    if canonical_name not in df.columns and mapped_name in df.columns:
        df[canonical_name] = df[mapped_name]
    if canonical_name not in df.columns:
        df[canonical_name] = default_value


def _normalize_catalog(df):
    _ensure_column(df, "name", "Unknown")
    _ensure_column(df, "game_id", "")
    _ensure_column(df, "rag_text_profile", "")
    _ensure_column(df, "platforms", "Not Listed")
    _ensure_column(df, "developers", "Not Listed")
    _ensure_column(df, "genres", "")
    _ensure_column(df, "themes", "")
    _ensure_column(df, "total_rating", 0.0)

    safe_df = df.copy()
    safe_df["name"] = safe_df["name"].fillna("Unknown").astype(str)
    safe_df["game_id"] = safe_df["game_id"].fillna("").astype(str)
    safe_df["rag_text_profile"] = safe_df["rag_text_profile"].fillna("").astype(str)
    safe_df["platforms"] = safe_df["platforms"].fillna("Not Listed").astype(str)
    safe_df["developers"] = safe_df["developers"].fillna("Not Listed").astype(str)
    safe_df["genres"] = safe_df["genres"].fillna("").astype(str)
    safe_df["themes"] = safe_df["themes"].fillna("").astype(str)
    safe_df["total_rating"] = pd.to_numeric(safe_df["total_rating"], errors="coerce").fillna(0.0)
    safe_df["is_high_rated"] = (safe_df["total_rating"] >= 80).astype(int)

    safe_df = safe_df[safe_df["game_id"].str.strip() != ""].copy()
    safe_df = safe_df.drop_duplicates(subset=["game_id"], keep="first")
    return safe_df


def _prepare_text_for_embedding(row):
    name = str(row.get("name", "") or "").strip()
    summary = str(row.get("summary", "") or "").strip()
    genres_list = str(row.get("genres_list", row.get("genres", "")) or "").strip()
    combined = " | ".join([part for part in [name, summary, genres_list] if part])
    return combined.strip()


def initialize_intelligence_layer():
    print("--- Initializing RAG Intelligence Layer ---")

    root_dir = Path(__file__).resolve().parent.parent
    parquet_path = root_dir / "data" / "app" / "app_game_catalog.parquet"
    vector_db_dir = root_dir / "data" / "vector_store"

    print(f"-> Loading catalog from: {parquet_path}")
    df = pd.read_parquet(parquet_path)
    safe_df = _normalize_catalog(df)

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

    metadata_cols = ["name", "platforms", "developers", "genres", "themes", "total_rating", "is_high_rated"]
    _ensure_column(safe_df, "summary", "")
    _ensure_column(safe_df, "genres_list", safe_df.get("genres", ""))

    filtered_rows = []
    skipped_empty = 0
    for _, row in safe_df.iterrows():
        text_for_embedding = _prepare_text_for_embedding(row)
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
