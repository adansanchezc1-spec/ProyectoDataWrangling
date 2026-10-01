# 02. Diagrama Lógico Relacional y Proceso de Normalización
**Estándares**: DAMA-DMBOK v2 (Logical Data Model - LDM) · SWEBOK v4 (Data Persistence Design) · ISO/IEC 9075  
**Fase PDCO**: `PLAN → DEVELOPMENT` | **SDLC Stage**: Detailed Database Design  
**Proyecto**: Sistema Data Wrangling & MDM Inmobiliario (Bogotá Real Estate)  
**Última revisión**: 2026-09-28 — Actividad 4: Corrección de coherencia diagrama ↔ script SQL (observación docente)  

> **Corrección Actividad 4**: Se agregaron los campos `created_at DATETIME` a las tablas `cat_localidades` y `cat_barrios` para reflejar exactamente la estructura implementada en `instalacion.sql`. Se añadieron también las restricciones `CHECK` faltantes en `cat_fuentes_origen` y `log_notificaciones`.

---

## 1. Demostración Formal del Proceso de Normalización (1NF → BCNF)

Para garantizar la eliminación total de redundancias, anomalías de inserción, borrado y actualización, el esquema relacional fue derivado mediante análisis formal de **Dependencias Funcionales (DF)** hasta alcanzar la **Forma Normal de Boyce-Codd (BCNF)**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        ESCALA DE NORMALIZACIÓN RELACIONAL                              │
├───────────────────┬───────────────────┬───────────────────┬────────────────────────────┤
│       1NF         │       2NF         │       3NF         │           BCNF             │
│                   │                   │                   │                            │
│• Valores Atómicos │• Cumple 1NF       │• Cumple 2NF       │• Cumple 3NF                │
│• No arrays/listas │• Sin dependencias │• Sin dependencias │• Para toda DF X → Y,       │
│• Clave Primaria   │  parciales de PK  │  transitivas      │  X es una Superclave       │
│  definida         │  compuesta        │  (X → Y → Z)      │  estricta                  │
└───────────────────┴───────────────────┴───────────────────┴────────────────────────────┘
```

### 1.1 Dependencias Funcionales en el Dominio Inmobiliario
Definimos el conjunto de atributos del dominio:
$$U = \{\text{id\_maestro}, \text{direccion}, \text{tamano\_m2}, \text{habitaciones}, \text{banos}, \text{estrato}, \text{precio}, \text{id\_barrio}, \text{nombre\_barrio}, \text{id\_localidad}, \text{nombre\_localidad}, \text{codigo\_dane}\}$$

Conjunto canónico de Dependencias Funcionales ($F$):
1. $DF_1: \text{id\_maestro} \to \{\text{direccion}, \text{tamano\_m2}, \text{habitaciones}, \text{banos}, \text{estrato}, \text{precio}, \text{id\_barrio}\}$
2. $DF_2: \{\text{direccion}, \text{tamano\_m2}, \text{id\_barrio}\} \to \text{id\_maestro}$ *(Clave Candidata / Hash de Unicidad)*
3. $DF_3: \text{id\_barrio} \to \{\text{nombre\_barrio}, \text{estrato\_moda}, \text{latitud}, \text{longitud}, \text{id\_localidad}\}$
4. $DF_4: \text{id\_localidad} \to \{\text{codigo\_dane}, \text{nombre\_localidad}, \text{zona\_bogota}\}$
5. $DF_5: \text{codigo\_dane} \to \{\text{id\_localidad}, \text{nombre\_localidad}, \text{zona\_bogota}\}$

---

### 1.2 Etapas de Descomposición

#### Paso 1: Primera Forma Normal (1NF)
- **Problema en datos crudos**: En el dataset de origen, el atributo `ubicacion` contiene información compuesta no atómica: `"Bogotá, Chapinero, Carrera 7 # 45-10"`.
- **Acción**: Se descompone en componentes atómicos normalizados:
  - `id_localidad` (Identificador discreto)
  - `id_barrio` (Identificador discreto)
  - `direccion_normalizada` (Vía y nomenclatura estandarizada)
- **Resultado 1NF**: Todas las columnas contienen valores escalares indivisibles; no existen listas ni grupos repetitivos.

#### Paso 2: Segunda Forma Normal (2NF)
- **Condición**: Todo atributo no-primo debe tener dependencia funcional completa de la clave primaria (no de subconjuntos de claves primarias compuestas).
- **Acción**: En las tablas del pipeline (`wrk_inmuebles_cleaned`, `fct_features_analiticas`, `mdm_inmuebles_maestros`), se emplean claves primarias subrogadas sintéticas (`BIGINT`, `UUID`) o claves naturales simples.
- **Resultado 2NF**: No existen dependencias parciales de claves compuestas.

#### Paso 3: Tercera Forma Normal (3NF)
- **Problema detectado**: En un diseño desnormalizado inicial existiría la transitividad:
  $$\text{id\_maestro} \xrightarrow{DF_1} \text{id\_barrio} \xrightarrow{DF_3} \text{id\_localidad} \xrightarrow{DF_4} \text{nombre\_localidad}$$
  Esto causaría anomalías de actualización: cambiar el nombre de una localidad obligaría a actualizar millones de filas de inmuebles.
- **Acción**: Descomposición en relaciones independientes sin pérdida de información (*Lossless Join Decomposition*):
  - $R_1(\underline{\text{id\_localidad}}, \text{codigo\_dane}, \text{nombre}, \text{zona\_bogota})$
  - $R_2(\underline{\text{id\_barrio}}, \text{id\_localidad}^*, \text{nombre\_barrio}, \text{estrato\_moda}, \text{latitud}, \text{longitud})$
  - $R_3(\underline{\text{id\_maestro}}, \text{id\_barrio}^*, \text{id\_tipo}^*, \text{direccion\_normalizada}, \text{tamano\_m2}, \dots)$
- **Resultado 3NF**: Se eliminan todas las dependencias transitivas.

#### Paso 4: Forma Normal de Boyce-Codd (BCNF)
- **Condición**: Para cada dependencia funcional no trivial $X \to Y$, el determinante $X$ debe ser una **superclave**.
- **Evaluación**:
  - En $R_1$: $\{\text{id\_localidad}\}$ y $\{\text{codigo\_dane}\}$ son superclaves (ambas únicas). $\checkmark$
  - En $R_2$: $\{\text{id\_barrio}\}$ es superclave. $\checkmark$
  - En $R_3$: $\{\text{id\_maestro}\}$ y $\{\text{hash\_duplicado}\}$ son superclaves. $\checkmark$
- **Resultado BCNF**: El esquema completo satisface BCNF.

---

## 2. Diagrama Lógico Relacional (Mermaid Relational ERD)

A continuación se presenta el esquema relacional con sus tablas, tipos de datos físicos estándar (ISO/IEC 9075), llaves primarias (`PK`), llaves foráneas (`FK`), restricciones de unicidad (`UK`) y relaciones de integridad referencial:

```mermaid
erDiagram
    cat_localidades ||--o{ cat_barrios : "fk_barrio_localidad (RESTRICT)"
    cat_barrios ||--o{ mdm_inmuebles_maestros : "fk_inmueble_barrio (RESTRICT)"
    cat_tipos_inmueble ||--o{ mdm_inmuebles_maestros : "fk_inmueble_tipo (RESTRICT)"
    cat_fuentes_origen ||--o{ wrk_datasets_ingesta : "fk_ingesta_fuente (RESTRICT)"
    
    wrk_datasets_ingesta ||--o{ stg_inmuebles_raw : "fk_raw_dataset (CASCADE)"
    wrk_datasets_ingesta ||--o{ log_rechazos_calidad : "fk_rechazo_dataset (CASCADE)"
    wrk_datasets_ingesta ||--o{ rpt_limpieza_ejecucion : "fk_reporte_dataset (CASCADE)"
    wrk_datasets_ingesta ||--o{ log_notificaciones : "fk_notificacion_dataset (CASCADE)"
    
    stg_inmuebles_raw ||--o| wrk_inmuebles_cleaned : "fk_cleaned_raw (CASCADE)"
    wrk_datasets_ingesta ||--o{ wrk_inmuebles_cleaned : "fk_cleaned_dataset (CASCADE)"
    cat_barrios ||--o{ wrk_inmuebles_cleaned : "fk_cleaned_barrio (RESTRICT)"
    cat_tipos_inmueble ||--o{ wrk_inmuebles_cleaned : "fk_cleaned_tipo (RESTRICT)"
    
    wrk_inmuebles_cleaned ||--o| fct_features_analiticas : "fk_feature_cleaned (CASCADE)"
    mdm_inmuebles_maestros ||--|| dim_entorno_urbano : "fk_entorno_maestro (CASCADE)"

    cat_localidades {
        INT id_localidad PK
        VARCHAR_10 codigo_dane UK
        VARCHAR_100 nombre
        VARCHAR_50 zona_bogota
        DATETIME created_at "DEFAULT CURRENT_TIMESTAMP"
    }

    cat_barrios {
        INT id_barrio PK
        INT id_localidad FK
        VARCHAR_120 nombre_barrio
        SMALLINT estrato_moda
        NUMERIC_10_7 latitud_centroide
        NUMERIC_10_7 longitud_centroide
        DATETIME created_at "DEFAULT CURRENT_TIMESTAMP"
    }

    cat_tipos_inmueble {
        INT id_tipo PK
        VARCHAR_30 codigo UK
        VARCHAR_100 descripcion
    }

    cat_fuentes_origen {
        INT id_fuente PK
        VARCHAR_80 nombre_fuente UK
        VARCHAR_20 tipo_formato_default "CHECK: CSV|EXCEL|JSON|PARQUET|XML"
        VARCHAR_20 estado "CHECK: ACTIVO|INACTIVO — DEFAULT ACTIVO"
    }

    wrk_datasets_ingesta {
        UUID id_dataset PK
        INT id_fuente FK
        VARCHAR_255 nombre_archivo
        CHAR_64 hash_sha256
        VARCHAR_120 usuario_email
        VARCHAR_30 estado_pipeline
        TIMESTAMPTZ fecha_ingesta
    }

    stg_inmuebles_raw {
        BIGINT id_raw PK
        UUID id_dataset FK
        TEXT ubicacion_raw
        TEXT tamano_raw
        TEXT habitaciones_raw
        TEXT banos_raw
        TEXT estrato_raw
        TEXT precio_raw
        TEXT fecha_raw
        TIMESTAMPTZ fecha_extraccion
    }

    wrk_inmuebles_cleaned {
        BIGINT id_cleaned PK
        BIGINT id_raw FK
        UUID id_dataset FK
        INT id_barrio FK
        INT id_tipo FK
        NUMERIC_10_2 tamano_m2
        SMALLINT habitaciones
        SMALLINT banos
        SMALLINT estrato
        NUMERIC_14_2 precio_cop
        SMALLINT anio_registro
        BOOLEAN es_valido
    }

    fct_features_analiticas {
        BIGINT id_feature PK
        BIGINT id_cleaned FK
        NUMERIC_14_2 precio_unitario_m2
        INT puntaje_entorno
        NUMERIC_5_2 bano_por_hab_ratio
        NUMERIC_8_4 densidad_comercial
        NUMERIC_8_4 parqueadero_ratio
        NUMERIC_12_4 factor_precio_millones
    }

    mdm_inmuebles_maestros {
        UUID id_maestro PK
        INT id_barrio FK
        INT id_tipo FK
        VARCHAR_200 direccion_normalizada
        NUMERIC_10_2 tamano_m2
        SMALLINT habitaciones
        SMALLINT banos
        SMALLINT estrato
        NUMERIC_14_2 precio_ultimo_cop
        NUMERIC_14_2 precio_unitario_m2
        SMALLINT anio_construccion_referencia
        NUMERIC_10_7 latitud_corregida
        NUMERIC_10_7 longitud_corregida
        CHAR_64 hash_duplicado UK
        TIMESTAMPTZ fecha_consolidacion
    }

    dim_entorno_urbano {
        BIGINT id_entorno PK
        UUID id_maestro FK
        INT parques_cercanos
        INT vias_principales
        NUMERIC_10_2 area_remocion_masa_m2
        INT grandes_superficies
        INT colegios_cercanos
        INT hospitales_cercanos
        INT puntaje_amenidades
    }

    log_rechazos_calidad {
        BIGINT id_rechazo PK
        UUID id_dataset FK
        VARCHAR_10 compuerta_bpmn
        VARCHAR_20 codigo_regla
        TEXT motivo_error
        JSONB payload_registro
        TIMESTAMPTZ fecha_rechazo
    }

    rpt_limpieza_ejecucion {
        BIGINT id_reporte PK
        UUID id_dataset FK
        INT total_registros_raw
        INT total_registros_limpios
        INT total_rechazados
        INT total_duplicados_eliminados
        INT total_nulos_imputados
        NUMERIC_8_3 tiempo_ejecucion_seg
        TIMESTAMPTZ fecha_generacion
    }

    log_notificaciones {
        BIGINT id_notificacion PK
        UUID id_dataset FK
        VARCHAR_120 email_destinatario
        VARCHAR_200 asunto
        VARCHAR_30 estado_envio "CHECK: ENVIADO|FALLIDO|PENDIENTE"
        DATETIME fecha_envio "DEFAULT CURRENT_TIMESTAMP"
    }
```

---

## 3. Políticas de Integridad Referencial

1. **`ON DELETE RESTRICT` (Protección de Integridad Maestra y Catálogos)**:
   - No es posible eliminar una localidad si existen barrios asociados (`cat_barrios.id_localidad`).
   - No es posible eliminar un barrio si existen inmuebles limpios o maestros asociados (`mdm_inmuebles_maestros.id_barrio`).
2. **`ON DELETE CASCADE` (Ciclo de Vida de Ingesta y Limpieza)**:
   - Si se elimina un lote de ingesta en `wrk_datasets_ingesta`, automáticamente se eliminan sus filas en staging (`stg_inmuebles_raw`), sus registros limpios (`wrk_inmuebles_cleaned`), sus features analíticas (`fct_features_analiticas`) y sus reportes/rechazos asociados, evitando registros huérfanos.
   - Si se elimina un inmueble maestro (`mdm_inmuebles_maestros`), su dimensión de entorno (`dim_entorno_urbano`) se elimina en cascada.
3. **`ON UPDATE CASCADE`**:
   - Cualquier actualización en claves primarias o códigos de referencia se propaga automáticamente a todas las tablas dependientes.
