import feedparser

RSS_FEEDS = [
    "https://www.123telugu.com/feed",
    "https://www.gulte.com/feed",
    "https://www.telugu360.com/feed",
]


async def fetch():

    articles = []

    for url in RSS_FEEDS:

        try:

            feed = feedparser.parse(url)

            for entry in feed.entries[:20]:

                articles.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "description": entry.get("summary", ""),
                    "source": feed.feed.get("title", "Tollywood"),
                    "published_at": entry.get("published", "")
                })

        except Exception as e:

            print(f"[tollywood] {e}")

    return articles