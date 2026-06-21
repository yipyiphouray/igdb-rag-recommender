# Technical Journey: IGDB RAG Recommender System

## Overview
This project implements a Retrieval-Augmented Generation (RAG) system for video game recommendations, utilizing SQLite as a relational source-of-truth and ChromaDB for semantic vector retrieval.

## Completed Pipeline
1.  **Data Engineering:** Developed `Build_FeatureEngineering.py` to aggregate raw game data into a unified `analytics_ready_games` view. 
    * *Improvement:* Implemented CTEs and `GROUP_CONCAT` to handle multi-value relational data (platforms, developers, publishers) as searchable "text blobs."
2.  **Semantic Indexing:** Established `initialize_vector_db.py` to map SQL views to vector embeddings using `SentenceTransformer`.
3.  **Hybrid Retrieval Engine:** Created `rag_engine.py` which combines vector-based semantic search with custom metadata filtering (Fuzzy String Matching) to handle specific user requests (e.g., "Switch" platform).


## Phase 2: ML-Driven Predictive Ranking

* **Status**: Completed.
* **Architecture**: Transitioned from global community ratings to a **two-phase hybrid recommendation engine**:
* **Phase 1 (Relevance-First)**: A two-stage pipeline combining Hybrid Retrieval (Vector + BM25) with Metadata-Aware SQL Filtering. This ensures candidates strictly match user constraints (e.g., platforms, co-op).
* **Phase 2 (ML-Driven Predictive Ranking)**: A `RandomForestRegressor` trained on `total_rating` replaces community heuristics. It provides a granular quality score, enabling the engine to prioritize titles based on learned quality baselines rather than simple popularity.


* **Performance**: Achieved **Spearman Rank Correlation of 0.6563**, validating that the model successfully preserves the relative quality hierarchy of recommendations.