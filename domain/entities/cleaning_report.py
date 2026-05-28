"""Domain entity: CleaningReport - Rich Domain Model.

Responsabilidades:
- Registrar estadísticas de limpieza durante el pipeline
- Generar resumen detallado de operaciones realizadas
- Mantener trazabilidad de cada paso de limpieza
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class CleaningReport:
    """Reporte de limpieza asociado a un dataset.

    Attributes:
        id: Identificador único del reporte
        dataset_id: ID del dataset procesado
        registros_procesados: Total de registros iniciales
        registros_eliminados: Total de registros eliminados
        nulos_removidos: Cantidad de nulos removidos
        duplicados_removidos: Cantidad de duplicados eliminados
        steps: Lista de pasos de limpieza ejecutados
        created_at: Timestamp de creación
    """

    id: str
    dataset_id: str
    registros_procesados: int = 0
    registros_eliminados: int = 0
    nulos_removidos: int = 0
    duplicados_removidos: int = 0
    steps: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_step(self, name: str, affected_rows: int, details: Dict[str, Any]) -> None:
        """Registra un paso de limpieza.

        Args:
            name: Nombre del paso (ej: "null_removal", "duplicate_removal")
            affected_rows: Cantidad de filas afectadas
            details: Información adicional del paso
        """
        step = {
            "name": name,
            "affected_rows": affected_rows,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.steps.append(step)

    def generar_resumen(self) -> Dict[str, Any]:
        """Genera resumen ejecutivo del reporte de limpieza.

        Returns:
            Diccionario con estadísticas agregadas.
        """
        self.registros_eliminados = self.nulos_removidos + self.duplicados_removidos
        summary = {
            "dataset_id": self.dataset_id,
            "registros_procesados": self.registros_procesados,
            "registros_eliminados": self.registros_eliminados,
            "registros_finales": self.registros_procesados - self.registros_eliminados,
            "nulos_removidos": self.nulos_removidos,
            "duplicados_removidos": self.duplicados_removidos,
            "porcentaje_eliminacion": (
                (self.registros_eliminados / self.registros_procesados * 100)
                if self.registros_procesados > 0
                else 0
            ),
            "pasos_ejecutados": len(self.steps),
            "created_at": self.created_at.isoformat(),
        }
        return summary

    def to_dict(self) -> Dict[str, Any]:
        """Serializa el reporte a diccionario."""
        return {
            "id": self.id,
            "dataset_id": self.dataset_id,
            "registros_procesados": self.registros_procesados,
            "registros_eliminados": self.registros_eliminados,
            "nulos_removidos": self.nulos_removidos,
            "duplicados_removidos": self.duplicados_removidos,
            "steps": self.steps,
            "resumen": self.generar_resumen(),
        }
