"""Infrastructure: DuplicateCleaner - Strategy Pattern Implementation.

Implementa la estrategia de eliminación de duplicados según RB-003.
"""
from typing import List, Dict, Any, Tuple

from domain.interfaces import IDataCleaner


class DuplicateCleaner(IDataCleaner):
    """Estrategia: Elimina duplicados por combinación de campos clave.

    Regla RB-003: Eliminar duplicados por (ubicacion, tamano_m2)
    Preserva la primera ocurrencia, elimina subsiguientes.

    Attributes:
        key_fields: Tupla de campos que forman la clave de duplicación
    """

    def __init__(self, key_fields: List[str] | None = None) -> None:
        """Inicializa el limpiador.

        Args:
            key_fields: Campos que forman la clave. Por defecto: ("ubicacion", "tamano_m2")
        """
        if key_fields is None:
            key_fields = ["ubicacion", "tamano_m2"]
        self.key_fields = tuple(key_fields)

    def _extract_key(self, row: Dict[str, Any]) -> Tuple[Any, ...]:
        """Extrae la clave compuesta de una fila.

        Args:
            row: Fila del dataset

        Returns:
            Tupla con valores de los campos clave
        """
        return tuple(row.get(k) for k in self.key_fields)

    def clean(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Elimina filas duplicadas preservando la primera ocurrencia.

        Algoritmo:
        1. Extrae clave compuesta de cada fila
        2. Rastrea claves vistas
        3. Si clave ya vista, descarta fila
        4. Si es nueva, la incluye

        Args:
            rows: Filas potencialmente duplicadas

        Returns:
            Filas sin duplicados (preserva primera ocurrencia)
        """
        seen: set = set()
        result: List[Dict[str, Any]] = []
        duplicados_removidos = 0

        for row in rows:
            key = self._extract_key(row)

            if key in seen:
                duplicados_removidos += 1
                continue

            seen.add(key)
            result.append(row)

        # Información de limpieza disponible para reportes
        self.duplicados_removidos = duplicados_removidos

        return result
