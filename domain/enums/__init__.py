"""Domain enums: DatasetStatus, Formato, TipoVariable"""
from enum import Enum


class DatasetStatus(Enum):
    RAW = "RAW"
    VALIDATED = "VALIDATED"
    STORED = "STORED"
    CLEANING = "CLEANING"
    PROFILED = "PROFILED"
    TRANSFORMED = "TRANSFORMED"
    UNIFIED = "UNIFIED"
    READY = "READY"
    ERROR = "ERROR"


class Formato(Enum):
    CSV = "CSV"
    EXCEL = "EXCEL"
    JSON = "JSON"


class TipoVariable(Enum):
    NUMERIC = "NUMERIC"
    CATEGORICAL = "CATEGORICAL"
    TEXT = "TEXT"
    DATETIME = "DATETIME"
