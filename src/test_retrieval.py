import chromadb
from chromadb.utils import embedding_functions

def _normalize_platform_requirements(platform_reqs):
    if platform_reqs is None:
        return []
    if isinstance(platform_reqs, str):
        return [platform_reqs.strip().lower()] if platform_reqs.strip() else []
    return [str(p).strip().lower() for p in platform_reqs if str(p).strip()]


def _doc_contains_all_terms(doc_text, terms):
    doc_l = (doc_text or "").lower()
    return all(term in doc_l for term in terms)


def intelligent_hybrid_search(
    query_vibe,
    platform_reqs=None,
    include_multiplayer=False,
    top_k=3,
    candidate_pool=20,
    vector_store_path="./data/vector_store",
    collection_name="igdb_game_profiles",
):
    """
    Hybrid semantic + rule-based retrieval with robust platform filtering.

    Args:
        query_vibe (str): semantic query, e.g. "cozy, relaxing"
        platform_reqs (str | list[str] | None): required platforms, e.g.
            "Nintendo Switch" or ["PC", "PlayStation 5"]
        include_multiplayer (bool): if True, keep only multiplayer-like entries
        top_k (int): number of final recommendations
        candidate_pool (int): size of initial candidate retrieval pool
    """
    platform_terms = _normalize_platform_requirements(platform_reqs)

    chroma_client = chromadb.PersistentClient(path=vector_store_path)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = chroma_client.get_collection(name=collection_name, embedding_function=embedding_fn)

    # Try native Chroma filtering first via where_document when platform terms exist.
    # This is a best-effort filter because most setups store platforms inside rag_text_profile text.
    primary_results = None
    if platform_terms:
        try:
            where_document = {"$and": [{"$contains": term} for term in platform_terms]}
            primary_results = collection.query(
                query_texts=[query_vibe],
                n_results=candidate_pool,
                where_document=where_document,
            )
        except Exception:
            primary_results = None

    # Always keep an unfiltered result set for fallback.
    unfiltered_results = collection.query(
        query_texts=[query_vibe],
        n_results=max(candidate_pool, top_k),
    )

    active_results = primary_results or unfiltered_results

    filtered_names = []
    for doc, meta in zip(active_results.get("documents", [[]])[0], active_results.get("metadatas", [[]])[0]):
        platforms_text = (meta.get("platforms", "") if meta else "")
        combined_text = f"{platforms_text} {doc or ''}".lower()

        if platform_terms and not all(term in combined_text for term in platform_terms):
            continue
        if include_multiplayer and "multiplayer" not in combined_text:
            continue

        filtered_names.append(meta.get("name", "Unknown Game") if meta else "Unknown Game")
        if len(filtered_names) >= top_k:
            break

    # Fallback: strict filters found no matches; return best semantic matches anyway.
    if not filtered_names:
        print("[WARN] No matches after hard filters. Returning top semantic matches without platform filters.")
        fallback_names = []
        for doc, meta in zip(unfiltered_results.get("documents", [[]])[0], unfiltered_results.get("metadatas", [[]])[0]):
            if include_multiplayer and not _doc_contains_all_terms(doc, ["multiplayer"]):
                continue
            fallback_names.append(meta.get("name", "Unknown Game") if meta else "Unknown Game")
            if len(fallback_names) >= top_k:
                break
        return fallback_names

    return filtered_names

if __name__ == "__main__":
    # Test: Cozy + Switch + Multiplayer
    matches = intelligent_hybrid_search(
        query_vibe="cozy, time with friends", 
        platform_reqs="Nintendo Switch",
        include_multiplayer=True
    )
    print(f"Top 3 recommendations: {matches}")
