"""Domain entity: RejectionLog"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RejectionLog:
    id: str
    dataset_id: str
    row_index: int
    reason_code: str
    message: str
    created_at: datetime

    def to_dict(self):
        return self.__dict__
