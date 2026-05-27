"""Domain interfaces: repository, email, cleaner, feature analyzer"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Iterable


class IDataRepository(ABC):
    @abstractmethod
    def save(self, entity: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> Iterable[Any]:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: str) -> None:
        raise NotImplementedError


class IEmailService(ABC):
    @abstractmethod
    def send(self, subject: str, body: str, to: str) -> None:
        raise NotImplementedError


class IDataCleaner(ABC):
    @abstractmethod
    def clean(self, dataset: Any) -> Any:
        raise NotImplementedError


class IFeatureAnalyzer(ABC):
    @abstractmethod
    def analyze(self, dataset: Any) -> dict:
        raise NotImplementedError
