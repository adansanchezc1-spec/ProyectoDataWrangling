"""Application Service: PipelineFacade - Orquestador del Pipeline BPMN.

Implementa el flujo ETL exacto con 4 gateways XOR según requisitos:

BPMN Flow:
  Origen Datos → RAW → EXTRACTING → [GATEWAY 1] → VALIDATING → [GATEWAY 2]
  → TRANSFORMING → [GATEWAY 3] → CLEANING → PROFILING → [GATEWAY 4]
  → QUALITY_GATE → MDM_LOADED → NOTIFIED

Gateways XOR:
  1. ¿Extracción completa? → Si/No
  2. ¿Formato válido? → Si/No (RF-003, RB-004)
  3. ¿Transformación completa? → Si/No
  4. ¿Calidad aceptable? → Si/No (RF-007, RF-008)
"""
from typing import Dict, Any, List, Optional, Tuple
from uuid import uuid4

from domain.entities import Dataset, CleaningReport, RejectionLog
from domain.interfaces import IDataRepository, IEmailService
from domain.enums import DatasetStatus
from domain.exceptions import (
    ExtraccionIncompletaException,
    FormatoInvalidoException,
    TransformacionFallidaException,
    CalidadInsuficienteException,
    DominioException,
)
from domain.validators import DatasetValidator, QualityValidator

from application.services.ingestion_service import IngestionService
from application.services.cleaning_service import CleaningService
from infrastructure.mdm.mdm_service import MDMService
from infrastructure.cleaning.null_cleaner import NullCleaner
from infrastructure.cleaning.format_cleaner import FormatCleaner
from infrastructure.cleaning.duplicate_cleaner import DuplicateCleaner
from infrastructure.notifications.notification_service import NotificationService
from infrastructure.repositories.folder_storage import FolderStorage
from infrastructure.analytics.feature_analyzer import FeatureAnalyzer


class PipelineFacade:
    """Fachada que orquesta el pipeline ETL completo.

    Coordina todos los servicios y ejecuta el flujo BPMN
    con gestión de gateways y manejo de rechazos.

    Attributes:
        ingestion_service: Servicio de ingesta
        cleaning_service: Servicio de limpieza
        mdm_service: Servicio de persistencia
        repository: Repositorio para entidades
        notification_service: Servicio de notificaciones
        email_service: Servicio de correos
    """

    def __init__(
        self,
        repository: IDataRepository,
        email_service: Optional[IEmailService] = None,
        folder_storage: Optional[FolderStorage] = None,
    ) -> None:
        """Inicializa el pipeline.

        Args:
            repository: Repositorio para persistencia
            email_service: Servicio de correos (opcional)
        """
        self.repository = repository
        self.email_service = email_service
        self.folder_storage = folder_storage or FolderStorage()

        # Inicializa servicios
        self.ingestion_service = IngestionService()
        self.cleaning_service = self._configure_cleaning_service()
        self.mdm_service = MDMService(repository, self.folder_storage)
        self.notification_service = NotificationService()

    def run_pipeline(
        self,
        file_path: str,
        user_email: str = "",
        year: int = 0,
        price_factor: float = 1.0,
    ) -> Dict[str, Any]:
        """Ejecuta el pipeline ETL completo.

        Flujo:
        1. INGESTION (Gateway 1: ¿Extracción completa?)
        2. VALIDATION (Gateway 2: ¿Formato válido?)
        3. CLEANING (Gateway 3: ¿Transformación completa?)
        4. QUALITY_GATE (Gateway 4: ¿Calidad aceptable?)
        5. MDM_LOADED
        6. NOTIFIED

        Args:
            file_path: Ruta al archivo a procesar
            user_email: Email del usuario para notificación
            year: Año del dataset

        Returns:
            Dict con resultado del pipeline

        Ejemplo:
            {
                "status": "success",
                "dataset_id": "...",
                "total_records": 150,
                "records_cleaned": 145,
                "mdm_url": "..."
            }
        """
        rejection_logs: List[RejectionLog] = []
        dataset: Optional[Dataset] = None
        cleaning_report: Optional[CleaningReport] = None

        try:
            # ========== STAGE 1: INGESTION ==========
            dataset = self._stage_ingestion(file_path)
            if user_email:
                dataset.user_email = user_email
            if year:
                dataset.year = year
            raw_path = self.folder_storage.persist_raw(dataset)

            # ========== GATEWAY 1: ¿Extracción completa? ==========
            if not self._gateway_1_extraction_complete(dataset):
                return self._handle_rejection(
                    dataset,
                    RejectionLog(
                        id=str(uuid4())[:8],
                        dataset_id=dataset.id,
                        motivo="Extracción incompleta: revisar archivo",
                        gateway_bpmn=1,
                        regla_negocio="RF-003",
                    ),
                )

            # ========== STAGE 2: VALIDATION ==========
            dataset = self._stage_validation(dataset)

            # ========== GATEWAY 2: ¿Formato válido? ==========
            try:
                self._gateway_2_format_valid(dataset)
            except (FormatoInvalidoException, DominioException) as e:
                return self._handle_rejection(
                    dataset,
                    RejectionLog(
                        id=str(uuid4())[:8],
                        dataset_id=dataset.id,
                        motivo=str(e),
                        gateway_bpmn=2,
                        regla_negocio="RB-004",
                    ),
                )

            # ========== STAGE 3: TRANSFORMATION/CLEANING ==========
            dataset, cleaning_report = self._stage_cleaning(dataset)
            cleaned_path = self.folder_storage.persist_cleaned(dataset)

            # ========== GATEWAY 3: ¿Transformación completa? ==========
            if not self._gateway_3_transformation_complete(dataset, cleaning_report):
                return self._handle_rejection(
                    dataset,
                    RejectionLog(
                        id=str(uuid4())[:8],
                        dataset_id=dataset.id,
                        motivo="Transformación incompleta: muy pocas filas válidas",
                        gateway_bpmn=3,
                        regla_negocio="RF-005",
                    ),
                )

            # ========== STAGE 4: PROFILING & QUALITY GATE ==========
            dataset = self._stage_profiling(dataset, price_factor=price_factor)

            # ========== GATEWAY 4: ¿Calidad aceptable? ==========
            try:
                self._gateway_4_quality_acceptable(dataset)
            except (CalidadInsuficienteException, DominioException) as e:
                return self._handle_rejection(
                    dataset,
                    RejectionLog(
                        id=str(uuid4())[:8],
                        dataset_id=dataset.id,
                        motivo=str(e),
                        gateway_bpmn=4,
                        regla_negocio="RF-007/RF-008",
                    ),
                )

            # ========== STAGE 5: MDM LOADING ==========
            mdm_result = self._stage_mdm_loading(dataset)

            # ========== STAGE 6: NOTIFICATION ==========
            email_result = self._stage_notification(dataset, cleaning_report)

            # Resultado final
            return {
                "status": "success",
                "dataset_id": dataset.id,
                "total_records": dataset.total_rows,
                "records_cleaned": dataset.total_rows,
                "cleaning_report": cleaning_report.to_dict() if cleaning_report else None,
                "mdm_summary": mdm_result,
                "email_result": email_result,
                "pipeline_status": dataset.status,
                "storage_paths": {
                    "raw": str(raw_path),
                    "cleaned": str(cleaned_path),
                    "mdm": mdm_result.get("master_dataset_path"),
                },
            }

        except DominioException as e:
            gateway = e.gateway_bpmn or 0
            return self._handle_rejection(
                dataset,
                RejectionLog(
                    id=str(uuid4())[:8],
                    dataset_id=dataset.id if dataset else "unknown",
                    motivo=str(e),
                    gateway_bpmn=gateway,
                    regla_negocio=e.reason or "N/A",
                    detalles=e.context,
                ),
            )
        except Exception as e:
            return {
                "status": "error",
                "dataset_id": dataset.id if dataset else None,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    # ========== STAGES ==========

    def _stage_ingestion(self, file_path: str) -> Dataset:
        """Stage 1: Ingesta de datos desde archivo.

        Transición: RAW → EXTRACTING

        Args:
            file_path: Ruta al archivo

        Returns:
            Dataset cargado

        Raises:
            ExtraccionIncompletaException: Si ingesta falla (Gateway 1)
        """
        dataset = self.ingestion_service.load(file_path)
        dataset.status = DatasetStatus.EXTRACTING.value
        self.notification_service.notify_all(
            "stage_ingestion_started",
            {"dataset_id": dataset.id, "source_file": file_path},
        )
        return dataset

    def _stage_validation(self, dataset: Dataset) -> Dataset:
        """Stage 2: Validación de estructura.

        Transición: EXTRACTING → VALIDATING

        Args:
            dataset: Dataset a validar

        Returns:
            Dataset con estado actualizado
        """
        dataset.validar_estructura()  # Valida columnas requeridas
        dataset.status = DatasetStatus.VALIDATING.value
        self.notification_service.notify_all(
            "stage_validation_started",
            {"dataset_id": dataset.id},
        )
        return dataset

    def _stage_cleaning(self, dataset: Dataset) -> Tuple[Dataset, CleaningReport]:
        """Stage 3: Limpieza y transformación.

        Transición: VALIDATING → TRANSFORMING → CLEANING

        Args:
            dataset: Dataset a limpiar

        Returns:
            Tupla (dataset_limpiado, cleaning_report)
        """
        dataset.status = DatasetStatus.TRANSFORMING.value
        dataset, cleaning_report = self.cleaning_service.run(dataset)
        self.notification_service.notify_all(
            "stage_cleaning_completed",
            {
                "dataset_id": dataset.id,
                "records_before": cleaning_report.registros_procesados,
                "records_after": dataset.total_rows,
            },
        )
        return dataset, cleaning_report

    def _stage_profiling(self, dataset: Dataset, price_factor: float = 1.0) -> Dataset:
        """Stage 4: Perfilado y análisis.

        Transición: CLEANING → PROFILING → QUALITY_GATE

        Args:
            dataset: Dataset a perfilar
            price_factor: Factor multiplicador del precio unitario

        Returns:
            Dataset con estado actualizado
        """
        dataset.status = DatasetStatus.PROFILING.value
        analyzer = FeatureAnalyzer()
        analysis = analyzer.analyze(dataset, price_factor=price_factor)
        dataset.metadata["feature_analysis"] = {
            "features": analysis["features"],
            "stats": analysis["stats"],
        }
        if analysis.get("enriched_records"):
            dataset.records = analysis["enriched_records"]
        dataset.status = DatasetStatus.QUALITY_GATE.value
        return dataset

    def _stage_mdm_loading(self, dataset: Dataset) -> Dict[str, Any]:
        """Stage 5: Carga en MDM.

        Transición: QUALITY_GATE → MDM_LOADED

        Args:
            dataset: Dataset a persistir

        Returns:
            Resumen de carga
        """
        result = self.mdm_service.load_to_mdm(dataset)
        self.notification_service.notify_all(
            "stage_mdm_loaded",
            {"dataset_id": dataset.id, "records": dataset.total_rows},
        )
        return result

    def _stage_notification(self, dataset: Dataset, cleaning_report: Optional[CleaningReport]) -> Dict[str, Any]:
        """Stage 6: Notificación final.

        Transición: MDM_LOADED → NOTIFIED

        Args:
            dataset: Dataset procesado
            cleaning_report: Reporte de limpieza

        Returns:
            Dict con resultado de la notificación
        """
        dataset.status = DatasetStatus.NOTIFIED.value
        email_result = {"sent": False, "to": "", "error": ""}

        if self.email_service and dataset.user_email:
            try:
                subject = f"Dataset {dataset.id} procesado exitosamente"
                body = (
                    f"El dataset ha sido procesado:\n"
                    f"- ID: {dataset.id}\n"
                    f"- Records: {dataset.total_rows}\n"
                    f"- Status: {dataset.status}\n"
                    f"- Archivo: {dataset.source_path}\n"
                    f"- Año: {dataset.year}\n"
                    f"\nResumen de limpieza:\n"
                    f"{cleaning_report.generar_resumen() if cleaning_report else 'N/A'}\n"
                )
                self.email_service.send(subject, body, dataset.user_email)
                email_result = {"sent": True, "to": dataset.user_email, "error": ""}
            except Exception as e:
                email_result = {"sent": False, "to": dataset.user_email, "error": str(e)}

        self.notification_service.notify_all(
            "stage_notification_sent",
            {"dataset_id": dataset.id, "email": email_result},
        )
        return email_result

    # ========== GATEWAYS ==========

    def _gateway_1_extraction_complete(self, dataset: Dataset) -> bool:
        """Gateway 1: ¿Extracción completa?

        Verifica que se hayan extraído datos válidos.

        Args:
            dataset: Dataset extraído

        Returns:
            True si extracción es satisfactoria
        """
        if not dataset.rows_preview or dataset.total_rows == 0:
            return False
        return True

    def _gateway_2_format_valid(self, dataset: Dataset) -> bool:
        """Gateway 2: ¿Formato válido?

        Valida formato y ubicación según RB-001, RB-004.

        Args:
            dataset: Dataset a validar

        Returns:
            True si formato es válido

        Raises:
            FormatoInvalidoException: Si formato no soportado
        """
        # Valida que sea Bogotá (RB-001)
        if not dataset.es_bogota():
            raise FormatoInvalidoException(
                "Dataset is not from Bogotá",
                reason="RB-001",
                context={"dataset_id": dataset.id},
                gateway_bpmn=2,
            )

        return True

    def _gateway_3_transformation_complete(
        self, dataset: Dataset, cleaning_report: CleaningReport
    ) -> bool:
        """Gateway 3: ¿Transformación completa?

        Valida que haya suficientes filas después de limpieza.

        Args:
            dataset: Dataset limpiado
            cleaning_report: Reporte de limpieza

        Returns:
            True si transformación fue satisfactoria
        """
        # Requiere al menos 50% de las filas originales
        min_ratio = 0.5
        ratio = dataset.total_rows / cleaning_report.registros_procesados
        return ratio >= min_ratio

    def _gateway_4_quality_acceptable(self, dataset: Dataset) -> bool:
        """Gateway 4: ¿Calidad aceptable?

        Valida coherencia semántica e integridad según RB-005, RF-007, RF-008.

        Args:
            dataset: Dataset a evaluar

        Returns:
            True si calidad es aceptable

        Raises:
            CalidadInsuficienteException: Si calidad no cumple
        """
        try:
            # Valida integridad y coherencia
            rows = dataset.records if dataset.records else dataset.rows_preview
            QualityValidator.validar_integridad(rows, min_cobertura=0.8)
            return True
        except DominioException as e:
            raise CalidadInsuficienteException(
                str(e),
                reason="RF-008",
                context={"dataset_id": dataset.id},
                gateway_bpmn=4,
            )

    # ========== HELPERS ==========

    def _handle_rejection(
        self, dataset: Dataset | None, rejection_log: RejectionLog
    ) -> Dict[str, Any]:
        """Maneja rechazo en gateway.

        Args:
            dataset: Dataset rechazado
            rejection_log: Log de rechazo

        Returns:
            Respuesta de pipeline rechazado
        """
        if dataset:
            dataset.status = DatasetStatus.REJECTED.value
        rejection_path = self.folder_storage.persist_rejection(rejection_log)

        self.notification_service.notify_all(
            "gateway_rejected",
            {
                "dataset_id": dataset.id if dataset else None,
                "gateway": rejection_log.gateway_bpmn,
                "reason": rejection_log.motivo,
            },
        )

        return {
            "status": "rejected",
            "dataset_id": dataset.id if dataset else None,
            "rejection_log": rejection_log.to_dict(),
            "gateway_bpmn": rejection_log.gateway_bpmn,
            "rejection_path": str(rejection_path),
        }

    def _configure_cleaning_service(self) -> CleaningService:
        """Configura el servicio de limpieza con estrategias.

        Returns:
            CleaningService con NullCleaner, FormatCleaner, DuplicateCleaner
        """
        service = CleaningService()

        # Orden importa: null → format → duplicate
        service.register_cleaner(
            NullCleaner(required_fields=Dataset.REQUIRED_COLUMNS)
        )

        format_rules = FormatCleaner.crear_rules_inmobiliarias()
        service.register_cleaner(FormatCleaner(rules=format_rules))

        service.register_cleaner(
            DuplicateCleaner(key_fields=["ubicacion", "tamano_m2", "habitaciones"])
        )

        return service
