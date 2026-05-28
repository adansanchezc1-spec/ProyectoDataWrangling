# UML Class Diagram - Sistema Data Wrangling

```mermaid
classDiagram
    class VistaCargaDataset {
        -selected_files: list
        +on_process_requested(files)
    }

    class VistaEstadoPipeline {
        +add_info_line(line)
        +update_stage_status(stage, status, details)
    }

    class VistaResultado {
        +show_result(result)
    }

    class DatasetController {
        -pipeline_facade: PipelineFacade
        +upload_and_process_dataset(file_path_or_paths)
        +subscribe(event, callback)
    }

    class PipelineFacade {
        -ingestion_service: IngestionService
        -cleaning_service: CleaningService
        -mdm_service: MDMService
        -folder_storage: FolderStorage
        +run_pipeline(file_path) dict
    }

    class IngestionService {
        +load(file_path) Dataset
    }

    class CleaningService {
        -cleaners: list
        +register_cleaner(cleaner)
        +run(dataset) tuple
    }

    class MDMService {
        -repository: IDataRepository
        -folder_storage: FolderStorage
        +load_to_mdm(dataset) dict
    }

    class FolderStorage {
        -raw_dir: Path
        -cleaned_dir: Path
        -mdm_dir: Path
        -rejected_dir: Path
        +persist_raw(dataset) Path
        +persist_cleaned(dataset) Path
        +append_to_master(dataset) Path
        +persist_rejection(rejection_log) Path
    }

    class Dataset {
        +id: str
        +source_path: str
        +format: str
        +status: str
        +schema: dict
        +records: list
        +rows_preview: list
        +total_rows: int
        +validar_estructura() bool
        +normalizar_ubicacion()
        +es_bogota() bool
        +to_dict() dict
    }

    class CleaningReport {
        +dataset_id: str
        +registros_procesados: int
        +nulos_removidos: int
        +duplicados_removidos: int
        +add_step(name, affected_rows, details)
        +to_dict() dict
    }

    class RejectionLog {
        +dataset_id: str
        +motivo: str
        +gateway_bpmn: int
        +regla_negocio: str
        +to_dict() dict
    }

    class DatasetValidator {
        +validar_columnas_minimas(schema, columnas) bool
        +validar_ubicacion(valor) str
        +validar_estrato(valor) int
    }

    class QualityValidator {
        +validar_consistencia_semantica(row) bool
        +validar_integridad(rows, min_cobertura) bool
    }

    class IDataCleaner {
        <<interface>>
        +clean(rows) list
    }

    class NullCleaner
    class FormatCleaner
    class DuplicateCleaner

    class IDataRepository {
        <<interface>>
        +save(entity)
        +get_by_id(entity_id)
        +list_all()
    }

    class JsonRepository

    VistaCargaDataset --> DatasetController
    VistaEstadoPipeline <-- DatasetController
    VistaResultado <-- DatasetController
    DatasetController --> PipelineFacade
    PipelineFacade --> IngestionService
    PipelineFacade --> CleaningService
    PipelineFacade --> MDMService
    PipelineFacade --> FolderStorage
    IngestionService --> Dataset
    CleaningService --> Dataset
    CleaningService --> CleaningReport
    CleaningService o-- IDataCleaner
    IDataCleaner <|.. NullCleaner
    IDataCleaner <|.. FormatCleaner
    IDataCleaner <|.. DuplicateCleaner
    PipelineFacade --> RejectionLog
    PipelineFacade --> DatasetValidator
    PipelineFacade --> QualityValidator
    MDMService --> FolderStorage
    MDMService --> IDataRepository
    IDataRepository <|.. JsonRepository
```
