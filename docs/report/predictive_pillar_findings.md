# Predictive Pillar Findings
## IGDB Game Discovery & RAG Recommendation System

**Project:** IGDB Game Discovery & RAG Recommendation System  
**Team:** QUEST ACCEPTED!  
**Course:** BUSA 649  
**Pillar:** Predictive Analytics  
**Document Type:** Evidence & Readiness Summary

---

# 1. Performance Findings

The predictive pillar migrated from a legacy SQLite-first retrieval pattern to a Parquet-native hybrid retrieval pipeline that fuses semantic vector similarity with BM25 lexical ranking.

Observed impact:

- Hybrid fusion improved retrieval precision for conceptual queries (for example, **"cozy horror"**) compared with the legacy SQLite retrieval path.
- Semantic retrieval increased intent sensitivity for mood/theme-based prompts.
- BM25 preserved exact-term resilience, reducing misses on specific titles and keyword-heavy queries.
- Combined ranking produced more consistently relevant top-k outputs across mixed query styles.

Interpretation:

> The hybrid approach outperformed single-path retrieval behavior by balancing conceptual understanding with lexical precision.

---

# 2. Validation Results

Predictive retrieval quality and operational stability were validated through mandatory scripts:

1. **`src/validate_vector_store.py`**
   - Vector store passed stability-oriented checks, including:
     - semantic diversity behavior across distinct intents,
     - self-similarity verification,
     - index-level consistency checks.

2. **`src/debug_engine.py`**
   - End-to-end hybrid retrieval execution completed without blocking runtime failures in smoke-test flow.

Validation summary:

> The vector store and runtime retrieval path satisfy the project’s validation-as-standard-practice requirement for index updates.

---

# 3. Conclusion

The Predictive Analytics Pillar is now **production-ready for the Streamlit MVP**.

Readiness is supported by:

- a Parquet-authoritative retrieval data foundation,
- a functioning hybrid fusion architecture (Semantic + BM25), and
- mandatory validation gates for both index integrity and runtime behavior.

This pillar now provides a stable predictive core for downstream prescriptive recommendation features.
