from __future__ import annotations

import math
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

