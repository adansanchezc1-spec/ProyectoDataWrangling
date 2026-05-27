"""Domain entity: Dataset"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass
class Dataset:
    id: str
    source_path: str
    format: str
    status: str
    created_at: datetime
    schema: Dict
    rows_preview: List[Dict]

    def validar_estructura(self) -> bool:
        raise NotImplementedError

    def normalizar_ubicacion(self) -> None:
        raise NotImplementedError

    def es_bogota(self) -> bool:
        raise NotImplementedError

    def to_dict(self) -> Dict:
        return self.__dict__
