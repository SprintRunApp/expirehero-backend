import sendgrid
from sendgrid.helpers.mail import Mail

from app.config import settings


class EmailService:
    def __init__(self):
        self.client = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        self.from_email = settings.SENDGRID_FROM_EMAIL

    def send_email(self, to_email: str, subject: str, content: str):
        print("🚀 WYSYŁAM EMAILA...")
        print("TO:", to_email)

        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=content
        )

        response = self.client.send(message)

        print("📬 STATUS:", response.status_code)

        return response.status_code


email_service = EmailService()