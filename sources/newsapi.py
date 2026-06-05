import httpx, os

async def fetch(categories=None):
    key = os.getenv("NEWSAPI_KEY")
    articles = []
    queries = categories or ["technology", "business", "india", "science", "world"]

    async with httpx.AsyncClient() as client:
        for q in queries:
            try:
                r = await client.get(
                    "https://newsapi.org/v2/everything",
                    params={
                        "apiKey": key,
                        "q": q,
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": 20
                    },
                    timeout=10.0
                )
                data = r.json()

                if data.get("status") != "ok":
                    print(f"[newsapi] Warning for '{q}': {data.get('message', 'unknown error')}")
                    continue

                for a in data.get("articles", []):
                    title = a.get("title", "")
                    url = a.get("url", "")

                    # skip removed/deleted articles
                    if not title or title == "[Removed]" or not url:
                        continue

                    articles.append({
                        "title": title,
                        "url": url,
                        "description": a.get("description", ""),
                        "source": a["source"]["name"],
                        "published_at": a.get("publishedAt", "")
                    })

            except Exception as e:
                print(f"[newsapi] Error fetching '{q}': {e}")
                continue

    return articles