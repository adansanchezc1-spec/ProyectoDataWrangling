"""Tkinter view for loading one or more datasets."""
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable, Optional


class VistaCargaDataset:
    """Dataset loading screen."""

    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title("Data Wrangling - Carga de Dataset")
        self.master.geometry("640x640")

        self.selected_file: Optional[str] = None
        self.selected_files: list[str] = []
        self.on_process_requested: Optional[Callable[[list[str], str, int, float], None]] = None

        self._create_widgets()

    def _create_widgets(self) -> None:
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(
            main_frame,
            text="Cargar Datasets Inmobiliarios",
            font=("Helvetica", 16, "bold"),
        )
        title.pack(pady=20)

        desc = ttk.Label(
            main_frame,
            text=(
                "Selecciona uno o varios archivos CSV, Excel o JSON "
                "con datos inmobiliarios de Bogota"
            ),
            wraplength=460,
            justify=tk.CENTER,
        )
        desc.pack(pady=10)

        file_frame = ttk.LabelFrame(main_frame, text="Seleccionar Archivos", padding="10")
        file_frame.pack(fill=tk.X, pady=20)

        self.btn_browse = ttk.Button(
            file_frame,
            text="Explorar...",
            command=self._on_browse_clicked,
        )
        self.btn_browse.pack(side=tk.LEFT, padx=10)

        self.lbl_file = ttk.Label(
            file_frame,
            text="Ningun archivo seleccionado",
            foreground="gray",
        )
        self.lbl_file.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        config_frame = ttk.LabelFrame(main_frame, text="Configuracion", padding="10")
        config_frame.pack(fill=tk.X, pady=5)

        row_idx = 0
        ttk.Label(config_frame, text="Año del dataset:").grid(row=row_idx, column=0, padx=5, pady=3, sticky=tk.W)
        self.entry_year = ttk.Entry(config_frame, width=8)
        self.entry_year.insert(0, "2024")
        self.entry_year.grid(row=row_idx, column=1, padx=5, pady=3, sticky=tk.W)

        row_idx += 1
        ttk.Label(config_frame, text="Email destino:").grid(row=row_idx, column=0, padx=5, pady=3, sticky=tk.W)
        self.entry_email = ttk.Entry(config_frame, width=40)
        self.entry_email.grid(row=row_idx, column=1, padx=5, pady=3, sticky=tk.W)
        ttk.Label(config_frame, text="Recibira el resumen", foreground="gray", font=("", 8)).grid(row=row_idx, column=2, padx=5, pady=3, sticky=tk.W)

        row_idx += 1
        ttk.Label(config_frame, text="Factor precio:").grid(row=row_idx, column=0, padx=5, pady=3, sticky=tk.W)
        self.entry_price_factor = ttk.Entry(config_frame, width=12)
        self.entry_price_factor.insert(0, "1.0")
        self.entry_price_factor.grid(row=row_idx, column=1, padx=5, pady=3, sticky=tk.W)
        ttk.Label(config_frame, text="Multiplicador del precio (ej: 1000000)", foreground="gray", font=("", 8)).grid(row=row_idx, column=2, padx=5, pady=3, sticky=tk.W)

        info_frame = ttk.LabelFrame(main_frame, text="Informacion del Archivo", padding="10")
        info_frame.pack(fill=tk.X, pady=10)

        self.txt_info = tk.Text(
            info_frame,
            height=5,
            width=60,
            state=tk.DISABLED,
            bg="#f0f0f0",
        )
        self.txt_info.pack(fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.btn_process = ttk.Button(
            button_frame,
            text="Procesar Dataset",
            command=self._on_process_clicked,
            state=tk.DISABLED,
        )
        self.btn_process.pack(side=tk.LEFT, padx=10)

        self.btn_clear = ttk.Button(
            button_frame,
            text="Limpiar Seleccion",
            command=self._on_clear_clicked,
        )
        self.btn_clear.pack(side=tk.LEFT, padx=10)

        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            mode="indeterminate",
        )
        self.progress.pack(fill=tk.X, pady=10)

        self.lbl_status = ttk.Label(
            main_frame,
            text="Listo",
            foreground="blue",
        )
        self.lbl_status.pack(pady=10)

    def _on_browse_clicked(self) -> None:
        file_paths = filedialog.askopenfilenames(
            title="Seleccionar datasets",
            filetypes=[
                ("Todos", "*.*"),
                ("CSV", "*.csv"),
                ("Excel", "*.xlsx *.xls"),
                ("JSON", "*.json"),
            ],
        )

        if file_paths:
            self.selected_files = list(file_paths)
            self.selected_file = self.selected_files[0]
            self._update_file_display()

    def _update_file_display(self) -> None:
        if not self.selected_files:
            return

        paths = [Path(file_path) for file_path in self.selected_files]
        total_size = sum(path.stat().st_size for path in paths) / (1024 * 1024)

        if len(paths) == 1:
            self.lbl_file.config(text=paths[0].name, foreground="green")
        else:
            self.lbl_file.config(text=f"{len(paths)} archivos seleccionados", foreground="green")

        names = "\n".join(f"- {path.name}" for path in paths)
        types = ", ".join(sorted({path.suffix.upper()[1:] for path in paths}))
        info_text = f"""Archivos:
{names}
Cantidad: {len(paths)}
Tamano total: {total_size:.2f} MB
Tipos: {types}
"""
        self.txt_info.config(state=tk.NORMAL)
        self.txt_info.delete(1.0, tk.END)
        self.txt_info.insert(tk.END, info_text)
        self.txt_info.config(state=tk.DISABLED)

        self.btn_process.config(state=tk.NORMAL)
        self.lbl_status.config(text="Listo para procesar", foreground="blue")

    def _on_process_clicked(self) -> None:
        if not self.selected_files:
            messagebox.showerror("Error", "Debes seleccionar un archivo primero")
            return

        email = self.entry_email.get().strip()

        try:
            year = int(self.entry_year.get().strip())
        except ValueError:
            messagebox.showerror("Error", "El año debe ser un numero valido (ej: 2024)")
            return

        try:
            price_factor = float(self.entry_price_factor.get().strip())
        except ValueError:
            messagebox.showerror("Error", "El factor precio debe ser un numero valido (ej: 1.0)")
            return

        if self.on_process_requested:
            self.lbl_status.config(text="Procesando...", foreground="orange")
            self.progress.start()
            self.btn_process.config(state=tk.DISABLED)
            self.on_process_requested(self.selected_files, email, year, price_factor)

    def _on_clear_clicked(self) -> None:
        self.selected_file = None
        self.selected_files = []
        self.lbl_file.config(text="Ningun archivo seleccionado", foreground="gray")
        self.txt_info.config(state=tk.NORMAL)
        self.txt_info.delete(1.0, tk.END)
        self.txt_info.config(state=tk.DISABLED)
        self.btn_process.config(state=tk.DISABLED)
        self.lbl_status.config(text="Listo", foreground="blue")
        self.progress.stop()
        self.progress_var.set(0)
        self.entry_email.delete(0, tk.END)
        self.entry_year.delete(0, tk.END)
        self.entry_year.insert(0, "2024")
        self.entry_price_factor.delete(0, tk.END)
        self.entry_price_factor.insert(0, "1.0")

    def show_error(self, title: str, message: str) -> None:
        self.lbl_status.config(text="Error en procesamiento", foreground="red")
        self.progress.stop()
        self.btn_process.config(state=tk.NORMAL)
        messagebox.showerror(title, message)

    def show_success(self, message: str) -> None:
        self.lbl_status.config(text="Procesamiento completado", foreground="green")
        self.progress.stop()
        self.btn_process.config(state=tk.NORMAL)
        messagebox.showinfo("Exito", message)

    def set_processing(self, is_processing: bool) -> None:
        if is_processing:
            self.progress.start()
            self.btn_process.config(state=tk.DISABLED)
            self.lbl_status.config(text="Procesando...", foreground="orange")
        else:
            self.progress.stop()
            self.btn_process.config(state=tk.NORMAL)
            self.lbl_status.config(text="Listo", foreground="blue")
