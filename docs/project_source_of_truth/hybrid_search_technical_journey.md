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

A major reliability issue during migration was a **collapsed legacy vector index** (uniform results and weak differentiation). We rebuilt indexing logic to improve embedding quality by constructing richer text inputs from catalog attributes. The active embedding profile should include high-signal structured metadata before long text fields so the model sees game identity, genre/theme context, platform context, gameplay mode, hidden-gem signals, and summary/storyline text.

Current indexing flow (`src/initialize_vector_db.py`):

- Loads the full Parquet catalog.
- Normalizes schema and embedding text fields.
- Builds a richer embedding document from title, genres, themes, keywords, platforms, game modes, player perspectives, developers, rating band, playtime profile, multiplayer profile, hidden-gem flag, high-rated flag, summary, storyline, and generated catalog/RAG profile when available.
- Clears stale vector-store artifacts before rebuilding.
- Indexes the full dataset in deterministic batches.
- Validates final collection count against catalog count.

## Healthy Hybrid Retrieval State

The engine now uses a robust hybrid retrieval strategy:

- **Semantic channel**: embedding-based nearest-neighbor retrieval.
- **Lexical channel**: BM25 keyword retrieval for exact-term resilience.
- **Lexical fallback**: automatic `SimpleBM25` fallback when `rank_bm25` is unavailable.
- **Fusion layer**: weighted semantic/lexical scoring (`0.9 / 0.1`) plus secondary rank shaping.
- **Soft metadata boosting**: seed-derived metadata is used as a post-retrieval boost, not a hard inclusion filter.
- **Seed-title exclusion**: reference games detected in prompts such as “similar to Stardew Valley” or “I played Hades” are excluded from final results while still shaping similarity boosts.
- **Auto-relaxation fallback**: if strict prefiltering yields zero candidates, the engine falls back to broad retrieval instead of returning an empty result set.
- **Post-fusion multipliers**: preference-based adjustments (e.g., 2D request boost and 3D avoidance penalty).

This design improves robustness for both intent-heavy queries and exact-title keyword queries while preventing cold-start style zero-result failures.

## Log Interpretation Guide

When `debug_scores=True`, each `[HybridDebug]` line exposes score arithmetic for each ranked result:

- `RawVec`, `RawBM25`: raw channel signals.
- `NormVec`, `NormBM25`: normalized channel signals used in weighted fusion.
- `Weights=(0.90,0.10)`: semantic and lexical constants.
- `Weighted`: `(0.9 * NormVec) + (0.1 * NormBM25)`.
- `RRF`: reciprocal-rank based blending component.
- `LexicalBonus`: token-overlap additive bonus.
- `MetadataBoost`: similarity boost from shared seed attributes (`genres_list`, `themes_list`, `developers_list`, `platforms_list`) using weighted Jaccard-style overlap.
- `Final`: final ranking score.

Arithmetic interpretation:

```text
Final = Weighted + RRF + LexicalBonus + MetadataBoost
```

Reviewers should verify that the weighted component adheres to `0.9/0.1`, then interpret rank movements from secondary adjustments (`RRF`, lexical bonus, metadata boost).

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
  - Confirms retrieval, fusion, soft metadata boosting, and ranking execute without runtime exceptions.
  - Provides telemetry required for score-audit interpretation.

### Operational Rule

**No deployment of updated vector data is considered complete unless both scripts pass.**

## Code-to-Documentation Mapping

| Code Function | Documented Purpose | Validation Command |
|---|---|---|
| `RAGAgent._get_prefilter_ids(...)` | Metadata/DataFrame prefilter and fallback broadening when constraints over-restrict candidates | `python src/debug_engine.py` |
| `RAGAgent._vector_search(...)` | Semantic candidate retrieval from vector index | `python src/debug_engine.py` |
| `RAGAgent._bm25_search(...)` | Lexical BM25 candidate retrieval for exact-term resilience | `python src/debug_engine.py` |
| `SimpleBM25.get_scores(...)` | Lexical fallback scoring when `rank_bm25` is unavailable | `python src/debug_engine.py` |
| `RAGAgent._get_similar_by_seed_attributes(...)` | Soft metadata similarity boost using list-field overlap (`*_list`) | `python src/debug_engine.py` |
| `RAGAgent._find_seed_games_mentioned_in_query(...)` | Detects explicit reference titles that should guide similarity but not be returned as recommendations | `python -m src.evaluate_rag_retrieval` |
| `rank_results(...)` | Fusion-aware ranking with metadata boosts and post-fusion multipliers | `python src/debug_engine.py` |
| `src/validate_vector_store.py` suite | Vector stability and collapse detection checks | `python src/validate_vector_store.py` |
| `src/evaluate_rag_retrieval.py` suite | Golden-query relevance checks, weight comparison, and seed-title exclusion validation | `python -m src.evaluate_rag_retrieval` |

## Lessons Learned

1. Embedding quality is highly sensitive to text preparation; sparse fields can silently degrade semantic retrieval.
2. Retrieval failures may come from candidate-gating and prefilter logic, not just vector quality.
3. Validation must include both **index health** and **runtime behavior**; passing one without the other is insufficient.
4. Health checks confirm the vector store is technically valid, but separate golden-query tests are still needed to judge whether retrieved games feel relevant to users.

## Current Status

- Parquet-native retrieval: active
- Full-catalog vector index: active and validated
- Hybrid semantic + lexical fusion: active
- Soft metadata boosting + seed-title exclusion + auto-relaxation fallback: active
- Post-deployment validation suite: integrated into standard operating procedure
