from __future__ import annotations

import math
import html
from typing import Iterable

import pandas as pd

from src.app.constants import LIST_DELIMITER


def split_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, float) and math.isnan(value):
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    return [item.strip() for item in text.split(LIST_DELIMITER) if item.strip()]


def join_list(values: Iterable[object]) -> str:
    cleaned = sorted({str(value).strip() for value in values if str(value).strip()})
    return LIST_DELIMITER.join(cleaned)


def format_percent(value: object, decimals: int = 1, missing: str = "Unknown") -> str:
    if value is None or pd.isna(value):
        return missing
    return f"{float(value) * 100:.{decimals}f}%"


def format_number(value: object, decimals: int = 0, missing: str = "Unknown") -> str:
    if value is None or pd.isna(value):
        return missing
    if decimals == 0:
        return f"{float(value):,.0f}"
    return f"{float(value):,.{decimals}f}"


def format_rating(value: object) -> str:
    return format_number(value, decimals=1)


def compact_text(value: object, max_chars: int = 240) -> str:
    if value is None or pd.isna(value):
        return ""
    text = " ".join(str(value).split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "..."


def html_escape(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return html.escape(str(value), quote=True)


def short_platform_name(value: str) -> str:
    text = value.lower()
    if "pc" in text or "windows" in text:
        return "PC"
    if "playstation 5" in text:
        return "PS5"
    if "playstation 4" in text:
        return "PS4"
    if "playstation" in text:
        return "PS"
    if "xbox series" in text:
        return "Xbox X|S"
    if "xbox one" in text:
        return "Xbox One"
    if "xbox" in text:
        return "Xbox"
    if "switch" in text:
        return "Switch"
    if "nintendo" in text:
        return "Nintendo"
    if "mac" in text:
        return "Mac"
    if "linux" in text:
        return "Linux"
    if "ios" in text or "iphone" in text or "ipad" in text:
        return "iOS"
    if "android" in text:
        return "Android"
    if "web" in text or "browser" in text:
        return "Web"
    return value[:16]


def badge_html(values: Iterable[str], css_class: str, max_items: int = 6, shorten_platforms: bool = False) -> str:
    cleaned = [str(value).strip() for value in values if str(value).strip()]
    if shorten_platforms:
        display_values = []
        seen = set()
        for value in cleaned:
            short = short_platform_name(value)
            if short not in seen:
                display_values.append(short)
                seen.add(short)
    else:
        display_values = cleaned

    shown = display_values[:max_items]
    badges = [f'<span class="{css_class}">{html_escape(value)}</span>' for value in shown]
    remaining = len(display_values) - len(shown)
    if remaining > 0:
        badges.append(f'<span class="{css_class}">+{remaining}</span>')
    return "".join(badges)


def contains_any(list_text: object, selected: Iterable[str]) -> bool:
    selected_set = {item.strip().lower() for item in selected if str(item).strip()}
    if not selected_set:
        return True
    values = {item.lower() for item in split_list(list_text)}
    return bool(values.intersection(selected_set))


def overlap_count(list_text: object, selected: Iterable[str]) -> int:
    selected_set = {item.strip().lower() for item in selected if str(item).strip()}
    if not selected_set:
        return 0
    values = {item.lower() for item in split_list(list_text)}
    return len(values.intersection(selected_set))

