import pytest

from domain.validators.prediction_validator import PredictionValidator
from domain.exceptions import MargenErrorExcedidoException, SignificanciaInsuficienteException


def test_validar_margen_error_ok():
    assert PredictionValidator.validar_margen_error(0.1) == pytest.approx(0.1)


def test_validar_margen_error_exceeds():
    with pytest.raises(MargenErrorExcedidoException):
        PredictionValidator.validar_margen_error(0.2)


def test_validar_margen_error_non_numeric():
    with pytest.raises(MargenErrorExcedidoException):
        PredictionValidator.validar_margen_error("bad")


def test_validar_significancia_ok():
    assert PredictionValidator.validar_significancia(0.01) == pytest.approx(0.01)


def test_validar_significancia_not_significant():
    with pytest.raises(SignificanciaInsuficienteException):
        PredictionValidator.validar_significancia(0.05)
