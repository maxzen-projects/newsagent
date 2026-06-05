import aiosqlite, datetime

DB_PATH = "agent.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
          CREATE TABLE IF NOT EXISTS run_log (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at        DATETIME NOT NULL,
            articles_raw  INT,
            articles_sent INT,
            email_status  TEXT,
            error_msg     TEXT
          )""")
        await db.execute("""
          CREATE TABLE IF NOT EXISTS sent_stories (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            url      TEXT NOT NULL,
            sent_at  DATE NOT NULL,
            UNIQUE(url, sent_at)
          )""")
        await db.commit()

async def log_run(raw, sent, status, error=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO run_log VALUES (NULL,?,?,?,?,?)",
            (datetime.datetime.now(), raw, sent, status, error)
        )
        await db.commit()

async def mark_sent(urls: list):
    today = datetime.date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executemany(
            "INSERT OR IGNORE INTO sent_stories VALUES (NULL,?,?)",
            [(u, today) for u in urls]
        )
        await db.commit()