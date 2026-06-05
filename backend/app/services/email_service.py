import resend

from app.config import settings


class EmailService:
    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY
        self.from_email = settings.RESEND_FROM_EMAIL

    def send_email(self, to_email: str, subject: str, content: str):
        print("🚀 WYSYŁAM EMAILA PRZEZ RESEND...")
        print("TO:", to_email)

        response = resend.Emails.send({
            "from": self.from_email,
            "to": [to_email],
            "subject": subject,
            "text": content,
        })

        print("📬 RESEND RESPONSE:", response)

        return response


email_service = EmailService()