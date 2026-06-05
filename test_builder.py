from dotenv import load_dotenv
load_dotenv()

from digest.builder import build_html

SAMPLE = [
    {
        "title": "India GDP grows 7.2% in Q1",
        "summary": "The Indian economy expanded by 7.2 percent in the first quarter of 2026, driven by strong manufacturing output and robust domestic consumption. Economists had forecast 6.8 percent growth, making this a positive surprise for markets.",
        "category": "Business",
        "text_url": "https://example.com/1",
        "video_url": "https://youtube.com/watch?v=abc",
        "source": "Reuters"
    },
    {
        "title": "Apple launches M5 MacBook Pro",
        "summary": "Apple unveiled its new MacBook Pro lineup powered by the M5 chip, delivering 40 percent faster CPU performance and a 30 percent improvement in battery life compared to the previous generation model released last year.",
        "category": "Technology",
        "text_url": "https://example.com/2",
        "video_url": None,
        "source": "TechCrunch"
    },
]

html = build_html(SAMPLE)

with open("preview.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"HTML generated — {len(html)} chars")
print("Open preview.html in your browser to check layout")