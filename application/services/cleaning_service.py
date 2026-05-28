"""Application Service: CleaningService.

Orquesta la ejecución de múltiples cleaners usando Strategy Pattern.
Genera CleaningReport con estadísticas detalladas.
"""
from typing import List, Dict, Any
from uuid import uuid4

from domain.entities import Dataset, CleaningReport
from domain.interfaces import IDataCleaner
from domain.enums import DatasetStatus
from domain.exceptions import TransformacionFallidaException


class CleaningService:
    """Orquestador de limpieza de datos usando Strategy Pattern.

    Ejecuta una secuencia de cleaners (NullCleaner, FormatCleaner, DuplicateCleaner)
    en orden y genera un reporte detallado.

    Attributes:
        cleaners: Lista de estrategias IDataCleaner a ejecutar
    """

    def __init__(self, cleaners: List[IDataCleaner] | None = None) -> None:
        """Inicializa el servicio.

        Args:
            cleaners: Lista de cleaners a ejecutar en orden
        """
        self.cleaners = cleaners or []

    def register_cleaner(self, cleaner: IDataCleaner) -> None:
        """Registra una nueva estrategia de limpieza.

        Args:
            cleaner: Implementación de IDataCleaner
        """
        if not isinstance(cleaner, IDataCleaner) and not hasattr(cleaner, "clean"):
            raise TypeError("Cleaner must implement IDataCleaner interface")
        self.cleaners.append(cleaner)

    def run(self, dataset: Dataset) -> tuple[Dataset, CleaningReport]:
        """Ejecuta la cadena de limpieza sobre el dataset.

        Flujo:
        1. Normaliza ubicaciones
        2. Ejecuta cada cleaner en orden
        3. Valida que haya filas después de limpieza
        4. Genera CleaningReport
        5. Actualiza estado del dataset

        Args:
            dataset: Dataset a limpiar

        Returns:
            Tupla (dataset_limpiado, cleaning_report)

        Raises:
            TransformacionFallidaException: Si limpieza falla (Gateway 3)
        """
        try:
            # Normaliza ubicaciones (RB-001)
            dataset.normalizar_ubicacion()

            # Crea reporte
            report = CleaningReport(
                id=str(uuid4())[:8],
                dataset_id=dataset.id,
                registros_procesados=len(dataset.rows_preview),
            )

            # Ejecuta cada cleaner
            rows = dataset.rows_preview
            for i, cleaner in enumerate(self.cleaners):
                rows_antes = len(rows)
                rows = cleaner.clean(rows)
                rows_despues = len(rows)
                eliminadas = rows_antes - rows_despues

                # Registra paso
                cleaner_name = type(cleaner).__name__
                report.add_step(
                    name=cleaner_name.lower(),
                    affected_rows=eliminadas,
                    details={"rows_before": rows_antes, "rows_after": rows_despues},
                )

                # Actualiza contadores en el reporte
                if "NullCleaner" in cleaner_name:
                    report.nulos_removidos += eliminadas
                elif "DuplicateCleaner" in cleaner_name:
                    report.duplicados_removidos += eliminadas

            # Valida que haya filas después de limpieza
            if len(rows) == 0:
                raise TransformacionFallidaException(
                    "All rows were removed during cleaning",
                    context={"initial_rows": report.registros_procesados},
                    gateway_bpmn=3,
                )

            # Actualiza dataset
            dataset.rows_preview = rows
            dataset.total_rows = len(rows)
            dataset.status = DatasetStatus.CLEANING.value

            return dataset, report

        except TransformacionFallidaException:
            raise
        except Exception as e:
            raise TransformacionFallidaException(
                f"Cleaning failed: {str(e)}",
                context={"error": str(e), "dataset_id": dataset.id},
                gateway_bpmn=3,
            )
