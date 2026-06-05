import asyncio
from dotenv import load_dotenv
load_dotenv()

from enricher.claude_client import enrich

SAMPLE = [
    {"title": "India GDP grows 7.2% in Q1", "url": "https://ex.com/1",
     "description": "Strong manufacturing output drove growth.", "source": "Reuters", "published_at": "2026-05-27"},
    {"title": "Apple launches M5 MacBook Pro", "url": "https://ex.com/2",
     "description": "New chip delivers 40% performance gains.", "source": "TechCrunch", "published_at": "2026-05-27"},
    {"title": "India GDP Q1 expansion surprises economists", "url": "https://ex.com/3",
     "description": "Duplicate of story 1.", "source": "Bloomberg", "published_at": "2026-05-27"},
    {"title": "SpaceX Starship completes orbital test", "url": "https://ex.com/4",
     "description": "Launch deemed a full success.", "source": "BBC", "published_at": "2026-05-26"},
    {"title": "RBI holds repo rate at 6.5%", "url": "https://ex.com/5",
     "description": "Monetary policy unchanged.", "source": "Mint", "published_at": "2026-05-26"},
]

async def test():
    print("Sending 5 articles to OpenAI (1 duplicate expected to be removed)...")
    result = await enrich(SAMPLE)

    print(f"\nReturned {len(result)} stories (expected 4)")
    print("-" * 50)

    for s in result:
        print(f"[{s.get('category', '?')}] {s.get('title', '')[:55]}")
        print(f"  Summary words: {len(s.get('summary','').split())}")
        print(f"  URL: {s.get('text_url','MISSING')}")
        print()

    errors = []
    for s in result:
        for key in ["title", "summary", "category", "text_url"]:
            if key not in s:
                errors.append(f"Missing key '{key}' in: {s.get('title','?')}")
        if len(s.get("summary", "").split()) > 80:
            errors.append(f"Summary too long in: {s.get('title','?')}")

    if errors:
        print("FAILURES:")
        for e in errors:
            print(" -", e)
    else:
        print("All schema checks passed.")

asyncio.run(test())