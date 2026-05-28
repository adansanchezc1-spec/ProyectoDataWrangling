"""Presentation Layer: VistaCargaDataset - Tkinter View para Carga de Datasets.

Primera pantalla del sistema que permite al usuario seleccionar
y cargar un archivo de dataset.
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional, Callable
from pathlib import Path


class VistaCargaDataset:
    """Vista para carga de datasets desde archivo.

    Widgets:
    - Frame principal con título
    - Selector de archivo con botón Browse
    - Información del archivo seleccionado
    - Botón para iniciar procesamiento
    - Indicador de progreso

    Callbacks:
    - on_file_selected: Se invoca cuando el usuario selecciona un archivo
    - on_process_requested: Se invoca cuando el usuario quiere procesar
    """

    def __init__(self, master: tk.Tk) -> None:
        """Inicializa la vista.

        Args:
            master: Widget Tk padre
        """
        self.master = master
        self.master.title("Data Wrangling - Carga de Dataset")
        self.master.geometry("600x400")

        self.selected_file: Optional[str] = None
        self.on_process_requested: Optional[Callable[[str], None]] = None

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Crea los widgets de la interfaz."""
        # Frame principal
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title = ttk.Label(
            main_frame,
            text="Cargar Dataset Inmobiliario",
            font=("Helvetica", 16, "bold"),
        )
        title.pack(pady=20)

        # Descripción
        desc = ttk.Label(
            main_frame,
            text="Selecciona un archivo CSV, Excel o JSON con datos inmobiliarios de Bogotá",
            wraplength=400,
            justify=tk.CENTER,
        )
        desc.pack(pady=10)

        # Frame para selección de archivo
        file_frame = ttk.LabelFrame(main_frame, text="Seleccionar Archivo", padding="10")
        file_frame.pack(fill=tk.X, pady=20)

        # Botón Browse
        self.btn_browse = ttk.Button(
            file_frame,
            text="Explorar...",
            command=self._on_browse_clicked,
        )
        self.btn_browse.pack(side=tk.LEFT, padx=10)

        # Label para mostrar archivo seleccionado
        self.lbl_file = ttk.Label(
            file_frame,
            text="Ningún archivo seleccionado",
            foreground="gray",
        )
        self.lbl_file.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Frame para información del archivo
        info_frame = ttk.LabelFrame(main_frame, text="Información del Archivo", padding="10")
        info_frame.pack(fill=tk.X, pady=20)

        # Información (será actualizado al seleccionar archivo)
        self.txt_info = tk.Text(
            info_frame,
            height=6,
            width=60,
            state=tk.DISABLED,
            bg="#f0f0f0",
        )
        self.txt_info.pack(fill=tk.BOTH, expand=True)

        # Frame para botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)

        # Botón Procesar
        self.btn_process = ttk.Button(
            button_frame,
            text="Procesar Dataset",
            command=self._on_process_clicked,
            state=tk.DISABLED,
        )
        self.btn_process.pack(side=tk.LEFT, padx=10)

        # Botón Limpiar
        self.btn_clear = ttk.Button(
            button_frame,
            text="Limpiar Selección",
            command=self._on_clear_clicked,
        )
        self.btn_clear.pack(side=tk.LEFT, padx=10)

        # Indicador de progreso
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            mode="indeterminate",
        )
        self.progress.pack(fill=tk.X, pady=10)

        # Label de estado
        self.lbl_status = ttk.Label(
            main_frame,
            text="Listo",
            foreground="blue",
        )
        self.lbl_status.pack(pady=10)

    def _on_browse_clicked(self) -> None:
        """Maneja el clic en botón Browse."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar dataset",
            filetypes=[
                ("Todos", "*.*"),
                ("CSV", "*.csv"),
                ("Excel", "*.xlsx *.xls"),
                ("JSON", "*.json"),
            ],
        )

        if file_path:
            self.selected_file = file_path
            self._update_file_display()

    def _update_file_display(self) -> None:
        """Actualiza la visualización del archivo seleccionado."""
        if not self.selected_file:
            return

        path = Path(self.selected_file)
        file_size = path.stat().st_size / (1024 * 1024)  # En MB

        # Actualiza label
        self.lbl_file.config(text=path.name, foreground="green")

        # Actualiza información
        info_text = f"""Archivo: {path.name}
Ruta: {self.selected_file}
Tamaño: {file_size:.2f} MB
Tipo: {path.suffix.upper()[1:]}
        """
        self.txt_info.config(state=tk.NORMAL)
        self.txt_info.delete(1.0, tk.END)
        self.txt_info.insert(tk.END, info_text)
        self.txt_info.config(state=tk.DISABLED)

        # Habilita botón Procesar
        self.btn_process.config(state=tk.NORMAL)

        # Actualiza estado
        self.lbl_status.config(text="Listo para procesar", foreground="blue")

    def _on_process_clicked(self) -> None:
        """Maneja el clic en botón Procesar."""
        if not self.selected_file:
            messagebox.showerror("Error", "Debes seleccionar un archivo primero")
            return

        if self.on_process_requested:
            self.lbl_status.config(text="Procesando...", foreground="orange")
            self.progress.start()
            self.btn_process.config(state=tk.DISABLED)
            self.on_process_requested(self.selected_file)

    def _on_clear_clicked(self) -> None:
        """Maneja el clic en botón Limpiar."""
        self.selected_file = None
        self.lbl_file.config(text="Ningún archivo seleccionado", foreground="gray")
        self.txt_info.config(state=tk.NORMAL)
        self.txt_info.delete(1.0, tk.END)
        self.txt_info.config(state=tk.DISABLED)
        self.btn_process.config(state=tk.DISABLED)
        self.lbl_status.config(text="Listo", foreground="blue")
        self.progress.stop()
        self.progress_var.set(0)

    def show_error(self, title: str, message: str) -> None:
        """Muestra un diálogo de error.

        Args:
            title: Título del error
            message: Mensaje de error
        """
        self.lbl_status.config(text="Error en procesamiento", foreground="red")
        self.progress.stop()
        self.btn_process.config(state=tk.NORMAL)
        messagebox.showerror(title, message)

    def show_success(self, message: str) -> None:
        """Muestra un diálogo de éxito.

        Args:
            message: Mensaje de éxito
        """
        self.lbl_status.config(text="Procesamiento completado", foreground="green")
        self.progress.stop()
        self.btn_process.config(state=tk.NORMAL)
        messagebox.showinfo("Éxito", message)

    def set_processing(self, is_processing: bool) -> None:
        """Establece el estado de procesamiento.

        Args:
            is_processing: True si está procesando
        """
        if is_processing:
            self.progress.start()
            self.btn_process.config(state=tk.DISABLED)
            self.lbl_status.config(text="Procesando...", foreground="orange")
        else:
            self.progress.stop()
            self.btn_process.config(state=tk.NORMAL)
            self.lbl_status.config(text="Listo", foreground="blue")
