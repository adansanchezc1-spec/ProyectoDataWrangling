import tkinter as tk
from typing import cast
from infrastructure.repositories.repository_factory import RepositoryFactory
from application.services.pipeline_facade import PipelineFacade
from presentation.controllers.dataset_controller import DatasetController
from presentation.views.view_load_dataset import VistaCargaDataset
from presentation.views.view_pipeline_status import VistaEstadoPipeline
from presentation.views.view_result import VistaResultado

def main():
    repo = RepositoryFactory.create_default()
    facade = PipelineFacade(repo)
    controller = DatasetController(facade)

    root = tk.Tk()
    load_view = VistaCargaDataset(root)

    status_win = tk.Toplevel(root)
    # status_win is a Toplevel window. Cast to tk.Toplevel to match the actual
    # runtime type and keep the type checker happy.
    status_view = VistaEstadoPipeline(cast(tk.Toplevel, status_win))

    result_win = tk.Toplevel(root)
    result_view = VistaResultado(result_win)

    # Wire: when user requests processing, call controller
    load_view.on_process_requested = controller.upload_and_process_dataset

    def ui(callback):
        return lambda data: root.after(0, lambda: callback(data or {}))

    # Subscribe controller events to update views
    controller.subscribe(
        "pipeline_started",
        ui(lambda d: status_view.add_info_line(f"Started: {d.get('file_paths', [])}")),
    )
    controller.subscribe(
        "pipeline_progress",
        ui(lambda d: status_view.add_info_line(d.get("message", ""))),
    )
    controller.subscribe("pipeline_completed", ui(result_view.show_result))
    controller.subscribe(
        "pipeline_error",
        ui(lambda err: status_view.add_info_line(f"ERROR: {err}")),
    )

    root.mainloop()

if __name__ == "__main__":
    main()
