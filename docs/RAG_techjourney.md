# Technical Journey: IGDB RAG Recommender System

## Overview
This project implements a Retrieval-Augmented Generation (RAG) system for video game recommendations, utilizing SQLite as a relational source-of-truth and ChromaDB for semantic vector retrieval.

## Completed Pipeline
1.  **Data Engineering:** Developed `Build_FeatureEngineering.py` to aggregate raw game data into a unified `analytics_ready_games` view. 
    * *Improvement:* Implemented CTEs and `GROUP_CONCAT` to handle multi-value relational data (platforms, developers, publishers) as searchable "text blobs."
2.  **Semantic Indexing:** Established `initialize_vector_db.py` to map SQL views to vector embeddings using `SentenceTransformer`.
3.  **Hybrid Retrieval Engine:** Created `rag_engine.py` which combines vector-based semantic search with custom metadata filtering (Fuzzy String Matching) to handle specific user requests (e.g., "Switch" platform).


## Current Ranking Architecture (Decoupled from ML)

* **Status**: Active.
* **RAG Retrieval Pipeline**:
  * **Hybrid candidate generation**: Vector retrieval + BM25 lexical retrieval.
  * **Fusion**: Reciprocal Rank Fusion (RRF) combines both retrieval signals.
  * **Metadata-aware adjustment**: Existing metadata boosts/penalties are applied for hard preference alignment.
* **Important decoupling**: The RAG engine no longer depends on the Random Forest predictive model for ranking. RAG ranking is now independent and based on hybrid retrieval relevance (`RRF + metadata`) only.

## Recommendation Layer Separation

The content-based recommender is now a separate module (`recommender_engine.py`) that serves questionnaire-driven top-N recommendations via cosine similarity. This separation enables:

* Independent evolution of semantic discovery (RAG) and recommendation scoring.
* Cleaner observability of retrieval quality versus preference matching quality.
* Reduced coupling between conversational retrieval and questionnaire personalization logic.

## Attribute-Boosted Seed Retrieval

The RAG engine now supports an explicit seed-game retrieval mode (`seed_game_id`) for high-precision similarity discovery.

1. The engine fetches seed attributes (`platforms`, `genres`, `themes`, `developers`) from `analytics_ready_games`.
2. It generates a restricted `allowed_ids` pool using `_get_similar_by_seed_attributes`, requiring attribute overlap (genre/theme, with platform alignment when available).
3. Hybrid retrieval (Vector + BM25) is then executed inside this restricted pool only, ensuring results are both semantically relevant and feature-similar to the seed game.
4. Final ranking remains hybrid relevance (`RRF + metadata`), where metadata boosts include developer overlap bonuses so seed-studio continuity is prioritized.
