"""Cleaner that removes rows with missing critical fields."""
from typing import List, Dict, Iterable


class NullCleaner:
    """Remove rows that are missing required keys or have null-like values."""

    def __init__(self, required_fields: Iterable[str] | None = None) -> None:
        self.required_fields = list(required_fields) if required_fields is not None else []

    def clean(self, rows: List[Dict]) -> List[Dict]:
        cleaned: List[Dict] = []
        for r in rows:
            skip = False
            for f in self.required_fields:
                if f not in r or r[f] is None:
                    skip = True
                    break
                # treat empty strings as missing
                if isinstance(r[f], str) and r[f].strip() == "":
                    skip = True
                    break
            if not skip:
                cleaned.append(r)
        return cleaned
"""NullCleaner: removes rows or fields with nulls according to rules"""


class NullCleaner:
    def clean(self, dataset):
        # Placeholder: implement null removal logic
        raise NotImplementedError
