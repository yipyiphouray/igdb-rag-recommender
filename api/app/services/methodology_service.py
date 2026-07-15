from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from app import config


def _load_json(path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


@lru_cache(maxsize=1)
def get_methodology_summary() -> dict[str, Any]:
    metrics = _load_json(config.APP_METHODOLOGY_METRICS_PATH)
    insight_summary = _load_json(config.APP_INSIGHT_SUMMARY_PATH)

    return {
        "data_source": "App-ready parquet/json artifacts generated from the curated IGDB analytical sample.",
        "metrics": metrics,
        "insight_summary": insight_summary,
        "caveats": [
            "The project uses a curated analytical sample, not the full IGDB catalog.",
            "Total rating is treated as a reception/quality signal, not objective truth.",
            "Total rating count is treated as rating evidence/activity, not direct popularity.",
            "PopScore interest is treated as a visibility/current-interest signal when available.",
            "Missing PopScore means unknown visibility, not low visibility.",
            "Diagnostic findings describe associations and should not be interpreted as causal claims.",
        ],
        "implementation_notes": [
            "The first website build reads app-ready parquet/json artifacts through the FastAPI backend.",
            "The frontend should not read local data artifacts directly.",
            "Cosine similarity should integrate into the Recommendations endpoint when teammate artifacts are ready.",
            "RAG should only recommend or explain games grounded in project data.",
        ],
    }
