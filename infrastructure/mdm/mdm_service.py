"""Infrastructure Service: MDMService - Master Data Management.

Carga el dataset limpio en el repositorio MDM (Master Data Management)
como la fuente de verdad única del negocio.
"""
from typing import Dict, Any
from uuid import uuid4

from domain.entities import Dataset
from domain.interfaces import IDataRepository
from domain.enums import DatasetStatus
from domain.exceptions import RepositorioException


class MDMService:
    """Servicio de Master Data Management para persistencia final.

    Responsabilidades:
    - Persistir dataset limpio en el MDM
    - Marcar como versión maestra/oficial
    - Mantener historial de versiones
    """

    def __init__(self, repository: IDataRepository) -> None:
        """Inicializa el servicio MDM.

        Args:
            repository: Repositorio donde persiste el MDM
        """
        self.repository = repository

    def load_to_mdm(self, dataset: Dataset) -> Dict[str, Any]:
        """Carga un dataset limpiolimited y validado en el MDM.

        Flujo:
        1. Enriquece el dataset con metadatos
        2. Marca estado como MDM_LOADED
        3. Persiste en repositorio
        4. Retorna resumen

        Args:
            dataset: Dataset limpiolimited a persistir

        Returns:
            Dict con resumen de carga al MDM

        Raises:
            RepositorioException: Si falla persistencia
        """
        try:
            # Actualiza estado
            dataset.status = DatasetStatus.MDM_LOADED.value

            # Persiste en repositorio
            self.repository.save(dataset)

            # Genera resumen
            summary = {
                "dataset_id": dataset.id,
                "mdm_status": "loaded",
                "total_records": dataset.total_rows,
                "source_file": dataset.source_path,
                "format": dataset.format,
                "status": dataset.status,
                "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            }

            return summary

        except RepositorioException:
            raise
        except Exception as e:
            raise RepositorioException(
                f"Failed to load dataset to MDM: {str(e)}",
                context={"dataset_id": dataset.id, "error": str(e)},
            )

    def get_dataset_by_id(self, dataset_id: str) -> Dict[str, Any] | None:
        """Recupera un dataset del MDM por su ID.

        Args:
            dataset_id: ID del dataset

        Returns:
            Dict con datos del dataset, o None si no existe
        """
        return self.repository.get_by_id(dataset_id)

    def list_all_datasets(self) -> list[Dict[str, Any]]:
        """Lista todos los datasets en el MDM.

        Returns:
            Lista de datasets
        """
        return list(self.repository.list_all())
