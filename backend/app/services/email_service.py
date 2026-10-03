import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from app.core.config import settings


@dataclass(frozen=True)
class EmailDeliveryResult:
    status: str
    detail: str = ""


def send_resolution_email(recipient: str, subject: str, reply: str) -> EmailDeliveryResult:
    """Send an agent's final reply through the configured SMTP provider."""
    if not settings.SMTP_ENABLED:
        return EmailDeliveryResult("not_configured")

    required_settings = [settings.SMTP_HOST, settings.SMTP_FROM_EMAIL]
    if not all(required_settings):
        return EmailDeliveryResult("failed", "SMTP host or sender address is missing")

    message = EmailMessage()
    message["Subject"] = f"Re: {subject}"
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = recipient
    message.set_content(reply)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            if settings.SMTP_USERNAME:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as error:
        print(f"Could not send resolution email: {error}")
        detail = str(error).replace("\n", " ").strip()[:240]
        return EmailDeliveryResult("failed", detail or "SMTP delivery failed")

    return EmailDeliveryResult("sent")
