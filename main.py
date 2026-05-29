import os
import tkinter as tk
from tkinter import Toplevel
from typing import Any, Callable, Optional
from dotenv import load_dotenv

from infrastructure.repositories.repository_factory import RepositoryFactory
from application.services.pipeline_facade import PipelineFacade
from presentation.controllers.dataset_controller import DatasetController
from presentation.views.view_load_dataset import VistaCargaDataset
from presentation.views.view_pipeline_status import VistaEstadoPipeline
from presentation.views.view_result import VistaResultado

from infrastructure.notifications.email_service import EmailService, FileLoggerEmailService
from infrastructure.notifications.email_decorators import (
    ValidacionEmailDecorator,
    NotificacionInsercionDecorator,
)

def main():
    load_dotenv()
    repo = RepositoryFactory.create_default()

    smtp_user = os.environ.get("SMTP_USERNAME", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))

    if smtp_user and smtp_pass:
        base_email = EmailService(
            host=smtp_host, port=smtp_port,
            username=smtp_user, password=smtp_pass,
        )
    else:
        print("SMTP_USERNAME/SMTP_PASSWORD no definidas. Los correos se guardan en data/EMAILS/")
        base_email = FileLoggerEmailService(email_dir="data/EMAILS")

    email_service = ValidacionEmailDecorator(
        NotificacionInsercionDecorator(base_email)
    )

    facade = PipelineFacade(repo, email_service=email_service)
    controller = DatasetController(facade)

    root = tk.Tk()
    load_view = VistaCargaDataset(root)

    status_win = Toplevel(root)
    status_view = VistaEstadoPipeline(status_win)
    status_win.withdraw()

    result_win = Toplevel(root)
    result_view = VistaResultado(result_win)
    result_win.withdraw()

    # Wire: when user requests processing, call controller
    load_view.on_process_requested = controller.upload_and_process_dataset

    def ui(callback: Callable[[dict[str, Any]], None]):
        return lambda data: root.after(0, lambda: callback(data or {}))

    def show_status_window() -> None:
        status_win.deiconify()
        status_win.lift()
        status_win.focus_force()

    def show_result_window() -> None:
        result_win.deiconify()
        result_win.lift()
        result_win.focus_force()

    def on_pipeline_started(data: dict[str, Any]) -> None:
        show_status_window()
        load_view.set_processing(True)
        status_view.add_info_line(f"Started: {data.get('file_paths', [])}")

    def on_pipeline_progress(data: dict[str, Any]) -> None:
        show_status_window()
        status_view.add_info_line(data.get("message", "Procesando dataset..."))

    def on_pipeline_completed(result: dict[str, Any]) -> None:
        load_view.set_processing(False)
        show_result_window()
        result_view.show_result(result)
        status_view.update_pipeline_result(result)

        status = result.get("status")
        if status == "success":
            mdm_path = result.get("storage_paths", {}).get("mdm", "")
            email_info = result.get("email_result", {})
            msg = f"Dataset procesado correctamente.\nMDM: {mdm_path}"
            if email_info.get("to"):
                if email_info.get("sent"):
                    msg += f"\nCorreo ENVIADO a: {email_info['to']}"
                else:
                    err = email_info.get("error", "")
                    msg += f"\nCorreo NO enviado a {email_info['to']}:\n{err}"
            load_view.show_success(msg)
        elif status == "rejected":
            rejection = result.get("rejection_log", {})
            load_view.show_error(
                "Dataset rechazado",
                rejection.get("motivo", "El dataset no cumple las reglas de calidad."),
            )
        elif status == "batch_completed":
            load_view.show_success(
                "Procesamiento multiple finalizado. Revisa la ventana de resultados."
            )
        else:
            load_view.show_error(
                "Error",
                result.get("error", "No fue posible procesar el dataset."),
            )

    def on_pipeline_error(error: dict[str, Any]) -> None:
        load_view.set_processing(False)
        show_status_window()
        status_view.add_info_line(f"ERROR: {error}")
        load_view.show_error("Error en pipeline", str(error))

    # Subscribe controller events to update views
    controller.subscribe("pipeline_started", ui(on_pipeline_started))
    controller.subscribe("pipeline_progress", ui(on_pipeline_progress))
    controller.subscribe("pipeline_completed", ui(on_pipeline_completed))
    controller.subscribe("pipeline_error", ui(on_pipeline_error))

    root.mainloop()

if __name__ == "__main__":
    main()
