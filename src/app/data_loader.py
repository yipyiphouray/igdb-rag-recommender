from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from src.app import config


def _streamlit_cache_data():
    try:
        import streamlit as st
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        if get_script_run_ctx() is not None:
            return st.cache_data
    except Exception:
        pass

    def lru_cache_data(func):
        return lru_cache(maxsize=1)(func)

    return lru_cache_data


cache_data = _streamlit_cache_data()


def _read_table(path: Path, csv_fallback: Path | None = None) -> pd.DataFrame:
    if path.exists():
        if path.suffix == ".parquet":
            return pd.read_parquet(path)
        if path.suffix == ".csv":
            return pd.read_csv(path)
    if csv_fallback and csv_fallback.exists():
        return pd.read_csv(csv_fallback)
    raise FileNotFoundError(f"Missing app data artifact: {path}")


@cache_data
def load_app_catalog() -> pd.DataFrame:
    return _read_table(config.APP_CATALOG_PATH, config.APP_CATALOG_CSV_PATH)


@cache_data
def load_hidden_gems() -> pd.DataFrame:
    return _read_table(config.APP_HIDDEN_GEMS_PATH, config.APP_HIDDEN_GEMS_CSV_PATH)


@cache_data
def load_filter_options() -> dict[str, Any]:
    if not config.APP_FILTER_OPTIONS_PATH.exists():
        return {}
    try:
        with config.APP_FILTER_OPTIONS_PATH.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


@cache_data
def load_json_artifact(path: str | Path) -> dict[str, Any]:
    artifact_path = Path(path)
    if not artifact_path.exists():
        return {}
    try:
        with artifact_path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


@cache_data
def load_csv_artifact(path: str | Path) -> pd.DataFrame:
    artifact_path = Path(path)
    if not artifact_path.exists():
        return pd.DataFrame()
    return pd.read_csv(artifact_path)

