# Análisis del sistema — Predicción de Precios de Vivienda en Bogotá

Fecha: 2026-05-27

## 1. Definición del problema

Los datasets inmobiliarios para Bogotá suelen ser informales: columnas inconsistentes, valores nulos, direcciones con variantes ortográficas (Bogotá, Bogota D.C., BogotÃ¡), y mezclas de formatos (CSV/Excel/JSON). El sistema debe ingerir fuentes heterogéneas, validar y limpiar datos, unificarlos en un MDM liviano y ejecutar un pipeline de predicción de precios robusto y trazable.

Objetivo final: proporcionar a usuarios una predicción de precio por inmueble con métricas de calidad estadística (p-value, margen de error) y auditoría de procesos.

## 2. Actores (4)

- **Client/Owner**: Submite datasets y solicita predicciones.
- **Data Quality Specialist**: Revisa reportes de limpieza y reglas de negocio violadas.
- **Market Intelligence Analyst**: Consume reportes y resultados para decisiones.
- **ETL System**: Actor técnico que ejecuta ingestion, cleaning, profiling, prediction y notificaciones.

## 3. Reglas de Negocio (RB)

- **RB-001 (Ubicación)**: Solo se aceptan inmuebles ubicados en Bogotá; ubicaciones deben normalizarse a variantes aceptadas `{"bogota", "bogotá", "bogota d.c"}`.
- **RB-002 (Estrato)**: `estrato` debe ser entero en el rango [1,6]. Valores fuera de rango invalidan el registro.
- **RB-003 (Duplicados)**: Registros duplicados (misma `ubicacion` normalizada + `tamano_m2` igual ±1% + `habitaciones` iguales) deben deduplicarse conservando la primera ocurrencia.
- **RB-004 (Margen de error)**: Predicciones aceptables requieren margen de error <= 0.15 (15%).
- **RB-005 (Significancia)**: Modelos deben presentar p-value < 0.05 para ser considerados estadísticamente significativos.
- **RB-006 (Email)**: Notificaciones por email requieren direcciones con dominio válido y formato RFC básico; si invalida, el envío es rechazado y registrado.

## 4. Requerimientos Funcionales (RF) — RF-001..RF-010

- **RF-001: Ingestión de archivos** — El sistema permite cargar CSV, Excel, JSON y mostrar preview. (Entidad: `Dataset`)
- **RF-002: Validación de estructura** — Verificar columnas mínimas: `ubicacion`, `tamano_m2`, `habitaciones`, `banos`, `estrato`, `precio`. (Entidad: `Dataset`, `DatasetValidator`)
- **RF-003: Normalización de ubicaciones** — Normalizar y detectar Bogotá. (Entidad: `Dataset`)
- **RF-004: Limpieza de datos** — Aplicar Null/Format/Duplicate cleaners. (Entidad: `CleaningReport`)
- **RF-005: Corrección de tipos** — Convertir `estrato` a int, `precio` a float, `tamano_m2` a float. (Entidad: `FormatCleaner`)
- **RF-006: Persistencia JSON** — Guardar datasets y metadatos en `JsonRepository` con operaciones CRUD. (Entidad: `JsonRepository`)
- **RF-007: Orquestación pipeline** — Ejecutar pipeline Ingest → Clean → Predict vía `PipelineFacade`. (Entidad: `PipelineFacade`)
- **RF-008: Validación estadística** — Calcular p-value y margen, y rechazar/aceptar predicción según RB-004/RB-005. (Entidad: `PredictionService`)
- **RF-009: Reportes y notificaciones** — Generar `CleaningReport` y notificar mediante `EmailService` con decoradores. (Entidad: `EmailService`, `CleaningReport`)
- **RF-010: Interfaces gráficas** — Proveer 3 pantallas Tkinter: carga, estado pipeline y resultado. (Entidad: `Presentation`)

## 5. Requerimientos No Funcionales (RNF)

- **RNF-001 (Calidad / Cobertura)**: Tests unitarios con `pytest` y cobertura >= 80% (objetivo 92%).
- **RNF-002 (Portabilidad)**: Python 3.13+, PEP8; UI en Tkinter (std lib).
- **RNF-003 (Confiabilidad)**: Escritura atómica en repositorio JSON (leer-modificar-escribir temp + rename).
- **RNF-004 (Seguridad de datos)**: No exponer datos sensibles en logs; sanitizar antes de persistir/email.
- **RNF-005 (Performance)**: Previews y transformaciones para datasets pequeños-medianos deben responder < 2s en ambiente de desarrollo razonable.

## 6. Restricciones (R)

- **R-001:** Persistencia en JSON plano (no DB relacional).
- **R-002:** UI obligatoria en Tkinter; no CLI pública.
- **R-003:** Solo dependencias permitidas: pandas, numpy, scikit-learn, openpyxl (confirmar antes de instalar).
- **R-004:** Código en inglés; comentarios / UI pueden ser español.

## 7. Mapa de Entidades y Responsabilidades

### `Dataset`
- Atributos: `id`, `source_path`, `format`, `status` (DatasetStatus), `created_at`, `schema`, `rows_preview`, `records`.
- Métodos de negocio: `validar_estructura()`, `normalizar_ubicacion()`, `es_bogota()`, `to_dict()`.

### `Solicitud` (Request for prediction)
- Atributos: `id`, `dataset_id`, `requested_by`, `parameters` (dict), `created_at`, `status`.
- Métodos: `validate_parameters()`, `to_dto()`.

### `Prediccion` (Prediction)
- Atributos: `id`, `solicitud_id`, `predicted_value`, `confidence_interval`, `p_value`, `margin`.
- Métodos: `es_significativa()` -> p_value < 0.05, `margen_aceptable()` -> margin <= 0.15.

### `CleaningReport`
- Atributos: `dataset_id`, `timestamp`, `removed_rows_count`, `duplicates_found`, `issues` (list).
- Métodos: `summary()`.

### `RejectionLog`
- Atributos: `id`, `entity_id`, `reason_code`, `message`, `context`, `created_at`.
- Métodos: `to_dict()`.

## 8. Enums necesarios

- `DatasetStatus`: RAW, VALIDATED, STORED, CLEANING, PROFILED, TRANSFORMED, UNIFIED, READY, ERROR
- `Formato`: CSV, EXCEL, JSON
- `TipoVariable`: NUMERIC, CATEGORICAL, TEXT, DATETIME

## 9. Trazabilidad (mapeo rápido RF → Entidades)

- RF-001 → `Dataset`, `DataLoader`
- RF-002 → `Dataset`, `DatasetValidator`
- RF-003 → `Dataset.normalizar_ubicacion()`
- RF-004 → `CleaningService`, `NullCleaner`, `DuplicateCleaner`, `FormatCleaner`
- RF-005 → `FormatCleaner`
- RF-006 → `JsonRepository`
- RF-007 → `PipelineFacade`
- RF-008 → `PredictionService`, `PredictionValidator`
- RF-009 → `CleaningReport`, `EmailService` + Decorators
- RF-010 → `presentation.views` (Tkinter)

## 10. Observaciones y riesgos

- Calidad de los datos dependerá de la heterogeneidad de fuentes; definir ejemplos de transformación y reglas de fallback será crítico.
- Requerimiento de Tkinter implica diseño de UX básico pero suficiente para POC; para producción considerar web UI.
- Debe confirmarse la lista de dependencias antes de instalación.

---

Este documento corresponde a la **Fase 1: Análisis**. Espero tu aprobación (`aprobado` o `continuar`) para generar la documentación de arquitectura (Fase 2) o para ajustar el análisis.
# AN�LISIS

## 1. Resumen del problema

El proyecto aborda la falta de formalidad y calidad en datasets inmobiliarios de Bogot�, proporcionando un sistema ETL que ingesta, valida, limpia y unifica datos de propiedades para generar predicciones de precios de vivienda con trazabilidad y reportes de calidad.

## 2. Actores

- Cliente/Propietario: solicita predicciones y provee datos.
- Especialista en Calidad de Datos: revisa CleaningReport y decisiones de rechazo.
- Analista de Inteligencia de Mercado: consume predicciones y reportes para an�lisis.
- Sistema ETL: procesado automatizado que ingesta, limpia, valida y predice.

## 3. Reglas de Negocio (RB)

- RB-001: Solo se aceptan registros con ubicaci�n en Bogot� (variantes aceptadas:  bogota, bogot�, bogota d.c).
- RB-002: estrato debe ser entero en [1,6]. Registros fuera de rango son rechazados.
- RB-003: Duplicados por direcci�n+tamano_m2 se eliminan, salvo conflicto de precio que se registra en RejectionLog.
- RB-004: Margen de error aceptable en predicci�n = 0.15 (15%).
- RB-005: Una predicci�n es significativa solo si p-value < 0.05.
- RB-006: Notificaciones por email deben verificarse y enviarse solo con direcciones v�lidas y plantillas aprobadas.

## 4. Requerimientos Funcionales (RF)

- RF-001: Ingest a dataset in CSV/Excel/JSON and persist as Dataset (Entity). (Entity: Dataset)
- RF-002: Validate dataset structure and required columns: ubicacion, tamano_m2, habitaciones, banos, estrato, precio. (Entity: Dataset, DatasetValidator)
- RF-003: Normalize location fields to canonical form and detect Bogot�. (Entity: Dataset)
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
- R-004: No databases�persistence is flat JSON files / Pandas.

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
- El Manual Tecnico.docx debe ser convertido a Markdown para extraer reglas m�s finas.
- Se deben confirmar las columnas m�nimas y tipos exactos en el manual.
- UI con Tkinter requiere control de hilos si la pipeline es larga (usar threading/queue).

---

**Siguiente paso:** espera tu aprobaci�n. Si apruebas, proceder� a la Fase 2 (documentaci�n de arquitectura) y generar� los diagramas y la estructura de carpetas vac�a solicitada.
