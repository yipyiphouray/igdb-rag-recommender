# IGDB Game Discovery and Hybrid RAG Recommender

A portfolio-grade game discovery system that combines structured metadata filtering with semantic retrieval. The stack has been migrated from legacy SQLite-first retrieval to a modern **Parquet + Vector Store** architecture optimized for scale and relevance.

## Architecture Overview

The recommender now uses a hybrid retrieval pipeline with clear separation of concerns:

- **Parquet Metadata Layer (`data/app/app_game_catalog.parquet`)**
  - Single source of truth for game catalog attributes.
  - Powers deterministic filtering (platform, release year, multiplayer flags, etc.).
  - Enables fast schema-normalized access through pandas.

- **Vector Index Layer (`data/vector_store/`)**
  - Embeddings are generated from game text profiles and indexed in Chroma (FAISS-class ANN behavior via vector index).
  - Powers semantic retrieval for natural-language intent (e.g., *"open world RPG with co-op"*).

- **Hybrid Ranking Engine (`src/rag_engine.py`)**
  - Executes metadata prefiltering from Parquet.
  - Runs vector retrieval + lexical retrieval (BM25).
  - Fuses scores into a final ranked recommendation list.

In short: **Parquet handles exact constraints, vectors handle meaning, and hybrid fusion balances both.**

## Setup Instructions

### 1) Install dependencies

```bash
pip install -r requirement.txt
```

### 2) Build/Rebuild the vector index

After refreshing `data/app/app_game_catalog.parquet`, initialize the vector database:

```bash
python src/initialize_vector_db.py
```

This script reads the full Parquet catalog, prepares embedding text, clears stale vector data, and writes a fresh index.

## Validation Suite (Post-Deployment)

After indexing, run these checks before shipping:

- `src/validate_vector_store.py`
  - Performs vector health auditing: content sampling, semantic diversity, self-similarity, and variance checks.
- `src/debug_engine.py`
  - Smoke-tests end-to-end retrieval by initializing `RAGAgent` and executing a real query.

Recommended sequence:

```bash
python src/validate_vector_store.py
python src/debug_engine.py
```

## Project Structure (Key Paths)

- `data/app/app_game_catalog.parquet`
  - **Primary catalog source of truth** for retrieval metadata.
- `data/vector_store/`
  - Persisted embedding index used by semantic retrieval.
- `src/initialize_vector_db.py`
  - Vector index build/rebuild pipeline.
- `src/rag_engine.py`
  - Hybrid retrieval and ranking engine used by the recommender.
- `src/validate_vector_store.py`
  - Automated vector quality and collapse detection checks.
- `src/debug_engine.py`
  - Runtime sanity check for query execution.

## Current System Capabilities

- Natural-language game discovery with semantic intent matching.
- Deterministic filtering over catalog attributes from Parquet.
- Hybrid ranking that combines vector relevance with lexical signals.
- Operational validation scripts to guard against vector collapse and runtime regressions.

## Notes

- If catalog row count and vector index count diverge, rebuild the index with:
  - `python src/initialize_vector_db.py`
- Keep Parquet and vector store in sync for stable search quality.
