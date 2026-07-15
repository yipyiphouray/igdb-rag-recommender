from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class MethodologySummary(BaseModel):
    data_source: str
    metrics: dict[str, Any]
    insight_summary: dict[str, Any]
    caveats: list[str]
    implementation_notes: list[str]
