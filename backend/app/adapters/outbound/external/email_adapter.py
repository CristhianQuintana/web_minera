import smtplib
from email.message import EmailMessage

from app.infrastructure.configuration.settings import Settings
from app.infrastructure.logging.logger import configure_logging

logger = configure_logging()


class SmtpEmailAdapter:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def send(self, to: str, subject: str, body: str) -> None:
        if not self._settings.smtp_host:
            raise RuntimeError("El servicio de correo no está configurado; la invitación no fue enviada.")
        message = EmailMessage()
        message["From"] = self._settings.smtp_from
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)
        with smtplib.SMTP(self._settings.smtp_host, self._settings.smtp_port, timeout=20) as smtp:
            smtp.starttls()
            if self._settings.smtp_user:
                smtp.login(self._settings.smtp_user, self._settings.smtp_password)
            refused = smtp.send_message(message)
            if refused:
                raise smtplib.SMTPRecipientsRefused(refused)
        logger.info("Correo de invitación enviado.")
