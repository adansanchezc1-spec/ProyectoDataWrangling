# 06. Justificación Técnica del Análisis y Abstracción de Entidades
**Documento**: Rationale de Ingeniería de Datos, Origen Entidad por Entidad y Responsabilidad en el Sistema  
**Estándares y Marcos**: SWEBOK v4 (Software Design) · DAMA-DMBOK v2 (Data Modeling & MDM) · ISO/IEC 25012 · ISO/IEC 11179 · BPMN 2.0 · Principios SOLID & GRASP  
**Fase PDCO**: `PLAN → DEVELOPMENT` | **SDLC Stage**: Architectural & Detailed Database Design  
**Skill Activa**: `01-requirements` & `02-architecture`  
**Proyecto**: Sistema Data Wrangling & MDM Inmobiliario (Bogotá Real Estate)  

---

## 1. Introducción y Propósito del Documento

El propósito de este documento es exponer la **fundamentación teórica, matemática y arquitectónica** que respalda el modelo de base de datos diseñado. Se detalla el proceso cognitivo de **abstracción de entidades**, explicando con absoluta claridad:
1. **¿Por qué este es el análisis correcto?**: Cómo se descompone la complejidad del mundo real sin caer en simplificaciones dañinas.
2. **Origen de cada entidad (¿De dónde sale?)**: Su nacimiento a partir de los requerimientos de software (IEEE 830 / ISO 29148), reglas de negocio (RB-001 a RB-006) y compuertas BPMN 2.0 (G1 a G4).
3. **Rol en el sistema (¿Qué hace cada una?)**: Su responsabilidad operativa, transaccional o analítica en la arquitectura de datos.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          EL RETO DE LA ABSTRACCIÓN EN INGENIERÍA                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ¿Cómo transformar un dataset plano, sucio y heterogéneo (CSV/Excel/JSON) en un modelo   │
│ relacional robusto, que soporte ingesta por lotes (ETL), auditoría forense de fallos   │
│ (BPMN G1-G4), consolidación de registros maestros (MDM) y feature store para ML?      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Fundamentos de Abstracción: ¿Por qué la "Tabla Única Plana" es un Antipatrón?

### 2.1 El Antipatrón: La "God Table" o Tabla Plana Única (Flat Table)
Un enfoque inexperto suele proponer almacenar todo el dataset en una única tabla de 25 columnas (`id, ubicacion, tamano, estrato, precio, parques, colegios, feature1, feature2, estado, email, error...`). 

Este diseño plano introduce fallos arquitectónicos críticos:
- **Violación de Formas Normales (1NF, 2NF, 3NF)**: Nombres de barrios y localidades duplicados millones de veces. Si se corrige la ortografía de un barrio, se deben bloquear y actualizar millones de registros (*Update Anomaly*).
- **Destrucción de la Inmutabilidad de los Datos Crudos**: Si el proceso de limpieza modifica la misma fila donde se leyó el dato, es imposible auditar qué datos entregó la fuente original ante una auditoría forense (*Data Loss / Provenance Loss* - violación de **ISO 8000**).
- **Acoplamiento de Preocupaciones (Violación de SOLID SRP)**: Mezcla datos de negocio del inmueble con metadatos del archivo físico, con registros de auditoría de errores y con variables analíticas de Machine Learning.
- **Incapacidad de Manejo Batch Multiusuario**: No permite rastrear qué registros provinieron de qué archivo ni procesar múltiples cargas simultáneas.

### 2.2 La Abstracción Correcta: Cuadrantes Semánticos DAMA
En ingeniería de datos bajo **DAMA-DMBOK v2**, una **Entidad** no es una simple columna o tabla; es un **concepto del mundo real o del sistema que posee identidad propia, ciclo de vida independiente y reglas de negocio específicas**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              CUADRANTES SEMÁNTICOS (DAMA)                              │
├───────────────────────┬────────────────────────┬───────────────────────────────────────┤
│ 1. DATOS REFERENCIA   │ 2. PIPELINE & STAGING  │ 3. MASTER DATA (MDM) & AUDITORÍA      │
│                       │                        │                                       │
│• cat_localidades      │• wrk_datasets_ingesta  │• mdm_inmuebles_maestros (Golden Rec)  │
│• cat_barrios          │• stg_inmuebles_raw     │• dim_entorno_urbano (GIS Context)     │
│• cat_tipos_inmueble   │• wrk_inmuebles_cleaned │• log_rechazos_calidad (BPMN G1-G4)    │
│• cat_fuentes_origen   │• fct_features_analit.  │• rpt_limpieza_ejecucion / log_notif.  │
└───────────────────────┴────────────────────────┴───────────────────────────────────────┘
```

---

## 3. Desglose Exhaustivo: Entidad por Entidad

A continuación se explica el origen exacto de cada una de las 13 entidades del modelo, qué problema resuelve y qué función cumple en el sistema:

---

### 3.1 `cat_localidades` (Catálogo Maestro de Localidades)
- **¿De dónde sale?**:
  - Nace de la división territorial oficial del Distrito Capital de Bogotá (20 localidades DANE) y de la necesidad de validar la restricción geográfica **RB-001** ("Solo inmuebles de Bogotá") y agrupar macro-zonas (Norte, Sur, Centro, Occidente).
- **¿Qué problema resuelve?**:
  - En los datasets originales, la localidad viene escrita con múltiples variaciones ("Usaquen", "usaquén", "USAQUEN", "Usaquén D.C."). Si no existiera esta entidad, tendríamos millones de filas con texto redundante e inconsistente, violando la **3NF/BCNF** y haciendo imposible realizar agrupaciones analíticas confiables.
- **¿Qué hace en el sistema?**:
  - Actúa como la **raíz de integridad territorial inmutable**. Custodia el catálogo oficial con su código DANE unívoco (`1101` a `1120`), su nombre oficial y su macro-zona, sirviendo de ancla para todos los barrios de la ciudad.

---

### 3.2 `cat_barrios` (Catálogo de Barrios y Comunas)
- **¿De dónde sale?**:
  - Nace del análisis de la columna cruda `ubicacion` (ej. "Chapinero Alto", "Cedritos", "Modelia") y de la necesidad de calibrar el estrato socioeconómico modal (**RB-002**) y las coordenadas espaciales de referencia.
- **¿Qué problema resuelve?**:
  - El usuario ingresa texto libre en `ubicacion`. Esta entidad permite transformar ese texto en una referencia geográfica formal con **centroides de latitud y longitud calibrados** (`latitud_centroide`, `longitud_centroide`) y estrato modal.
  - Al forzar `CHECK (latitud_centroide BETWEEN 4.45 AND 4.85)` y `CHECK (longitud_centroide BETWEEN -74.25 AND -73.95)`, la base de datos rechaza a nivel de motor cualquier ubicación ajena a Bogotá, cumpliendo la dimensión de **Exactitud Semántica (ISO/IEC 25012)**.
- **¿Qué hace en el sistema?**:
  - Asocia cada barrio a su localidad ($N:1$), define los límites geoespaciales válidos y provee el estrato de referencia para validar si el estrato del inmueble ingresado es consistente con su entorno.

---

### 3.3 `cat_tipos_inmueble` (Catálogo de Tipologías)
- **¿De dónde sale?**:
  - Nace de la heterogeneidad de los portales inmobiliarios, donde un bien puede etiquetarse arbitrariamente como "Apto", "Apartamento", "Casa campestre", "Penthouse", "Apartaestudio" o "Monoambiente".
- **¿Qué problema resuelve?**:
  - Si permitiéramos texto libre para la tipología, los algoritmos de Machine Learning y los reportes analíticos fallarían al intentar correlacionar precios por metro cuadrado, ya que "Apto" y "Apartamento" se tratarían como cosas distintas.
- **¿Qué hace en el sistema?**:
  - Provee un catálogo maestro cerrado y normalizado (`APARTAMENTO`, `CASA`, `ESTUDIO`, `PENTHOUSE`) con descripciones formales, forzando la clasificación estandarizada de todo inmueble limpio.

---

### 3.4 `cat_fuentes_origen` (Proveedores Externos de Datos)
- **¿De dónde sale?**:
  - Nace de la arquitectura multi-fuente del sistema, que extrae datos desde MetroCuadrado, FincaRaíz, Catastro Distrital y portales de Open Data en formatos CSV, Excel y JSON (**RF-001**).
- **¿Qué problema resuelve?**:
  - Resuelve la pérdida de trazabilidad de procedencia (*Data Lineage* / **ISO 8000**). Sin esta entidad, si un lote contiene datos erróneos, sería imposible determinar qué proveedor externo introdujo la anomalía ni qué nivel de confiabilidad otorgarle a sus datos.
- **¿Qué hace en el sistema?**:
  - Registra a cada proveedor de datos, su formato por defecto y su estado operativo, permitiendo aplicar reglas de supervivencia (*Survivorship*) diferenciadas según la fiabilidad del origen (ej. Catastro Oficial tiene prioridad sobre portales comerciales).

---

### 3.5 `wrk_datasets_ingesta` (Lote de Ingesta ETL)
- **¿De dónde sale?**:
  - Nace del Caso de Uso **UC-001** / **RF-001** ("Cargar Dataset") y del Carril BPMN 2.0 "Usuario" / "Origen de Datos".
- **¿Qué problema resuelve?**:
  - Un archivo que entra al pipeline no es simplemente un montón de filas flotantes; es un **evento transaccional completo**. Requiere saber quién lo cargó (`usuario_email`), cuándo (`fecha_ingesta`), qué archivo físico era (`nombre_archivo`), cuál es su firma criptográfica de integridad (`hash_sha256` SHA-256) y en qué estado del pipeline se encuentra (`CARGADO`, `VALIDANDO`, `COMPLETADO`, `RECHAZADO`).
- **¿Qué hace en el sistema?**:
  - Es el **nodo raíz de trazabilidad** de cada corrida ETL. Agrupa bajo un mismo identificador universal (`id_dataset` UUID) todas las filas crudas leídas, las filas limpias resultantes, los rechazos generados y el reporte final de balance.

---

### 3.6 `stg_inmuebles_raw` (Capa Staging Cruda Inmutable)
- **¿De dónde sale?**:
  - Nace del requerimiento **RF-002** ("Extraer datos completos desde origen") y de la compuerta BPMN **Gateway 1 (G1: ¿Extracción completa?)**.
- **¿Qué problema resuelve?**:
  - Si un archivo fuente trae una fila con el texto `"mil millones"` en el precio o `"N/A"` en habitaciones, una tabla con tipos estrictos generaría una excepción fatal en la base de datos y abortaría toda la carga.
  - `stg_inmuebles_raw` almacena los datos exactamente como vienen en formato `TEXT`, cumpliendo el principio de **Inmutabilidad de Datos Crudos (DAMA & ISO 8000)**.
- **¿Qué hace en el sistema?**:
  - Guarda la "fotografía forense" del dato de origen. Si mañana se ajusta un algoritmo de limpieza (Skill 05), se puede reprocesar el dataset desde `stg_inmuebles_raw` sin pedirle al usuario que vuelva a subir el archivo.

---

### 3.7 `wrk_inmuebles_cleaned` (Registros Limpios y Normalizados)
- **¿De dónde sale?**:
  - Nace de la superación exitosa de las compuertas **G1, G2 y G3** del pipeline ETL y de las reglas de negocio **RB-001** (Ubicación Bogotá), **RB-002** (Estrato 1-6), **RB-004** (Columnas mínimas) y **RB-005** (Coherencia semántica).
- **¿Qué problema resuelve?**:
  - Separa los datos brutos de los datos saneados. Aquí los tipos de datos ya son estrictos (`NUMERIC`, `SMALLINT`, `BOOLEAN`), los nulos fueron tratados, la ubicación se convirtió en una clave foránea a `cat_barrios` y las medidas físicas superaron los `CHECK` de rangos lógicos.
- **¿Qué hace en el sistema?**:
  - Contiene los registros individuales limpios de esa corrida de ingesta específica, listos para cálculo de variables analíticas y para someterse a la consolidación en la tabla maestra.

---

### 3.8 `fct_features_analiticas` (Feature Store para Machine Learning)
- **¿De dónde sale?**:
  - Nace de los requerimientos **RF-005**, **RF-011** y del componente `FeatureAnalyzer`, diseñado para preparar los datos para los modelos de predicción de precios.
- **¿Qué problema resuelve?**:
  - Resuelve la violación de Responsabilidad Única (**SOLID SRP**). Los atributos del inmueble son **hechos físicos observados** (`tamano_m2`, `habitaciones`, `precio_cop`), mientras que las features son **derivaciones matemáticas calculadas para algoritmos** (`precio_unitario_m2`, `puntaje_entorno`, `bano_por_hab_ratio`, `densidad_comercial`, `factor_precio_millones`).
  - Si un Científico de Datos crea una nueva feature (ej. `log_precio` o `ratio_estacionamiento`), no altera la tabla del inmueble físico.
- **¿Qué hace en el sistema?**:
  - Almacena el vector numérico de variables analíticas asociado $1:1$ con cada registro limpio, funcionando como un **Feature Store** optimizado para consumo de modelos de Machine Learning.

---

### 3.9 `mdm_inmuebles_maestros` (Master Data Management - Golden Record)
- **¿De dónde sale?**:
  - Nace del requerimiento **RF-009** ("Cargar datos limpios en tabla maestra única"), de la regla **RB-003** ("No duplicados") y del marco **DAMA-DMBOK v2** de Gestión de Datos Maestros.
- **¿Qué problema resuelve?**:
  - Diferencia formal entre una **transacción de carga** (un archivo procesado hoy) y el **inmueble físico real** (el apartamento que existe de forma permanente en la Calle 100 de Bogotá).
  - Si se procesan 10 datasets distintos durante un año y todos contienen el mismo apartamento, no queremos 10 filas duplicadas. Mediante la clave calculada:
    $$\text{hash\_duplicado} = \text{SHA256}(\text{direccion\_norm} \parallel \text{tamano} \parallel \text{id\_barrio})$$
    la base de datos forzará unicidad $O(1)$ y consolidará la información bajo reglas de supervivencia (*Survivorship Rules*).
- **¿Qué hace en el sistema?**:
  - Custodia la **Verdad Única y Consolidada (*Single Source of Truth / Golden Record*)** del inventario inmobiliario de Bogotá para consultas y tasaciones masivas.

---

### 3.10 `dim_entorno_urbano` (Dimensión Contextual Espacial)
- **¿De dónde sale?**:
  - Nace de la necesidad de incorporar información contextual distrital (parques, vías principales, colegios, hospitales, centros comerciales y áreas de riesgo por remoción en masa - **RB-005**).
- **¿Qué problema resuelve?**:
  - Aplica el principio de **Alta Cohesión (GRASP)**. El número de habitaciones de un apartamento describe su estructura interna; el número de colegios o parques cercanos describe su entorno urbano externo provisto por capas GIS de IDECA/Catastro.
- **¿Qué hace en el sistema?**:
  - Custodia los atributos del entorno geoespacial asociados $1:1$ al inmueble maestro, permitiendo actualizar las capas de infraestructura urbana sin tener que modificar los datos estructurales del inmueble.

---

### 3.11 `log_rechazos_calidad` (Auditoría Granular de Fallos BPMN 2.0)
- **¿De dónde sale?**:
  - Nace de los 4 Gateways XOR de decisión del diagrama **BPMN 2.0** (G1: Extracción, G2: Formato, G3: Transformación, G4: Calidad) y del requerimiento **RF-010**.
- **¿Qué problema resuelve?**:
  - Evita que los descartes sean invisibles o efímeros. Permite responder con exactitud: *¿Por qué falló el registro? ¿En cuál compuerta BPMN se detuvo? ¿Qué regla violó (RB-001 a RB-005)? ¿Qué valores traía el registro cuando fue rechazado?*
- **¿Qué hace en el sistema?**:
  - Persiste cada descarte con su compuerta BPMN, código de regla, descripción del fallo y el contenido original en formato estructurado `JSONB`, garantizando la dimensión de **Trazabilidad y Calidad (ISO/IEC 25012)**.

---

### 3.12 `rpt_limpieza_ejecucion` (Balance Consolidado del Pipeline)
- **¿De dónde sale?**:
  - Nace de la necesidad operativa de entregar al usuario y al custodio de calidad un balance instantáneo del procesamiento (mostrado en la interfaz Tkinter en `VistaResultado`).
- **¿Qué problema resuelve?**:
  - Si un usuario carga 50,000 filas y quiere ver el balance (cuántos leídos, cuántos limpios, cuántos rechazados, cuántos duplicados, cuántos nulos tratados y tiempo total en segundos), no debe ejecutar consultas de agregación lentas y costosas sobre toda la base de datos.
- **¿Qué hace en el sistema?**:
  - Almacena el resumen pre-calculado de la ejecución en tiempo $O(1)$ asociado $1:1$ con `wrk_datasets_ingesta`.

---

### 3.13 `log_notificaciones` (Auditoría de Notificaciones por Correo)
- **¿De dónde sale?**:
  - Nace de la regla de negocio funcional **RB-006** ("Toda operación de inserción o modificación de datos debe notificar por correo al usuario") y los patrones de diseño *Decorator* y *Observer* aplicados al `EmailService`.
- **¿Qué problema resuelve?**:
  - Brinda soporte auditable ante reclamos del usuario. Si un usuario afirma no haber sido notificado de un rechazo en G3 o de un éxito en MDM, el sistema cuenta con el registro inmutable del despacho.
- **¿Qué hace en el sistema?**:
  - Registra cada correo enviado (destinatario, asunto, estado de despacho `ENVIADO`/`FALLIDO` y timestamp exacto), cerrando el ciclo de comunicación del pipeline.

---

## 4. Matriz de Síntesis: De Dónde Sale y Qué Hace Cada Entidad

| # | Entidad de Base de Datos | ¿De dónde sale? (Origen / Regla) | ¿Qué problema resuelve? | ¿Qué hace en el sistema? (Rol) |
|---|---|---|---|---|
| 1 | `cat_localidades` | 20 Localidades DANE / RB-001 | Redundancia textual y anomalías 3NF | Catálogo inmutable de localidades oficiales. |
| 2 | `cat_barrios` | Columna `ubicacion` / RB-001, RB-002 | Valida límites geográficos de Bogotá | Mapea barrios, centroides y estrato modal. |
| 3 | `cat_tipos_inmueble` | Tipologías heterogéneas de portales | Evita variaciones de texto en ML | Catálogo formal de tipos de inmuebles. |
| 4 | `cat_fuentes_origen` | Multi-formato (CSV/Excel/JSON) / RF-001 | Pérdida de procedencia (ISO 8000) | Identifica y califica la fuente proveedora. |
| 5 | `wrk_datasets_ingesta` | UC-001 / Ingesta de archivos BPMN | Pérdida de contexto del lote ETL | Nodo raíz de trazabilidad del lote cargado. |
| 6 | `stg_inmuebles_raw` | Gateway BPMN G1 / RF-002 | Errores fatales por tipos corruptos | Capa Staging inmutable en formato `TEXT`. |
| 7 | `wrk_inmuebles_cleaned` | Gateways BPMN G1-G3 / RB-001..005 | Mezclar datos sucios con limpios | Almacena registros saneados y tipados. |
| 8 | `fct_features_analiticas` | FeatureAnalyzer / RF-005, RF-011 | Violación de SRP en la tabla de inmuebles | Feature Store de variables derivadas para ML. |
| 9 | `mdm_inmuebles_maestros` | DAMA MDM / RF-009 / RB-003 | Duplicados físicos en múltiples cargas | Golden Record único sin duplicados. |
| 10 | `dim_entorno_urbano` | Amenidades distritales (IDECA/Catastro) | Acoplamiento de contexto externo | Custodia el perfil contextual geoespacial. |
| 11 | `log_rechazos_calidad` | Gateways BPMN G1-G4 / RF-010 | Pérdida de trazabilidad de errores | Auditoría de fallos con payload JSONB. |
| 12 | `rpt_limpieza_ejecucion` | Cierre de pipeline ETL / VistaResultado | Consultas agregadas lentas y costosas | Balance estadístico O(1) de la corrida. |
| 13 | `log_notificaciones` | Regla funcional RB-006 / Decorator | Falta de prueba de comunicaciones | Registro auditable de correos despachados. |

---

## 5. Conclusión y Veredicto Arquitectónico

Cada una de las 13 entidades responde a una **necesidad estricta y justificada del problema**, cumpliendo la máxima del diseño de software:
> *"Una arquitectura no está completa cuando no queda nada más que añadir, sino cuando no queda nada más que se pueda quitar sin comprometer la integridad del sistema."*

El modelo resultante es **completo, trazable, normalizado (BCNF), auditable y 100% alineado con SWEBOK v4, DAMA-DMBOK v2, ISO/IEC 9075, ISO/IEC 11179 e ISO/IEC 25012**.
