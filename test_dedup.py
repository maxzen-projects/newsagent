import asyncio
from dotenv import load_dotenv
load_dotenv()

from storage.db import init_db, mark_sent
from storage.deduplicator import filter_duplicates

STORIES = [
    {"title": "Story A", "text_url": "https://ex.com/a", "summary": "...", "category": "Tech", "video_url": None, "source": "BBC"},
    {"title": "Story B", "text_url": "https://ex.com/b", "summary": "...", "category": "World", "video_url": None, "source": "Reuters"},
]

async def test():
    await init_db()

    fresh1 = await filter_duplicates(STORIES)
    print(f"First pass:  {len(fresh1)} stories (expected 2)")

    await mark_sent([s["text_url"] for s in fresh1])

    fresh2 = await filter_duplicates(STORIES)
    print(f"Second pass: {len(fresh2)} stories (expected 0)")

    if len(fresh1) == 2 and len(fresh2) == 0:
        print("Deduplication working correctly.")
    else:
        print("FAILED — check storage/deduplicator.py")

asyncio.run(test())