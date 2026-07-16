# Technical Journey: Hybrid Search Recommender System

## Overview

This project now runs a Parquet-native Hybrid RAG architecture for game discovery and recommendation. The legacy SQLite-first retrieval workflow has been replaced by a modern pipeline where:

- `data/app/app_game_catalog.parquet` is the authoritative metadata source.
- Chroma vector index (`data/vector_store/`) provides semantic retrieval.
- `src/rag_engine.py` fuses semantic and lexical retrieval into one ranked output.

The primary objective of this transition was to eliminate schema drift and retrieval fragility while scaling to the full 47,835-game catalog.

## Migration Summary

### 1) Data Layer Transition (SQLite -> Parquet)

The retrieval layer no longer depends on SQLite table joins during query-time execution. Instead:

- Catalog metadata is loaded directly via pandas from Parquet.
- Filtering and candidate constraints run with DataFrame operations.
- Column compatibility is preserved via schema mapping (`COLUMN_MAP`) for canonical fields such as `platforms`, `genres`, and playtime metadata.

This shift simplified runtime dependencies and removed SQL coupling from the online recommendation path.

### 2) Index Rebuild and Recovery

A major reliability issue during migration was a **collapsed legacy vector index** (uniform results and weak differentiation). We rebuilt indexing logic to improve embedding quality by constructing richer text inputs from catalog attributes (name + summary + genres).

Current indexing flow (`src/initialize_vector_db.py`):

- Loads the full Parquet catalog.
- Normalizes schema and embedding text fields.
- Clears stale vector-store artifacts before rebuilding.
- Indexes the full dataset in deterministic batches.
- Validates final collection count against catalog count.

## Healthy Hybrid Retrieval State

The engine now uses a robust hybrid retrieval strategy:

- **Semantic channel**: embedding-based nearest-neighbor retrieval.
- **Lexical channel**: BM25 keyword retrieval for exact-term resilience.
- **Fusion layer**: hybrid score composition with normalized signals and metadata-aware adjustments.

This design improves robustness for both intent-heavy queries and exact-title keyword queries.

## Validation as a Standard Practice

A formal validation suite is now part of the RAG workflow and should be treated as mandatory after each index rebuild.

### Required Checks

- `src/validate_vector_store.py`
  - Data-content sampling and embedding sanity checks.
  - Semantic diversity tests across distinct intent queries.
  - Self-similarity verification (target title must retrieve itself at top rank).
  - Statistical variance checks to detect embedding collapse.

- `src/debug_engine.py`
  - End-to-end runtime smoke test for `RAGAgent.search(...)`.
  - Confirms that retrieval, fusion, and ranking execute without runtime exceptions.

### Operational Rule

**No deployment of updated vector data is considered complete unless both scripts pass.**

## Lessons Learned

1. Embedding quality is highly sensitive to text preparation; sparse fields can silently degrade semantic retrieval.
2. Retrieval failures may come from candidate-gating and prefilter logic, not just vector quality.
3. Validation must include both **index health** and **runtime behavior**; passing one without the other is insufficient.

## Current Status

- Parquet-native retrieval: active
- Full-catalog vector index: active and validated
- Hybrid semantic + lexical fusion: active
- Post-deployment validation suite: integrated into standard operating procedure
