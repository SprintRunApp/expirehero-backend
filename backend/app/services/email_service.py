import resend

from app.config import settings


class EmailService:
    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY
        self.from_email = settings.RESEND_FROM_EMAIL

    def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        cc_email: str | None = None,
    ):
        print("🚀 WYSYŁAM EMAILA PRZEZ RESEND...")
        print("TO:", to_email)

        payload = {
            "from": self.from_email,
            "to": [to_email],
            "subject": subject,
            "text": content,
        }

        if cc_email and cc_email != to_email:
            payload["cc"] = [cc_email]
            print("CC:", cc_email)

        response = resend.Emails.send(payload)

        print("📬 RESEND RESPONSE:", response)

        return response


email_service = EmailService()