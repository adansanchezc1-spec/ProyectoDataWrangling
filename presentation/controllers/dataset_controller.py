"""Controller: DatasetController"""

class DatasetController:
    def __init__(self, pipeline_facade):
        self.pipeline_facade = pipeline_facade

    def upload_dataset(self, path: str):
        """Handle dataset upload event from the view."""
        return self.pipeline_facade.run_pipeline(path)
