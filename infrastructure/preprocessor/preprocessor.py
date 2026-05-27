"""Preprocessor pipeline to apply cleaners to raw records."""
from typing import List, Dict, Iterable, Callable


class Preprocessor:
    """Apply a chain of cleaners to records.

    Cleaners must implement `clean(records: List[Dict]) -> List[Dict]`.
    """

    def __init__(self, cleaners: Iterable[Callable] | None = None) -> None:
        self.cleaners = list(cleaners) if cleaners is not None else []

    def add(self, cleaner: Callable) -> None:
        self.cleaners.append(cleaner)

    def run(self, records: List[Dict]) -> List[Dict]:
        out = records
        for c in self.cleaners:
            out = c.clean(out)
        return out
