def viral_score(article):

    text = (
        article.get("title", "") +
        " " +
        article.get("description", "")
    ).lower()

    score = 0

    viral_keywords = {
        "box office": 40,
        "controversy": 40,
        "viral": 35,
        "pawan kalyan": 35,
        "ram charan": 30,
        "prabhas": 30,
        "jagan": 35,
        "revanth": 30,
        "heatwave": 30,
        "monsoon": 30,
        "cyclone": 40,
        "results": 30,
        "recruitment": 35,
    }

    for keyword, points in viral_keywords.items():
        if keyword in text:
            score += points

    return score