import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall()
print("=== SQLite Table Record Counts ===")
for (t,) in tables:
    count = cur.execute(f'SELECT COUNT(*) FROM "{t}";').fetchone()[0]
    if count > 0:
        print(f"  {t}: {count} records")
conn.close()

