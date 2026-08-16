import aiosqlite
import datetime
import re
from urllib.parse import urlparse

DB_PATH = "agent.db"


def normalize_title(title):
    return re.sub(r"[\W_]+", " ", title.lower()).strip()


def story_domain(url):
    return urlparse(url).netloc.lower()


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS run_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at DATETIME NOT NULL,
            articles_raw INTEGER,
            articles_sent INTEGER,
            email_status TEXT,
            error_msg TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS sent_stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            title TEXT,
            title_norm TEXT,
            domain TEXT,
            sent_datetime DATETIME NOT NULL
        )
        """)

        cur = await db.execute("PRAGMA table_info(sent_stories)")
        columns = [row[1] for row in await cur.fetchall()]

        if "title" not in columns:
            await db.execute("ALTER TABLE sent_stories ADD COLUMN title TEXT")
        if "title_norm" not in columns:
            await db.execute("ALTER TABLE sent_stories ADD COLUMN title_norm TEXT")
        if "domain" not in columns:
            await db.execute("ALTER TABLE sent_stories ADD COLUMN domain TEXT")
        if "published_at" not in columns:
            await db.execute("ALTER TABLE sent_stories ADD COLUMN published_at DATETIME")
        if "sent_datetime" not in columns:
            await db.execute("ALTER TABLE sent_stories ADD COLUMN sent_datetime DATETIME")
            if "sent_at" in columns:
                await db.execute("UPDATE sent_stories SET sent_datetime = sent_at WHERE sent_datetime IS NULL")

        await db.commit()


async def log_run(raw, sent, status, error=None):
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            """
            INSERT INTO run_log
            VALUES (NULL, ?, ?, ?, ?, ?)
            """,
            (
                datetime.datetime.utcnow(),
                raw,
                sent,
                status,
                error
            )
        )

        await db.commit()


async def mark_sent(entries):

    now = datetime.datetime.utcnow().isoformat()
    rows = []

    for entry in entries:
        if isinstance(entry, str):
            url = entry
            title = ""
            published_at = None
        else:
            url = entry.get("text_url") or entry.get("url") or ""
            title = entry.get("title", "")
            published_at = entry.get("published_at")

        domain = story_domain(url)
        title_norm = normalize_title(title)

        rows.append((url, title, title_norm, domain, now, published_at))

    async with aiosqlite.connect(DB_PATH) as db:

        await db.executemany(
            """
            INSERT OR REPLACE INTO sent_stories
            (url, title, title_norm, domain, sent_datetime, published_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows
        )

        await db.commit()