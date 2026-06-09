import aiosqlite
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse

from .db import DB_PATH


def normalize_title(title):
    return re.sub(r"[^a-z0-9 ]+", " ", title.lower()).strip()


def token_set_ratio(a, b):
    a_tokens = set(a.split())
    b_tokens = set(b.split())
    if not a_tokens or not b_tokens:
        return 0
    matched = len(a_tokens & b_tokens)
    return int(100 * (2 * matched) / (len(a_tokens) + len(b_tokens)))


def story_domain(url):
    return urlparse(url).netloc.lower()


async def filter_duplicates(stories, locked_titles=None):

    if locked_titles is None:
        locked_titles = set()

    cutoff = (
        datetime.utcnow() - timedelta(days=2)
    ).isoformat()

    async with aiosqlite.connect(DB_PATH) as db:

        fresh = []

        for story in stories:
            if story.get("bypass_db_dupe"):
                print("BYPASS DB DUPE:", f"{story.get('score',0):.0f}", story.get('title', ""))
                fresh.append(story)
                continue

            title = story.get("title", "")

            url = story.get("text_url") or story.get("url") or ""
            domain = story_domain(url)
            title_norm = normalize_title(story.get("title", ""))

            cur = await db.execute(
                """
                SELECT title_norm
                FROM sent_stories
                WHERE domain = ?
                AND sent_datetime >= ?
                """,
                (
                    domain,
                    cutoff
                )
            )

            rows = await cur.fetchall()
            is_duplicate = False

            if url:
                cur = await db.execute(
                    """
                    SELECT 1
                    FROM sent_stories
                    WHERE published_at >= ?
                    AND url = ?
                    """,
                    (
                        cutoff,
                        url
                    )
                )
                exists = await cur.fetchone()
                if exists:
                    is_duplicate = True

            if not is_duplicate:
                for (other_title_norm,) in rows:
                    if token_set_ratio(title_norm, other_title_norm) >= 92:
                        is_duplicate = True
                        break

            if is_duplicate:
                print("REMOVED DB DUPE:", f"{story.get('score',0):.0f}", title)
            else:
                print("KEEPING DB:", f"{story.get('score',0):.0f}", title)
                fresh.append(story)

        return fresh