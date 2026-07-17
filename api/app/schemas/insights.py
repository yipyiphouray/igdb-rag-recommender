from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class InsightsSummary(BaseModel):
    dataset: dict[str, Any] = Field(default_factory=dict)
    descriptive: dict[str, Any] = Field(default_factory=dict)
    diagnostic: dict[str, Any] = Field(default_factory=dict)
    dashboard: dict[str, Any] = Field(default_factory=dict)
