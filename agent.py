import asyncio
import datetime
import json
import re
from difflib import SequenceMatcher
from urllib.parse import urlparse

from dotenv import load_dotenv
from digest.builder import build_html
from digest.sender import send_digest
from enricher.claude_client import enrich
from sources import rss, gnews
from storage.db import init_db, log_run, mark_sent
from storage.deduplicator import filter_duplicates
from utils.scoring import score_article
from utils.json_writer import save_articles
from sources import tollywood
from utils.categorizer import detect_category, detect_category_and_keywords, detect_subject



CRICKET_KEYWORDS = [
    "cricket",
    "ipl",
    "bcci",
    "virat",
    "rohit",
    "sachin",
    "vaibhav suryavanshi",
]

CRICKET_SUBJECTS = {
    "vaibhav": ["vaibhav", "suryavanshi", "sooryavanshi"],
    "kohli": ["virat kohli", "kohli"],
    "sachin": ["sachin"],
    "rohit": ["rohit sharma", "rohit"],
    "indian team": ["team india", "bcci"],
}

PERSON_CAPS = {
    "pawan kalyan": 1,
    "mahesh babu": 1,
    "ram charan": 1,
    "prabhas": 1,
    "allu arjun": 1,
    "virat kohli": 1,
}

STOPWORDS = {
    "the", "a", "an", "to", "for", "and", "of", "in", "on", "with",
    "after", "by", "via", "from", "at", "via", "new", "india",
}


def article_fingerprint(article):
    url = article.get("text_url") or article.get("url") or ""
    if url:
        return url
    return normalize_title(article.get("title", ""))


def person_for(article):
    text = (article.get("title", "") + " " + article.get("description", "")).lower()
    for person in PERSON_CAPS:
        if text_contains(text, person):
            return person
    return None


def stem_token(token):
    for suffix in ("ing", "ers", "er", "es", "s"):
        if token.endswith(suffix) and len(token) - len(suffix) >= 3:
            return token[:-len(suffix)]
    return token


def semantic_same_story(a, b):
    title_a = normalize_title(a.get("title", ""))
    title_b = normalize_title(b.get("title", ""))
    if not title_a or not title_b:
        return False

    if token_set_ratio(title_a, title_b) >= 78:
        return True

    a_tokens = {
        stem_token(token)
        for token in title_a.split()
        if token not in STOPWORDS and len(token) > 2
    }
    b_tokens = {
        stem_token(token)
        for token in title_b.split()
        if token not in STOPWORDS and len(token) > 2
    }

    common = a_tokens & b_tokens
    if len(common) >= 4:
        if any(word in common for word in ("drunk", "police", "hyderabad", "weekend", "arrest", "cinema", "imax", "peddi")):
            return True
        if abs(len(a_tokens) - len(b_tokens)) <= 6:
            return True
    if token_set_ratio(title_a, title_b) >= 72 and len(common) >= 3:
        return True

    return False


def normalize_title(title):
    return re.sub(r"[^a-z0-9 ]+", " ", title.lower()).strip()


def text_contains(text, keyword):
    pattern = r"\b" + re.escape(keyword) + r"\b"
    return re.search(pattern, text) is not None


def token_set_ratio(a, b):
    a_tokens = set(a.split())
    b_tokens = set(b.split())
    if not a_tokens or not b_tokens:
        return 0
    matched = len(a_tokens & b_tokens)
    return int(100 * (2 * matched) / (len(a_tokens) + len(b_tokens)))


def subject_for(title):
    title = title.lower()
    for subject, keywords in CRICKET_SUBJECTS.items():
        if any(text_contains(title, keyword) for keyword in keywords):
            return subject
    if any(keyword in title for keyword in CRICKET_KEYWORDS):
        return "cricket"
    return None


def story_domain(article):
    return urlparse(article.get("url", "") or article.get("text_url", "")).netloc.lower()


def similar_headlines(a, b):
    title_a = normalize_title(a.get("title", ""))
    title_b = normalize_title(b.get("title", ""))

    if title_a == title_b:
        return True

    return token_set_ratio(title_a, title_b) >= 92


def is_cricket_article(article):
    text = (article.get("title", "") + " " + article.get("description", "")).lower()
    CRICKET_TERMS = {
        "cricket",
        "bcci",
        "ipl",
        "odi",
        "t20",
        "virat",
        "kohli",
        "rohit",
        "dhoni",
        "sachin",
        "bumrah",
        "vaibhav",
        "suryavanshi",
        "sooryavanshi",
        "wicket",
        "bowler",
        "batsman",
        "stump",
        "maiden",
        "catch",
        "run out",
        "lbw",
        "no ball",
        "wide",
    }

    return any(text_contains(text, term) for term in CRICKET_TERMS)

load_dotenv()

def is_active_window():
    h = datetime.datetime.now().hour
    return 0 <= h < 18   # 12 AM – 6 PM


async def run_agent():

    if not is_active_window():
        print("Outside active window — skipping")
        return

    print("Fetching news...")

    raw_lists = await asyncio.gather(
        rss.fetch(),
        gnews.fetch(),
        gnews.fetch_cricket(),
        gnews.fetch_celebs(),
        tollywood.fetch(),
        return_exceptions=True
    )

    raw = [
        article
        for lst in raw_lists
        if isinstance(lst, list)
        for article in lst
    ]

    print(f"Fetched {len(raw)} raw articles")

    import json
    import os

    os.makedirs("api", exist_ok=True)

    with open(
    "api/articles.json",
    "w",
    encoding="utf-8"
    ) as f:
        json.dump(raw, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(raw)} articles to api/articles.json")

    # Remove exact title duplicates immediately after fetching
    seen_titles = set()
    unique = []
    for article in raw:
        title = article.get("title", "")
        key = normalize_title(title)
        if not key:
            unique.append(article)
            continue
        if key in seen_titles:
            print("REMOVED FETCH DUP:", title)
            continue
        seen_titles.add(key)
        unique.append(article)

    raw = unique

    # Hard locality filter: keep only AP/Telangana / Telugu-relevant stories
    AP_KEYWORDS = [
        "andhra",
        "telangana",
        "hyderabad",
        "amaravati",
        "vizag",
        "visakhapatnam",
        "vijayawada",
        "tirupati",
        "ram charan",
        "prabhas",
        "allu arjun",
        "tollywood",
    ]

    raw = [
        a
        for a in raw
        if is_cricket_article(a) or any(
            k in (a.get("title", "") + " " + a.get("description", "")).lower()
            for k in AP_KEYWORDS
        )
    ]

    print(f"After locality filter: {len(raw)} articles")
    print(f"After locality filter: {len(raw)} articles")

    save_articles(
    "api/locality_articles.json",
    raw
    )

    # Score articles
    for article in raw:
        article["score"] = score_article(article)
        category = detect_category(article)
        article["_original_category"] = category
        article["bypass_db_dupe"] = (
            article["score"] > 1000 or
            (category in {"cricket", "tollywood"} and article["score"] > 700)
        )

    # Deduplicate semantically before ranking so the top stories do not contain the same event in multiple variants.
    semantic_deduped = []
    for article in sorted(raw, key=lambda x: x["score"], reverse=True):
        duplicate = next(
            (kept for kept in semantic_deduped if semantic_same_story(article, kept)),
            None
        )
        if duplicate:
            print(
                "REMOVED SEMANTIC DUP:",
                f"{article.get('score',0):.0f}",
                article.get("title", ""),
                "vs",
                duplicate.get("title", "")
            )
            continue
        semantic_deduped.append(article)
    raw = semantic_deduped
    raw = semantic_deduped

    save_articles(
    "api/semantic_articles.json",
    raw
    )

    # Apply subject-level caps before ranking so the final digest doesn't get flooded
    # by one subject such as Vaibhav, Ram Charan, or monsoon.
    MAX_SUBJECT = {
        "suryakumar": 1,
        "vaibhav": 1,
        "ram_charan": 1,
        "prabhas": 1,
        "monsoon": 1,
    }

    subject_buckets = {}
    others = []
    for article in raw:
        subject = detect_subject(article)
        if subject and subject in MAX_SUBJECT:
            subject_buckets.setdefault(subject, []).append(article)
        else:
            others.append(article)

    capped = []
    for subject, articles in subject_buckets.items():
        articles.sort(key=lambda x: x["score"], reverse=True)
        capped.extend(articles[:MAX_SUBJECT[subject]])

    capped.extend(others)
    raw = capped

    seen_persons = {}
    filtered_persons = []
    for article in sorted(raw, key=lambda a: a["score"], reverse=True):
        person = person_for(article)
        if person:
            count = seen_persons.get(person, 0)
            if count >= PERSON_CAPS.get(person, 1):
                print("SKIP PERSON CAP:", person, article.get("title", ""))
                continue
            seen_persons[person] = count + 1
        filtered_persons.append(article)
    raw = filtered_persons

    raw.sort(
        key=lambda a: a["score"],
        reverse=True
    )

    TOP_LOCK = 15
    locked_titles = set()
    subject_counts = {}

    for article in raw[:TOP_LOCK]:
        title = article.get("title", "")
        subject = subject_for(title)

        if subject:
            subject_counts.setdefault(subject, 0)
            if subject_counts[subject] < 2:
                subject_counts[subject] += 1
                locked_titles.add(title)
            else:
                print("SKIP LOCK DUPLICATE SUBJECT:", subject, title)
        else:
            locked_titles.add(title)

    print("LOCKED TITLES:", len(locked_titles), locked_titles)

    print("\nSCORED ARTICLES BEFORE DEDUPE")
    for article in raw:
        category, matched_keywords = detect_category_and_keywords(article)
        title = article.get("title", "")
        score = article["score"]
        print(
            f"CATEGORY DEBUG: {title}\n"
            f" category={category}\n"
            f" matched_keywords={matched_keywords}"
        )
        print(f"{category:10} | {score:4.0f} | KEEP | {title}")
        if "ram charan" in title.lower() or "peddi" in title.lower():
            print("RAM CHARAN SCORE:", score)

    MONSOON_KEYWORDS = [
        "monsoon",
        "rain",
        "rainfall",
        "imd",
        "heavy rain",
        "weather alert",
    ]

    clustered_weather = []
    clustered_weather_titles = []

    MAX_WEATHER_CLUSTER = 2
    weather_count = 0

    for article in sorted(raw, key=lambda x: x["score"], reverse=True):
        if detect_category(article) != "weather":
            continue

        if weather_count >= MAX_WEATHER_CLUSTER:
            print("REMOVED WEATHER CLUSTER:", f"{article['score']:.0f}", article.get("title", ""))
            continue

        clustered_weather.append(article)
        weather_count += 1

    raw = [article for article in raw if detect_category(article) != "weather"] + clustered_weather
    raw.sort(key=lambda a: a["score"], reverse=True)

    MIN_SCORE = 50
    raw = [article for article in raw if article.get("score", 0) >= MIN_SCORE]

    local_keywords = [
        "andhra pradesh",
        "telangana",
        "hyderabad",
        "amaravati",
        "visakhapatnam",
        "vizag",
        "vijayawada",
        "tirupati",
        "tollywood",
        "telugu movie",
        "telugu movies",
        "pawan kalyan",
        "chandrababu naidu",
        "nara lokesh",
        "revanth reddy",
        "janasena",
        "tdp",
        "ysrcp",
        "allu arjun",
        "ram charan",
        "jr ntr",
        "prabhas",
        "rain",
        "cyclone",
        "heatwave",
        "weather",
        "recruitment",
        "results",
        "exam",
        "notification",
        "counselling"
    ]

    local = [
        article
        for article in raw
        if any(
            keyword in (
                article.get("title", "") +
                " " +
                article.get("description", "")
            ).lower()
            for keyword in local_keywords
        )
    ]

    print(
        f"Found {len(local)} AP/Telangana/Telugu stories"
    )

    for story in local[:10]:
        print("-", story["title"])

    # Move local stories to front
    raw.sort(
        key=lambda article: any(
            keyword in (
                article.get("title", "") +
                " " +
                article.get("description", "")
            ).lower()
            for keyword in local_keywords
        ),
        reverse=True
    )

    # Cluster high-frequency subjects early so the digest preserves topic diversity.
    SUBJECT_CLUSTER_KEYWORDS = {
        "vaibhav": ["vaibhav", "suryavanshi", "sooryavanshi"],
        "ram_charan": ["ram charan"],
        "prabhas": ["prabhas"],
        "monsoon": ["monsoon", "rain", "rainfall", "heatwave", "cyclone"],
    }

    clustered_subjects = {}
    next_raw = []
    for article in sorted(raw, key=lambda x: x.get("score", 0), reverse=True):
        title = article.get("title", "").lower()
        assigned = False
        for cluster_name, keywords in SUBJECT_CLUSTER_KEYWORDS.items():
            if any(text_contains(title, k) for k in keywords):
                if cluster_name not in clustered_subjects:
                    clustered_subjects[cluster_name] = article
                    next_raw.append(article)
                else:
                    kept = clustered_subjects[cluster_name]
                    sim = token_set_ratio(normalize_title(kept.get("title", "")), normalize_title(article.get("title", "")))
                    if sim >= 85:
                        print("REMOVED SUBJECT CLUSTER DUP:", f"{article.get('score',0):.0f}", cluster_name, title)
                    else:
                        next_raw.append(article)
                assigned = True
                break
        if not assigned:
            next_raw.append(article)
    raw = next_raw

    # Deduplicate similar headlines by exact or very-high similarity within the same source
    deduped = []

    for article in raw:

        title = article.get("title", "")
        category = detect_category(article)
        score = article.get("score", 0)

        # Do not auto-keep locked items here; they should still pass duplicate checks
        # but we keep track of locked titles separately for final selection.

        duplicate = next(
            (kept for kept in deduped if semantic_same_story(article, kept)),
            None
        )

        if duplicate:
            print(
                "REMOVED DUPLICATE:", f"{score:.0f}", category, title,
                "REASON: similar to",
                duplicate.get("title")
            )
            continue

        deduped.append(article)

    raw = deduped

    print(
        f"After deduplication: {len(raw)} articles"
    )

    # Filter low-engagement stories
    BLACKLIST = [
        "yuva sangam",
        "cultural bridge",
        "seminar",
        "workshop",
        "conference",
        "chess tournament",
    ]

    filtered = []
    for article in raw:
        title_lower = article.get("title", "").lower()
        if any(word in title_lower for word in BLACKLIST):
            print("REMOVED BLACKLIST:", article.get("title"))
            continue
        filtered.append(article)

    raw = filtered

    print(
        f"After blacklist filter: {len(raw)} articles"
    )

    # Filter duplicates from database before AI
    # Map url to text_url first
    for article in raw:
        if "url" in article and "text_url" not in article:
            article["text_url"] = article["url"]

    raw = await filter_duplicates(raw, locked_titles)

    print(
        f"After DB duplicate filter: {len(raw)} articles"
    )

    candidates = sorted(raw, key=lambda x: x.get("score", 0), reverse=True)[:15]

    print("\nFINAL TOP STORIES")
    for article in candidates:
        print(
            f"{article.get('score',0):4.0f} | {article.get('title','')}"
        )

    print(f"\nSending {len(candidates)} candidates to Claude")
    print("\nEnriching articles with OpenAI...")

    enriched = await enrich(candidates)
    print(f"Claude returned {len(enriched)} stories")

    if not enriched:
        await log_run(len(raw), 0, "SKIPPED", "Claude returned empty")
        print("Claude returned empty — skipping send")
        return

    enriched_map = {}
    for story in enriched:
        key = article_fingerprint(story)
        if key:
            enriched_map[key] = story

    final = []
    for candidate in candidates:
        key = article_fingerprint(candidate)
        story = None
        if key and key in enriched_map:
            story = dict(enriched_map[key])
            story["category"] = candidate.get("_original_category") or detect_category(candidate)
        else:
            story = dict(candidate)
            story["category"] = candidate.get("_original_category") or detect_category(candidate)
            story["summary"] = story.get("summary") or story.get("description", "")[:200]
        final.append(story)

    print(
        f"Selected {len(final)} stories"
    )
    save_articles(
    "api/final_articles.json",
    final
    )

    fresh = final

    print(
        f"{len(fresh)} fresh stories to send"
    )

    print("\nFinal Digest Stories:\n")

    for i, story in enumerate(
        fresh,
        start=1
    ):

        print(
            f"{i}. "
            f"[{story.get('category', 'General')}] "
            f"{story.get('title', 'Untitled')}"
        )

    html = build_html(fresh)

    status = send_digest(html)

    await mark_sent(fresh)

    await log_run(
        len(raw),
        len(fresh),
        status
    )

    print(
        f"\n✓ Sent {len(fresh)} stories — status {status}"
    )


if __name__ == "__main__":

    print("Starting news agent...")

    asyncio.run(init_db())
    asyncio.run(run_agent())

