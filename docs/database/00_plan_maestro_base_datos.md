# Plan Maestro de Diseño e Ingeniería de Base de Datos
**Proyecto**: Sistema Data Wrangling & MDM Inmobiliario (Bogotá Real Estate)  
**Estándares y Marcos**: SWEBOK v4 · DAMA-DMBOK v2 · ISO/IEC 9075 · ISO/IEC 11179 · ISO/IEC 25012 · ISO 8000 · IEEE 830 / ISO 29148 · MySQL 8.0+ / 8.4+ LTS  
**Fase PDCO**: `PLAN → DEVELOPMENT` | **SDLC Stage**: Architectural & Detailed Database Design  
**Skill Activa**: `01-requirements` & `02-architecture`  
**Versión**: 1.0.0  
**Fecha**: 2026-09-05  

---

## 1. Resumen Ejecutivo y Marco Normativo

Este documento establece la arquitectura formal, el modelado conceptual, lógico y físico, el diccionario de metadatos y las directrices de gobierno de datos para el **Sistema de Data Wrangling y Predicción de Precios de Vivienda en Bogotá**. El diseño garantiza la transición desde datos heterogéneos y crudos (CSV, Excel, JSON) hacia un **Modelo Relacional en Forma Normal de Boyce-Codd (BCNF)** y un **Master Data Management (MDM - Golden Record)** con soporte analítico.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         ARQUITECTURA DE MODELADO DAMA-DMBOK                      │
├──────────────────────────┬──────────────────────────┬────────────────────────────┤
│  MODELO CONCEPTUAL (CDM) │   MODELO LÓGICO (LDM)    │    MODELO FÍSICO (PDM)     │
│                          │                          │                            │
│• Abstracción de Negocio  │• Normalización 1NF→BCNF  │• DDL ISO/IEC 9075 (SQL)    │
│• Entidades Fuertes/Déb.  │• Esquema Relacional      │• Tipado estricto & Checks  │
│• Diagrama EER (Mermaid)  │• Claves PK, FK, UK       │• Estrategia de Índices     │
│• Cardinalidad & Dominio  │• Diccionario ISO 11179   │• Integridad Referencial    │
└──────────────────────────┴──────────────────────────┴────────────────────────────┘
```

### 1.1 Cumplimiento de Estándares Internacionales

| Estándar | Dimensión Técnica | Aplicación en el Proyecto |
|---|---|---|
| **SWEBOK v4 (Cap. 2)** | *Software Design / Data Persistence* | Desacoplamiento mediante *Repository Pattern* (SOLID-DIP), alta cohesión y encapsulamiento. |
| **DAMA-DMBOK v2 (Cap. 5, 8, 10, 11)** | *Data Modeling, Master Data, Metadata, Quality* | Proceso estructurado CDM $\to$ LDM $\to$ PDM, consolidación de *Golden Records* y gobierno de metadatos. |
| **ISO/IEC 9075** | *SQL Database Language Standard* | Sintaxis DDL estandarizada, integridad referencial (`ON DELETE RESTRICT/CASCADE`), aserciones y restricciones `CHECK`. |
| **ISO/IEC 11179** | *Metadata Registries (MDR) & Data Elements* | Diccionario de datos formal, nombres estandarizados, representaciones unívocas y dominios de valor. |
| **ISO/IEC 25012** | *Data Quality Model* | Verificación de exactitud sintáctica/semántica, completitud, consistencia, unicidad y credibilidad. |
| **ISO 8000** | *Data Quality / Master Data Provenance* | Trazabilidad de origen por dataset (hash SHA-256), linaje de transformaciones y reglas de supervivencia. |
| **ISO/IEC 25010** | *System & Software Quality* | Índices B-Tree y espaciales para optimización de consultas $<30\text{ms}$ en volúmenes masivos. |

---

## 2. Estructura de Documentación del Módulo de Base de Datos

La documentación completa y detallada del subsistema de datos se distribuye en los siguientes entregables especializados:

1. [01. Diagrama Conceptual Entidad-Relación (EER)](file:///c:/Users/ADAN/OneDrive/Documentos/3-Universidad/tercer/Lenguaje/Proyecto%20final/ProyectoDataWrangling/docs/database/01_diagrama_conceptual_er.md):
   - Abstracción semántica y taxonomía de entidades (Referencia, Maestras, Transaccionales, Auditoría).
   - Diagrama EER completo en notación *Crow's Foot* con cardinalidades formales y atributos clave.
2. [02. Diagrama Lógico Relacional y Normalización](file:///c:/Users/ADAN/OneDrive/Documentos/3-Universidad/tercer/Lenguaje/Proyecto%20final/ProyectoDataWrangling/docs/database/02_diagrama_logico_relacional.md):
   - Justificación matemática y demostración de normalización (1NF, 2NF, 3NF, BCNF).
   - Diagrama Lógico Relacional (tablas, PK, FK, tipos y relaciones).
3. [03. Diccionario de Metadatos ISO/IEC 11179](file:///c:/Users/ADAN/OneDrive/Documentos/3-Universidad/tercer/Lenguaje/Proyecto%20final/ProyectoDataWrangling/docs/database/03_diccionario_datos_iso11179.md):
   - Catálogo estandarizado de elementos de datos, tipos SQL, nulabilidad, rangos de dominio y trazabilidad de reglas de negocio (RB-001 a RB-006, RF-001 a RF-011).
4. [04. Esquema DDL Estándar ISO/IEC 9075](file:///c:/Users/ADAN/OneDrive/Documentos/3-Universidad/tercer/Lenguaje/Proyecto%20final/ProyectoDataWrangling/docs/database/04_esquema_ddl_iso9075.sql):
   - Script SQL ejecutable con creación de esquemas, tablas, restricciones `CHECK`, llaves foráneas con políticas de actualización/borrado e índices de rendimiento.
5. [05. Protocolo DAMA MDM y Calidad ISO 25012 / ISO 8000](file:///c:/Users/ADAN/OneDrive/Documentos/3-Universidad/tercer/Lenguaje/Proyecto%20final/ProyectoDataWrangling/docs/database/05_protocolo_dama_mdm_calidad.md):
   - Estrategia de consolidación *Golden Record*, algoritmo de deduplicación semántica por hash, reglas de supervivencia y linaje de compuertas BPMN G1-G4.
6. [06. Justificación Técnica del Análisis y Abstracción de Entidades](file:///c:/Users/ADAN/OneDrive/Documentos/3-Universidad/tercer/Lenguaje/Proyecto%20final/ProyectoDataWrangling/docs/database/06_justificacion_analisis_abstraccion_entidades.md):
   - Fundamentación de por qué este es el modelo correcto, desmontaje del antipatrón *God Table*, justificación decisión por decisión y validación con principios SOLID/GRASP y SWEBOK.

---

## 3. Matriz de Trazabilidad Requerimientos vs. Base de Datos

| ID Regla / Req | Requerimiento de Negocio / Calidad | Implementación en Base de Datos | Objeto de Base de Datos |
|---|---|---|---|
| **RB-001** | Restricción de dominio: Solo inmuebles de Bogotá | Coordenadas delimitadas y asociación obligatoria a `cat_barrios` / `cat_localidades`. | `cat_barrios.chk_barrio_latitud`, `chk_barrio_longitud` |
| **RB-002** | Restricción de dominio: Estrato $\in [1, 6]$ | Restricción declarativa `CHECK (estrato BETWEEN 1 AND 6)`. | `wrk_inmuebles_cleaned.chk_cleaned_estrato`, `cat_barrios.chk_barrio_estrato` |
| **RB-003** | Restricción de integridad: Cero duplicados | Llave única calculada `hash_duplicado` sobre dirección, tamaño y barrio. | `mdm_inmuebles_maestros.hash_duplicado (UNIQUE)` |
| **RB-004** | Restricción de calidad: Columnas mínimas y formato | Esquema tipado estricto en staging y tracking de lotes en `wrk_datasets_ingesta`. | `wrk_datasets_ingesta`, `stg_inmuebles_raw` |
| **RB-005** | Consistencia semántica: Rangos lógicos en m², habitaciones, baños y precio | Restricciones `CHECK` en medidas físicas y límites numéricos realistas. | `wrk_inmuebles_cleaned.chk_cleaned_tamano`, `chk_cleaned_precio` |
| **RB-006** | Notificación por email de operaciones y fallos | Tabla de registro de notificaciones despachadas y destinatarios. | `log_notificaciones` |
| **RF-009** | Tabla maestra unificada (MDM) | Tabla central `mdm_inmuebles_maestros` y dimensión de entorno urbano. | `mdm_inmuebles_maestros`, `dim_entorno_urbano` |
| **RF-010** | Trazabilidad de fallos por compuertas BPMN | Tabla de auditoría con compuerta de fallo (G1-G4), regla infringida y payload JSON. | `log_rechazos_calidad` |
| **RF-011** | Variable temporal (año/fecha) para ML | Campo `anio_registro` normalizado y utilizado para modelos analíticos. | `wrk_inmuebles_cleaned.anio_registro`, `fct_features_analiticas` |

---

## 4. Próximos Pasos en el Ciclo SDLC (Fase DEVELOPMENT & CONTROL)

1. **Implementación de Repositorio Relacional**:
   - Crear `infrastructure/repositories/mysql_repository.py` implementando la interfaz abstracta `IDataRepository` sobre MySQL Server (vía `mysql-connector-python` o SQLAlchemy).
2. **Pruebas Automatizadas de Integridad (Skill 04)**:
   - Crear `tests/unit/test_database_integrity.py` para validar constraints de clave única, rangos `CHECK`, triggers de auditoría y cascadas de eliminación.
3. **Carga y Migración de Datos de Referencia**:
   - Script de inicialización de las 20 localidades oficiales de Bogotá y catálogo de tipos de inmuebles.
