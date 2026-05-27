"""Cleaner that coerces and formats fields to expected types."""
from typing import List, Dict, Iterable, Callable


class FormatCleaner:
    """Apply simple formatting/coercion rules to rows.

    rules: dict of field -> callable(value) that returns converted value or raises.
    """

    def __init__(self, rules: dict[str, Callable] | None = None) -> None:
        self.rules = rules or {}

    def clean(self, rows: List[Dict]) -> List[Dict]:
        result: List[Dict] = []
        for r in rows:
            nr = dict(r)
            for field, fn in self.rules.items():
                if field in nr:
                    try:
                        nr[field] = fn(nr[field])
                    except Exception:
                        # keep original if conversion fails
                        pass
            result.append(nr)
        return result
"""FormatCleaner: correct types and formats (e.g., estrato -> int)"""


class FormatCleaner:
    def clean(self, dataset):
        # Placeholder: implement type conversions
        raise NotImplementedError
