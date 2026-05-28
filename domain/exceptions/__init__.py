"""Domain exceptions package - Centralized exception hierarchy.

Contiene la base de excepciones de dominio y todas las excepciones
específicas del pipeline ETL, mapeadas a requisitos funcionales y
reglas de negocio.
"""
from typing import Optional, Dict, Any


class DominioException(Exception):
    """Excepción base para errores del dominio.

    Attributes:
        message: Descripción del error
        reason: Código de regla de negocio/requerimiento (ej: RF-003, RB-001)
        context: Contexto adicional del error
        gateway_bpmn: Gateway BPMN que generó el error (1-4)
    """

    def __init__(
        self,
        message: str,
        *,
        reason: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        gateway_bpmn: Optional[int] = None,
    ):
        super().__init__(message)
        self.reason = reason
        self.context = context or {}
        self.gateway_bpmn = gateway_bpmn


class DatasetInvalidoException(DominioException):
    """Dataset no cumple estructura mínima (RF-002, RB-004)."""

    pass


class ExtraccionIncompletaException(DominioException):
    """Extracción de datos incompleta (Gateway 1 BPMN, RF-003)."""

    pass


class FormatoInvalidoException(DominioException):
    """Formato de archivo no soportado (Gateway 2 BPMN, RB-004)."""

    pass


class TransformacionFallidaException(DominioException):
    """Transformación de datos falló (Gateway 3 BPMN)."""

    pass


class CalidadInsuficienteException(DominioException):
    """Calidad de datos no cumple estándares (Gateway 4 BPMN, RF-007, RF-008)."""

    pass


class UbicacionNoBogotaException(DominioException):
    """Ubicación no corresponde a Bogotá (RB-001, RB-004)."""

    pass


class CoherenciaDatosException(DominioException):
    """Falta coherencia semántica en datos (RB-005, RF-005)."""

    pass


class SignificanciaInsuficienteException(DominioException):
    """Datos carecen de significancia estadística."""

    pass


class MargenErrorExcedidoException(DominioException):
    """Margen de error excedido en validación."""

    pass


class RepositorioException(DominioException):
    """Error en operación de repositorio."""

    pass


class NotificacionException(DominioException):
    """Error en envío de notificación."""

    pass