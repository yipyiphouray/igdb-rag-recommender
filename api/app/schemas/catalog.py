from __future__ import annotations

from pydantic import BaseModel, Field


class GameSummary(BaseModel):
    game_id: int
    name: str
    slug: str | None = None
    release_year: int | None = None
    cover_url: str | None = None
    screenshot_url: str | None = None
    summary: str | None = None
    total_rating: float | None = None
    total_rating_count: int | None = None
    custom_interest_score: float | None = None
    custom_interest_percentile: float | None = None
    extraction_cohort: str | None = None
    platforms: list[str] = Field(default_factory=list)
    genres: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)
    game_modes: list[str] = Field(default_factory=list)
    player_perspectives: list[str] = Field(default_factory=list)
    normal_playtime_hours: float | None = None
    hidden_gem_balanced_flag: bool = False
    rag_ready_flag: bool = False


class GameDetail(GameSummary):
    storyline: str | None = None
    keywords: list[str] = Field(default_factory=list)
    developers: list[str] = Field(default_factory=list)
    publishers: list[str] = Field(default_factory=list)
    rating_band: str | None = None
    rating_reliable_flag: bool = False
    main_game_flag: bool = False
    data_caveats: list[str] = Field(default_factory=list)


class CatalogResponse(BaseModel):
    items: list[GameSummary]
    page: int
    page_size: int
    total_items: int
    total_pages: int
