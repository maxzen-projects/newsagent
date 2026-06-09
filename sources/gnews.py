import httpx
import os


async def fetch_queries(queries):

    key = os.getenv("GNEWS_API_KEY")

    articles = []

    async with httpx.AsyncClient() as client:

        for q in queries:

            r = await client.get(
                "https://gnews.io/api/v4/search",
                params={
                    "q": q,
                    "lang": "en",
                    "max": 10,
                    "apikey": key
                }
            )

            data = r.json()

            for a in data.get("articles", []):

                articles.append({
                    "title": a["title"],
                    "url": a["url"],
                    "description": a.get("description", ""),
                    "source": a["source"]["name"],
                    "published_at": a["publishedAt"]
                })

    return articles


async def fetch():
    queries = [
        "Andhra Pradesh",
        "Telangana",
        "Hyderabad",
        "Tollywood"
    ]
    return await fetch_queries(queries)


async def fetch_cricket():
    queries = [
        "cricket",
        "IPL",
        "BCCI",
        "Team India",
        "Virat Kohli",
        "Rohit Sharma",
        "Shreyas Iyer",
        "Sachin Tendulkar",
        "Vaibhav Suryavanshi"
    ]
    return await fetch_queries(queries)


async def fetch_celebs():
    queries = [
        "Ram Charan",
        "Pawan Kalyan",
        "Jr NTR",
        "Allu Arjun",
        "Prabhas",
        "Mahesh Babu"
    ]
    return await fetch_queries(queries)
