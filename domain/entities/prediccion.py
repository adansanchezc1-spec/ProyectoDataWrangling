"""Domain entity: Prediccion"""
from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


@dataclass
class Prediccion:
    id: str
    solicitud_id: str
    estimated_price: float
    p_value: float
    margin: float
    confidence_interval: Tuple[float, float]
    created_at: datetime

    def es_significativa(self) -> bool:
        return self.p_value < 0.05

    def margen_aceptable(self) -> bool:
        return self.margin <= 0.15
