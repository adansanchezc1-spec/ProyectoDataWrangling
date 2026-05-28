"""Validators for prediction results: significance and margin."""
from typing import Any

from domain.exceptions import MargenErrorExcedidoException, SignificanciaInsuficienteException


class PredictionValidator:
    @staticmethod
    def validar_margen_error(margen: Any) -> float:
        try:
            m = float(margen)
        except Exception:
            raise MargenErrorExcedidoException(
                f"Margin must be numeric, got: {margen}", reason="RB-004", context={"value": margen}
            )
        if m > 0.15:
            raise MargenErrorExcedidoException(
                f"Margin exceeds allowed threshold (0.15): {m}", reason="RB-004", context={"value": m}
            )
        return m

    @staticmethod
    def validar_significancia(p_value: Any) -> float:
        try:
            p = float(p_value)
        except Exception:
            raise SignificanciaInsuficienteException(
                f"p-value must be numeric, got: {p_value}", reason="RB-005", context={"value": p_value}
            )
        if p >= 0.05:
            raise SignificanciaInsuficienteException(
                f"p-value not significant (<0.05 required): {p}", reason="RB-005", context={"value": p}
            )
        return p
