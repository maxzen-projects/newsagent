import feedparser, yaml

async def fetch(feed_urls=None):
    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)
    urls = feed_urls or cfg.get("rss_feeds", [])
    articles = []
    for url in urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            articles.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "description": entry.get("summary", ""),
                "source": feed.feed.get("title", "RSS"),
                "published_at": entry.get("published", "")
            })
    return articles