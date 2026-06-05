import sqlite3

conn = sqlite3.connect('agent.db')
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
rows = conn.execute("SELECT * FROM run_log").fetchall()
print('Tables:', tables)
print('run_log rows:', rows)
conn.close()