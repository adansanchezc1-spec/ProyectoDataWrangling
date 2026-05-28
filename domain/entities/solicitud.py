"""Domain entity: Solicitud"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass
class Solicitud:
    id: str
    dataset_id: str
    parameters: Dict
    requested_by: str
    status: str
    created_at: datetime

    def validate_parameters(self):
        raise NotImplementedError
