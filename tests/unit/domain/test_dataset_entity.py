import pytest
from datetime import datetime, timezone

from domain.entities.dataset import Dataset
from domain.exceptions import DatasetInvalidoException


def test_validar_estructura_success():
    ds = Dataset(
        id="1",
        source_path="/tmp/fake.csv",
        format="csv",
        status="new",
        created_at=datetime.now(timezone.utc),
        schema={
            "ubicacion": "str",
            "tamano_m2": "float",
            "habitaciones": "int",
            "banos": "int",
            "estrato": "int",
            "precio": "float",
        },
        rows_preview=[{"ubicacion": "Bogotá Centro", "precio": 100000}]
    )

    assert ds.validar_estructura() is True


def test_validar_estructura_missing_raises():
    ds = Dataset(
        id="2",
        source_path="/tmp/fake2.csv",
        format="csv",
        status="new",
        created_at=datetime.now(timezone.utc),
        schema={"ubicacion": "str", "precio": "float"},
        rows_preview=[],
    )

    with pytest.raises(DatasetInvalidoException):
        ds.validar_estructura()


def test_normalizar_ubicacion_and_es_bogota():
    ds = Dataset(
        id="3",
        source_path="/tmp/fake3.csv",
        format="csv",
        status="new",
        created_at=datetime.now(timezone.utc),
        rows_preview=[{"ubicacion": " Bogotá,  Cundinamarca "}, {"ubicacion": "Bogotá, Usaquén"}],
    )

    ds.normalizar_ubicacion()
    assert ds.rows_preview[0]["ubicacion"] == "bogota cundinamarca"
    assert ds.rows_preview[1]["ubicacion"] == "bogota usaquen"
    # es_bogota checks que todas las filas sean Bogotá (RB-001)
    assert ds.es_bogota() is True
