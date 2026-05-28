# State Diagram - Pipeline ETL BPMN

```mermaid
stateDiagram-v2
    [*] --> SELECTED: Usuario proporciona dataset original
    SELECTED --> RAW: Extraer datos de fuente / persistir data/RAW

    RAW --> REJECTED: Gateway 1 no / extraccion incompleta
    RAW --> EXTRACTING: Gateway 1 si

    EXTRACTING --> VALIDATING: Validar formato, estructura y columnas
    VALIDATING --> REJECTED: Gateway 2 no / formato o estructura invalida
    VALIDATING --> TRANSFORMING: Gateway 2 si

    TRANSFORMING --> CLEANING: Transformar estructura, normalizar valores y tipos
    CLEANING --> CLEANED: Eliminar duplicados / persistir data/CLEANED
    CLEANED --> REJECTED: Gateway 3 no / transformacion incompleta
    CLEANED --> QUALITY_GATE: Gateway 3 si

    QUALITY_GATE --> REJECTED: Gateway 4 no / calidad insuficiente
    QUALITY_GATE --> PROCESSED_MDM: Gateway 4 si / cargar tabla maestra unica

    PROCESSED_MDM --> NOTIFIED: Persistir data/PROCESSED/MDM/master_dataset.json
    NOTIFIED --> DELIVERED: Usuario recibe dataset limpio
    DELIVERED --> [*]

    REJECTED --> REJECTION_STORED: Persistir data/REJECTED con detalle del fallo
    REJECTION_STORED --> NOTIFIED_REJECTION: Usuario recibe rechazo
    NOTIFIED_REJECTION --> [*]
```

## Data Storages BPMN

- `data/RAW/`: datasets originales extraidos.
- `data/CLEANED/`: datasets transformados, normalizados y deduplicados.
- `data/PROCESSED/MDM/master_dataset.json`: tabla maestra unica.
- `data/REJECTED/`: rechazos con gateway, regla y detalle del fallo.
