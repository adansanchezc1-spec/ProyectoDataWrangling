"""Application service: IngestionService (skeleton)"""
from typing import Dict


class IngestionService:
    """Factory method for loaders and basic validation checks."""

    REQUIRED_COLUMNS = [
        "ubicacion",
        "tamano_m2",
        "habitaciones",
        "banos",
        "estrato",
        "precio",
    ]

    def __init__(self, repository=None):
        self.repository = repository

    def load(self, path: str, formato: str) -> Dict:
        """Load dataset from path and return a dict with metadata and dataframe.

        This is a placeholder; actual loaders are implemented later.
        """
        raise NotImplementedError

    def validate_columns(self, columns: list) -> bool:
        return all(col in columns for col in self.REQUIRED_COLUMNS)
