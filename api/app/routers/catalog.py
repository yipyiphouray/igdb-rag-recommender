from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query

from app.schemas.catalog import CatalogResponse, GameDetail
from app.services.catalog_service import get_game, list_games, load_filter_options

router = APIRouter(tags=["catalog"])


@router.get("/catalog/filter-options")
def filter_options() -> dict[str, Any]:
    return load_filter_options()


@router.get("/catalog/games", response_model=CatalogResponse)
def catalog_games(
    search: str = "",
    platform: Annotated[list[str] | None, Query()] = None,
    genre: Annotated[list[str] | None, Query()] = None,
    theme: Annotated[list[str] | None, Query()] = None,
    release_year_min: int | None = None,
    release_year_max: int | None = None,
    min_rating: float | None = None,
    min_reviews: int | None = None,
    hidden_gems_only: bool = False,
    sort: str = "highest_rating",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=24, ge=1, le=100),
) -> dict[str, Any]:
    return list_games(
        search=search,
        platform=platform,
        genre=genre,
        theme=theme,
        release_year_min=release_year_min,
        release_year_max=release_year_max,
        min_rating=min_rating,
        min_reviews=min_reviews,
        hidden_gems_only=hidden_gems_only,
        sort=sort,
        page=page,
        page_size=page_size,
    )


@router.get("/catalog/games/{game_id}", response_model=GameDetail)
def catalog_game_detail(game_id: int) -> dict[str, Any]:
    game = get_game(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found in app catalog.")
    return game
