"""Simple repository using pandas for CSV/JSON interchange."""
from typing import Optional

import os
try:
    import pandas as pd
except Exception:  # pragma: no cover - pandas optional during static analysis
    pd = None


class PandasRepository:
    """Minimal helper for loading/saving datasets via pandas."""

    def load_csv(self, path: str, **kwargs) -> Optional[object]:
        if pd is None:
            raise RuntimeError("pandas is required to load CSV files")
        return pd.read_csv(path, **kwargs)

    def save_df_to_json(self, df, path: str, orient: str = "records") -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_json(path, orient=orient, force_ascii=False)

    def to_records(self, df):
        if pd is None:
            raise RuntimeError("pandas is required")
        return df.to_dict(orient="records")
"""Infrastructure: PandasRepository skeleton implementing IDataRepository"""
from typing import Any, Iterable


class PandasRepository:
    def save(self, entity: Any) -> None:
        raise NotImplementedError

    def get_by_id(self, id: str) -> Any:
        raise NotImplementedError

    def list_all(self) -> Iterable[Any]:
        raise NotImplementedError

    def update(self, entity: Any) -> None:
        raise NotImplementedError

    def delete(self, id: str) -> None:
        raise NotImplementedError
