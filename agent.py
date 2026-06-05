import asyncio, datetime, os
from dotenv import load_dotenv
load_dotenv()

from sources import newsapi, rss, youtube
from enricher.claude_client import enrich
from digest.builder import build_html
from digest.sender import send_digest
from storage.db import init_db, log_run, mark_sent
from storage.deduplicator import filter_duplicates

def is_active_window():
    h = datetime.datetime.now().hour
    return 0 <= h < 18   # 12 AM – 6 PM

async def run_agent():
    if not is_active_window():
        print("Outside active window — skipping")
        return

    # 1. Fetch from all sources in parallel
    raw_lists = await asyncio.gather(
        newsapi.fetch(), rss.fetch(), return_exceptions=True
    )
    raw = [a for lst in raw_lists if isinstance(lst, list) for a in lst]

    # 2. Enrich with Claude
    enriched = await enrich(raw)
    if not enriched:
        await log_run(len(raw), 0, "SKIPPED", "Claude returned empty")
        return

    # 3. Add YouTube links
    for story in enriched:
        story["video_url"] = await youtube.fetch_video(story["title"])

    # 4. Filter duplicates already sent today
    fresh = await filter_duplicates(enriched)

    # 5. Build and send email
    html = build_html(fresh)
    status = send_digest(html)

    # 6. Persist to DB
    await mark_sent([s["text_url"] for s in fresh])
    await log_run(len(raw), len(fresh), status)
    print(f"✓ Sent {len(fresh)} stories — status {status}")

if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(run_agent())


from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler(timezone="Asia/Kolkata")

@scheduler.scheduled_job("cron", hour="*/2")
def scheduled_run():
    asyncio.run(run_agent())

scheduler.start()