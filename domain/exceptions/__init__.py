"""Domain exceptions package

Contains the base domain exception and specific domain exceptions used across
the domain layer.
"""

from typing import Optional


class DominioException(Exception):
    """Base exception for domain errors."""

    def __init__(self, message: str, *, reason: Optional[str] = None, context: Optional[dict] = None):
        super().__init__(message)
        self.reason = reason
        self.context = context or {}


class DatasetInvalidoException(DominioException):
    pass


class UbicacionNoBogotaException(DominioException):
    pass


class CoherenciaDatosException(DominioException):
    pass


class SignificanciaInsuficienteException(DominioException):
    pass


class MargenErrorExcedidoException(DominioException):
    pass

