"""Infrastructure: EmailService - Base implementation.

Servicio base para envío de correos SMTP.
Diseñado para ser decorado con ValidacionEmailDecorator y NotificacionInsercionDecorator.
"""
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
        """Inicializa el servicio de correo.

        Args:
            host: Servidor SMTP
            port: Puerto SMTP
            username: Usuario para autenticación
            password: Contraseña para autenticación
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def send(self, subject: str, body: str, to: str) -> bool:
        """Envía un correo por SMTP.

        Args:
            subject: Asunto del correo
            body: Cuerpo del mensaje
            to: Destinatario(s), separados por comas

        Returns:
            True si se envió exitosamente

        Raises:
            NotificacionException: Si hay error en envío
        """
        try:
            # Crea mensaje MIME
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = self.username or "noreply@data-wrangling.local"
            msg["To"] = to

            msg.attach(MIMEText(body, "plain"))

            # Conecta y envía
            with smtplib.SMTP(self.host, self.port, timeout=10) as server:
                if self.username and self.password:
                    server.starttls()
                    server.login(self.username, self.password)

                server.sendmail(msg["From"], to.split(","), msg.as_string())

            return True

        except smtplib.SMTPException as e:
            raise NotificacionException(
                f"SMTP error sending email to {to}",
                context={"error": str(e), "to": to},
            )
        except Exception as e:
            raise NotificacionException(
                f"Error sending email to {to}",
                context={"error": str(e), "to": to},
            )

    def validate_email(self, email: str) -> bool:
        """Valida formato básico de correo electrónico.

        Args:
            email: Email a validar

        Returns:
            True si formato es válido
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
