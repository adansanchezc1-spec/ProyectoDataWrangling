"""Validators for Dataset domain concerns."""
from typing import Any

from domain.exceptions import CoherenciaDatosException, UbicacionNoBogotaException


class DatasetValidator:
    @staticmethod
    def validar_estrato(valor: Any) -> int:
        """Validate that 'estrato' is an integer in [1,6]. Returns int or raises."""
        try:
            estrato = int(valor)
        except Exception:
            raise CoherenciaDatosException(
                f"Estrato must be integer in [1,6], got: {valor}", reason="RB-002", context={"value": valor}
            )
        if not 1 <= estrato <= 6:
            raise CoherenciaDatosException(
                f"Estrato out of range [1,6]: {estrato}", reason="RB-002", context={"value": estrato}
            )
        return estrato

    @staticmethod
    def validar_ubicacion(valor: Any) -> str:
        """Normalize and validate that location belongs to Bogotá.

        Returns normalized string or raises UbicacionNoBogotaException.
        """
        if not isinstance(valor, str):
            raise UbicacionNoBogotaException(
                f"Location must be a string, got: {type(valor)}", reason="RB-001", context={"value": valor}
            )
        # Normalize similarly to Dataset.normalizar_ubicacion
        import unicodedata, re

        def _remove_accents(text: str) -> str:
            nkfd = unicodedata.normalize("NFKD", text)
            return "".join([c for c in nkfd if not unicodedata.combining(c)])

        val = valor.strip().lower()
        val = _remove_accents(val)
        val = re.sub(r"[\.,]", "", val)
        val = re.sub(r"\s+", " ", val)
        if not val.startswith("bogota"):
            raise UbicacionNoBogotaException(
                f"Location not in Bogotá: {valor}", reason="RB-001", context={"value": valor}
            )
        return val
