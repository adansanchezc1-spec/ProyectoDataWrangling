"""Infrastructure: EmailService and FileLoggerEmailService.

Servicio base para envío de correos SMTP.
Diseñado para ser decorado con ValidacionEmailDecorator y NotificacionInsercionDecorator.

FileLoggerEmailService: escribe los correos en archivos locales como fallback
cuando no hay SMTP configurado (útil para desarrollo/desktop).
"""
import datetime
import os
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional

from domain.interfaces import IEmailService
from domain.exceptions import NotificacionException


class EmailService(IEmailService):
    """Servicio base para envío de correos por SMTP.

    Attributes:
        host: Servidor SMTP
        port: Puerto SMTP
        username: Usuario SMTP (opcional)
        password: Contraseña SMTP (opcional)
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 25,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def send(self, subject: str, body: str, to: str) -> bool:
        try:
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = self.username or "danysancubi@gmail.com"
            msg["To"] = to
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.host, self.port, timeout=10) as server:
                if self.username and self.password:
                    server.starttls()
                    server.login(self.username, self.password)
                server.sendmail(msg["From"], to.split(","), msg.as_string())
            return True

        except smtplib.SMTPException as e:
            raise NotificacionException(
                f"SMTP error sending email to {to}: {e}",
                context={"error": str(e), "to": to},
            )
        except Exception as e:
            raise NotificacionException(
                f"Error sending email to {to}: {e}",
                context={"error": str(e), "to": to},
            )

    def validate_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))


class FileLoggerEmailService(IEmailService):
    """Escribe los correos en disco en vez de enviarlos por SMTP.

    Útil para desarrollo/desktop donde no hay servidor SMTP disponible.
    Los correos se guardan en data/EMAILS/{timestamp}_{to}.txt
    """

    def __init__(self, email_dir: str = "data/EMAILS") -> None:
        self.email_dir = Path(email_dir)
        self.email_dir.mkdir(parents=True, exist_ok=True)

    def send(self, subject: str, body: str, to: str) -> bool:
        timestamp = datetime.datetime.now().isoformat(timespec="seconds").replace(":", "-")
        safe_to = re.sub(r"[^a-zA-Z0-9@._-]", "_", to)
        filename = f"{timestamp}_{safe_to}.txt"
        filepath = self.email_dir / filename

        content = (
            f"To: {to}\n"
            f"Subject: {subject}\n"
            f"Date: {timestamp}\n"
            f"{'='*60}\n"
            f"{body}\n"
        )
        filepath.write_text(content, encoding="utf-8")
        return True

    def validate_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
