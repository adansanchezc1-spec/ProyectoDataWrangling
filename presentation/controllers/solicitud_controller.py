"""Controller: SolicitudController"""

class SolicitudController:
    def __init__(self, pipeline_facade):
        self.pipeline_facade = pipeline_facade

    def request_prediction(self, dataset_id: str, params: dict):
        return self.pipeline_facade.request_prediction(dataset_id, params)
