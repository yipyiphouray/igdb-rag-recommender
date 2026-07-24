from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
APP_DATA_DIR = DATA_DIR / "app"
ANALYTICS_DIR = DATA_DIR / "analytics"
DESCRIPTIVE_DIR = ANALYTICS_DIR / "descriptive"
DIAGNOSTIC_DIR = ANALYTICS_DIR / "diagnostic"

APP_CATALOG_PATH = APP_DATA_DIR / "app_game_catalog.parquet"
APP_HIDDEN_GEMS_PATH = APP_DATA_DIR / "app_hidden_gems.parquet"
APP_FILTER_OPTIONS_PATH = APP_DATA_DIR / "app_filter_options.json"
APP_INSIGHT_SUMMARY_PATH = APP_DATA_DIR / "app_insight_summary.json"
APP_INSIGHTS_DASHBOARD_PATH = APP_DATA_DIR / "app_insights_dashboard.json"
APP_METHODOLOGY_METRICS_PATH = APP_DATA_DIR / "app_methodology_metrics.json"

PREDICTIVE_DIR = ANALYTICS_DIR / "predictive"
RAG_DIR = DATA_DIR / "rag"

API_NAME = "igdb-website-api"
API_VERSION = "0.1.0"
