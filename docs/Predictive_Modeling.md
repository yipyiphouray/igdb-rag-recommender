# Semantic Retrieval and Hybrid Ranking Methodology

## 1. Overview

The discovery stack emphasizes **semantic retrieval + hybrid ranking** rather than SQLite-based similarity lookups. The system combines transformer embeddings with lexical BM25 signals to provide stable relevance across both natural-language intent and exact keyword phrasing.

## 2. Retrieval Architecture

### Semantic Search (Transformer Embeddings)

Game documents are embedded with transformer encoders and indexed in the vector store. Query embeddings are compared using distance-to-similarity transforms where needed.

Semantic retrieval captures intent patterns such as:

- mood/style descriptors (e.g., cozy, horror, open-world),
- gameplay motifs,
- implicit thematic relationships not expressible by exact keyword matching alone.

### Lexical Search (BM25)

BM25 runs over textual catalog fields to preserve precision for:

- title tokens,
- exact phrase overlap,
- domain keywords that may be underrepresented in embeddings.

When `rank_bm25` is unavailable, runtime falls back to an in-repo `SimpleBM25` implementation to preserve lexical retrieval continuity.

Seed-based metadata is applied as a soft post-retrieval signal (not a hard filter), using overlap from Parquet list fields (`genres_list`, `themes_list`, `developers_list`, `platforms_list`).

## 3. Hybrid Fusion Logic

Final candidate ranking is produced by fusing semantic and lexical channels with normalized scoring.

### Current Fusion Formula

```text
Score = (SEMANTIC_WEIGHT * normalized_vec)
      + (LEXICAL_WEIGHT * normalized_bm25)
      + metadata_boosts
```

Current constants in runtime:

- `SEMANTIC_WEIGHT = 0.9`
- `LEXICAL_WEIGHT = 0.1`

Implementation note:

- The pipeline also supports RRF-style candidate blending as a primary rank signal in some paths.
- The weighted formula above remains the interpretable semantic/lexical score component and is retained as a secondary scoring factor.

## 4. Fallback and Prefilter Order

Runtime order is documented and implemented as:

1. Metadata/DataFrame prefilter constraints.
2. Semantic vector retrieval.
3. BM25 lexical retrieval (or `SimpleBM25` fallback).
4. Fusion scoring (weighted normalized vector/BM25 + metadata boosts).
   - Metadata boosts are similarity-derived (weighted Jaccard-style overlap), not static constants.
5. Post-fusion multipliers/penalties (e.g., 2D preference boost, 3D avoidance penalty).

## 5. Why This Replaces Legacy SQLite Similarity

Previous SQLite-centric retrieval patterns were effective for deterministic filtering but limited for semantic intent matching. The current hybrid strategy preserves deterministic metadata controls while improving semantic generalization.

Practically, this means:

- better recall for conceptual queries,
- better precision for exact lexical constraints,
- lower brittleness under sparse or noisy text input.

## 6. Supporting Data Layer

All metadata filtering and compatibility logic is powered by:

- `data/app/app_game_catalog.parquet` (single source of truth),
- DataFrame-based filtering and schema mapping in runtime retrieval.

No online recommendation step depends on SQLite joins for candidate generation.

## 7. Quality Assurance

The retrieval stack is validated through dedicated operational checks:

- `src/validate_vector_store.py` for vector health and collapse detection.
- `src/debug_engine.py` for end-to-end execution sanity.

### Validation Enforcement Boundary

Validation is a **CI/Ops-gated deployment requirement**, not a runtime hard-stop inside search execution.

That means:

- Validator failure should block index promotion/deployment.
- Runtime search code remains available for development/debug contexts unless deployment policy explicitly wraps execution with a hard gate.
- Runtime prefiltering auto-relaxes to broad retrieval when strict filters collapse to zero candidates.
