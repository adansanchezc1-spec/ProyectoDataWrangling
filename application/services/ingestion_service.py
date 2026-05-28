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
    """

    REQUIRED_COLUMNS = [
        "ubicacion",
        "tamano_m2",
        "habitaciones",
        "banos",
        "estrato",
        "precio",
    ]

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

    def _load_csv(self, path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Carga un archivo CSV.

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

            with open(path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None:
                    raise ValueError("CSV is empty")

                field_map = {
                    col: self._normalize_column_name(col)
                    for col in reader.fieldnames
                }
                schema = {field_map[col]: "string" for col in reader.fieldnames}

                for row in reader:
                    rows.append(
                        {
                            field_map[col]: value
                            for col, value in row.items()
                            if col is not None
                        }
                    )

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
        """Normalizes incoming source headers for schema validation."""
        return str(column).strip().lstrip("\ufeff")
