# Hybrid Retrieval Methodology

Last updated: July 28, 2026

This document describes the retained hybrid retrieval methodology for catalog-backed game-discovery retrieval. It is no longer the primary runtime path for the final website recommendation page.

## 1. Current Status

Status: Retained as an internal retrieval/evaluation stack.

The final website currently separates the recommendation and chatbot responsibilities:

- `Recommend Me_` uses the metadata cosine-similarity recommendation service.
- `Ask the Guide_` uses project-context retrieval, structured project/catalog tools, and an LLM phrasing layer.
- Lightweight hybrid game retrieval remains available for internal testing, Streamlit workbench behavior, and retrieval-quality evaluation.

The current default hybrid retrieval backend remains lightweight semantic retrieval plus BM25 lexical retrieval when this retained stack is used.

The Chroma backend still exists in code as an optional backend, but it is not the default deployment path and is not required for the final website.

Current default:

```text
RAG_BACKEND=lightweight
```

Default runtime files:

- `src/lightweight_rag_engine.py`
- `src/app/rag_service.py`
- `data/app/app_game_catalog.parquet`
- `data/rag/lightweight/game_embeddings.npy`
- `data/rag/lightweight/game_ids.json`
- `data/rag/lightweight/manifest.json`

Optional Chroma backend files:

- `src/rag_engine.py`
- `data/vector_store/`

## 2. Current Product Boundary

This document should not be read as the source of truth for `Recommend Me_`.

Current final product boundary:

| Layer | Current final product role |
|---|---|
| `Recommend Me_` | Metadata cosine-similarity recommendation from structured preferences. |
| `Ask the Guide_` | Scoped project/catalog/methodology Q&A with tool routing and project-context retrieval. |
| Lightweight hybrid retrieval | Internal/development retrieval stack and optional evaluation path. |
| Chroma retrieval | Optional local comparison backend only. |

## 3. Purpose

Hybrid retrieval exists to combine two useful signals:

- semantic similarity from embeddings;
- lexical similarity from exact keyword overlap.

Semantic retrieval helps with intent-heavy queries such as cozy farming games, atmospheric horror, hidden-gem RPGs, or story-rich adventures.

BM25 lexical retrieval helps with exact terms such as title tokens, platform names, specific genres, and keywords that embeddings may underweight.

The goal is not to let the LLM invent recommendations. The retrieval engine must rank catalog-backed games from project artifacts.

## 4. Default Lightweight Retrieval Architecture

The lightweight backend uses local NumPy embeddings and BM25.

Runtime flow:

```text
User query
-> metadata prefilter
-> query embedding
-> NumPy cosine similarity search
-> BM25 lexical search
-> hybrid fusion
-> seed-title exclusion
-> metadata/ranking adjustments
-> top ranked catalog games
```

The lightweight backend avoids Chroma as a runtime dependency. This is better for free-hosting deployment because it uses small local artifacts and a simpler dependency footprint.

## 5. Embedding Text Profile

The embedding text should not include only title, summary, and genre.

The active embedding profile should include high-signal fields before long descriptive fields:

- title;
- genres;
- themes;
- keywords;
- platforms;
- game modes;
- player perspectives;
- developers;
- rating band;
- playtime profile;
- multiplayer profile;
- hidden-gem flag;
- high-rated flag;
- summary;
- storyline;
- generated catalog/RAG text profile when available.

Reason: structured metadata improves retrieval for natural-language game discovery queries.

## 6. Lexical BM25 Layer

BM25 runs over catalog text fields.

Primary lexical fields:

- name;
- summary;
- storyline;
- genres;
- themes;
- platforms;
- `rag_text_profile`.

If the `rank_bm25` package is unavailable, the project uses the in-repo `SimpleBM25` fallback.

Status: BM25 fallback is intentional. It protects local and free-hosted environments from optional dependency failures.

## 7. Fusion Logic

The default lightweight backend uses:

```text
SEMANTIC_WEIGHT = 0.8
LEXICAL_WEIGHT = 0.2
```

Current weighted component:

```text
Weighted = (0.8 * normalized_vector_score)
         + (0.2 * normalized_bm25_score)
```

The final score also includes reciprocal-rank style blending, lexical bonus, seed metadata boost, and downstream ranking adjustments where applicable.

The older Chroma backend uses different constants:

```text
SEMANTIC_WEIGHT = 0.9
LEXICAL_WEIGHT = 0.1
```

That Chroma weighting is retained only for the optional Chroma backend.

## 8. Seed Game Logic

When a user names a reference game, such as:

```text
I played Hades recently. Recommend similar games.
```

the engine treats the named title as a seed.

Seed behavior:

- find the referenced game in the catalog;
- use its metadata to boost similar games;
- exclude the seed game from final results;
- return alternatives instead of repeating the game the user already named.

This behavior supports retrieval-quality testing and possible future recommendation integration. In the current final website, ranked recommendations should still be routed through `Recommend Me_`.

## 9. Metadata Filters and Relaxation

The engine applies metadata constraints when available.

Supported constraints include:

- platform terms;
- release-year terms;
- co-op or multiplayer terms;
- hidden-gem intent;
- 2D or 3D graphics preference;
- selected ranking mode.

If strict filtering collapses to zero candidates, the lightweight backend relaxes constraints and falls back to broader retrieval.

Reason: returning some catalog-backed candidates is usually better than failing from over-restrictive filters.

## 10. Data Source

The authoritative runtime catalog is:

```text
data/app/app_game_catalog.parquet
```

The retained retrieval layer does not depend on SQLite joins during online retrieval.

SQLite remains important for the broader data engineering and relational database part of the project. It is not the online source for the current final website recommendation path.

## 11. Build and Validation Commands

Default lightweight backend:

```text
python -m src.build_lightweight_rag_index
python -m src.evaluate_rag_retrieval --backend lightweight
```

Optional Chroma backend:

```text
python src/initialize_vector_db.py
python src/validate_vector_store.py
python src/debug_engine.py
python -m src.evaluate_rag_retrieval --backend chroma
```

Operational rule: rebuild and validate retrieval artifacts after changing the embedding text profile, catalog schema, or ranking logic.

## 12. Deployment Position

For free-hosted deployment, prefer the lightweight backend if this retained retrieval stack is enabled.

Reason:

- no Chroma server or persistent Chroma runtime requirement;
- smaller artifact surface;
- simpler environment setup;
- local NumPy files are easier to ship or mount;
- fewer deployment failure points.

The Chroma backend is retained as an optional development and comparison path. The final website should not depend on Chroma for deployment.

## 12. Current Limitations

Hybrid retrieval quality depends on:

- app catalog quality;
- summary and storyline coverage;
- metadata completeness;
- embedding profile quality;
- seed-game matching quality;
- query specificity;
- availability of lightweight RAG artifacts.

The retrieval engine should not be described as live IGDB search.

The retrieval engine should not be described as an LLM-only recommendation method.
