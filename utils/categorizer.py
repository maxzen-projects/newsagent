import re

CATEGORY_KEYWORDS = {
    "weather": {
        "monsoon": 5,
        "rainfall": 4,
        "rain": 4,
        "cyclone": 5,
        "imd": 3,
        "weather": 2,
        "warning": 2,
        "alert": 2,
        "heatwave": 4,
        "storm": 3,
    },
    "politics": {
        "pawan kalyan": 5,
        "chandrababu": 4,
        "nara lokesh": 4,
        "revanth reddy": 4,
        "jagan": 4,
        "tdp": 3,
        "ysrcp": 3,
        "janasena": 3,
        "minister": 2,
        "government": 2,
        "assembly": 1,
        "cabinet": 1,
        "committee": 1,
    },
    "cricket": {
        "vaibhav": 6,
        "suryavanshi": 6,
        "sooryavanshi": 6,
        "virat": 5,
        "kohli": 5,
        "sachin": 4,
        "dhoni": 4,
        "rohit": 4,
        "bcci": 4,
        "ipl": 4,
        "team india": 4,
        "cricket": 4,
        "odi": 4,
        "t20": 4,
        "wicket": 4,
        "bowler": 4,
        "batsman": 4,
        "fifer": 4,
        "maiden": 3,
    },
    "tollywood": {
        "prabhas": 5,
        "ram charan": 5,
        "allu arjun": 5,
        "jr ntr": 5,
        "mahesh babu": 5,
        "tollywood": 4,
        "telugu film": 4,
        "telugu movie": 4,
        "box office": 4,
        "collection": 4,
        "trailer": 3,
        "teaser": 3,
        "release date": 3,
        "peddi": 4,
        "ott": 3,
    },
    "jobs": {
        "exam": 4,
        "results": 4,
        "recruitment": 4,
        "notification": 4,
        "hall ticket": 3,
        "tspsc": 3,
        "appsc": 3,
        "university": 3,
    },
    "business": {
        "investment": 3,
        "industry": 3,
        "economy": 3,
        "startup": 3,
        "business": 2,
        "trade": 2,
        "manufacturing": 2,
    },
    "general": {
        "medical": 2,
        "hospital": 2,
        "tourism": 2,
    },
}

SUBJECT_KEYWORDS = {
    "suryakumar": ["suryakumar", "sky", "suryakumar yadav"],
    "vaibhav": ["vaibhav", "suryavanshi", "sooryavanshi"],
    "ram_charan": ["ram charan"],
    "prabhas": ["prabhas"],
    "monsoon": ["monsoon", "rain", "rainfall", "heatwave", "cyclone"],
}


def text_contains(text, keyword):
    pattern = r"\b" + re.escape(keyword) + r"\b"
    return re.search(pattern, text) is not None


def detect_category_and_keywords(article):
    title = article.get("title", "").lower()
    description = article.get("description", "").lower()

    scores = {key: 0 for key in CATEGORY_KEYWORDS}
    title_scores = {key: 0 for key in CATEGORY_KEYWORDS}
    matched_keywords = {key: [] for key in CATEGORY_KEYWORDS}

    for category, mapping in CATEGORY_KEYWORDS.items():
        for keyword, points in mapping.items():
            if text_contains(title, keyword):
                scores[category] += points
                title_scores[category] += points
                matched_keywords[category].append(f"title:{keyword}")
            elif text_contains(description, keyword):
                scores[category] += max(1, points // 2)
                matched_keywords[category].append(f"desc:{keyword}")

    # Choose the highest-confidence category; low scores default to general.
    best = max(scores, key=scores.get)
    max_score = scores[best]
    best_title_score = title_scores[best]

    if max_score < 5:
        best = "general"
    elif best == "weather" and scores["cricket"] >= scores["weather"] + 3:
        best = "cricket"
    elif best == "cricket" and scores["weather"] >= scores["cricket"] + 3:
        best = "weather"

    flat_matches = [f"{cat}:{kw}" for cat, kws in matched_keywords.items() for kw in kws]
    return best, flat_matches


def detect_category(article):
    category, _ = detect_category_and_keywords(article)
    return category


def detect_subject(article):
    text = (
        article.get("title", "") +
        " " +
        article.get("description", "")
    ).lower()

    for subject, keywords in SUBJECT_KEYWORDS.items():
        if any(text_contains(text, keyword) for keyword in keywords):
            return subject

    return None
