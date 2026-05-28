"""Infrastructure: NullCleaner - Strategy Pattern Implementation.

Implementa la estrategia de limpieza de valores nulos en el dataset.
"""
from typing import List, Dict, Any

from domain.interfaces import IDataCleaner


class NullCleaner(IDataCleaner):
    """Estrategia: Elimina filas con campos nulos en columnas críticas.

    Attributes:
        required_fields: Campos que no pueden ser nulos
    """

    def __init__(self, required_fields: List[str] | None = None) -> None:
        """Inicializa el limpiador.

        Args:
            required_fields: Campos obligatorios sin nulos
        """
        self.required_fields = list(required_fields) if required_fields is not None else []

    def clean(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Elimina filas que tienen nulos en campos requeridos.

        Regla: Una fila se rechaza si:
        - Falta alguno de los required_fields
        - El valor es None
        - El valor es string vacío o solo espacios

        Args:
            rows: Filas originales

        Returns:
            Filas filtradas sin nulos en campos críticos
        """
        cleaned: List[Dict[str, Any]] = []
        nulos_removidos = 0

        for row in rows:
            skip = False
            for field in self.required_fields:
                # Verifica presencia del campo
                if field not in row:
                    skip = True
                    break

                # Verifica que no sea None
                if row[field] is None:
                    skip = True
                    break

                # Verifica que no sea string vacío
                if isinstance(row[field], str) and row[field].strip() == "":
                    skip = True
                    break

            if not skip:
                cleaned.append(row)
            else:
                nulos_removidos += 1

        return cleaned
