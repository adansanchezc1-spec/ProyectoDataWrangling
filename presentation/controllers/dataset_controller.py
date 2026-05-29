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

    def upload_and_process_dataset(
        self,
        file_path: str | list[str],
        user_email: str = "",
        year: int = 0,
        price_factor: float = 1.0,
    ) -> None:
        """Carga y procesa un dataset (caso de uso principal).

        Ejecuta el pipeline en un thread separado para no bloquear la UI.
        Las credenciales SMTP se cargan desde variables de entorno (.env).

        Args:
            file_path: Ruta o rutas al archivo a procesar
            user_email: Email del usuario para notificación
            year: Año del dataset
            price_factor: Factor multiplicador del precio unitario
        """
        file_paths = [file_path] if isinstance(file_path, str) else list(file_path)

        # Notifica inicio
        self._notify_observers("pipeline_started", {"file_paths": file_paths})

        # Ejecuta en thread separado
        thread = Thread(
            target=self._process_dataset_background,
            args=(file_paths, user_email, year, price_factor),
            daemon=False,
        )
        thread.start()

    def _process_dataset_background(
        self,
        file_paths: list[str],
        user_email: str = "",
        year: int = 0,
        price_factor: float = 1.0,
    ) -> None:
        """Procesa el dataset en background (thread).

        Args:
            file_paths: Rutas a los archivos
            user_email: Email del usuario para notificación
            year: Año del dataset
            price_factor: Factor multiplicador del precio unitario
        """
        try:
            results: list[Dict[str, Any]] = []

            for index, file_path in enumerate(file_paths, start=1):
                self._notify_observers(
                    "pipeline_progress",
                    {
                        "message": (
                            f"Iniciando pipeline {index}/{len(file_paths)}: "
                            f"{file_path}"
                        )
                    },
                )
                result = self.pipeline_facade.run_pipeline(
                    file_path,
                    user_email=user_email,
                    year=year,
                    price_factor=price_factor,
                )
                results.append(result)

            # Notifica resultado
            if len(results) == 1:
                self._notify_observers("pipeline_completed", results[0])
            else:
                self._notify_observers(
                    "pipeline_completed",
                    {
                        "status": "batch_completed",
                        "total": len(results),
                        "success_count": sum(
                            1 for item in results if item.get("status") == "success"
                        ),
                        "rejected_count": sum(
                            1 for item in results if item.get("status") == "rejected"
                        ),
                        "error_count": sum(
                            1 for item in results if item.get("status") == "error"
                        ),
                        "results": results,
                    },
                )

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
