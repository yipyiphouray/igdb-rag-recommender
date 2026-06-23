from __future__ import annotations

from pathlib import Path

from src.app import config


RAG_ARTIFACTS = {
    "game_profiles": config.RAG_DIR / "game_profiles.parquet",
    "retrieval_metadata": config.RAG_DIR / "retrieval_metadata.parquet",
    "vector_store": config.RAG_DIR / "vector_store",
}


def rag_status() -> dict[str, bool]:
    return {name: path.exists() for name, path in RAG_ARTIFACTS.items()}


def answer_game_query(query: str, filters: dict | None = None, top_k: int = 5) -> dict:
    status = rag_status()
    if not all(status.values()):
        return {
            "answer_text": (
                "RAG retrieval is not integrated yet. This page is ready for the "
                "teammate's vector-store and retrieval artifacts."
            ),
            "retrieved_game_ids": [],
            "retrieved_games": [],
            "applied_filters": filters or {},
            "retrieval_scores": [],
            "warnings": ["RAG artifacts are missing or incomplete."],
        }

    return {
        "answer_text": "RAG artifacts are present, but the final retrieval callable has not been wired yet.",
        "retrieved_game_ids": [],
        "retrieved_games": [],
        "applied_filters": filters or {},
        "retrieval_scores": [],
        "warnings": ["Retrieval implementation pending teammate integration."],
    }


def artifact_path(name: str) -> Path:
    return RAG_ARTIFACTS[name]
