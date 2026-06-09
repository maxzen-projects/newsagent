import json, os, yaml
from openai import OpenAI
from .prompts import SYSTEM_PROMPT

def enrich_sync(raw_articles: list) -> list:
    # If no API key present or user explicitly requests simulation, return a simple
    # pass-through enriched structure for local testing to avoid external calls.
    if not os.getenv("OPENAI_API_KEY") or os.getenv("SIMULATE_ENRICH") == "1":
        enriched = []
        for a in raw_articles:
            summary = a.get("description") or a.get("title", "")
            summary = (summary[:200] + "...") if len(summary) > 200 else summary
            enriched.append({
                "title": a.get("title"),
                "url": a.get("url") or a.get("text_url"),
                "summary": summary,
                "category": a.get("category", None),
            })
        return enriched

    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)["agent"]

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Avoid using str.format() because SYSTEM_PROMPT contains JSON-like braces.
    # Use simple replaces for the expected placeholders to prevent KeyError.
    system = SYSTEM_PROMPT.replace("{n}", str(cfg.get("top_n", "")))
    system = system.replace("{categories}", ", ".join(cfg.get("categories", [])))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Articles JSON:\n{json.dumps(raw_articles)}"}
        ],
        temperature=0.2
    )

    raw_text = response.choices[0].message.content.strip()

    if "```" in raw_text:
        parts = raw_text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:]
            part = part.strip()
            if part.startswith("[") or part.startswith("{"):
                try:
                    return json.loads(part)
                except json.JSONDecodeError:
                    continue

    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, dict):
            for v in parsed.values():
                if isinstance(v, list):
                    return v
        if isinstance(parsed, list):
            return parsed
        return []
    except json.JSONDecodeError as e:
        print(f"[enricher] JSON parse error: {e}")
        print(f"[enricher] Raw response:\n{raw_text[:500]}")
        return []

async def enrich(raw_articles: list) -> list:
    return enrich_sync(raw_articles)