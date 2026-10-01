# 05. Protocolo DAMA MDM y Calidad de Datos (ISO 8000 / ISO 25012)
**Estándares**: DAMA-DMBOK v2 (Cap. 10 Master Data & Cap. 13 Data Quality) · ISO 8000 · ISO/IEC 25012 · BPMN 2.0  
**Fase PDCO**: `PLAN → DEVELOPMENT` | **SDLC Stage**: Data Governance & Quality Architecture  
**Proyecto**: Sistema Data Wrangling & MDM Inmobiliario (Bogotá Real Estate)  

---

## 1. Arquitectura de Master Data Management (MDM - Golden Record)

Bajo las mejores prácticas de **DAMA-DMBOK v2**, el sistema implementa un estilo de arquitectura **MDM Híbrido / Consolidación Centralizada** (*Centralized Golden Record Hub*). Los datasets transaccionales heterogéneos provenientes de diversas fuentes se procesan en lotes y se unifican en un único repositorio maestro sin duplicidades.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                         PIPELINE DE CONSOLIDACIÓN MDM (DAMA)                           │
├───────────────────┬───────────────────┬────────────────────────┬───────────────────────┤
│ 1. INGESTA HETER. │ 2. SANEAMIENTO    │ 3. MATCHING & DEDUP   │ 4. GOLDEN RECORD HUB  │
│                   │                   │                        │                       │
│ CSV / Excel / JSON│ Normalización     │ Algoritmo Hashing      │ Inmueble Maestro      │
│ Fuertes variab.   │ Imputación Nulos  │ Deduplicación          │ Entorno Urbano        │
│ Staging RAW       │ Val. Dominios     │ Reglas Supervivencia   │ Features Analíticas   │
└───────────────────┴───────────────────┴────────────────────────┴───────────────────────┘
```

---

## 2. Algoritmo de Deduplicación y Clave Semántica Universal

Para garantizar la regla de negocio **RB-003** y el estándar **ISO 8000-110** (Master Data Quality), se define una función determinística de hash criptográfico que identifica unívocamente un inmueble físico independiente de la fuente de captura:

$$\text{hash\_duplicado} = \text{SHA256}(\text{norm\_str}(\text{direccion}) \parallel \text{round}(\text{tamano\_m2}, 1) \parallel \text{id\_barrio})$$

### 2.1 Reglas de Normalización de Texto (`norm_str`):
1. Conversión a minúsculas (`lower()`).
2. Eliminación de acentos y diacríticos (descomposición Unicode NFKD).
3. Estandarización de vías: `calle` $\to$ `cl`, `carrera` $\to$ `kr`, `avenida` $\to$ `av`, `diagonal` $\to$ `dg`, `transversal` $\to$ `tv`.
4. Supresión de caracteres especiales y colapso de espacios múltiples en uno solo.

---

## 3. Protocolo de Supervivencia de Atributos (*Survivorship Rules*)

Cuando un registro entrante genera colisión en `hash_duplicado` contra un registro preexistente en `mdm_inmuebles_maestros`, se aplican las siguientes reglas de supervivencia formal:

| Atributo Maestro | Regla de Supervivencia | Justificación de Negocio |
|---|---|---|
| `precio_ultimo_cop` | **Most Recent** (Más reciente por `fecha_registro`) | Refleja la dinámica económica del mercado actual en Bogotá. |
| `tamano_m2`, `habs`, `banos` | **Most Complete / Maximum Certainty** | Si el nuevo registro proviene de Catastro Distrital, tiene prioridad sobre portales comerciales. |
| `latitud`, `longitud` | **Spatial High Precision** | Se conservan las coordenadas con menor desviación respecto al centroide de `cat_barrios`. |
| `entorno_urbano` | **Incremental Merge** | Se recalculan amenidades (parques, vías, colegios) con la última capa geoespacial distrital. |

---

## 4. Matriz de Calidad de Datos según ISO/IEC 25012

El estándar **ISO/IEC 25012** define 15 dimensiones de calidad de datos divididas en características inherentes y dependientes del sistema. A continuación se detalla su instrumentación en la base de datos:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                       15 DIMENSIONES DE CALIDAD ISO/IEC 25012                          │
├───────────────────────────────┬────────────────────────────────────────────────────────┤
│   CARACTERÍSTICAS INHERENTES  │       IMPLEMENTACIÓN Y MÉTRICAS EN BASE DE DATOS       │
├───────────────────────────────┼────────────────────────────────────────────────────────┤
│ 1. Exactitud Sintáctica       │ Tipado estricto SQL (NUMERIC, SMALLINT, DATE, UUID).   │
│ 2. Exactitud Semántica        │ Restricciones CHECK (estrato ∈ [1,6], precio > 0).     │
│ 3. Completitud                │ Restricciones NOT NULL en atributos críticos de RB-004.│
│ 4. Consistencia               │ Integridad referencial (FKs con ON DELETE RESTRICT).   │
│ 5. Credibilidad               │ Trazabilidad de origen y firma hash SHA-256 (ISO 8000).│
│ 6. Actualidad                 │ Timestamps auditables (fecha_ingesta, fecha_cons.).    │
├───────────────────────────────┼────────────────────────────────────────────────────────┤
│  CARACTERÍSTICAS DEPENDIENTES │       IMPLEMENTACIÓN Y MÉTRICAS EN BASE DE DATOS       │
├───────────────────────────────┼────────────────────────────────────────────────────────┤
│ 7. Accesibilidad              │ Repositorio desacoplado mediante Repository Pattern.   │
│ 8. Conformidad                │ Estándar SQL ISO/IEC 9075 y metadatos ISO/IEC 11179.   │
│ 9. Confidencialidad           │ Anonimización de datos personales y RBAC.              │
│ 10. Eficiencia                │ Índices B-Tree compuestos para latencia P95 < 20ms.    │
│ 11. Precisión                 │ Coordenadas con 7 decimales y moneda en NUMERIC(14,2). │
│ 12. Trazabilidad              │ Auditoría en log_rechazos_calidad y rpt_limpieza.      │
│ 13. Comprensibilidad          │ Diccionario de datos formal y nombres semánticos.      │
│ 14. Disponibilidad            │ Transacciones ACID y persistencia relacional robusta.  │
│ 15. Portabilidad / SGBD       │ Estandarización exclusiva en MySQL Server 8.0+ / 8.4+. │
└───────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 5. Trazabilidad con Compuertas BPMN 2.0 y Auditoría de Rechazos

Cada registro descartado se persiste en `log_rechazos_calidad` mapeando directamente la compuerta de decisión BPMN y el motivo técnico:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        MAPEO DE COMPUERTAS BPMN A BASE DE DATOS                        │
├──────────┬─────────────────────────────┬─────────────┬─────────────────────────────────┤
│ COMPUERTA│ EVENTO DE RECHAZO           │ REGLA       │ REGISTRO DE AUDITORÍA (DB)      │
├──────────┼─────────────────────────────┼─────────────┼─────────────────────────────────┤
│   G1     │ Extracción incompleta       │ RF-002      │ compuerta_bpmn = 'G1'           │
│          │ Archivo fuente dañado       │             │ motivo = 'Source corrupted'     │
├──────────┼─────────────────────────────┼─────────────┼─────────────────────────────────┤
│   G2     │ Formato o estructura no OK  │ RB-004      │ compuerta_bpmn = 'G2'           │
│          │ Faltan columnas requeridas  │             │ motivo = 'Missing required col' │
├──────────┼─────────────────────────────┼─────────────┼─────────────────────────────────┤
│   G3     │ Transformación fallida      │ RB-001      │ compuerta_bpmn = 'G3'           │
│          │ Ubicación fuera de Bogotá   │ RB-002      │ motivo = 'Out of domain Bogota' │
├──────────┼─────────────────────────────┼─────────────┼─────────────────────────────────┤
│   G4     │ Calidad / Semántica inválida│ RB-005      │ compuerta_bpmn = 'G4'           │
│          │ Tamano <= 0, Precio corrupto│ RB-003      │ motivo = 'Semantic range fail'  │
└──────────┴─────────────────────────────┴─────────────┴─────────────────────────────────┘
```
