import sqlite3
import pandas as pd
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

def initialize_intelligence_layer():
    print("--- Initializing RAG Intelligence Layer ---")
    
    # 1. Paths
    ROOT_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = ROOT_DIR / "data" / "database" / "igdb_games.db"
    VECTOR_DB_DIR = ROOT_DIR / "data" / "vector_store"
    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
    
    # 2. Extract from your new analytics view
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    # This query pulls the exact column your build script just created
    df = pd.read_sql_query("SELECT game_id, name, rag_text_profile FROM analytics_ready_games;", conn)
    conn.close()
    
    print(f"-> Extracted {len(df)} profiles.")
    
    # 3. Chroma Initialization
    chroma_client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    collection = chroma_client.get_or_create_collection(
        name="igdb_game_profiles",
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"}
    )
    
    # 4. Upsert (Create or Update vectors)
    print("-> Indexing into Vector Store...")
    collection.upsert(
        documents=df["rag_text_profile"].tolist(),
        ids=df["game_id"].astype(str).tolist(),
        metadatas=df[["name"]].to_dict(orient="records")
    )
    
    print(f"[SUCCESS] Vector store materialized. Count: {collection.count()}")

if __name__ == "__main__":
    initialize_intelligence_layer()