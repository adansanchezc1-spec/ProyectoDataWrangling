"""Infrastructure: Email Decorators - Decorator Pattern.

Implementa ValidacionEmailDecorator y NotificacionInsercionDecorator
para agregar funcionalidad al EmailService sin modificar su código.
"""
import re
from typing import Optional

from domain.interfaces import IEmailService
from domain.exceptions import NotificacionException


class EmailDecorator(IEmailService):
    """Clase base para decoradores de EmailService.

    Implementa el patrón Decorator para agregar comportamiento
    sin modificar el servicio original.
    """

    def __init__(self, wrapped_service: IEmailService) -> None:
        """Inicializa el decorador.

        Args:
            wrapped_service: Servicio a decorar
        """
        self._wrapped = wrapped_service

    def send(self, subject: str, body: str, to: str) -> bool:
        """Delega al servicio envuelto.

        Args:
            subject: Asunto
            body: Cuerpo
            to: Destinatario

        Returns:
            True si envío exitoso
        """
        return self._wrapped.send(subject, body, to)

    def validate_email(self, email: str) -> bool:
        """Delega validación al servicio envuelto."""
        return self._wrapped.validate_email(email)


class ValidacionEmailDecorator(EmailDecorator):
    """Decorador que valida correos antes de enviar (RB-006).

    Verifica que el destinatario tenga un formato válido de email.
    """

    def send(self, subject: str, body: str, to: str) -> bool:
        """Valida correos antes de enviar.

        Args:
            subject: Asunto
            body: Cuerpo
            to: Destinatario(s)

        Returns:
            True si envío exitoso

        Raises:
            NotificacionException: Si email inválido
        """
        # Valida cada destinatario (pueden ser múltiples separados por coma)
        emails = [e.strip() for e in to.split(",")]

        for email in emails:
            if not self._is_valid_email(email):
                raise NotificacionException(
                    f"Invalid email format: {email}",
                    context={"email": email},
                )

        # Si todos son válidos, delega al siguiente
        return self._wrapped.send(subject, body, to)

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Valida formato de email con regex.

        Args:
            email: Email a validar

        Returns:
            True si formato válido
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))


class NotificacionInsercionDecorator(EmailDecorator):
    """Decorador que agrega contexto de inserción a notificaciones (RB-006).

    Enriquece el cuerpo del mensaje con información sobre la inserción de datos
    en el MDM y añade firma de procesamiento.
    """

    def send(self, subject: str, body: str, to: str) -> bool:
        """Decora el mensaje con información de inserción.

        Args:
            subject: Asunto
            body: Cuerpo original
            to: Destinatario

        Returns:
            True si envío exitoso
        """
        # Enriquece el asunto
        decorated_subject = f"[Data Wrangling - MDM Insertion] {subject}"

        # Enriquece el cuerpo con contexto
        decorated_body = self._enrich_body(body)

        # Delega al siguiente en la cadena
        return self._wrapped.send(decorated_subject, decorated_body, to)

    @staticmethod
    def _enrich_body(original_body: str) -> str:
        """Enriquece el cuerpo del mensaje.

        Args:
            original_body: Cuerpo original

        Returns:
            Cuerpo enriquecido con contexto
        """
        from datetime import datetime

        timestamp = datetime.utcnow().isoformat()
        signature = (
            f"\n\n---\n"
            f"Sistema de Data Wrangling - Bogotá Real Estate\n"
            f"Inserción procesada: {timestamp}\n"
            f"Mensaje automático - No responder"
        )

        return f"{original_body}{signature}"
