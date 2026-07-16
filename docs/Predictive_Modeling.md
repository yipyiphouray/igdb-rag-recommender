# Semantic Retrieval and Hybrid Ranking Methodology

## 1. Overview

The discovery stack now emphasizes **semantic retrieval + hybrid ranking** rather than SQLite-based similarity lookups. The system combines transformer embeddings with lexical BM25 signals to provide stable relevance across both natural-language intent and exact keyword phrasing.

## 2. Retrieval Architecture

### Semantic Search (Transformer Embeddings)

Game documents are embedded with `SentenceTransformer` and indexed in the vector store. Query embeddings are compared using cosine-style similarity (distance transformed to similarity where needed).

Semantic retrieval captures intent patterns such as:

- mood/style descriptors (e.g., cozy, horror, open-world),
- gameplay motifs,
- implicit thematic relationships not expressible by exact keyword matching alone.

### Lexical Search (BM25)

BM25 runs over textual catalog fields to preserve precision for:

- title tokens,
- exact phrase overlap,
- domain keywords that may be underrepresented in embeddings.

## 3. Hybrid Fusion Logic

Final candidate ranking is produced by fusing semantic and lexical channels with normalized scoring:

- Vector similarity signal (normalized/clamped to a comparable scale).
- BM25 signal normalized to 0-1 over candidate scores.
- Optional rank-based bonus and metadata-aware adjustments.

This prevents a single channel from dominating due to raw score magnitude differences and yields better retrieval stability across heterogeneous query styles.

## 4. Why This Replaces Legacy SQLite Similarity

Previous SQLite-centric retrieval patterns were effective for deterministic filtering but limited for semantic intent matching. The current hybrid RAG strategy preserves deterministic metadata controls while significantly improving semantic generalization.

Practically, this means:

- better recall for conceptual queries,
- better precision for exact lexical constraints,
- lower brittleness under sparse or noisy text input.

## 5. Supporting Data Layer

All metadata filtering and compatibility logic is now powered by:

- `data/app/app_game_catalog.parquet` (single source of truth),
- DataFrame-based filtering and schema mapping in runtime retrieval.

No online recommendation step depends on SQLite joins for candidate generation.

## 6. Quality Assurance

The retrieval stack is validated through dedicated operational checks:

- `src/validate_vector_store.py` for vector health and collapse detection.
- `src/debug_engine.py` for end-to-end execution sanity.

These checks are part of the required post-indexing workflow to ensure semantic quality remains stable after data/index refreshes.
