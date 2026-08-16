from datetime import datetime, timezone
from utils.categorizer import detect_category

LOCAL = {
"andhra pradesh": 5,
"telangana": 5,
"hyderabad": 5,
"amaravati": 5,
"visakhapatnam": 5,
"vizag": 5,
"vijayawada": 5,
"tirupati": 5,
}

POLITICS = {
"pawan kalyan": 35,
"chandrababu": 30,
"nara lokesh": 25,
"revanth reddy": 25,
"jagan": 30,
"tdp": 20,
"ysrcp": 20,
"janasena": 20,
}

WEATHER = {
"rain": 30,
"monsoon": 30,
"heatwave": 30,
"cyclone": 40,
"imd": 25,
"warning": 20,
"alert": 20,
"heavy rainfall": 30,
"orange alert": 25,
"red alert": 35,
}

JOBS = {
"exam": 30,
"result": 30,
"results": 30,
"recruitment": 35,
"notification": 35,
"hall ticket": 25,
"counselling": 25,
"tspsc": 35,
"appsc": 35,
"group 1": 25,
"group 2": 25,
"group 4": 25,
"jee": 20,
"neet": 20,
"ugc net": 20,
}

TOLLYWOOD = {
"tollywood": 25,
"movie": 15,
"film": 15,
"cinema": 15,

"box office": 40,
"collection": 40,
"collections": 40,

"trailer": 35,
"teaser": 35,
"first look": 35,
"glimpse": 35,

"release date": 25,
"ott": 25,
"netflix": 20,
"amazon prime": 20,
"aha": 20,

"prabhas": 50,
"ram charan": 50,
"allu arjun": 50,
"jr ntr": 50,
"mahesh babu": 50,
"chiranjeevi": 50,
"balakrishna": 50,

"nani": 20,
"vijay devarakonda": 20,
"nithiin": 20,
"varun tej": 20,
"nag chaitanya": 20,
"akhil": 20,

"samantha": 20,
"rashmika": 20,
"sreeleela": 20,
"keerthy suresh": 20,
"pooja hegde": 20,
"anushka": 20,

"siddu jonnalagadda": 20,
"adivi sesh": 20,
"vishwak sen": 20,
"kiran abbavaram": 20,

"rajamouli": 20,
"trivikram": 20,
"sukumar": 20,
"koratala siva": 20,


}

TECH = {
"ai": 20,
"artificial intelligence": 20,
"data centre": 25,
"datacenter": 25,
"startup": 20,
"funding": 20,
"investment": 20,


"google": 15,
"microsoft": 15,
"amazon": 15,
"meta": 15,
"tcs": 15,
"infosys": 15,
"wipro": 15,


}

UTILITY = {
"electricity": 20,
"power cut": 30,
"water supply": 30,
"traffic": 20,
"metro": 20,
"road closure": 25,
"fuel price": 25,
"gas cylinder": 25,
"ration": 25,
"pension": 25,
}

NON_LOCAL = {
    "delhi": -50,
    "uttar pradesh": -50,
    "rajasthan": -50,
    "bihar": -50,
    "punjab": -50,
    "kolkata": -50,
    "west bengal": -50
}

SOURCE_SCORE = {
"the hindu": 10,
"reuters": 10,
"bbc": 10,
"123telugu": 8,
"gulte": 8,
"telugu360": 8,
"greatandhra": 8,
"m9": 8,
}

import re

TRENDING_KEYWORDS = {
    "pawan kalyan": 500,
    "allu arjun": 500,
    "prabhas": 500,
    "mahesh babu": 450,
    "ram charan": 450,
    "jr ntr": 450,
    "virat kohli": 500,
    "rohit sharma": 450,
    "dhoni": 450,
    "ipl": 400,
    "monsoon": 350,
    "cyclone": 400,
    "heatwave": 300,
    "hyderabad": 200,
    "andhra pradesh": 150,
    "telangana": 150,
}

VIRAL_EVENT_KEYWORDS = {
    "dies": 600,
    "death": 600,
    "arrested": 500,
    "attack": 500,
    "explosion": 700,
    "accident": 500,
    "warning": 400,
    "alert": 400,
    "viral": 400,
    "controversy": 350,
    "record": 300,
    "breaks internet": 500,
    "shocking": 400,
    "exclusive": 300,
}

SOCIAL_MEDIA_WORDS = [
    "watch",
    "video",
    "viral",
    "fans",
    "reaction",
    "trolling",
    "responds",
    "clarifies",
    "slams",
    "lashes out",
]

CELEBRITY_SCORES = {
    "pawan kalyan": 300,
    "allu arjun": 300,
    "prabhas": 300,
    "mahesh babu": 250,
    "ram charan": 250,
    "jr ntr": 250,
    "samantha": 200,
}

SHORTS_KEYWORDS = [
    "viral",
    "record",
    "shocking",
    "warning",
    "alert",
    "watch",
    "video",
    "rain",
    "heatwave",
    "ram charan",
    "peddi",
    "cricket",
]

POLITICAL_NOISE = [
    "hitler",
    "north-south",
    "jagir",
    "row",
    "slams",
    "fumes",
    "lashes out",
]

CRICKET_KEYWORDS = [
    "cricket",
    "ipl",
    "virat",
    "kohli",
    "rohit",
    "dhoni",
    "sachin",
    "bumrah",
    "vaibhav suryavanshi"
]

CELEBRITY_KEYWORDS = [
    "ram charan",
    "pawan kalyan",
    "jr ntr",
    "allu arjun",
    "prabhas",
    "mahesh babu",
    "samantha"
]

WEATHER_KEYWORDS = [
    "rain",
    "monsoon",
    "heatwave",
    "imd",
    "cyclone",
    "weather alert"
]

JOBS_KEYWORDS = [
    "tspsc",
    "appsc",
    "recruitment",
    "job notification",
    "exam result"
]

BORING_KEYWORDS = [
    "meeting",
    "committee",
    "conference",
    "memorandum",
    "cultural exchange",
    "review meeting",
    "official visit",
    "budget discussion"
]


def contains_word(text, keyword):
    pattern = r"\b" + re.escape(keyword) + r"\b"
    return re.search(pattern, text) is not None


def add_scores(text, mapping):
    score = 0

    for keyword, points in mapping.items():
        if contains_word(text, keyword):
            score += points

    return score


def youtube_score(article):
    score = 0
    title = article.get("title", "").lower()

    if "ram charan" in title:
        score += 100
    if "pawan kalyan" in title:
        score += 100
    if "cricket" in title:
        score += 120
    if "rain" in title:
        score += 80
    if "hyderabad" in title:
        score += 50
    if "telangana" in title:
        score += 50

    return score


def trending_boost(title):
    return add_scores(title, TRENDING_KEYWORDS)


def viral_event_boost(title):
    return add_scores(title, VIRAL_EVENT_KEYWORDS)


def social_media_bonus(text):
    score = 0
    for word in SOCIAL_MEDIA_WORDS:
        if contains_word(text, word):
            score += 200
    return score


def shorts_score(title):
    title_lower = title.lower()
    score = 0

    for word in SHORTS_KEYWORDS:
        if word in title_lower:
            score += 50

    return score


def score_article(article):
    text = (
        article.get("title", "") +
        " " +
        article.get("description", "")
    ).lower()

    title = article.get("title", "").lower()
    description = article.get("description", "").lower()

    location_score = add_scores(text, LOCAL) + add_scores(text, NON_LOCAL)
    celebrity_score = add_scores(title, CELEBRITY_SCORES)
    viral_score = trending_boost(title) + viral_event_boost(title)
    social_score = social_media_bonus(title) + social_media_bonus(description)
    source = article.get("source", "").lower()

    score = \
        celebrity_score * 3 + \
        viral_score * 3 + \
        social_score + \
        location_score + \
        add_scores(source, SOURCE_SCORE) + \
        youtube_score(article) + \
        shorts_score(title)

    if any(contains_word(title, noise) for noise in POLITICAL_NOISE):
        score -= 200

    published = article.get("published_at")

    if published:
        try:
            dt = datetime.fromisoformat(
                published.replace("Z", "+00:00")
            )

            age_hours = (
                datetime.now(timezone.utc) - dt
            ).total_seconds() / 3600

            if age_hours < 1:
                score += 60
            elif age_hours < 3:
                score += 45
            elif age_hours < 6:
                score += 30
            elif age_hours < 12:
                score += 15
            elif age_hours > 48:
                score -= 40
            elif age_hours > 24:
                score -= 20
        except Exception:
            pass

    return score

