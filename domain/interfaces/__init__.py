"""Domain interfaces: Contratos para inyección de dependencias.

Define las abstracciones para Repository, EmailService, DataCleaner
y otros servicios que la aplicación necesita inyectar.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable, Dict, List, Optional


class IDataRepository(ABC):
    """Contrato para operaciones CRUD de entidades de dominio."""

    @abstractmethod
    def save(self, entity: Any) -> None:
        """Guarda una entidad (insert o update).

        Args:
            entity: Entidad a guardar

        Raises:
            RepositorioException: Si hay error en persistencia
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[Any]:
        """Recupera una entidad por su ID.

        Args:
            entity_id: ID de la entidad

        Returns:
            Entidad si existe, None en caso contrario
        """
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> Iterable[Any]:
        """Lista todas las entidades.

        Returns:
            Iterable de entidades
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: Any) -> None:
        """Actualiza una entidad.

        Args:
            entity: Entidad con cambios

        Raises:
            RepositorioException: Si hay error
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity_id: str) -> None:
        """Elimina una entidad por su ID.

        Args:
            entity_id: ID a eliminar

        Raises:
            RepositorioException: Si hay error
        """
        raise NotImplementedError


class IEmailService(ABC):
    """Contrato para envío de notificaciones por correo."""

    @abstractmethod
    def send(self, subject: str, body: str, to: str) -> bool:
        """Envía un correo electrónico.

        Args:
            subject: Asunto del correo
            body: Cuerpo del mensaje
            to: Destinatario(s)

        Returns:
            True si se envió exitosamente

        Raises:
            NotificacionException: Si hay error en envío
        """
        raise NotImplementedError

    @abstractmethod
    def validate_email(self, email: str) -> bool:
        """Valida formato de correo electrónico.

        Args:
            email: Email a validar

        Returns:
            True si es válido
        """
        raise NotImplementedError


class IDataCleaner(ABC):
    """Contrato para Strategy Pattern de limpieza de datos."""

    @abstractmethod
    def clean(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ejecuta la estrategia de limpieza.

        Args:
            rows: Lista de filas a limpiar

        Returns:
            Lista de filas limpias
        """
        raise NotImplementedError


class IFeatureAnalyzer(ABC):
    """Contrato para análisis de características."""

    @abstractmethod
    def analyze(self, dataset: Any) -> Dict[str, Any]:
        """Analiza un dataset.

        Args:
            dataset: Dataset a analizar

        Returns:
            Diccionario con análisis de características
        """
        raise NotImplementedError


class INotificationObserver(ABC):
    """Contrato para Observer Pattern de notificaciones."""

    @abstractmethod
    def update(self, event: str, data: Dict[str, Any]) -> None:
        """Recibe notificación de evento.

        Args:
            event: Tipo de evento (ej: "dataset_cleaned", "gateway_rejected")
            data: Datos del evento
        """
        raise NotImplementedError
