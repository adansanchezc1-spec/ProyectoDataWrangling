"""Cleaner that removes duplicate rows based on a key subset."""
from typing import List, Dict, Iterable, Tuple


class DuplicateCleaner:
    """Remove duplicates preserving the first occurrence.

    key_fields: sequence of fields used to identify duplicates.
    """

    def __init__(self, key_fields: Iterable[str] | None = None) -> None:
        self.key_fields = tuple(key_fields) if key_fields is not None else tuple()

    def _key(self, row: Dict) -> Tuple:
        return tuple(row.get(k) for k in self.key_fields)

    def clean(self, rows: List[Dict]) -> List[Dict]:
        seen = set()
        out: List[Dict] = []
        for r in rows:
            k = self._key(r)
            if k in seen:
                continue
            seen.add(k)
            out.append(r)
        return out
"""DuplicateCleaner: remove duplicates by address/size/location"""


class DuplicateCleaner:
    def clean(self, dataset):
        # Placeholder: implement duplicate detection and removal
        raise NotImplementedError
