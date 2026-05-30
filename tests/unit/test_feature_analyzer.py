from datetime import datetime
from unittest.mock import MagicMock

from infrastructure.analytics.feature_analyzer import FeatureAnalyzer


DEFAULT_RECORDS = [
    {"precio": 200000000.0, "tamano_m2": 50.0, "habitaciones": 3, "banos": 2,
     "estrato": 4, "parqueadero": 1, "colegios": 2, "hospitales": 1, "parques": 1,
     "grandes_superficies": 0},
]


def _dataset(records=None):
    ds = MagicMock()
    ds.records = DEFAULT_RECORDS if records is None else records
    ds.rows_preview = []
    return ds


def test_basic_analysis():
    analyzer = FeatureAnalyzer()
    result = analyzer.analyze(_dataset())
    assert "features" in result
    assert "precio_unitario" in result["features"]
    assert "stats" in result
    assert result["enriched_records"] is not None


def test_price_factor_scales_precio_unitario():
    records = [{"precio": 100.0, "tamano_m2": 10.0}]
    analyzer = FeatureAnalyzer()
    result_1x = analyzer.analyze(_dataset(records), price_factor=1.0)
    result_1k = analyzer.analyze(_dataset(records), price_factor=1000.0)
    pu_1x = result_1x["derived"]["precio_unitario"][0]
    pu_1k = result_1k["derived"]["precio_unitario"][0]
    assert pu_1x == 10.0
    assert pu_1k == 10000.0


def test_price_factor_default_is_one():
    records = [{"precio": 50.0, "tamano_m2": 5.0}]
    analyzer = FeatureAnalyzer()
    result = analyzer.analyze(_dataset(records))
    assert result["derived"]["precio_unitario"][0] == 10.0


def test_empty_records():
    analyzer = FeatureAnalyzer()
    result = analyzer.analyze(_dataset([]))
    assert result["features"] == []
    assert result["stats"] == {}


def test_missing_values():
    records = [{"precio": None, "tamano_m2": None, "habitaciones": None, "banos": None,
                "estrato": None, "parqueadero": None}]
    analyzer = FeatureAnalyzer()
    result = analyzer.analyze(_dataset(records))
    assert result["features"] == [
        "precio_unitario", "puntaje_entorno", "densidad_comercial",
        "bano_por_hab", "parqueadero_ratio",
    ]
    for vals in result["derived"].values():
        assert vals[0] is None or vals[0] == 0.0


def test_statistics_computed():
    records = [
        {"precio": 100.0, "tamano_m2": 10.0, "habitaciones": 2, "banos": 1,
         "estrato": 3, "parqueadero": 1},
        {"precio": 200.0, "tamano_m2": 20.0, "habitaciones": 3, "banos": 2,
         "estrato": 4, "parqueadero": 1},
    ]
    analyzer = FeatureAnalyzer()
    result = analyzer.analyze(_dataset(records))
    stats = result["stats"]
    assert "precio" in stats
    assert "precio_unitario" in stats
    assert stats["precio"]["mean"] == 150.0
    assert stats["precio_unitario"]["mean"] == 10.0


def test_derived_features_enriched_in_records():
    records = [{"precio": 150.0, "tamano_m2": 15.0, "habitaciones": 3, "banos": 2,
                "estrato": 4, "parqueadero": 1}]
    analyzer = FeatureAnalyzer()
    result = analyzer.analyze(_dataset(records))
    enriched = result["enriched_records"]
    assert len(enriched) == 1
    assert enriched[0]["precio_unitario"] == 10.0
    assert enriched[0]["bano_por_hab"] == 2.0 / 3.0
