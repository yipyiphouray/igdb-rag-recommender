# Predictive Analytics Pillar Plan
## IGDB Game Discovery & RAG Recommendation System

**Project:** IGDB Game Discovery & RAG Recommendation System  
**Team:** QUEST ACCEPTED!  
**Course:** BUSA 649  
**Pillar:** Predictive Analytics  
**Document Type:** Pillar Plan (Execution Blueprint)  
**Primary Runtime Engine:** `src/rag_engine.py`  
**Primary Data Source:** `data/app/app_game_catalog.parquet`

---

# 1. Objectives

The predictive analytics pillar is designed to deliver high-accuracy retrieval and ranking for game discovery queries by combining semantic and lexical evidence in one hybrid pipeline.

Primary objective:

> **Implement robust hybrid retrieval (Semantic + Lexical) to improve recommendation relevance across both intent-heavy and exact-term search behavior.**

Target outcomes:

- Improve conceptual-query retrieval quality (e.g., mood, theme, style, play pattern).
- Preserve exact-title and keyword precision for known-item searches.
- Produce one stable, explainable ranked result set for downstream recommendation delivery.

---

# 2. Methodology

### Methodology Outcome

The system successfully transitioned from **Hard Metadata Filtering** to **Candidate Boosting**, resolving prior cold-start and zero-result retrieval failures.

## 2.1 Hybrid Retrieval Architecture

The predictive pillar uses a dual-channel retrieval approach:

1. **Semantic Channel (Vector / Transformer Embeddings)**
   - Uses transformer-generated embeddings to capture intent-level similarity.
   - Supports conceptual matching where user phrasing may not overlap directly with catalog keywords.

2. **Lexical Channel (BM25)**
   - Uses term-frequency/inverse-document-frequency-style lexical ranking.
   - Preserves precision for exact-title, franchise, mechanic, and keyword-specific queries.

3. **Fusion Layer (Hybrid Ranking)**
   - Combines semantic and lexical scores into one ranked list.
   - Reduces single-channel failure modes by balancing conceptual relevance with exact-term confidence.

## 2.2 Operational Data Foundation

The production retrieval workflow is Parquet-native:

- `data/app/app_game_catalog.parquet` is the authoritative catalog metadata source.
- Vector assets are maintained in `data/vector_store/`.
- Runtime fusion and ranking are executed through `src/rag_engine.py`.

This design replaces brittle query-time SQLite joins in the online retrieval path and improves schema consistency between indexing and serving.

---

# 3. Validation SOP (Mandatory)

Validation is a release-gate requirement for every index update.

## Required Checks

1. **`src/validate_vector_store.py`** (Mandatory)
   - Validates vector-store integrity and retrieval stability.
   - Runs diversity and self-similarity checks to catch embedding degradation.

2. **`src/debug_engine.py`** (Mandatory)
   - Executes end-to-end runtime smoke checks for hybrid retrieval.
   - Confirms that retrieval, fusion, and ranking execute without runtime failures.
  - Confirms soft metadata boosting and auto-relaxation behavior are active in runtime traces.

## Enforcement Rule

> **No vector index update is considered complete unless both scripts pass successfully.**

Passing only one check is insufficient for deployment readiness.

---

# 4. Deliverables

The predictive pillar is considered operationally complete when the following artifacts are maintained and aligned:

- `data/app/app_game_catalog.parquet` (source of truth)
- `data/vector_store/` (validated vector index)
- `src/rag_engine.py` (hybrid retrieval runtime)
- `src/validate_vector_store.py` (index validation suite)
- `src/debug_engine.py` (runtime debug/smoke suite)
- `docs/plan/predictive_analytics_pillar_plan.md` (this execution plan)

---

# 5. Success Criteria

The plan is successful when:

1. Hybrid retrieval reliably supports both conceptual and exact-match query types.
2. Fusion logic remains stable after index refreshes.
3. Validation SOP is consistently executed for each index update.
4. Predictive output is ready to support prescriptive recommendation experiences in the Streamlit MVP.
