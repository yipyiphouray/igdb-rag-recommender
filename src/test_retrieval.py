import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

def test_retrieval(query):
    print(f"Searching for: '{query}'...")
    
    ROOT_DIR = Path(__file__).resolve().parent.parent
    VECTOR_DB_DIR = ROOT_DIR / "data" / "vector_store"
    
    # 1. Connect to your materialized brain
    chroma_client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    collection = chroma_client.get_collection(
        name="igdb_game_profiles", 
        embedding_function=embedding_fn
    )
    
    # 2. Query the brain
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    
    # 3. Print the matches
    print("\nTop 3 Matches:")
    for i, name in enumerate(results['metadatas'][0]):
        print(f"{i+1}: {name['name']}")

if __name__ == "__main__":
    # Test a complex query that isn't just a genre
    test_retrieval("I want a dark, atmospheric game with a deep mystery story.")