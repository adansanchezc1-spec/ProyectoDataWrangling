"""Presentation Layer: VistaResultado - Tkinter View para Resultados.

Tercera pantalla que muestra los resultados del procesamiento
con estadísticas detalladas del pipeline.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional
from datetime import datetime


class VistaResultado:
    """Vista para mostrar resultados del procesamiento del dataset.

    Widgets:
    - Título y estado general
    - Tabla de estadísticas principales
    - Árbol de gateways con resultados
    - Panel de reporte de limpieza
    - Botones de acción (Descargar, Nuevo Dataset, Exportar)
    """

    def __init__(self, master: tk.Tk) -> None:
        """Inicializa la vista.

        Args:
            master: Widget Tk padre
        """
        self.master = master
        self.master.title("Data Wrangling - Resultados")
        self.master.geometry("900x700")

        self.current_result: Optional[Dict[str, Any]] = None
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Crea los widgets de la interfaz."""
        # Frame principal
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        self.title_label = ttk.Label(
            main_frame,
            text="Resultados del Procesamiento",
            font=("Helvetica", 16, "bold"),
        )
        self.title_label.pack(pady=10)

        # Frame para estado general
        status_frame = ttk.LabelFrame(main_frame, text="Estado General", padding="10")
        status_frame.pack(fill=tk.X, pady=10)

        # Label de estado (color dinámico)
        self.lbl_status = ttk.Label(
            status_frame,
            text="Pendiente",
            font=("Helvetica", 12, "bold"),
        )
        self.lbl_status.pack(side=tk.LEFT)

        # Información rápida
        self.lbl_info = ttk.Label(status_frame, text="")
        self.lbl_info.pack(side=tk.LEFT, padx=20)

        # Frame para estadísticas principales
        stats_frame = ttk.LabelFrame(main_frame, text="Estadísticas", padding="10")
        stats_frame.pack(fill=tk.X, pady=10)

        # Crear tabla de estadísticas
        self.tree_stats = ttk.Treeview(
            stats_frame,
            columns=("Valor",),
            height=6,
        )
        self.tree_stats.heading("#0", text="Métrica")
        self.tree_stats.heading("Valor", text="Valor")
        self.tree_stats.column("#0", width=300)
        self.tree_stats.column("Valor", width=300)
        self.tree_stats.pack(fill=tk.BOTH, expand=True)

        # Frame para gateways
        gateways_frame = ttk.LabelFrame(main_frame, text="Gateways BPMN", padding="10")
        gateways_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.tree_gateways = ttk.Treeview(
            gateways_frame,
            columns=("Resultado", "Detalles"),
            height=5,
        )
        self.tree_gateways.heading("#0", text="Gateway")
        self.tree_gateways.heading("Resultado", text="Resultado")
        self.tree_gateways.heading("Detalles", text="Detalles")
        self.tree_gateways.column("#0", width=150)
        self.tree_gateways.column("Resultado", width=100)
        self.tree_gateways.column("Detalles", width=350)
        self.tree_gateways.pack(fill=tk.BOTH, expand=True)

        # Frame para reporte de limpieza
        report_frame = ttk.LabelFrame(main_frame, text="Reporte de Limpieza", padding="10")
        report_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.txt_report = tk.Text(
            report_frame,
            height=6,
            width=80,
            state=tk.DISABLED,
            bg="#f0f0f0",
        )
        self.txt_report.pack(fill=tk.BOTH, expand=True)

        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.btn_download = ttk.Button(
            button_frame,
            text="Descargar",
            state=tk.DISABLED,
        )
        self.btn_download.pack(side=tk.LEFT, padx=5)

        self.btn_export = ttk.Button(
            button_frame,
            text="Exportar Reporte",
            state=tk.DISABLED,
        )
        self.btn_export.pack(side=tk.LEFT, padx=5)

        self.btn_new_dataset = ttk.Button(
            button_frame,
            text="Nuevo Dataset",
            command=self._on_new_dataset_clicked,
        )
        self.btn_new_dataset.pack(side=tk.LEFT, padx=5)

        self.btn_close = ttk.Button(
            button_frame,
            text="Cerrar",
            command=self._on_close_clicked,
        )
        self.btn_close.pack(side=tk.RIGHT, padx=5)

    def show_result(self, result: Dict[str, Any]) -> None:
        """Muestra el resultado del procesamiento.

        Args:
            result: Dict con resultado del pipeline
        """
        self.current_result = result

        if result.get("status") == "success":
            self._show_success_result(result)
        elif result.get("status") == "rejected":
            self._show_rejection_result(result)
        else:
            self._show_error_result(result)

    def _show_success_result(self, result: Dict[str, Any]) -> None:
        """Muestra resultado exitoso.

        Args:
            result: Resultado del pipeline
        """
        # Actualiza título
        self.title_label.config(text="✓ Procesamiento Completado Exitosamente")

        # Actualiza estado
        self.lbl_status.config(text="✓ ÉXITO", foreground="green")
        self.lbl_info.config(
            text=f"Dataset {result.get('dataset_id')} cargado en MDM"
        )

        # Limpia tablas
        for item in self.tree_stats.get_children():
            self.tree_stats.delete(item)
        for item in self.tree_gateways.get_children():
            self.tree_gateways.delete(item)

        # Añade estadísticas
        stats = {
            "Dataset ID": result.get("dataset_id"),
            "Total de Registros": result.get("total_records"),
            "Registros Limpios": result.get("records_cleaned"),
            "Estado Final": result.get("pipeline_status"),
            "Procesado": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        for metric, value in stats.items():
            self.tree_stats.insert("", "end", text=metric, values=[str(value)])

        # Todos los gateways pasaron
        gateways = [
            ("Gateway 1", "✓ APROBADO", "Extracción completa"),
            ("Gateway 2", "✓ APROBADO", "Formato válido"),
            ("Gateway 3", "✓ APROBADO", "Transformación completa"),
            ("Gateway 4", "✓ APROBADO", "Calidad aceptable"),
        ]

        for gateway, resultado, detalles in gateways:
            self.tree_gateways.insert("", "end", text=gateway, values=[resultado, detalles])

        # Muestra reporte de limpieza
        self._display_cleaning_report(result.get("cleaning_report"))

        # Habilita botones
        self.btn_download.config(state=tk.NORMAL)
        self.btn_export.config(state=tk.NORMAL)

    def _show_rejection_result(self, result: Dict[str, Any]) -> None:
        """Muestra resultado de rechazo.

        Args:
            result: Resultado de rechazo
        """
        self.title_label.config(text="✗ Dataset Rechazado")
        self.lbl_status.config(text="✗ RECHAZADO", foreground="red")

        rejection_log = result.get("rejection_log", {})
        gateway = result.get("gateway_bpmn", "Desconocido")

        self.lbl_info.config(
            text=f"Rechazo en Gateway {gateway}: {rejection_log.get('motivo', 'Sin detalles')}"
        )

        # Limpia tablas
        for item in self.tree_stats.get_children():
            self.tree_stats.delete(item)
        for item in self.tree_gateways.get_children():
            self.tree_gateways.delete(item)

        # Muestra detalles del rechazo
        self.tree_stats.insert(
            "",
            "end",
            text="Dataset ID",
            values=[result.get("dataset_id", "N/A")],
        )
        self.tree_stats.insert(
            "",
            "end",
            text="Motivo",
            values=[rejection_log.get("motivo", "Sin especificar")],
        )
        self.tree_stats.insert(
            "",
            "end",
            text="Regla de Negocio",
            values=[rejection_log.get("regla_negocio", "N/A")],
        )

        # Muestra gateway que rechazó
        self.tree_gateways.insert(
            "",
            "end",
            text=f"Gateway {gateway}",
            values=["✗ RECHAZO", rejection_log.get("motivo", "")],
        )

        self.txt_report.config(state=tk.NORMAL)
        self.txt_report.delete(1.0, tk.END)
        self.txt_report.insert(tk.END, "El dataset fue rechazado y no cargado en el MDM.")
        self.txt_report.config(state=tk.DISABLED)

    def _show_error_result(self, result: Dict[str, Any]) -> None:
        """Muestra resultado de error.

        Args:
            result: Resultado de error
        """
        self.title_label.config(text="✗ Error en el Procesamiento")
        self.lbl_status.config(text="✗ ERROR", foreground="red")
        self.lbl_info.config(text=result.get("error", "Error desconocido"))

        self.txt_report.config(state=tk.NORMAL)
        self.txt_report.delete(1.0, tk.END)
        self.txt_report.insert(tk.END, f"Error: {result.get('error')}\nTipo: {result.get('error_type')}")
        self.txt_report.config(state=tk.DISABLED)

    def _display_cleaning_report(self, report: Optional[Dict[str, Any]]) -> None:
        """Muestra el reporte de limpieza.

        Args:
            report: Diccionario del reporte
        """
        if not report:
            return

        self.txt_report.config(state=tk.NORMAL)
        self.txt_report.delete(1.0, tk.END)

        resumen = report.get("resumen", {})
        report_text = f"""
REPORTE DE LIMPIEZA
===================
Registros Procesados: {resumen.get('registros_procesados')}
Registros Eliminados: {resumen.get('registros_eliminados')}
Registros Finales: {resumen.get('registros_finales')}
Porcentaje Eliminación: {resumen.get('porcentaje_eliminacion'):.1f}%

Detalle:
- Nulos Removidos: {resumen.get('nulos_removidos')}
- Duplicados Removidos: {resumen.get('duplicados_removidos')}
- Pasos Ejecutados: {resumen.get('pasos_ejecutados')}
        """

        self.txt_report.insert(tk.END, report_text)
        self.txt_report.config(state=tk.DISABLED)

    def _on_new_dataset_clicked(self) -> None:
        """Maneja el clic en botón Nuevo Dataset."""
        if messagebox.askyesno("Confirmación", "¿Deseas procesar otro dataset?"):
            # Podría estar wired a cambiar de vista
            pass

    def _on_close_clicked(self) -> None:
        """Maneja el clic en botón Cerrar."""
        self.master.quit()
