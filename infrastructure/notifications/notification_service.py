"""Infrastructure: NotificationService - Observer Pattern Implementation.

Notificador que mantiene una lista de observadores y les notifica
eventos del pipeline ETL.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from domain.interfaces import INotificationObserver
from domain.exceptions import NotificacionException


class NotificationService:
    """Servicio de notificación con patrón Observer.

    Coordina eventos del pipeline (gateway rejections, dataset loaded, etc)
    y notifica a todos los observadores registrados.
    """

    def __init__(self) -> None:
        """Inicializa el servicio sin observadores."""
        self._observers: List[INotificationObserver] = []
        self._event_history: List[Dict[str, Any]] = []

    def attach_observer(self, observer: INotificationObserver) -> None:
        """Registra un observador.

        Args:
            observer: Implementación de INotificationObserver

        Raises:
            NotificacionException: Si observador inválido
        """
        if not hasattr(observer, "update"):
            raise NotificacionException(
                "Observer must implement INotificationObserver",
                context={"observer": type(observer).__name__},
            )
        self._observers.append(observer)

    def detach_observer(self, observer: INotificationObserver) -> None:
        """Desregistra un observador.

        Args:
            observer: Observador a remover
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_all(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Notifica un evento a todos los observadores.

        Args:
            event: Tipo de evento (ej: "gateway_rejected", "dataset_loaded")
            data: Datos asociados al evento

        Raises:
            NotificacionException: Si hay error en notificación
        """
        event_data = data or {}

        # Registra en historial
        self._record_event(event, event_data)

        # Notifica cada observador
        for observer in self._observers:
            try:
                observer.update(event, event_data)
            except Exception as e:
                raise NotificacionException(
                    f"Error notifying observer {type(observer).__name__}",
                    context={"observer": type(observer).__name__, "error": str(e)},
                )

    def _record_event(self, event: str, data: Dict[str, Any]) -> None:
        """Registra el evento en historial.

        Args:
            event: Tipo de evento
            data: Datos del evento
        """
        record = {
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        self._event_history.append(record)

    def get_event_history(self) -> List[Dict[str, Any]]:
        """Obtiene el historial de eventos.

        Returns:
            Lista de eventos registrados
        """
        return list(self._event_history)

    def clear_event_history(self) -> None:
        """Limpia el historial de eventos."""
        self._event_history.clear()
