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
        self.on_process_requested: Optional[Callable[[list[str], str, float], None]] = None

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
        file_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        btn_row = ttk.Frame(file_frame)
        btn_row.pack(fill=tk.X)

        self.btn_browse = ttk.Button(
            btn_row,
            text="Agregar archivos",
            command=self._on_browse_clicked,
        )
        self.btn_browse.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_remove = ttk.Button(
            btn_row,
            text="Quitar seleccionado",
            command=self._on_remove_clicked,
        )
        self.btn_remove.pack(side=tk.LEFT, padx=5)

        self.btn_clear = ttk.Button(
            btn_row,
            text="Limpiar todo",
            command=self._on_clear_clicked,
        )
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        self.lbl_file_count = ttk.Label(btn_row, text="Ningun archivo seleccionado", foreground="gray")
        self.lbl_file_count.pack(side=tk.RIGHT, padx=5)

        list_frame = ttk.Frame(file_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.lst_files = tk.Listbox(list_frame, yscrollcommand=scroll.set, height=6)
        scroll.config(command=self.lst_files.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.lst_files.pack(fill=tk.BOTH, expand=True)

        config_frame = ttk.LabelFrame(main_frame, text="Configuracion", padding="10")
        config_frame.pack(fill=tk.X, pady=5)

        row_idx = 0
        ttk.Label(config_frame, text="Email destino:").grid(row=row_idx, column=0, padx=5, pady=3, sticky=tk.W)
        self.entry_email = ttk.Entry(config_frame, width=40)
        self.entry_email.grid(row=row_idx, column=1, padx=5, pady=3, sticky=tk.W)
        ttk.Label(config_frame, text="Recibira el resumen", foreground="gray", font=("", 8)).grid(row=row_idx, column=2, padx=5, pady=3, sticky=tk.W)

        row_idx += 1
        ttk.Label(config_frame, text="Factor precio:").grid(row=row_idx, column=0, padx=5, pady=3, sticky=tk.W)
        self.entry_price_factor = ttk.Entry(config_frame, width=12)
        self.entry_price_factor.insert(0, "1000000")
        self.entry_price_factor.grid(row=row_idx, column=1, padx=5, pady=3, sticky=tk.W)
        ttk.Label(config_frame, text="Multiplicador (millones COP, default 1.000.000)", foreground="gray", font=("", 8)).grid(row=row_idx, column=2, padx=5, pady=3, sticky=tk.W)

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

        if not file_paths:
            return

        existing = set(self.selected_files)
        nuevos = [p for p in file_paths if p not in existing]
        if not nuevos:
            return

        self.selected_files.extend(nuevos)
        self.selected_file = self.selected_files[0]
        self._update_file_display()

    def _on_remove_clicked(self) -> None:
        selection = self.lst_files.curselection()
        if not selection:
            return
        index = selection[0]
        removed = self.selected_files.pop(index)
        self._update_file_display()

    def _update_file_display(self) -> None:
        self.lst_files.delete(0, tk.END)

        if not self.selected_files:
            self.lbl_file_count.config(text="Ningun archivo seleccionado", foreground="gray")
            self.btn_process.config(state=tk.DISABLED)
            self.txt_info.config(state=tk.NORMAL)
            self.txt_info.delete(1.0, tk.END)
            self.txt_info.config(state=tk.DISABLED)
            return

        paths = [Path(f) for f in self.selected_files]
        total_size = sum(p.stat().st_size for p in paths) / (1024 * 1024)

        for p in paths:
            self.lst_files.insert(tk.END, p.name)

        label = f"{len(paths)} archivos — {total_size:.2f} MB"
        self.lbl_file_count.config(text=label, foreground="green")

        types = ", ".join(sorted({p.suffix.upper()[1:] for p in paths}))
        info_text = f"Cantidad: {len(paths)}\nTamano total: {total_size:.2f} MB\nTipos: {types}"
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
            price_factor = float(self.entry_price_factor.get().strip())
        except ValueError:
            messagebox.showerror("Error", "El factor precio debe ser un numero valido (ej: 1000000)")
            return

        if self.on_process_requested:
            self.lbl_status.config(text="Procesando...", foreground="orange")
            self.progress.start()
            self.btn_process.config(state=tk.DISABLED)
            self.on_process_requested(self.selected_files, email, price_factor)

    def _on_clear_clicked(self) -> None:
        self.selected_file = None
        self.selected_files = []
        self._update_file_display()
        self.lbl_status.config(text="Listo", foreground="blue")
        self.progress.stop()
        self.progress_var.set(0)
        self.entry_email.delete(0, tk.END)
        self.entry_price_factor.delete(0, tk.END)
        self.entry_price_factor.insert(0, "1000000")

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
