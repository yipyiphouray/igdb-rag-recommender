# Technical Journey: Hybrid Search System

Last updated: July 24, 2026

This document records the technical migration path for the project retrieval stack.

## 1. Current Status

Status: Active, revised.

The project still uses hybrid search.

The current default backend is now:

```text
lightweight NumPy embeddings + BM25 lexical retrieval
```

The older Chroma implementation remains in the repository as an optional backend. It is not the preferred deployment default.

## 2. Why the Retrieval Stack Changed

The project originally used a Chroma vector-store workflow for semantic game retrieval.

That direction worked locally, but it created deployment risk:

- larger dependency footprint;
- heavier persistent vector-store artifact;
- more moving parts for free-hosted deployment;
- harder debugging when vector-store state became stale or collapsed.

The project moved to a lightweight retrieval backend to reduce deployment complexity while keeping the core retrieval logic.

## 3. Current Runtime Architecture

Current default runtime:

```text
data/app/app_game_catalog.parquet
-> data/rag/lightweight/game_embeddings.npy
-> data/rag/lightweight/game_ids.json
-> data/rag/lightweight/manifest.json
-> src/lightweight_rag_engine.py
-> src/app/rag_service.py
```

The API service uses `src/app/rag_service.py` to select the backend.

Default backend:

```text
RAG_BACKEND=lightweight
```

Supported backend aliases:

- `lightweight`
- `numpy`
- `lightweight_numpy`
- `lightweight_numpy_bm25`

Optional Chroma aliases:

- `chroma`
- `chromadb`
- `vector_store`

## 4. Migration Summary

### Phase 1: SQLite-first retrieval

The early retrieval approach depended more heavily on SQLite/database-oriented lookup behavior.

Limitation: this was useful for deterministic filtering but weaker for natural-language game discovery.

### Phase 2: Chroma semantic retrieval

The project added vector retrieval through Chroma.

Benefit: better semantic matching.

Limitation: vector-store deployment and artifact stability were more complex than necessary for the final website direction.

### Phase 3: Hybrid semantic + lexical retrieval

The project added BM25 lexical retrieval and fused it with semantic similarity.

Benefit: better balance between natural-language intent and exact keyword matching.

### Phase 4: Lightweight deployment backend

The project moved the default backend to NumPy embeddings plus BM25.

Benefit: simpler free-hosted deployment path while preserving hybrid retrieval.

## 5. Current Hybrid Retrieval Behavior

The active lightweight backend performs:

- DataFrame-based metadata prefiltering.
- Query embedding with sentence-transformers.
- NumPy cosine similarity against local embedding artifacts.
- BM25 lexical retrieval over catalog text.
- Weighted semantic/lexical fusion.
- Reciprocal-rank style blending.
- Lexical token bonus.
- Seed-game metadata boosting.
- Seed-title exclusion.
- Hidden-gem ranking adjustment.
- 2D/3D preference adjustment.
- Constraint relaxation when filters are too restrictive.

## 6. Current Fusion Constants

The lightweight backend uses:

```text
SEMANTIC_WEIGHT = 0.8
LEXICAL_WEIGHT = 0.2
```

The optional Chroma backend uses:

```text
SEMANTIC_WEIGHT = 0.9
LEXICAL_WEIGHT = 0.1
```

Interpretation:

- semantic score captures conceptual similarity;
- lexical score protects exact keyword and title relevance;
- secondary rank shaping adjusts the result after the core retrieval blend.

## 7. Artifact Build Process

Default lightweight build command:

```text
python -m src.build_lightweight_rag_index
```

The lightweight build creates:

```text
data/rag/lightweight/game_embeddings.npy
data/rag/lightweight/game_ids.json
data/rag/lightweight/manifest.json
```

These generated artifacts should not be committed to GitHub if they are large or environment-specific.

## 8. Validation Process

Default lightweight validation:

```text
python -m src.evaluate_rag_retrieval --backend lightweight
```

Optional Chroma validation:

```text
python src/validate_vector_store.py
python src/debug_engine.py
python -m src.evaluate_rag_retrieval --backend chroma
```

Validation should check:

- retrieval runs without runtime errors;
- semantic and lexical signals are non-collapsed;
- exact title queries retrieve sensible matches;
- seed games are excluded from final recommendations;
- hidden-gem intent affects ranking without overpowering relevance;
- no-result behavior is handled cleanly.

## 9. Code-to-Documentation Mapping

| Code | Current purpose |
|---|---|
| `src/app/rag_service.py` | Backend selector and response normalizer for game retrieval. |
| `src/lightweight_rag_engine.py` | Default lightweight semantic + BM25 retrieval engine. |
| `src/build_lightweight_rag_index.py` | Builds lightweight NumPy embedding artifacts. |
| `src/evaluate_rag_retrieval.py` | Evaluates retrieval quality for lightweight or Chroma backends. |
| `src/rag_engine.py` | Optional Chroma-based hybrid retrieval engine. |
| `src/initialize_vector_db.py` | Builds the optional Chroma vector store. |
| `src/validate_vector_store.py` | Validates optional Chroma vector-store health. |
| `src/debug_engine.py` | Smoke-tests optional Chroma runtime behavior. |

## 10. Current Product Boundary

The hybrid retrieval stack supports catalog-backed recommendation and game-discovery retrieval.

It is not the same thing as `Ask the Guide_` project-document retrieval.

Current distinction:

- `Recommend Me_` and game retrieval use catalog embeddings and hybrid search.
- `Ask the Guide_` uses project-document retrieval, structured tools, and an LLM for grounded project answers.

This separation is intentional.

## 11. Deployment Position

Use lightweight retrieval as the default deployment target.

Reason:

- smaller artifact set;
- fewer dependencies;
- easier free-hosting path;
- no required Chroma runtime state;
- cleaner local/backend startup.

Keep Chroma only as an optional development backend unless the team explicitly decides to deploy it.

## 12. Lessons Learned

Embedding quality depends heavily on text preparation.

Retrieval quality depends on both semantic and lexical signals.

Exact metadata constraints can collapse results if used too aggressively.

Seed games should guide recommendations but should not appear as returned recommendations.

Validation must check both technical health and human-perceived relevance.
