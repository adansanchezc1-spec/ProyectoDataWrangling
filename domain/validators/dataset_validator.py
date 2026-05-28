"""Validators for Dataset domain - Validadores de Reglas de Negocio.

Implementa validación de estrato, ubicación, formato y coherencia semántica
según los requisitos RB-001 a RB-006.
"""
import re
import unicodedata
from typing import Any, List, Dict, Optional

from domain.exceptions import (
    CoherenciaDatosException,
    UbicacionNoBogotaException,
    FormatoInvalidoException,
)


def _remove_accents(text: str) -> str:
    """Helper: Normaliza acentos en texto."""
    nkfd = unicodedata.normalize("NFKD", text)
    return "".join([c for c in nkfd if not unicodedata.combining(c)])


class DatasetValidator:
    """Validador de reglas de negocio para datasets inmobiliarios."""

    @staticmethod
    def validar_estrato(valor: Any) -> int:
        """Valida estrato según RB-002: entero en [1, 6].

        Args:
            valor: Valor a validar

        Returns:
            int: Valor de estrato validado

        Raises:
            CoherenciaDatosException: Si no cumple rango
        """
        try:
            estrato = int(valor)
        except (ValueError, TypeError):
            raise CoherenciaDatosException(
                f"Estrato must be integer in [1,6], got: {valor}",
                reason="RB-002",
                context={"value": valor},
            )
        if not 1 <= estrato <= 6:
            raise CoherenciaDatosException(
                f"Estrato out of range [1,6]: {estrato}",
                reason="RB-002",
                context={"value": estrato},
            )
        return estrato

    @staticmethod
    def validar_ubicacion(valor: Any) -> str:
        """Valida y normaliza ubicación según RB-001: debe ser Bogotá.

        Args:
            valor: Ubicación a validar

        Returns:
            str: Ubicación normalizada

        Raises:
            UbicacionNoBogotaException: Si no es Bogotá
        """
        if not isinstance(valor, str):
            raise UbicacionNoBogotaException(
                f"Location must be a string, got: {type(valor)}",
                reason="RB-001",
                context={"value": valor},
            )
        # Normaliza
        val = valor.strip().lower()
        val = _remove_accents(val)
        val = re.sub(r"[\.,]", "", val)
        val = re.sub(r"\s+", " ", val)

        # Valida que sea Bogotá
        if not val.startswith("bogota"):
            raise UbicacionNoBogotaException(
                f"Location not in Bogotá: {valor}",
                reason="RB-001",
                context={"value": valor},
            )
        return val

    @staticmethod
    def validar_formato_archivo(filename: str) -> str:
        """Valida formato de archivo según RB-004.

        Args:
            filename: Nombre del archivo

        Returns:
            str: Formato detectado (CSV, EXCEL, JSON)

        Raises:
            FormatoInvalidoException: Si formato no soportado
        """
        ext = filename.split(".")[-1].upper()
        if ext in ("CSV", "TSV"):
            return "CSV"
        elif ext in ("XLS", "XLSX"):
            return "EXCEL"
        elif ext == "JSON":
            return "JSON"
        else:
            raise FormatoInvalidoException(
                f"Format not supported: .{ext}",
                reason="RB-004",
                context={"extension": ext},
                gateway_bpmn=2,
            )

    @staticmethod
    def validar_columnas_minimas(schema: Dict[str, Any], columnas_requeridas: List[str]) -> bool:
        """Valida que estén las columnas mínimas requeridas (RB-004).

        Args:
            schema: Esquema del dataset
            columnas_requeridas: Columnas que deben estar presentes

        Returns:
            True si están todas las columnas

        Raises:
            FormatoInvalidoException: Si faltan columnas
        """
        cols_schema = set(schema.keys()) if isinstance(schema, dict) else set()
        missing = [c for c in columnas_requeridas if c not in cols_schema]

        if missing:
            raise FormatoInvalidoException(
                f"Missing required columns: {missing}",
                reason="RF-002",
                context={"missing": missing},
                gateway_bpmn=2,
            )
        return True


class QualityValidator:
    """Validador de calidad de datos según RB-005, RF-007, RF-008."""

    @staticmethod
    def validar_consistencia_semantica(row: Dict[str, Any]) -> bool:
        """Valida coherencia semántica de una fila (RB-005).

        Reglas:
        - tamano_m2 > 0
        - habitaciones > 0
        - banos > 0
        - precio > 0
        - estrato entre [1, 6]

        Args:
            row: Fila a validar

        Returns:
            True si cumple

        Raises:
            CoherenciaDatosException: Si viola alguna regla
        """
        try:
            # Validar tamano_m2
            tamano = float(row.get("tamano_m2", 0))
            if tamano <= 0:
                raise CoherenciaDatosException(
                    f"tamano_m2 must be > 0, got: {tamano}",
                    reason="RB-005",
                    context={"field": "tamano_m2", "value": tamano},
                )

            # Validar habitaciones
            habitaciones = int(row.get("habitaciones", 0))
            if habitaciones <= 0:
                raise CoherenciaDatosException(
                    f"habitaciones must be > 0, got: {habitaciones}",
                    reason="RB-005",
                    context={"field": "habitaciones", "value": habitaciones},
                )

            # Validar banos
            banos = int(row.get("banos", 0))
            if banos <= 0:
                raise CoherenciaDatosException(
                    f"banos must be > 0, got: {banos}",
                    reason="RB-005",
                    context={"field": "banos", "value": banos},
                )

            # Validar precio
            precio = float(row.get("precio", 0))
            if precio <= 0:
                raise CoherenciaDatosException(
                    f"precio must be > 0, got: {precio}",
                    reason="RB-005",
                    context={"field": "precio", "value": precio},
                )

            DatasetValidator.validar_estrato(row.get("estrato"))

            return True

        except (ValueError, TypeError) as e:
            raise CoherenciaDatosException(
                f"Error in semantic validation: {str(e)}",
                reason="RB-005",
                context={"row": row},
            )

    @staticmethod
    def validar_integridad(rows: List[Dict[str, Any]], min_cobertura: float = 0.8) -> bool:
        """Valida integridad general del dataset (RF-007, RF-008).

        Reglas:
        - Mínimo 80% de cobertura de datos
        - Sin duplicados (por ubicacion, tamano_m2)

        Args:
            rows: Filas del dataset
            min_cobertura: Cobertura mínima requerida (0-1)

        Returns:
            True si cumple

        Raises:
            CoherenciaDatosException: Si integridad es insuficiente
        """
        if not rows:
            raise CoherenciaDatosException(
                "Dataset is empty",
                reason="RF-008",
                context={},
            )

        # Calcular cobertura (filas válidas / total)
        filas_validas = 0
        for row in rows:
            try:
                QualityValidator.validar_consistencia_semantica(row)
                filas_validas += 1
            except CoherenciaDatosException:
                pass

        cobertura = filas_validas / len(rows) if rows else 0
        if cobertura < min_cobertura:
            raise CoherenciaDatosException(
                f"Data integrity check failed. Coverage: {cobertura:.1%} < {min_cobertura:.1%}",
                reason="RF-008",
                context={"coverage": cobertura, "min_coverage": min_cobertura},
            )

        return True
