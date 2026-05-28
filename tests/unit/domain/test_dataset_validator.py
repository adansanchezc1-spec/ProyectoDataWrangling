import pytest

from domain.validators.dataset_validator import DatasetValidator
from domain.exceptions import CoherenciaDatosException, UbicacionNoBogotaException


def test_validar_estrato_valid():
    assert DatasetValidator.validar_estrato(1) == 1
    assert DatasetValidator.validar_estrato("6") == 6


@pytest.mark.parametrize("bad", ["a", None, 0, 7])
def test_validar_estrato_invalid(bad):
    with pytest.raises(CoherenciaDatosException):
        DatasetValidator.validar_estrato(bad)


def test_validar_ubicacion_valid_and_normalized():
    val = "Bogotá, Centro"
    norm = DatasetValidator.validar_ubicacion(val)
    assert norm.startswith("bogota")


def test_validar_ubicacion_invalid():
    with pytest.raises(UbicacionNoBogotaException):
        DatasetValidator.validar_ubicacion("Medellin")
