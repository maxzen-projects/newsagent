import json
import os


def save_articles(path, articles):
    """
    Save articles to any path and automatically
    create missing folders.
    """

    folder = os.path.dirname(path)

    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            articles,
            f,
            ensure_ascii=False,
            indent=2,
            default=str
        )

    print(f"Saved {len(articles)} articles -> {path}")