from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.catalog import GameSummary


ChatRouteMode = Literal[
    "custom_question",
    "dataset_size",
    "dataset_year_range",
    "explain_data",
    "explain_hidden_gems",
    "explain_limitations",
    "explain_project",
    "explain_rag",
    "explain_recommendation",
    "recommend_me_guidance",
    "recommend_games",
    "rating_coverage",
    "search_catalog",
    "website_navigation",
]


class ChatFilters(BaseModel):
    platforms: list[str] = Field(default_factory=list)
    release_year_min: int | None = None
    release_year_max: int | None = None
    multiplayer_mode: str | None = None


class ChatHistoryMessage(BaseModel):
    role: str = Field(pattern="^(user|guide)$")
    content: str = Field(min_length=1, max_length=1600)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1200)
    route_mode: ChatRouteMode | None = None
    conversation_id: str | None = None
    max_results: int = Field(default=5, ge=1, le=10)
    filters: ChatFilters | None = None
    history: list[ChatHistoryMessage] = Field(default_factory=list, max_length=12)


class ChatRetrievedGame(GameSummary):
    rank: int
    retrieval_score: float | None = None
    semantic_score: float | None = None
    lexical_score: float | None = None
    evidence: str
    match_explanation: str | None = None
    caveats: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    mode: str
    status: str
    route_mode: ChatRouteMode | None = None
    conversation_id: str | None = None
    retrieved_games: list[ChatRetrievedGame] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    applied_filters: dict[str, Any] = Field(default_factory=dict)
    follow_up_prompts: list[str] = Field(default_factory=list)
    contextual_query: str | None = None
    interpreted_preferences: dict[str, Any] = Field(default_factory=dict)
    chat_intent: str | None = None
    intent_confidence: float | None = None
    route_source: str | None = None
    matched_intent_example: str | None = None


class ChatStatusResponse(BaseModel):
    status: str
    catalog_available: bool
    vector_store_available: bool
    collection_available: bool
    engine: str
    warnings: list[str] = Field(default_factory=list)
