"""Domain entity: Dataset"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any
import unicodedata
import re

from domain.exceptions import DatasetInvalidoException


def _remove_accents(text: str) -> str:
    nkfd = unicodedata.normalize("NFKD", text)
    return "".join([c for c in nkfd if not unicodedata.combining(c)])


@dataclass
class Dataset:
    id: str
    source_path: str
    format: str
    status: str
    created_at: datetime
    schema: Dict[str, Any] = field(default_factory=dict)
    rows_preview: List[Dict[str, Any]] = field(default_factory=list)

    REQUIRED_COLUMNS = [
        "ubicacion",
        "tamano_m2",
        "habitaciones",
        "banos",
        "estrato",
        "precio",
    ]

    def validar_estructura(self) -> bool:
        """Validate that required columns exist in schema or preview.

        Returns True if valid, otherwise raises DatasetInvalidoException.
        """
        cols = set()
        if self.schema:
            cols = set(self.schema.keys())
        elif self.rows_preview:
            cols = set(self.rows_preview[0].keys())

        missing = [c for c in self.REQUIRED_COLUMNS if c not in cols]
        if missing:
            raise DatasetInvalidoException(
                f"Missing required columns: {missing}", reason="RF-002", context={"missing": missing}
            )
        return True

    def normalizar_ubicacion(self) -> None:
        """Normalize location fields in rows_preview in-place.

        Operations: lowercase, remove accents, strip spaces, collapse whitespace,
        remove dots.
        """
        for row in self.rows_preview:
            if "ubicacion" in row and isinstance(row["ubicacion"], str):
                val = row["ubicacion"].strip().lower()
                val = _remove_accents(val)
                # remove punctuation like dots and commas
                val = re.sub(r"[\.,]", "", val)
                # collapse whitespace
                val = re.sub(r"\s+", " ", val)
                row["ubicacion"] = val

    def es_bogota(self) -> bool:
        """Return True if dataset appears to be from Bogotá.

        Checks the first preview row's `ubicacion` field after normalization.
        """
        if not self.rows_preview:
            return False
        first = self.rows_preview[0].get("ubicacion")
        if not isinstance(first, str):
            return False
        norm = _remove_accents(first.strip().lower())
        norm = re.sub(r"[\.,]", "", norm)
        norm = re.sub(r"\s+", " ", norm)
        # Accept variations that start with 'bogota'
        return norm.startswith("bogota")

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "source_path": self.source_path,
            "format": self.format,
            "status": self.status,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "schema": self.schema,
            "rows_preview": self.rows_preview,
        }

