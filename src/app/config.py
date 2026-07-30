from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
DATABASE_PATH = DATA_DIR / "database" / "igdb_games.db"

DESCRIPTIVE_DIR = DATA_DIR / "analytics" / "descriptive"
DIAGNOSTIC_DIR = DATA_DIR / "analytics" / "diagnostic"

APP_DATA_DIR = DATA_DIR / "app"
RECOMMENDATIONS_DIR = DATA_DIR / "recommendations"
RAG_DIR = DATA_DIR / "rag"

APP_CATALOG_PATH = APP_DATA_DIR / "app_game_catalog.parquet"
APP_CATALOG_CSV_PATH = APP_DATA_DIR / "app_game_catalog.csv"
APP_HIDDEN_GEMS_PATH = APP_DATA_DIR / "app_hidden_gems.parquet"
APP_HIDDEN_GEMS_CSV_PATH = APP_DATA_DIR / "app_hidden_gems.csv"
APP_FILTER_OPTIONS_PATH = APP_DATA_DIR / "app_filter_options.json"
APP_INSIGHT_SUMMARY_PATH = APP_DATA_DIR / "app_insight_summary.json"
APP_INSIGHTS_DASHBOARD_PATH = APP_DATA_DIR / "app_insights_dashboard.json"
APP_METHODOLOGY_METRICS_PATH = APP_DATA_DIR / "app_methodology_metrics.json"

