"""Presentation Layer: DatasetController - MVC Controller.

Orquesta la comunicación entre la Vista (Tkinter) y el Modelo (PipelineFacade).
Implementa los casos de uso del sistema.
"""
from typing import Dict, Any, Callable, Optional
from threading import Thread

from application.services.pipeline_facade import PipelineFacade
from domain.exceptions import DominioException


class DatasetController:
    """Controlador del modelo MVC.

    Responsabilidades:
    - Manejar eventos desde las vistas
    - Invocar el pipeline
    - Actualizar el estado de la aplicación
    - Notificar a las vistas de cambios

    Attributes:
        pipeline_facade: Orquestador del pipeline ETL
        observers: Callbacks de vista para actualizaciones
    """

    def __init__(self, pipeline_facade: PipelineFacade) -> None:
        """Inicializa el controlador.

        Args:
            pipeline_facade: Instancia del orquestador principal
        """
        self.pipeline_facade = pipeline_facade
        self._observers: Dict[str, list[Callable]] = {
            "pipeline_started": [],
            "pipeline_progress": [],
            "pipeline_completed": [],
            "pipeline_error": [],
        }

    def subscribe(self, event: str, callback: Callable) -> None:
        """Suscribe una vista a eventos del controlador.

        Args:
            event: Tipo de evento ("pipeline_started", "pipeline_completed", etc)
            callback: Función a invocar cuando el evento ocurra
        """
        if event not in self._observers:
            self._observers[event] = []
        self._observers[event].append(callback)

    def _notify_observers(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Notifica a todos los observadores de un evento.

        Args:
            event: Tipo de evento
            data: Datos asociados
        """
        for callback in self._observers.get(event, []):
            try:
                callback(data or {})
            except Exception as e:
                print(f"Error in observer callback: {e}")

    def upload_and_process_dataset(self, file_path: str) -> None:
        """Carga y procesa un dataset (caso de uso principal).

        Ejecuta el pipeline en un thread separado para no bloquear la UI.

        Args:
            file_path: Ruta al archivo a procesar
        """
        # Notifica inicio
        self._notify_observers("pipeline_started", {"file_path": file_path})

        # Ejecuta en thread separado
        thread = Thread(
            target=self._process_dataset_background,
            args=(file_path,),
            daemon=False,
        )
        thread.start()

    def _process_dataset_background(self, file_path: str) -> None:
        """Procesa el dataset en background (thread).

        Args:
            file_path: Ruta al archivo
        """
        try:
            # Notifica progreso
            self._notify_observers("pipeline_progress", {"message": "Iniciando pipeline..."})

            # Ejecuta pipeline
            result = self.pipeline_facade.run_pipeline(file_path)

            # Notifica resultado
            self._notify_observers("pipeline_completed", result)

        except DominioException as e:
            self._notify_observers(
                "pipeline_error",
                {
                    "error": str(e),
                    "reason": e.reason,
                    "context": e.context,
                },
            )
        except Exception as e:
            self._notify_observers(
                "pipeline_error",
                {
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )

    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Recupera un dataset procesado desde el MDM.

        Args:
            dataset_id: ID del dataset

        Returns:
            Dict con datos del dataset, o None si no existe
        """
        return self.pipeline_facade.mdm_service.get_dataset_by_id(dataset_id)

    def list_all_datasets(self) -> list[Dict[str, Any]]:
        """Lista todos los datasets procesados en el MDM.

        Returns:
            Lista de datasets
        """
        return self.pipeline_facade.mdm_service.list_all_datasets()

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del pipeline.

        Returns:
            Dict con información de estado
        """
        event_history = self.pipeline_facade.notification_service.get_event_history()
        return {
            "total_events": len(event_history),
            "events": event_history[-10:],  # Últimos 10 eventos
        }
