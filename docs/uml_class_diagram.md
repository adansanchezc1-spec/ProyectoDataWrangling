# UML Class Diagram - Sistema Data Wrangling

```mermaid
---
title: Diagrama de Clases — Sistema DataWrangling
---
classDiagram

    %% ==============================
    %%  PRESENTATION LAYER - VIEWS
    %% ==============================

    class VistaCargaDataset {
        -master: tk.Tk
        -selected_file: Optional[str]
        -selected_files: list[str]
        -on_process_requested: Optional[Callable]
        -btn_browse: ttk.Button
        -lbl_file: ttk.Label
        -entry_year: ttk.Entry
        -entry_email: ttk.Entry
        -entry_price_factor: ttk.Entry
        -txt_info: tk.Text
        -btn_process: ttk.Button
        -btn_clear: ttk.Button
        -progress_var: tk.DoubleVar
        -progress: ttk.Progressbar
        -lbl_status: ttk.Label
        +__init__(master: tk.Tk) void
        -_create_widgets() void
        -_on_browse_clicked() void
        -_update_file_display() void
        -_on_process_clicked() void
        -_on_clear_clicked() void
        +show_error(title: str, message: str) void
        +show_success(message: str) void
        +set_processing(is_processing: bool) void
    }

    class VistaEstadoPipeline {
        -master: tk.Tk | tk.Toplevel
        -pipeline_data: Dict[str, Any]
        -tree_stages: ttk.Treeview
        -progress_var: tk.DoubleVar
        -progress: ttk.Progressbar
        -lbl_progress: ttk.Label
        -txt_info: tk.Text
        -btn_refresh: ttk.Button
        -btn_clear: ttk.Button
        +__init__(master: tk.Tk | tk.Toplevel) void
        -_create_widgets() void
        -_initialize_stages_tree() void
        +update_stage_status(stage: str, status: str, details: str) void
        +update_overall_progress(percentage: float, message: str) void
        +add_info_line(line: str) void
        +update_pipeline_result(result: Dict[str, Any]) void
        -_refresh_status() void
        -_clear_status() void
    }

    class VistaResultado {
        -master: tk.Tk | tk.Toplevel
        -current_result: Optional[Dict[str, Any]]
        -title_label: ttk.Label
        -lbl_status: ttk.Label
        -lbl_info: ttk.Label
        -tree_stats: ttk.Treeview
        -tree_gateways: ttk.Treeview
        -txt_report: tk.Text
        -btn_download: ttk.Button
        -btn_export: ttk.Button
        -btn_new_dataset: ttk.Button
        -btn_close: ttk.Button
        +__init__(master: tk.Tk | tk.Toplevel) void
        -_create_widgets() void
        +show_result(result: Dict[str, Any]) void
        -_show_success_result(result: Dict[str, Any]) void
        -_show_rejection_result(result: Dict[str, Any]) void
        -_show_batch_result(result: Dict[str, Any]) void
        -_show_error_result(result: Dict[str, Any]) void
        -_display_cleaning_report(report: Optional[Dict]) void
        -_on_new_dataset_clicked() void
        -_on_close_clicked() void
    }

    %% ==============================
    %%  PRESENTATION LAYER - CONTROLLERS
    %% ==============================

    class DatasetController {
        -pipeline_facade: PipelineFacade
        -_observers: Dict[str, list[Callable]]
        +__init__(pipeline_facade: PipelineFacade) void
        +subscribe(event: str, callback: Callable) void
        -_notify_observers(event: str, data: Optional[Dict]) void
        +upload_and_process_dataset(file_path: str|list[str], user_email: str, year: int, price_factor: float) void
        -_process_dataset_background(file_paths: list[str], user_email: str, year: int, price_factor: float) void
        +get_dataset(dataset_id: str) Optional[Dict]
        +list_all_datasets() list[Dict]
        +get_pipeline_status() Dict
    }

    class SolicitudController {
        -pipeline_facade: PipelineFacade
        +__init__(pipeline_facade) void
        +request_prediction(dataset_id: str, params: dict) Any
    }

    %% ==============================
    %%  APPLICATION - SERVICES
    %% ==============================

    class PipelineFacade {
        -repository: IDataRepository
        -email_service: Optional[IEmailService]
        -folder_storage: FolderStorage
        -ingestion_service: IngestionService
        -cleaning_service: CleaningService
        -mdm_service: MDMService
        -notification_service: NotificationService
        +__init__(repository: IDataRepository, email_service: Optional[IEmailService], folder_storage: Optional[FolderStorage]) void
        +run_pipeline(file_path: str, user_email: str, year: int, price_factor: float) Dict
        -_stage_ingestion(file_path: str) Dataset
        -_stage_validation(dataset: Dataset) Dataset
        -_stage_cleaning(dataset: Dataset) Tuple[Dataset, CleaningReport]
        -_stage_profiling(dataset: Dataset, price_factor: float) Dataset
        -_stage_mdm_loading(dataset: Dataset) Dict
        -_stage_notification(dataset: Dataset, report: Optional[CleaningReport]) Dict
        -_gateway_1_extraction_complete(dataset: Dataset) bool
        -_gateway_2_format_valid(dataset: Dataset) bool
        -_gateway_3_transformation_complete(dataset: Dataset, report: CleaningReport) bool
        -_gateway_4_quality_acceptable(dataset: Dataset) bool
        -_handle_rejection(dataset: Dataset|None, log: RejectionLog) Dict
        -_configure_cleaning_service() CleaningService
    }

    class IngestionService {
        +REQUIRED_COLUMNS: list[str]
        +SOURCE_COLUMN_MAP: dict
        +UBICACION_SOURCE_COLUMNS: set
        +__init__() void
        +load(file_path: str) Dataset
        -_detect_delimiter(path: Path) str
        -_load_csv(path: Path) Tuple
        -_load_excel(path: Path) Tuple
        -_load_json(path: Path) Tuple
        -_normalize_column_name(column: Any)$ str
        -_normalizar_decimales(rows: List[Dict])$ List[Dict]
    }

    class CleaningService {
        -cleaners: List[IDataCleaner]
        +__init__(cleaners: Optional[List[IDataCleaner]]) void
        +register_cleaner(cleaner: IDataCleaner) void
        +run(dataset: Dataset) Tuple[Dataset, CleaningReport]
    }

    class PredictionService {
        -engine: Any
        +__init__(engine: Any) void
        +predict(dataset: Any, params: dict) Any
    }

    %% ==============================
    %%  APPLICATION - DTOs
    %% ==============================

    class SolicitudDTO {
        <<dataclass>>
        +id: str
        +dataset_id: str
        +parameters: Dict
        +requested_by: str
    }

    class DatasetDTO {
        <<dataclass>>
        +id: str
        +source_path: str
        +format: str
        +schema: Dict
        +preview: List[Dict]
    }

    %% ==============================
    %%  DOMAIN - ENTITIES
    %% ==============================

    class Dataset {
        <<dataclass>>
        +REQUIRED_COLUMNS: list[str]$
        +id: str
        +source_path: str
        +format: str
        +status: str
        +created_at: datetime
        +schema: Dict[str, Any]
        +rows_preview: List[Dict]
        +records: List[Dict]
        +total_rows: int
        +user_email: str
        +year: int
        +metadata: Dict[str, Any]
        +validar_estructura() bool
        +normalizar_ubicacion() void
        +es_bogota() bool
        +esta_completo() bool
        +to_dict() Dict
    }

    class CleaningReport {
        <<dataclass>>
        +id: str
        +dataset_id: str
        +registros_procesados: int
        +registros_eliminados: int
        +nulos_removidos: int
        +duplicados_removidos: int
        +steps: List[Dict]
        +created_at: datetime
        +add_step(name: str, affected_rows: int, details: Dict) void
        +generar_resumen() Dict
        +to_dict() Dict
    }

    class RejectionLog {
        <<dataclass>>
        +id: str
        +dataset_id: str
        +motivo: str
        +gateway_bpmn: int
        +regla_negocio: str
        +fecha: datetime
        +detalles: Dict[str, Any]
        +row_index: Optional[int]
        +to_dict() Dict
        +mensaje_descriptivo() str
    }

    class Solicitud {
        <<dataclass>>
        +id: str
        +dataset_id: str
        +parameters: Dict
        +requested_by: str
        +status: str
        +created_at: datetime
        +validate_parameters() void
    }

    class Prediccion {
        <<dataclass>>
        +id: str
        +solicitud_id: str
        +estimated_price: float
        +p_value: float
        +margin: float
        +confidence_interval: Tuple[float, float]
        +created_at: datetime
        +es_significativa() bool
        +margen_aceptable() bool
    }

    %% ==============================
    %%  DOMAIN - VALIDATORS
    %% ==============================

    class DatasetValidator {
        +validar_estrato(valor: Any)$ int
        +validar_ubicacion(valor: Any)$ str
        +validar_formato_archivo(filename: str)$ str
        +validar_columnas_minimas(schema: Dict, columnas: List[str])$ bool
    }

    class QualityValidator {
        +validar_consistencia_semantica(row: Dict)$ bool
        +validar_integridad(rows: List[Dict], min_cobertura: float)$ bool
    }

    class PredictionValidator {
        +validar_margen_error(margen: Any)$ float
        +validar_significancia(p_value: Any)$ float
    }

    %% ==============================
    %%  DOMAIN - INTERFACES
    %% ==============================

    class IDataRepository {
        <<interface>>
        +save(entity: Any) void*
        +get_by_id(entity_id: str) Optional[Any]*
        +list_all() Iterable[Any]*
        +update(entity: Any) void*
        +delete(entity_id: str) void*
    }

    class IEmailService {
        <<interface>>
        +send(subject: str, body: str, to: str) bool*
        +validate_email(email: str) bool*
    }

    class IDataCleaner {
        <<interface>>
        +clean(rows: List[Dict]) List[Dict]*
    }

    class IFeatureAnalyzer {
        <<interface>>
        +analyze(dataset: Any) Dict*
    }

    class INotificationObserver {
        <<interface>>
        +update(event: str, data: Dict)*
    }

    %% ==============================
    %%  DOMAIN - ENUMS
    %% ==============================

    class DatasetStatus {
        <<enum>>
        +RAW
        +EXTRACTING
        +VALIDATING
        +TRANSFORMING
        +CLEANING
        +CLEANED
        +PROFILING
        +QUALITY_GATE
        +MDM_LOADED
        +NOTIFIED
        +REJECTED
        +ERROR
    }

    class Formato {
        <<enum>>
        +CSV
        +EXCEL
        +JSON
        +es_valido(formato: str)$ bool
        +from_extension(filename: str)$ Formato
    }

    class TipoVariable {
        <<enum>>
        +NUMERIC
        +CATEGORICAL
        +TEXT
        +DATETIME
    }

    %% ==============================
    %%  DOMAIN - EXCEPTIONS
    %% ==============================

    class DominioException {
        <<exception>>
        +reason: Optional[str]
        +context: Dict
        +gateway_bpmn: Optional[int]
        +__init__(message: str, *, reason: str, context: Dict, gateway_bpmn: int) void
    }

    class DatasetInvalidoException {
        <<exception>>
    }
    class ExtraccionIncompletaException {
        <<exception>>
    }
    class FormatoInvalidoException {
        <<exception>>
    }
    class TransformacionFallidaException {
        <<exception>>
    }
    class CalidadInsuficienteException {
        <<exception>>
    }
    class UbicacionNoBogotaException {
        <<exception>>
    }
    class CoherenciaDatosException {
        <<exception>>
    }
    class SignificanciaInsuficienteException {
        <<exception>>
    }
    class MargenErrorExcedidoException {
        <<exception>>
    }
    class RepositorioException {
        <<exception>>
    }
    class NotificacionException {
        <<exception>>
    }

    %% ==============================
    %%  INFRASTRUCTURE - REPOSITORIES
    %% ==============================

    class FolderStorage {
        +MASTER_FILE: str$
        +METADATA_FILE: str$
        -base_dir: Path
        -raw_dir: Path
        -cleaned_dir: Path
        -mdm_dir: Path
        -rejected_dir: Path
        +__init__(base_dir: str) void
        -_ensure_directories() void
        +persist_raw(dataset: Dataset) Path
        +persist_cleaned(dataset: Dataset) Path
        +persist_rejection(log: RejectionLog) Path
        +append_to_master(dataset: Dataset) Path
        -_read_metadata(meta_path: Path) Dict
        -_read_existing_keys(csv_path: Path) set
        -_get_fieldnames(records: List[Dict])$ List[str]
        -_write_json(path: Path, payload: Dict) Path
        -_record_key(row: Dict)$ tuple
    }

    class JsonRepository {
        -storage_dir: Path
        +__init__(storage_dir: str) void
        -_path_for_id(entity_id: str) Path
        +save(entity: Any) void
        +get_by_id(entity_id: str) Optional[Any]
        +list_all() Iterable[Any]
        +update(entity: Any) void
        +delete(entity_id: str) void
    }

    class PandasRepository {
        +load_csv(path: str, **kwargs) Optional[object]
        +save_df_to_json(df, path: str, orient: str) void
        +to_records(df) List[Dict]
    }

    class RepositoryFactory {
        +create(repo_type: Literal["json","pandas"], **kwargs)$ IDataRepository
        +create_default()$ IDataRepository
    }

    %% ==============================
    %%  INFRASTRUCTURE - NOTIFICATIONS
    %% ==============================

    class EmailService {
        -host: str
        -port: int
        -username: Optional[str]
        -password: Optional[str]
        +__init__(host: str, port: int, username: str, password: str) void
        +send(subject: str, body: str, to: str) bool
        +validate_email(email: str) bool
    }

    class FileLoggerEmailService {
        -email_dir: Path
        +__init__(email_dir: str) void
        +send(subject: str, body: str, to: str) bool
        +validate_email(email: str) bool
    }

    class EmailDecorator {
        <<abstract>>
        -_wrapped: IEmailService
        +__init__(wrapped_service: IEmailService) void
        +send(subject: str, body: str, to: str) bool
        +validate_email(email: str) bool
    }

    class ValidacionEmailDecorator {
        +send(subject: str, body: str, to: str) bool
        -_is_valid_email(email: str)$ bool
    }

    class NotificacionInsercionDecorator {
        +send(subject: str, body: str, to: str) bool
        -_enrich_body(original_body: str)$ str
    }

    class NotificationService {
        -_observers: List[INotificationObserver]
        -_event_history: List[Dict]
        +__init__() void
        +attach_observer(observer: INotificationObserver) void
        +detach_observer(observer: INotificationObserver) void
        +notify_all(event: str, data: Optional[Dict]) void
        -_record_event(event: str, data: Dict) void
        +get_event_history() List[Dict]
        +clear_event_history() void
    }

    %% ==============================
    %%  INFRASTRUCTURE - CLEANING
    %% ==============================

    class NullCleaner {
        -required_fields: List[str]
        +__init__(required_fields: Optional[List[str]]) void
        +clean(rows: List[Dict]) List[Dict]
    }

    class FormatCleaner {
        -rules: Dict[str, Callable]
        +__init__(rules: Optional[Dict[str, Callable]]) void
        +clean(rows: List[Dict]) List[Dict]
        +crear_rules_inmobiliarias()$ Dict[str, Callable]
    }

    class DuplicateCleaner {
        -key_fields: tuple
        +__init__(key_fields: Optional[List[str]]) void
        -_extract_key(row: Dict) tuple
        +clean(rows: List[Dict]) List[Dict]
    }

    %% ==============================
    %%  INFRASTRUCTURE - MDM / ANALYTICS / INGESTION / PREPROCESSOR
    %% ==============================

    class MDMService {
        -repository: IDataRepository
        -folder_storage: FolderStorage
        +__init__(repository: IDataRepository, folder_storage: Optional[FolderStorage]) void
        +load_to_mdm(dataset: Dataset) Dict
        +get_dataset_by_id(dataset_id: str) Optional[Dict]
        +list_all_datasets() list[Dict]
    }

    class FeatureAnalyzer {
        +analyze(dataset: Dataset, price_factor: float) Dict
        -_compute_derived_features(records, price_factor)$ Dict
        -_enrich_records(records, derived)$ List[Dict]
        -_compute_statistics(enriched)$ Dict
    }

    class PredictionEngine {
        -model: Any
        +__init__(model: Any) void
        +predict(dataset: Any, params: dict) Any
    }

    class DataLoader {
        -preview_rows: int
        +__init__(preview_rows: int) void
        +load(path: str) Dict
        -_load_csv(path: str) Dict
        -_load_json(path: str) Dict
        -_load_excel(path: str) Dict
    }

    class Preprocessor {
        -cleaners: list[Callable]
        +__init__(cleaners: Optional[Iterable[Callable]]) void
        +add(cleaner: Callable) void
        +run(records: List[Dict]) List[Dict]
    }

    %% ========================================================================
    %%  RELATIONSHIPS
    %% ========================================================================

    %% Presentation → Controller
    VistaCargaDataset ..> DatasetController : notifica via callback
    VistaEstadoPipeline ..> DatasetController : notifica via callback
    VistaResultado ..> DatasetController : notifica via callback
    DatasetController --> PipelineFacade : usa

    %% Controller → Application Services
    DatasetController ..> SolicitudController : delega prediccion
    DatasetController *-- PipelineFacade : compone

    %% PipelineFacade → domain entities
    PipelineFacade --> Dataset : crea y modifica
    PipelineFacade --> RejectionLog : crea en rechazo
    PipelineFacade --> DatasetValidator : usa
    PipelineFacade --> QualityValidator : usa
    PipelineFacade --> FeatureAnalyzer : usa en profiling

    %% PipelineFacade → Application services
    PipelineFacade *-- IngestionService : compone
    PipelineFacade *-- CleaningService : compone
    PipelineFacade *-- MDMService : compone
    PipelineFacade *-- NotificationService : compone
    PipelineFacade --> FolderStorage : usa
    PipelineFacade --> IEmailService : usa

    %% Application services → Domain
    IngestionService --> Dataset : crea
    IngestionService ..> DatasetValidator : usa
    CleaningService --> Dataset : limpia
    CleaningService --> CleaningReport : genera
    CleaningService o-- IDataCleaner : agrega (Strategy)

    %% Prediction
    PredictionService --> PredictionEngine : usa
    PredictionService ..> Solicitud : procesa

    %% DTOs (uso futuro)
    SolicitudDTO ..> Solicitud : mapea
    DatasetDTO ..> Dataset : mapea

    %% Domain entities
    Dataset ..> DatasetStatus : referencia estado
    Dataset ..> Formato : referencia formato
    CleaningReport ..> Dataset : referenciado por dataset_id
    RejectionLog ..> Dataset : referenciado por dataset_id
    Solicitud ..> Dataset : referenciado por dataset_id
    Prediccion ..> Solicitud : referenciado por solicitud_id

    %% Validators (todos static, sin estado)
    DatasetValidator ..> Dataset : valida
    QualityValidator ..> Dataset : valida
    PredictionValidator ..> Prediccion : valida

    %% Interfaces → Implementaciones (Repository)
    IDataRepository <|.. JsonRepository : implements
    IDataRepository <|.. PandasRepository : implements
    RepositoryFactory ..> IDataRepository : factory method

    %% Interfaces → Implementaciones (Email)
    IEmailService <|.. EmailService : implements
    IEmailService <|.. FileLoggerEmailService : implements
    EmailDecorator ..|> IEmailService : implements
    EmailDecorator --> IEmailService : wraps (Decorator)
    EmailDecorator <|-- ValidacionEmailDecorator : extends
    EmailDecorator <|-- NotificacionInsercionDecorator : extends
    ValidacionEmailDecorator --> EmailDecorator : decora
    NotificacionInsercionDecorator --> EmailDecorator : decora

    %% Interfaces → Implementaciones (Cleaning)
    IDataCleaner <|.. NullCleaner : implements
    IDataCleaner <|.. FormatCleaner : implements
    IDataCleaner <|.. DuplicateCleaner : implements

    %% Observer pattern
    NotificationService o-- INotificationObserver : notifica
    DatasetController ..|> INotificationObserver : se suscribe

    %% Infrastructure → Domain
    FolderStorage --> Dataset : persiste
    FolderStorage --> RejectionLog : persiste en rechazo
    MDMService --> IDataRepository : usa
    MDMService --> FolderStorage : persiste archivos
    FeatureAnalyzer --> Dataset : analiza

    %% Preprocessor / DataLoader
    DataLoader ..> Dataset : produce registros
    Preprocessor o-- IDataCleaner : agrega cleaners

    %% Exception hierarchy
    DominioException <|-- DatasetInvalidoException
    DominioException <|-- ExtraccionIncompletaException
    DominioException <|-- FormatoInvalidoException
    DominioException <|-- TransformacionFallidaException
    DominioException <|-- CalidadInsuficienteException
    DominioException <|-- UbicacionNoBogotaException
    DominioException <|-- CoherenciaDatosException
    DominioException <|-- SignificanciaInsuficienteException
    DominioException <|-- MargenErrorExcedidoException
    DominioException <|-- RepositorioException
    DominioException <|-- NotificacionException

```
