# ANÁLISIS

## 1. Resumen del problema

El proyecto aborda la falta de formalidad y calidad en datasets inmobiliarios de Bogotá, proporcionando un sistema ETL que ingesta, valida, limpia y unifica datos de propiedades para generar predicciones de precios de vivienda con trazabilidad y reportes de calidad.

## 2. Actores

- Cliente/Propietario: solicita predicciones y provee datos.
- Especialista en Calidad de Datos: revisa CleaningReport y decisiones de rechazo.
- Analista de Inteligencia de Mercado: consume predicciones y reportes para análisis.
- Sistema ETL: procesado automatizado que ingesta, limpia, valida y predice.

## 3. Reglas de Negocio (RB)

- RB-001: Solo se aceptan registros con ubicación en Bogotá (variantes aceptadas:  bogota, bogotá, bogota d.c).
- RB-002: estrato debe ser entero en [1,6]. Registros fuera de rango son rechazados.
- RB-003: Duplicados por dirección+tamano_m2 se eliminan, salvo conflicto de precio que se registra en RejectionLog.
- RB-004: Margen de error aceptable en predicción = 0.15 (15%).
- RB-005: Una predicción es significativa solo si p-value < 0.05.
- RB-006: Notificaciones por email deben verificarse y enviarse solo con direcciones válidas y plantillas aprobadas.

## 4. Requerimientos Funcionales (RF)

- RF-001: Ingest a dataset in CSV/Excel/JSON and persist as Dataset (Entity). (Entity: Dataset)
- RF-002: Validate dataset structure and required columns: ubicacion, tamano_m2, habitaciones, banos, estrato, precio. (Entity: Dataset, DatasetValidator)
- RF-003: Normalize location fields to canonical form and detect Bogotá. (Entity: Dataset)
- RF-004: Clean nulls and standardize types (estrato->int, precio->float). (Entity: CleaningReport)
- RF-005: Remove duplicates according to business rules. (Entity: CleaningReport, RejectionLog)
- RF-006: Persist cleaned dataset via repository with atomic JSON storage. (Entity: JsonRepository, Dataset)
- RF-007: Run prediction pipeline and produce Prediccion object with p-value and margin. (Entity: PredictionService, Prediccion)
- RF-008: Provide UI to upload dataset, monitor pipeline, and view results. (Entity: presentation views)
- RF-009: Send notification emails upon critical events (insertion, rejection). (Entity: EmailService, EmailDecorator)
- RF-010: Produce a CleaningReport and RejectionLog for auditability. (Entity: CleaningReport, RejectionLog)

## 5. Requerimientos No Funcionales (RNF)

- RNF-001: Codebase in Python 3.13+, PEP 8 compliant.
- RNF-002: GUI must be graphical using Tkinter; no CLI-only solutions.
- RNF-003: Unit test coverage = 80% (target 92%).
- RNF-004: Persistence uses JSON files and Pandas; operations must be atomic.
- RNF-005: No external dependencies beyond allowed list (pandas, numpy, scikit-learn, openpyxl).

## 6. Restricciones (R)

- R-001: Language: Python 3.13+ default; all code identifiers in English.
- R-002: UI must be implemented with Tkinter.
- R-003: Email service uses SMTP (configurable host/port) and must support decorator chain.
- R-004: No databases—persistence is flat JSON files / Pandas.

## 7. Mapa de Entidades y Responsabilidades

### Entity: Dataset
- Attributes:
  - id: str
  - source_path: str
  - format: Formato
  - status: DatasetStatus
  - created_at: datetime
  - schema: dict (column->type)
  - rows_preview: list[dict]
- Business Methods:
  - validar_estructura() -> bool
  - normalizar_ubicacion() -> None
  - es_bogota() -> bool
  - to_dict() -> dict

### Entity: Solicitud
- Attributes:
  - id: str
  - dataset_id: str
  - parameters: dict (model params, filters)
  - requested_by: str
  - status: str
  - created_at: datetime
- Business Methods:
  - validate_parameters()
  - mark_parametrized()

### Entity: Prediccion
- Attributes:
  - id: str
  - solicitud_id: str
  - estimated_price: float
  - p_value: float
  - margin: float
  - confidence_interval: tuple[float, float]
  - created_at: datetime
- Business Methods:
  - es_significativa() -> bool  # p_value < 0.05
  - margen_aceptable() -> bool  # margin <= 0.15
  - to_dict() -> dict

### Entity: CleaningReport
- Attributes:
  - id: str
  - dataset_id: str
  - steps: list[dict]  # each step: {name, affected_rows, details}
  - summary: dict
  - created_at: datetime
- Business Methods:
  - add_step(name, affected_rows, details)
  - generate_summary()

### Entity: RejectionLog
- Attributes:
  - id: str
  - dataset_id: str
  - row_index: int
  - reason_code: str
  - message: str
  - created_at: datetime
- Business Methods:
  - to_dict()

## 8. Enums

- DatasetStatus: RAW, VALIDATED, STORED, CLEANING, PROFILED, TRANSFORMED, UNIFIED, READY, ERROR
- Formato: CSV, EXCEL, JSON
- TipoVariable: NUMERIC, CATEGORICAL, TEXT, DATETIME

## 9. Mapeo RF->Entidades (resumen)
- RF-001 -> Dataset, JsonRepository
- RF-002 -> DatasetValidator, Dataset
- RF-003 -> Dataset.normalizar_ubicacion
- RF-004 -> CleaningService, NullCleaner, FormatCleaner
- RF-005 -> DuplicateCleaner, RejectionLog
- RF-006 -> JsonRepository
- RF-007 -> PredictionService, Prediccion
- RF-008 -> presentation.views
- RF-009 -> EmailService, EmailDecorator
- RF-010 -> CleaningReport, RejectionLog

## 10. Observaciones y Riesgos
- El Manual Tecnico.docx debe ser convertido a Markdown para extraer reglas más finas.
- Se deben confirmar las columnas mínimas y tipos exactos en el manual.
- UI con Tkinter requiere control de hilos si la pipeline es larga (usar threading/queue).

---

**Siguiente paso:** espera tu aprobación. Si apruebas, procederé a la Fase 2 (documentación de arquitectura) y generaré los diagramas y la estructura de carpetas vacía solicitada.
