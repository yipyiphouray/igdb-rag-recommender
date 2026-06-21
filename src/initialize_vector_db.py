import sqlite3
import pandas as pd
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

def chunk_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]

def initialize_intelligence_layer():
    print("--- Initializing RAG Intelligence Layer ---")

    ROOT_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = ROOT_DIR / "data" / "database" / "igdb_games.db"
    VECTOR_DB_DIR = ROOT_DIR / "data" / "vector_store"
    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        game_id,
        IFNULL(name, 'Unknown') AS name,
        IFNULL(rag_text_profile, '') AS rag_text_profile,
        IFNULL(platforms, 'Not Listed') AS platforms,
        IFNULL(developers, 'Not Listed') AS developers,
        IFNULL(total_rating, 0.0) AS total_rating,
        CASE WHEN IFNULL(total_rating, 0) >= 80 THEN 1 ELSE 0 END AS is_high_rated
    FROM analytics_ready_games;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    safe_df = df.fillna({
        "name": "Unknown",
        "rag_text_profile": "",
        "platforms": "Not Listed",
        "developers": "Not Listed",
        "total_rating": 0.0,
        "is_high_rated": 0,
    })

    chroma_client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    # Clear old collection to avoid ID collisions during re-indexing
    chroma_client.delete_collection("igdb_game_profiles")
    collection = chroma_client.create_collection(
        name="igdb_game_profiles",
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"}
    )

    metadata_cols = ["name", "platforms", "developers", "total_rating", "is_high_rated"]
    
    # Prepare full data lists
    docs = safe_df["rag_text_profile"].astype(str).tolist()
    ids = safe_df["game_id"].astype(str).tolist()
    metadatas = safe_df[metadata_cols].to_dict(orient="records")

    # Batch process to stay under Chroma's limit
    batch_size = 4000
    print(f"-> Indexing {len(safe_df)} games in batches of {batch_size}...")
    
    for i in range(0, len(docs), batch_size):
        end = i + batch_size
        collection.upsert(
            documents=docs[i:end],
            ids=ids[i:end],
            metadatas=metadatas[i:end]
        )
        print(f"   Indexed batch {i} to {min(end, len(docs))}")

    print(f"[SUCCESS] Vector store updated. Total count: {collection.count()}")

if __name__ == "__main__":
    initialize_intelligence_layer()