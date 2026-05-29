from statistics import mean, stdev
from typing import Any, Dict, List, Optional


class FeatureAnalyzer:
    def analyze(self, dataset, price_factor: float = 1.0) -> Dict[str, Any]:
        records = dataset.records if dataset.records else dataset.rows_preview
        if not records:
            return {"features": [], "derived": {}, "stats": {}}

        derived = self._compute_derived_features(records, price_factor)
        enriched = self._enrich_records(records, derived)
        stats = self._compute_statistics(enriched)
        return {"features": list(derived.keys()), "derived": derived, "stats": stats, "enriched_records": enriched}

    @staticmethod
    def _compute_derived_features(records: List[Dict[str, Any]], price_factor: float = 1.0) -> Dict[str, List[Optional[float]]]:
        features: Dict[str, List[Optional[float]]] = {
            "precio_unitario": [],
            "puntaje_entorno": [],
            "densidad_comercial": [],
            "bano_por_hab": [],
            "parqueadero_ratio": [],
        }
        for row in records:
            try:
                precio = _float(row.get("precio"))
                tamano = _float(row.get("tamano_m2"))
                features["precio_unitario"].append(precio / tamano * price_factor if tamano else None)
            except Exception:
                features["precio_unitario"].append(None)

            try:
                score = int(
                    _float(row.get("colegios", 0))
                    + _float(row.get("hospitales", 0))
                    + _float(row.get("parques", 0))
                )
                features["puntaje_entorno"].append(score)
            except Exception:
                features["puntaje_entorno"].append(None)

            try:
                sup = _float(row.get("grandes_superficies", 0))
                area = _float(row.get("tamano_m2"))
                features["densidad_comercial"].append(sup / area if area else None)
            except Exception:
                features["densidad_comercial"].append(None)

            try:
                banos = _float(row.get("banos", 0))
                habs = _float(row.get("habitaciones", 0))
                features["bano_por_hab"].append(banos / habs if habs else None)
            except Exception:
                features["bano_por_hab"].append(None)

            try:
                parq = _float(row.get("parqueadero", 0))
                area = _float(row.get("tamano_m2"))
                features["parqueadero_ratio"].append(parq / area if area else None)
            except Exception:
                features["parqueadero_ratio"].append(None)

        return features

    @staticmethod
    def _enrich_records(records: List[Dict[str, Any]], derived: Dict[str, List[Optional[float]]]) -> List[Dict[str, Any]]:
        enriched = []
        for i, row in enumerate(records):
            enriched_row = dict(row)
            for feat_name, feat_vals in derived.items():
                if i < len(feat_vals) and feat_vals[i] is not None:
                    enriched_row[feat_name] = feat_vals[i]
            enriched.append(enriched_row)
        return enriched

    @staticmethod
    def _compute_statistics(enriched: List[Dict[str, Any]]) -> Dict[str, Any]:
        stats = {}
        numeric_cols = [
            "precio", "tamano_m2", "habitaciones", "banos", "estrato",
            "parqueadero", "precio_unitario", "puntaje_entorno", "densidad_comercial",
            "bano_por_hab", "parqueadero_ratio",
        ]
        for col in numeric_cols:
            vals = [_float(r.get(col)) for r in enriched]
            vals = [v for v in vals if v is not None]
            if len(vals) > 1:
                stats[col] = {
                    "mean": round(mean(vals), 2),
                    "min": round(min(vals), 2),
                    "max": round(max(vals), 2),
                    "std": round(stdev(vals), 2),
                    "count": len(vals),
                }
            elif len(vals) == 1:
                stats[col] = {"mean": vals[0], "min": vals[0], "max": vals[0], "std": 0, "count": 1}
        return stats


def _float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
