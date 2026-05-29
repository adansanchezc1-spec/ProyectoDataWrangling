"""Application Service: IngestionService.

Orquesta la extracción e ingesta de datos según el formato del archivo.
Implementa Factory Method para crear loaders específicos por formato.
"""
import csv
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from uuid import uuid4

from domain.entities import Dataset
from domain.enums import Formato, DatasetStatus
from domain.exceptions import (
    ExtraccionIncompletaException,
    FormatoInvalidoException,
    DatasetInvalidoException,
)
from domain.validators import DatasetValidator

try:
    import openpyxl
except ImportError:
    openpyxl = None

try:
    import pandas as pd
except ImportError:
    pd = None


class IngestionService:
    """Servicio de ingesta que carga datasets según el formato.

    Características:
    - Factory Method para crear loaders por formato
    - Validación de columnas requeridas
    - Manejo de errores específicos por formato
    - Mapeo de nombres de columna fuente a nombres del sistema
    - Detección automática de delimitador CSV (; , tab)
    """

    REQUIRED_COLUMNS = [
        "ubicacion",
        "tamano_m2",
        "habitaciones",
        "banos",
        "estrato",
        "precio",
    ]

    SOURCE_COLUMN_MAP = {
        "subzona": "ubicacion",
        "zona": "ubicacion",
        "barrio": "ubicacion",
        "localidad": "ubicacion",
        "precios": "precio",
        "precio_millon": "precio",
        "area": "tamano_m2",
        "metros": "tamano_m2",
        "tamano": "tamano_m2",
        "alcobas": "habitaciones",
        "cuartos": "habitaciones",
        "habitacion": "habitaciones",
        "habitaciones": "habitaciones",
        "ba\u00f1os": "banos",
        "banos": "banos",
        "estrato": "estrato",
        "fecha": "fecha",
        "año": "fecha",
        "year": "fecha",
        "date": "fecha",
        "fecha_construccion": "fecha",
        "anio": "fecha",
        "annio": "fecha",
    }

    UBICACION_SOURCE_COLUMNS = {"subzona", "zona", "barrio", "localidad"}

    def __init__(self) -> None:
        """Inicializa el servicio sin dependencias externas (inyectadas en load)."""
        pass

    def load(self, file_path: str) -> Dataset:
        """Carga un dataset desde archivo en el formato detectado.

        Flujo:
        1. Detecta formato por extensión
        2. Lee datos según formato
        3. Valida columnas mínimas
        4. Retorna entidad Dataset

        Args:
            file_path: Ruta al archivo a ingerir

        Returns:
            Entidad Dataset con datos cargados

        Raises:
            FormatoInvalidoException: Si formato no soportado (Gateway 2)
            ExtraccionIncompletaException: Si la lectura falla (Gateway 1)
            DatasetInvalidoException: Si faltan columnas requeridas (RF-002)
        """
        path = Path(file_path)

        # Valida que archivo existe
        if not path.exists():
            raise ExtraccionIncompletaException(
                f"File not found: {file_path}",
                context={"path": file_path},
                gateway_bpmn=1,
            )

        # Detecta formato y carga
        try:
            formato = Formato.from_extension(path.name)
        except FormatoInvalidoException:
            raise

        # Lee datos según formato
        if formato == Formato.CSV:
            rows, schema = self._load_csv(path)
        elif formato == Formato.EXCEL:
            rows, schema = self._load_excel(path)
        elif formato == Formato.JSON:
            rows, schema = self._load_json(path)
        else:
            raise FormatoInvalidoException(
                f"Format not implemented: {formato.value}",
                reason="RB-004",
                context={"format": formato.value},
                gateway_bpmn=2,
            )

        # Normaliza separadores decimales (coma europea → punto)
        rows = self._normalizar_decimales(rows)

        # Reconstruye schema tras transformaciones
        if rows:
            schema = {col: "string" for col in rows[0].keys()}

        # Valida columnas
        DatasetValidator.validar_columnas_minimas(schema, self.REQUIRED_COLUMNS)

        # Crea entidad Dataset
        dataset_id = str(uuid4())[:8]
        dataset = Dataset(
            id=dataset_id,
            source_path=str(path),
            format=formato.value,
            status=DatasetStatus.RAW.value,
            created_at=__import__("datetime").datetime.utcnow(),
            schema=schema,
            rows_preview=rows[:min(100, len(rows))],  # Primeras 100 filas
            records=rows,
            total_rows=len(rows),
        )

        return dataset

    def _detect_delimiter(self, path: Path) -> str:
        """Detecta el delimitador de un CSV examinando la primera línea.

        Returns:
            str: Delimitador detectado (; , o tab)
        """
        with open(path, "r", encoding="utf-8-sig") as f:
            first_line = f.readline()

        semicolons = first_line.count(";")
        commas = first_line.count(",")
        tabs = first_line.count("\t")

        if semicolons > commas and semicolons > tabs:
            return ";"
        elif tabs > commas and tabs > semicolons:
            return "\t"
        return ","

    def _load_csv(self, path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Carga un archivo CSV con detección automática de delimitador.

        Aplica mapeo de columnas fuente a nombres del sistema y
        transforma valores de ubicación y separadores decimales.

        Args:
            path: Ruta al CSV

        Returns:
            Tupla (rows, schema)

        Raises:
            ExtraccionIncompletaException: Si hay error de lectura
        """
        try:
            rows = []
            schema = {}
            delimiter = self._detect_delimiter(path)
            ubicacion_sources: Dict[str, bool] = {}

            with open(path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                if reader.fieldnames is None:
                    raise ValueError("CSV is empty")

                field_map = {}
                for col in reader.fieldnames:
                    normalized = self._normalize_column_name(col)
                    field_map[col] = normalized
                    col_lower = col.strip().lower()
                    if col_lower in self.UBICACION_SOURCE_COLUMNS:
                        ubicacion_sources[col] = True

                schema = {field_map[col]: "string" for col in reader.fieldnames}

                for row in reader:
                    new_row = {}
                    for col, value in row.items():
                        if col is None:
                            continue
                        new_col = field_map.get(col, col)
                        if col in ubicacion_sources and isinstance(value, str):
                            value = f"Bogotá, {value}"
                        new_row[new_col] = value
                    rows.append(new_row)

            if not rows:
                raise ValueError("CSV has no data rows")

            return rows, schema

        except Exception as e:
            raise ExtraccionIncompletaException(
                f"Failed to load CSV: {str(e)}",
                context={"file": path.name, "error": str(e)},
                gateway_bpmn=1,
            )

    def _load_excel(self, path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Carga un archivo Excel.

        Args:
            path: Ruta al Excel

        Returns:
            Tupla (rows, schema)

        Raises:
            ExtraccionIncompletaException: Si hay error de lectura
        """
        if pd is None:
            raise ExtraccionIncompletaException(
                "pandas is required to load Excel files",
                context={"file": path.name},
                gateway_bpmn=1,
            )

        try:
            df = pd.read_excel(path)
            df.columns = [self._normalize_column_name(col) for col in df.columns]
            rows = df.to_dict(orient="records")
            schema = {col: "string" for col in df.columns}

            if rows is None or len(rows) == 0:
                raise ValueError("Excel sheet is empty")

            return rows, schema

        except Exception as e:
            raise ExtraccionIncompletaException(
                f"Failed to load Excel: {str(e)}",
                context={"file": path.name, "error": str(e)},
                gateway_bpmn=1,
            )

    def _load_json(self, path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Carga un archivo JSON.

        Espera que el JSON sea un array de objetos.

        Args:
            path: Ruta al JSON

        Returns:
            Tupla (rows, schema)

        Raises:
            ExtraccionIncompletaException: Si hay error de lectura
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Valida que sea lista
            if not isinstance(data, list):
                raise ValueError("JSON root must be an array of objects")

            if len(data) == 0:
                raise ValueError("JSON array is empty")

            rows = [
                {
                    self._normalize_column_name(key): value
                    for key, value in row.items()
                }
                for row in data
                if isinstance(row, dict)
            ]

            # Infiere schema del primer objeto
            schema = {}
            if isinstance(rows[0], dict):
                schema = {col: "string" for col in rows[0].keys()}

            return rows, schema

        except json.JSONDecodeError as e:
            raise ExtraccionIncompletaException(
                f"Failed to parse JSON: {str(e)}",
                context={"file": path.name, "error": str(e)},
                gateway_bpmn=1,
            )
        except Exception as e:
            raise ExtraccionIncompletaException(
                f"Failed to load JSON: {str(e)}",
                context={"file": path.name, "error": str(e)},
                gateway_bpmn=1,
            )

    @staticmethod
    def _normalize_column_name(column: Any) -> str:
        """Normaliza nombres de columna fuente y aplica mapeo a nombres del sistema.

        Retorna siempre en minúsculas para que coincida con reglas de
        normalización y limpieza (FormatCleaner, _normalizar_decimales).
        """
        col = str(column).strip().lstrip("\ufeff")
        col_lower = col.lower().strip()
        mapped = IngestionService.SOURCE_COLUMN_MAP.get(col_lower)
        if mapped:
            return mapped
        return col_lower

    @staticmethod
    def _normalizar_decimales(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convierte comas decimales europeas a puntos en campos numéricos.

        - Si un valor tiene UNA sola coma (ej: "15,76235525"), se reemplaza
          por punto: "15.76235525" (decimal europeo).
        - Si tiene MÚLTIPLES comas (ej: "16,364,832.92"), se interpreta como
          separador de millares y se eliminan todas las comas: "16364832.92".
        - Búsqueda case-insensitive sobre nombres de columna.
        """
        from itertools import chain

        all_keys = set(chain.from_iterable(row.keys() for row in rows))
        campos_numericos_lower = {
            "tamano_m2", "habitaciones", "banos", "estrato", "precio",
            "parqueadero", "long_com_corr", "parques", "vias",
            "remocion_masa", "grandes_superficies", "colegios", "hospitales",
        }
        for row in rows:
            for actual_key in list(row.keys()):
                if actual_key.lower() in campos_numericos_lower:
                    val = row[actual_key]
                    if isinstance(val, str):
                        if val.count(",") == 1:
                            row[actual_key] = val.replace(",", ".")
                        elif val.count(",") > 1:
                            row[actual_key] = val.replace(",", "")
        return rows
