import sqlite3
conn = sqlite3.connect('data/database/igdb_games.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(analytics_ready_games)")
columns = [row[1] for row in cursor.fetchall()]
print(f"Available columns: {columns}")