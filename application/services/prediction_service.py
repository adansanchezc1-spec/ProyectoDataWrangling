"""Application service: PredictionService (skeleton)"""
from typing import Any


class PredictionService:
    def __init__(self, engine=None):
        self.engine = engine

    def predict(self, dataset: Any, params: dict) -> Any:
        """Run prediction using the injected prediction engine."""
        if self.engine is None:
            raise NotImplementedError("Prediction engine not configured")
        return self.engine.predict(dataset, params)
