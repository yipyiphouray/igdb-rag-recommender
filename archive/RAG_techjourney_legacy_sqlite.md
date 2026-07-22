# Technical Journey: IGDB RAG Recommender System

## Overview
This project implements a Retrieval-Augmented Generation (RAG) system for video game recommendations, utilizing SQLite as a relational source-of-truth and ChromaDB for semantic vector retrieval.

## Completed Pipeline
1.  **Data Engineering:** Developed `Build_FeatureEngineering.py` to aggregate raw game data into a unified `analytics_ready_games` view. 
    * *Improvement:* Implemented CTEs and `GROUP_CONCAT` to handle multi-value relational data (platforms, developers, publishers) as searchable "text blobs."
2.  **Semantic Indexing:** Established `initialize_vector_db.py` to map SQL views to vector embeddings using `SentenceTransformer`.
3.  **Hybrid Retrieval Engine:** Created `rag_engine.py` which combines vector-based semantic search with custom metadata filtering (Fuzzy String Matching) to handle specific user requests (e.g., "Switch" platform).

## Current Status
* **Search Engine:** Functional, supporting filtered queries and metadata-aware retrieval.
* **Ranking:** Currently uses community rating heuristics.

## Proposed Improvements (To-Do)
1.  **Fine-Grained Ranking:** Transition from binary 1/0 high-rating flags to numerical `total_rating` sorting for precise recommendation ranking.
2.  **ML-Driven Personalization:** Implement a predictive ranking model using the features generated in `modeling_train_features.csv` to move beyond global community averages toward user-specific preferences.
3.  **UI Integration:** Expose the `RAGAgent` class via a REST API or Streamlit interface for frontend integration.




Phase 2: Ranking Logic
Current Implementation: Global Community Ranking using raw total_rating scores from IGDB.

System Capability: The system retrieves semantic candidates and performs a fine-grained sort using the actual community rating, ensuring the highest-quality titles appear at the top of the recommendation list.

Future ML Target: The system is architected to transition from global community rankings to Personalized Ranking by training a model on historical user engagement data and feature embeddings generated in Build_FeatureEngineering.py.