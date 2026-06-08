import sqlite3

conn = sqlite3.connect("data/database/igdb_games.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT,
    summary TEXT,
    first_release_date INTEGER,
    total_rating REAL,
    total_rating_count INTEGER
);
""")

conn.commit()
conn.close()