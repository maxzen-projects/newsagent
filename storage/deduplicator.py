import aiosqlite
import datetime
from .db import DB_PATH

async def filter_duplicates(stories: list) -> list:
    today = datetime.date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        fresh = []
        for story in stories:
            cur = await db.execute(
                "SELECT 1 FROM sent_stories WHERE url=? AND sent_at=?",
                (story["text_url"], today)
            )
            if not await cur.fetchone():
                fresh.append(story)
        return fresh