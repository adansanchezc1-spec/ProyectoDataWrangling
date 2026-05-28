"""DTO: DatasetDTO"""
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class DatasetDTO:
    id: str
    source_path: str
    format: str
    schema: Dict
    preview: List[Dict]
