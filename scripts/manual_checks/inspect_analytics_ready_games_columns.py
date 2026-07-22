import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "database" / "igdb_games.db"


def inspect_columns() -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(analytics_ready_games)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Available columns: {columns}")


if __name__ == "__main__":
    inspect_columns()
