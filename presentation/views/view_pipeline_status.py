"""Presentation Layer: VistaEstadoPipeline - Tkinter View para Estado del Pipeline.

Segunda pantalla que muestra el progreso del pipeline en tiempo real
con información de cada etapa y gateway.
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional
from datetime import datetime


class VistaEstadoPipeline:
    """Vista para monitoreo del estado del pipeline ETL.

    Widgets:
    - Título y descripción
    - Árbol jerárquico de etapas del pipeline
    - Panel de información detallada
    - Indicador de progreso general
    - Log de eventos en tiempo real
    """

    def __init__(self, master: tk.Tk | tk.Toplevel) -> None:
        """Inicializa la vista.

        Args:
            master: Widget Tk padre
        """
        self.master = master
        self.master.title("Data Wrangling - Estado del Pipeline")
        self.master.geometry("800x600")

        self.pipeline_data: Dict[str, Any] = {}
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Crea los widgets de la interfaz."""
        # Frame principal
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title = ttk.Label(
            main_frame,
            text="Estado del Pipeline ETL",
            font=("Helvetica", 16, "bold"),
        )
        title.pack(pady=10)

        # Frame de etapas
        stages_frame = ttk.LabelFrame(main_frame, text="Etapas del Pipeline", padding="10")
        stages_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Árbol de etapas
        self.tree_stages = ttk.Treeview(
            stages_frame,
            columns=("Estado", "Detalles"),
            height=8,
        )
        self.tree_stages.heading("#0", text="Etapa")
        self.tree_stages.heading("Estado", text="Estado")
        self.tree_stages.heading("Detalles", text="Detalles")
        self.tree_stages.column("#0", width=200)
        self.tree_stages.column("Estado", width=100)
        self.tree_stages.column("Detalles", width=300)
        self.tree_stages.pack(fill=tk.BOTH, expand=True)

        # Scroll para el árbol
        scroll = ttk.Scrollbar(stages_frame, orient=tk.VERTICAL, command=self.tree_stages.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_stages.config(yscroll=scroll.set)

        # Frame para progreso general
        progress_frame = ttk.LabelFrame(main_frame, text="Progreso General", padding="10")
        progress_frame.pack(fill=tk.X, pady=10)

        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate",
        )
        self.progress.pack(fill=tk.X)

        self.lbl_progress = ttk.Label(progress_frame, text="0%")
        self.lbl_progress.pack(pady=5)

        # Frame para información detallada
        info_frame = ttk.LabelFrame(main_frame, text="Información Detallada", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.txt_info = tk.Text(
            info_frame,
            height=8,
            width=60,
            state=tk.DISABLED,
            bg="#f0f0f0",
        )
        self.txt_info.pack(fill=tk.BOTH, expand=True)

        # Scroll para el texto
        scroll_info = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.txt_info.yview)
        scroll_info.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_info.config(yscroll=scroll_info.set)

        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.btn_refresh = ttk.Button(
            button_frame,
            text="Actualizar",
            command=self._refresh_status,
        )
        self.btn_refresh.pack(side=tk.LEFT, padx=5)

        self.btn_clear = ttk.Button(
            button_frame,
            text="Limpiar",
            command=self._clear_status,
        )
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        # Inicializa árbol con etapas
        self._initialize_stages_tree()

    def _initialize_stages_tree(self) -> None:
        """Inicializa el árbol con las etapas del pipeline."""
        stages = {
            "1. Ingestion": ["Extracción", "Gateway 1: ¿Completa?"],
            "2. Validation": ["Validación", "Gateway 2: ¿Formato válido?"],
            "3. Cleaning": ["Limpieza", "Gateway 3: ¿Transformación completa?"],
            "4. Quality Gate": ["Perfilado", "Gateway 4: ¿Calidad aceptable?"],
            "5. MDM Loading": ["Persistencia", "Carga en repositorio"],
            "6. Notification": ["Notificación", "Envío de alertas"],
        }

        for stage, details in stages.items():
            stage_id = self.tree_stages.insert("", "end", text=stage, values=["Pendiente", ""])
            for detail in details:
                self.tree_stages.insert(stage_id, "end", text=detail, values=["", ""])

    def update_stage_status(self, stage: str, status: str, details: str = "") -> None:
        """Actualiza el estado de una etapa.

        Args:
            stage: Nombre de la etapa (ej: "1. Ingestion")
            status: Estado (Pendiente, En Progreso, Completado, Error)
            details: Información adicional
        """
        for item in self.tree_stages.get_children():
            if self.tree_stages.item(item)["text"] == stage:
                self.tree_stages.item(item, values=[status, details])
                break

    def update_overall_progress(self, percentage: float, message: str = "") -> None:
        """Actualiza el progreso general.

        Args:
            percentage: Porcentaje completado (0-100)
            message: Mensaje de estado
        """
        self.progress_var.set(percentage)
        self.lbl_progress.config(text=f"{percentage:.0f}%")

    def add_info_line(self, line: str) -> None:
        """Añade una línea al panel de información.

        Args:
            line: Texto a añadir
        """
        self.txt_info.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.txt_info.insert(tk.END, f"[{timestamp}] {line}\n")
        self.txt_info.see(tk.END)
        self.txt_info.config(state=tk.DISABLED)

    def update_pipeline_result(self, result: Dict[str, Any]) -> None:
        """Actualiza la vista con el resultado final del pipeline.

        Args:
            result: Dict con resultado del pipeline
        """
        self.txt_info.config(state=tk.NORMAL)
        self.txt_info.delete(1.0, tk.END)

        if result.get("status") == "success":
            info_text = f"""
RESULTADO EXITOSO
=================
Dataset ID: {result.get('dataset_id')}
Total de registros: {result.get('total_records')}
Registros limpios: {result.get('records_cleaned')}
Estado: {result.get('pipeline_status')}

Reporte de limpieza:
{result.get('cleaning_report')}
            """
            self.progress_var.set(100)
            self.lbl_progress.config(text="100%")

        else:
            info_text = f"""
ERROR EN PIPELINE
=================
Error: {result.get('error')}
Tipo: {result.get('error_type')}
Dataset ID: {result.get('dataset_id')}
            """
            self.progress_var.set(0)
            self.lbl_progress.config(text="Error")

        self.txt_info.insert(tk.END, info_text)
        self.txt_info.config(state=tk.DISABLED)

    def _refresh_status(self) -> None:
        """Maneja el clic en botón Actualizar."""
        # Podría conectarse a un backend para obtener estado actual
        pass

    def _clear_status(self) -> None:
        """Limpia la visualización de estado."""
        self.txt_info.config(state=tk.NORMAL)
        self.txt_info.delete(1.0, tk.END)
        self.txt_info.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.lbl_progress.config(text="0%")
