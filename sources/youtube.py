import os
from googleapiclient.discovery import build

async def fetch_video(query: str) -> str | None:
    yt = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))
    resp = yt.search().list(
        q=query, part="snippet", type="video",
        maxResults=1, order="date"
    ).execute()
    items = resp.get("items", [])
    if items:
        vid_id = items[0]["id"]["videoId"]
        return f"https://youtube.com/watch?v={vid_id}"
    return None