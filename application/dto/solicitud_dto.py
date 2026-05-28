"""DTO: SolicitudDTO"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class SolicitudDTO:
    id: str
    dataset_id: str
    parameters: Dict
    requested_by: str
