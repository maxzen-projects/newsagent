from dotenv import load_dotenv
load_dotenv()

from digest.builder import build_html
from digest.sender import send_digest

SAMPLE = [
    {
        "title": "Test story — pipeline working",
        "summary": "This is a test email sent from the Agentic News Digest pipeline to verify SendGrid delivery and HTML rendering are both configured correctly end to end.",
        "category": "Technology",
        "text_url": "https://example.com",
        "video_url": None,
        "source": "Test"
    }
]

html = build_html(SAMPLE)
status = send_digest(html)
print(f"SendGrid status: {status}")
print("202 = success, email on its way")