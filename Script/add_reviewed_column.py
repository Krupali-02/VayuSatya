# Script/add_reviewed_column.py
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  # repo root
DB_PATH = BASE_DIR / "Data" / "vayusatya.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA table_info(reports);")
cols = [row[1] for row in cur.fetchall()]

if "reviewed" not in cols:
    cur.execute("ALTER TABLE reports ADD COLUMN reviewed INTEGER DEFAULT 0;")
    conn.commit()
    print("Added 'reviewed' column to reports table.")
else:
    print("'reviewed' column already exists.")

conn.close()