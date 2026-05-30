"""Infrastructure: FormatCleaner - Strategy Pattern Implementation.

Implementa la estrategia de normalización de tipos y formatos.
"""
from typing import List, Dict, Any, Callable, Optional

from domain.interfaces import IDataCleaner


class FormatCleaner(IDataCleaner):
    """Estrategia: Coerciona y formatea campos a tipos esperados.

    Attributes:
        rules: Mapeo de field -> callable que convierte el valor
    """

    def __init__(self, rules: Dict[str, Callable[[Any], Any]] | None = None) -> None:
        """Inicializa el limpiador con reglas de conversión.

        Args:
            rules: Dict con field -> conversion_function
                   Ej: {"estrato": int, "precio": float}
        """
        self.rules = rules or {}

    def clean(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aplica reglas de conversión a cada fila.

        Comportamiento:
        - Si el campo existe y hay regla, intenta conversión
        - Si la conversión falla, mantiene el valor original
        - Si no hay regla, deja el campo intacto

        Args:
            rows: Filas a formatear

        Returns:
            Filas con campos convertidos a tipos esperados
        """
        result: List[Dict[str, Any]] = []

        for row in rows:
            formatted_row = dict(row)

            for field, conversion_fn in self.rules.items():
                if field in formatted_row and formatted_row[field] is not None:
                    try:
                        formatted_row[field] = conversion_fn(formatted_row[field])
                    except Exception:
                        # Mantiene valor original si conversión falla
                        pass

            result.append(formatted_row)

        return result

    @staticmethod
    def crear_rules_inmobiliarias() -> Dict[str, Callable[[Any], Any]]:
        """Crea reglas de conversión estándar para datos inmobiliarios.

        Returns:
            Dict con reglas predefinidas
        """
        return {
            "tamano_m2": float,
            "habitaciones": lambda x: int(round(float(x))),
            "banos": lambda x: int(round(float(x))),
            "estrato": lambda x: int(round(float(x))),
            "precio": float,
            "parqueadero": lambda x: int(round(float(x))),
            "long_com_corr": float,
            "parques": lambda x: int(round(float(x))),
            "vias": lambda x: int(round(float(x))),
            "remocion_masa": float,
            "grandes_superficies": lambda x: int(round(float(x))),
            "colegios": lambda x: int(round(float(x))),
            "hospitales": lambda x: int(round(float(x))),
            "fecha": lambda x: int(str(x)[:4]),
        }
