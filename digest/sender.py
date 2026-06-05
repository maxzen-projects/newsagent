import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import datetime

def send_digest(html_content: str) -> str:
    recipients = os.getenv("TO_EMAILS", "").split(",")
    message = Mail(
        from_email=(os.getenv("FROM_EMAIL"), os.getenv("FROM_NAME")),
        to_emails=recipients,
        subject=f"News Digest — {datetime.date.today()}",
        html_content=html_content
    )
    sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    response = sg.send(message)
    return str(response.status_code)