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
