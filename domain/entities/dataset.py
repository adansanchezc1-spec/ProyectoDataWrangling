"""Domain entity: Dataset - Rich Domain Model.

Responsabilidades:
- Encapsular lógica de normalización de ubicación
- Validar estructura según requisitos de negocio (RB-001, RB-002, RB-004, RB-005)
- Mantener estado del dataset en el pipeline BPMN
- Métodos de interrogación sobre completitud y validez
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any
import unicodedata
import re

from domain.exceptions import DatasetInvalidoException


def _remove_accents(text: str) -> str:
    """Helper: Normaliza acentos en texto."""
    nkfd = unicodedata.normalize("NFKD", text)
    return "".join([c for c in nkfd if not unicodedata.combining(c)])


@dataclass
class Dataset:
    """Entidad Dataset representando un dataset inmobiliario de Bogotá.

    Attributes:
        id: Identificador único del dataset
        source_path: Ruta al archivo fuente
        format: Formato del archivo (CSV, EXCEL, JSON)
        status: Estado actual en pipeline BPMN
        created_at: Timestamp de creación
        schema: Esquema detectado (dict con tipos)
        rows_preview: Muestra de filas del dataset
        total_rows: Total de filas procesadas
    """

    id: str
    source_path: str
    format: str
    status: str
    created_at: datetime
    schema: Dict[str, Any] = field(default_factory=dict)
    rows_preview: List[Dict[str, Any]] = field(default_factory=list)
    records: List[Dict[str, Any]] = field(default_factory=list)
    total_rows: int = 0
    user_email: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Columnas requeridas por RB-004
    REQUIRED_COLUMNS = [
        "ubicacion",
        "tamano_m2",
        "habitaciones",
        "banos",
        "estrato",
        "precio",
    ]

    def validar_estructura(self) -> bool:
        """Valida que el dataset tenga todas las columnas requeridas.

        Raises:
            DatasetInvalidoException: Si faltan columnas críticas.

        Returns:
            True si la validación pasa.
        """
        cols = set()
        if self.schema:
            cols = set(self.schema.keys())
        elif self.records:
            cols = set(self.records[0].keys())
        elif self.rows_preview:
            cols = set(self.rows_preview[0].keys())

        missing = [c for c in self.REQUIRED_COLUMNS if c not in cols]
        if missing:
            raise DatasetInvalidoException(
                f"Missing required columns: {missing}",
                reason="RF-002",
                context={"missing": missing},
            )
        return True

    def normalizar_ubicacion(self) -> None:
        """Normaliza ubicaciones en rows_preview según RB-001.

        Operaciones:
        - Minúsculas
        - Remover acentos
        - Remover puntuación
        - Colapsar espacios en blanco
        """
        rows = self.records if self.records else self.rows_preview
        for row in rows:
            if "ubicacion" in row and isinstance(row["ubicacion"], str):
                val = row["ubicacion"].strip().lower()
                val = _remove_accents(val)
                val = re.sub(r"[\.,]", "", val)
                val = re.sub(r"\s+", " ", val)
                row["ubicacion"] = val
        self.rows_preview = rows[: min(100, len(rows))]

    def es_bogota(self) -> bool:
        """Verifica si el dataset es de Bogotá (RB-001).

        Returns:
            True si la primera fila tiene ubicación de Bogotá normalizada.
        """
        rows = self.records if self.records else self.rows_preview
        if not rows:
            return False
        for row in rows:
            value = row.get("ubicacion")
            if not isinstance(value, str):
                return False
            norm = _remove_accents(value.strip().lower())
            norm = re.sub(r"[\.,]", "", norm)
            norm = re.sub(r"\s+", " ", norm)
            if not norm.startswith("bogota"):
                return False
        return True

    def esta_completo(self) -> bool:
        """Determina si el dataset está completo (todas las filas con datos).

        Returns:
            True si no hay filas nulas y hay preview.
        """
        rows = self.records if self.records else self.rows_preview
        if not rows or self.total_rows == 0:
            return False
        # Verificar que al menos una fila esté completa
        for row in rows:
            missing = [col for col in self.REQUIRED_COLUMNS if col not in row or row[col] is None]
            if not missing:
                return True
        return False

    def to_dict(self) -> Dict:
        """Serializa dataset a diccionario."""
        return {
            "id": self.id,
            "source_path": self.source_path,
            "format": self.format,
            "status": self.status,
            "created_at": (
                self.created_at.isoformat()
                if isinstance(self.created_at, datetime)
                else self.created_at
            ),
            "schema": self.schema,
            "rows_preview": self.rows_preview,
            "records": self.records,
            "total_rows": self.total_rows,
            "user_email": self.user_email,
            "metadata": self.metadata,
        }

