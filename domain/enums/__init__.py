"""Domain enums: Estados BPMN, Formatos, Tipos de Variables.

Enums que representan estados finitos del pipeline y tipos de datos.
Mapeados exactamente al flujo BPMN con 4 gateways XOR.
"""
from enum import Enum


class DatasetStatus(Enum):
    """Estados del dataset en el pipeline BPMN.

    Flujo: RAW → EXTRACTING → VALIDATING → TRANSFORMING → CLEANING →
           PROFILING → QUALITY_GATE → MDM_LOADED → NOTIFIED

    Gateways XOR:
    1. ¿Extracción completa? EXTRACTING → VALIDATING
    2. ¿Formato válido? VALIDATING → TRANSFORMING
    3. ¿Transformación completa? TRANSFORMING → CLEANING
    4. ¿Calidad aceptable? PROFILING → QUALITY_GATE → MDM_LOADED
    """

    RAW = "RAW"  # Datos extraídos sin procesar
    EXTRACTING = "EXTRACTING"  # En proceso de extracción (Gateway 1)
    VALIDATING = "VALIDATING"  # En proceso de validación (Gateway 2)
    TRANSFORMING = "TRANSFORMING"  # En proceso de transformación (Gateway 3)
    CLEANING = "CLEANING"  # En proceso de limpieza
    PROFILING = "PROFILING"  # En proceso de perfilado
    QUALITY_GATE = "QUALITY_GATE"  # En evaluación de calidad (Gateway 4)
    MDM_LOADED = "MDM_LOADED"  # Cargado en Master Data Management
    NOTIFIED = "NOTIFIED"  # Notificación enviada, proceso completo
    REJECTED = "REJECTED"  # Rechazado en algún gateway
    ERROR = "ERROR"  # Error durante procesamiento


class Formato(Enum):
    """Formatos de archivo soportados (RB-004)."""

    CSV = "CSV"
    EXCEL = "EXCEL"
    JSON = "JSON"

    @classmethod
    def es_valido(cls, formato: str) -> bool:
        """Verifica si un formato es válido.

        Args:
            formato: String del formato

        Returns:
            True si está en Formato enum
        """
        return formato.upper() in cls.__members__

    @classmethod
    def from_extension(cls, filename: str) -> "Formato":
        """Deduce el formato de la extensión de archivo.

        Args:
            filename: Nombre del archivo

        Returns:
            Formato enum correspondiente

        Raises:
            FormatoInvalidoException: Si extensión no es soportada
        """
        from domain.exceptions import FormatoInvalidoException

        ext = filename.split(".")[-1].upper()
        if ext in ("CSV", "TSV"):
            return cls.CSV
        elif ext in ("XLS", "XLSX"):
            return cls.EXCEL
        elif ext == "JSON":
            return cls.JSON
        else:
            raise FormatoInvalidoException(
                f"Extension not supported: .{ext}",
                reason="RB-004",
                context={"extension": ext},
                gateway_bpmn=2,
            )


class TipoVariable(Enum):
    """Tipos de variables detectadas en datos."""

    NUMERIC = "NUMERIC"
    CATEGORICAL = "CATEGORICAL"
    TEXT = "TEXT"
    DATETIME = "DATETIME"
