from __future__ import annotations

from src.app.components.game_card import render_game_card


def render_game_detail(row) -> None:
    render_game_card(row, show_explanation=True)
