"""Domain entity: CleaningReport"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict


@dataclass
class CleaningReport:
    id: str
    dataset_id: str
    steps: List[Dict] = field(default_factory=list)
    summary: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_step(self, name: str, affected_rows: int, details: Dict):
        self.steps.append({"name": name, "affected_rows": affected_rows, "details": details})

    def generate_summary(self):
        raise NotImplementedError
