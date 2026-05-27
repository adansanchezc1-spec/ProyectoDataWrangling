"""Application service: PipelineFacade (skeleton)"""
from typing import Any


class PipelineFacade:
    def __init__(self, ingestion_service=None, cleaning_service=None, prediction_service=None, repository=None, notifier=None):
        self.ingestion = ingestion_service
        self.cleaning = cleaning_service
        self.prediction = prediction_service
        self.repository = repository
        self.notifier = notifier

    def run_pipeline(self, path: str) -> Any:
        """Orchestrate ingestion -> cleaning -> prediction. Returns a prediction object."""
        raise NotImplementedError

    def request_prediction(self, dataset_id: str, params: dict) -> Any:
        raise NotImplementedError
