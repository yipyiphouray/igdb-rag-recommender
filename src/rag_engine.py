import chromadb
from chromadb.utils import embedding_functions


class RAGAgent:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./data/vector_store")
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_collection(
            name="igdb_game_profiles", 
            embedding_function=self.embedding_fn
        )

    def search(self, query, platform=None, top_n=3):
        results = self.collection.query(
            query_texts=[query],
            n_results=10
        )

        candidates = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        for idx, (doc, meta) in enumerate(zip(docs, metas)):
            try:
                meta = meta if isinstance(meta, dict) else {}

                # Fuzzy platform filter (substring match).
                if platform and platform.lower() not in meta.get("platforms", "").lower():
                    continue

                name = meta.get("name", "Not Listed")
                platforms = meta.get("platforms", "Not Listed")
                developers = meta.get("developers", "Not Listed")
                total_rating = float(meta.get("total_rating", 0) or 0)

                candidates.append(
                    {
                        "name": name,
                        "description": (doc or "")[:250] + "...",
                        "platforms": platforms,
                        "developers": developers,
                        "total_rating": total_rating,
                    }
                )
            except Exception as exc:
                print(f"[WARN] Skipping candidate at index {idx} due to metadata error: {exc}")
                continue

        # Fine-grained ranking: highest numerical rating first.
        candidates.sort(key=lambda x: x.get("total_rating", 0), reverse=True)
        return candidates[:top_n]


if __name__ == "__main__":
    agent = RAGAgent()
    print("Agent initialized. Testing queries...")

    test_query = "A cozy game for friends"
    results = agent.search(test_query, platform="Switch")

    print(f"\nResults for '{test_query}' on Switch:")
    for i, match in enumerate(results):
        print(f"\n{i+1}. {match['name']} (Rating: {match.get('total_rating', 0):.1f})")
        print(f"   Platforms: {match['platforms']}")
        print(f"   Description: {match['description']}")
