-- ============================================================================
-- SECCIÓN 0: IDENTIFICACIÓN DEL PROYECTO
-- ============================================================================
-- Proyecto      : Sistema Data Wrangling & Master Data Management (MDM)
--                 Inmobiliario — Bogotá Real Estate
-- Actividad     : 4 — Implementación Física, Validación y Pruebas SQL
-- Integrantes   : Adán Y. Sánchez Cubillos
--                 [Nombre completo integrante 2 — Marles]
--                 [Nombre completo integrante 3 — Pineda]
-- Universidad   : Universidad de La Salle
-- Asignatura    : Lenguaje y Modelado de Datos
-- SGBD          : MySQL Server 8.0.x / 8.4 LTS
-- Versión MySQL : 8.0 (Compatible con XAMPP / MySQL Workbench / phpMyAdmin)
-- Charset       : utf8mb4 / COLLATE utf8mb4_unicode_ci
-- Fecha         : 2026-09-28
-- Estándares    : DAMA-DMBOK v2 · ISO/IEC 9075 · IEEE 830
-- ----------------------------------------------------------------------------
-- ADVERTENCIA DE USO SEGURO:
--   Este script está diseñado EXCLUSIVAMENTE para ejecutarse en una base de
--   datos LOCAL de laboratorio creada para esta actividad académica.
--   NO ejecutar sobre bases de datos institucionales, empresariales,
--   compartidas o que contengan información real.
--   Todos los datos incluidos son 100% ficticios con propósito de prueba.
-- ============================================================================


-- ============================================================================
-- SECCIÓN 1: CREACIÓN Y SELECCIÓN DE LA BASE DE DATOS
-- ============================================================================
-- Se crea la base de datos si no existe, configurando el juego de caracteres
-- utf8mb4 para soporte completo de Unicode (tildes, ñ, emojis) y la
-- collation unicode_ci para comparaciones insensibles a mayúsculas/minúsculas.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS sistema_data_wrangling
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Seleccionar el esquema de trabajo para todas las sentencias posteriores
USE sistema_data_wrangling;


-- ============================================================================
-- SECCIÓN 2: LIMPIEZA PREVIA — DROP TABLE EN ORDEN INVERSO DE DEPENDENCIAS
-- ============================================================================
-- Se deshabilita temporalmente la revisión de claves foráneas para poder
-- eliminar las tablas en cualquier orden sin errores de integridad referencial.
-- El orden inverso garantiza que las tablas dependientes se eliminen primero.
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 0;

-- Grupo D: Auditoría y Notificaciones (dependientes de wrk_datasets_ingesta)
DROP TABLE IF EXISTS log_notificaciones;
DROP TABLE IF EXISTS rpt_limpieza_ejecucion;
DROP TABLE IF EXISTS log_rechazos_calidad;

-- Grupo C: Master Data Management
DROP TABLE IF EXISTS dim_entorno_urbano;
DROP TABLE IF EXISTS mdm_inmuebles_maestros;

-- Grupo B: Pipeline ETL
DROP TABLE IF EXISTS fct_features_analiticas;
DROP TABLE IF EXISTS wrk_inmuebles_cleaned;
DROP TABLE IF EXISTS stg_inmuebles_raw;
DROP TABLE IF EXISTS wrk_datasets_ingesta;

-- Grupo A: Catálogos y Datos de Referencia (sin dependencias entrantes)
DROP TABLE IF EXISTS cat_fuentes_origen;
DROP TABLE IF EXISTS cat_tipos_inmueble;
DROP TABLE IF EXISTS cat_barrios;
DROP TABLE IF EXISTS cat_localidades;

SET FOREIGN_KEY_CHECKS = 1;


-- ============================================================================
-- SECCIÓN 3: CREACIÓN DE TABLAS EN ORDEN DE DEPENDENCIAS
-- ============================================================================
-- El orden de creación respeta las dependencias de claves foráneas:
-- primero las tablas padre (sin FK entrantes) y luego las tablas hijo.
-- Cada tabla incluye: tipos de datos, obligatoriedad (NOT NULL), valores
-- predeterminados, claves primarias, foráneas, unicidad y restricciones CHECK.
-- ============================================================================


-- ============================================================================
-- GRUPO A: CATÁLOGOS Y DATOS DE REFERENCIA (REFERENCE DATA)
-- Sin dependencias de claves foráneas. Son las tablas "padre" del modelo.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 3.1 cat_localidades — Catálogo de las 20 Localidades Oficiales de Bogotá D.C.
-- Fuente de referencia: División político-administrativa DANE (Código DANE).
-- ----------------------------------------------------------------------------
CREATE TABLE cat_localidades (
    id_localidad   INT            AUTO_INCREMENT PRIMARY KEY     COMMENT 'Identificador subrogado de localidad',
    codigo_dane    VARCHAR(10)    NOT NULL UNIQUE                COMMENT 'Código oficial DANE (ej. 1101 para Usaquén)',
    nombre         VARCHAR(100)   NOT NULL                       COMMENT 'Nombre oficial de la localidad',
    zona_bogota    VARCHAR(50)    NOT NULL                       COMMENT 'Zona geográfica: Norte, Sur, Centro, Occidente, Chapinero',
    created_at     DATETIME       DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT 'Timestamp de inserción del registro'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Catálogo oficial de las 20 localidades de Bogotá D.C. según DANE';

-- ----------------------------------------------------------------------------
-- 3.2 cat_barrios — Catálogo de Barrios y Sectores de Bogotá
-- Depende de: cat_localidades (FK obligatoria 1:N).
-- Restricciones: estrato en [1-6], coordenadas dentro del polígono de Bogotá.
-- ----------------------------------------------------------------------------
CREATE TABLE cat_barrios (
    id_barrio           INT            AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador subrogado de barrio',
    id_localidad        INT            NOT NULL                   COMMENT 'FK → cat_localidades: localidad contenedora',
    nombre_barrio       VARCHAR(120)   NOT NULL                   COMMENT 'Nombre del barrio o sector geográfico',
    estrato_moda        SMALLINT       NOT NULL                   COMMENT 'Estrato socioeconómico modal del barrio (1 a 6)',
    latitud_centroide   DECIMAL(10,7)  NOT NULL                   COMMENT 'Latitud del centroide del barrio (WGS84)',
    longitud_centroide  DECIMAL(10,7)  NOT NULL                   COMMENT 'Longitud del centroide del barrio (WGS84)',
    created_at          DATETIME       DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT 'Timestamp de inserción',
    CONSTRAINT fk_barrio_localidad FOREIGN KEY (id_localidad)
        REFERENCES cat_localidades (id_localidad) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_barrio_estrato   CHECK (estrato_moda BETWEEN 1 AND 6),
    CONSTRAINT chk_barrio_latitud   CHECK (latitud_centroide  BETWEEN  4.4500000 AND  4.8500000),
    CONSTRAINT chk_barrio_longitud  CHECK (longitud_centroide BETWEEN -74.2500000 AND -73.9500000)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Catálogo de barrios y sectores de Bogotá con coordenadas y estrato';

-- ----------------------------------------------------------------------------
-- 3.3 cat_tipos_inmueble — Catálogo de Tipologías de Inmueble
-- Catálogo cerrado y normalizado para la clasificación física del inmueble.
-- ----------------------------------------------------------------------------
CREATE TABLE cat_tipos_inmueble (
    id_tipo     INT          AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador subrogado del tipo de inmueble',
    codigo      VARCHAR(30)  NOT NULL UNIQUE            COMMENT 'Código único del tipo (ej. APARTAMENTO, CASA)',
    descripcion VARCHAR(100) NOT NULL                   COMMENT 'Descripción tipológica completa'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Catálogo cerrado de tipologías de inmueble residencial';

-- ----------------------------------------------------------------------------
-- 3.4 cat_fuentes_origen — Catálogo de Fuentes de Datos Inmobiliarios
-- Registra las fuentes institucionales o comerciales de cada dataset ingestado.
-- CORRECCIÓN ACTIVIDAD 4: Se agregan CHECK sobre formato y estado (observación docente).
-- ----------------------------------------------------------------------------
CREATE TABLE cat_fuentes_origen (
    id_fuente             INT          AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador subrogado de la fuente',
    nombre_fuente         VARCHAR(80)  NOT NULL UNIQUE            COMMENT 'Nombre descriptivo único de la fuente de datos',
    tipo_formato_default  VARCHAR(20)  NOT NULL                   COMMENT 'Formato de archivo esperado: CSV, EXCEL, JSON, PARQUET, XML',
    estado                VARCHAR(20)  DEFAULT 'ACTIVO' NOT NULL  COMMENT 'Estado operativo de la fuente: ACTIVO o INACTIVO',
    -- CORRECCIÓN: Restricciones CHECK faltantes identificadas en revisión de Actividad 4
    CONSTRAINT chk_fuente_formato CHECK (tipo_formato_default IN ('CSV', 'EXCEL', 'JSON', 'PARQUET', 'XML')),
    CONSTRAINT chk_fuente_estado  CHECK (estado IN ('ACTIVO', 'INACTIVO'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Catálogo de fuentes de origen de datasets inmobiliarios';


-- ============================================================================
-- GRUPO B: PIPELINE ETL — TABLAS TRANSACCIONALES DE INGESTA Y PROCESAMIENTO
-- Representan las capas del proceso de Data Wrangling: raw → cleaned → features.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 3.5 wrk_datasets_ingesta — Registro de Lotes de Ingesta (Metadatos ETL)
-- Cada fila representa un archivo completo procesado por el pipeline.
-- El id_dataset es un UUID v4 generado por la aplicación.
-- ----------------------------------------------------------------------------
CREATE TABLE wrk_datasets_ingesta (
    id_dataset      VARCHAR(36)   PRIMARY KEY                    COMMENT 'UUID v4 — identificador único del lote de ingesta',
    id_fuente       INT           NOT NULL                       COMMENT 'FK → cat_fuentes_origen: fuente del archivo',
    nombre_archivo  VARCHAR(255)  NOT NULL                       COMMENT 'Nombre físico del archivo fuente',
    hash_sha256     CHAR(64)      NOT NULL                       COMMENT 'Firma SHA-256 del archivo para verificación de integridad',
    usuario_email   VARCHAR(120)  NOT NULL                       COMMENT 'Correo del analista responsable de la ingesta',
    estado_pipeline VARCHAR(30)   DEFAULT 'CARGADO' NOT NULL     COMMENT 'Estado del lote dentro del pipeline ETL',
    fecha_ingesta   DATETIME      DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT 'Timestamp de carga del archivo al sistema',
    CONSTRAINT fk_ingesta_fuente FOREIGN KEY (id_fuente)
        REFERENCES cat_fuentes_origen (id_fuente) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_ingesta_estado CHECK (
        estado_pipeline IN ('CARGADO','EXTRAYENDO','VALIDANDO','TRANSFORMANDO','PERFILANDO','COMPLETADO','RECHAZADO')
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Metadatos y estado de cada lote de archivo procesado por el pipeline ETL';

-- ----------------------------------------------------------------------------
-- 3.6 stg_inmuebles_raw — Capa Staging: Datos Crudos Sin Transformar
-- Todos los campos de atributo son TEXT para preservar exactamente el valor
-- original de la fuente, sin coerción de tipo ni validación de dominio.
-- ----------------------------------------------------------------------------
CREATE TABLE stg_inmuebles_raw (
    id_raw           BIGINT    AUTO_INCREMENT PRIMARY KEY      COMMENT 'Identificador subrogado del registro crudo',
    id_dataset       VARCHAR(36) NOT NULL                      COMMENT 'FK → wrk_datasets_ingesta: lote de origen',
    ubicacion_raw    TEXT                                      COMMENT 'Texto original del campo ubicación/dirección',
    tamano_raw       TEXT                                      COMMENT 'Texto original del campo tamaño/área',
    habitaciones_raw TEXT                                      COMMENT 'Texto original del campo habitaciones',
    banos_raw        TEXT                                      COMMENT 'Texto original del campo baños',
    estrato_raw      TEXT                                      COMMENT 'Texto original del campo estrato',
    precio_raw       TEXT                                      COMMENT 'Texto original del campo precio',
    fecha_raw        TEXT                                      COMMENT 'Texto original del campo fecha o año',
    fecha_extraccion DATETIME  DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT 'Timestamp de lectura desde la fuente',
    CONSTRAINT fk_raw_dataset FOREIGN KEY (id_dataset)
        REFERENCES wrk_datasets_ingesta (id_dataset) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Capa staging: registros inmobiliarios exactamente como vienen de la fuente (TEXT sin transformar)';

-- ----------------------------------------------------------------------------
-- 3.7 wrk_inmuebles_cleaned — Capa Working: Datos Normalizados y Validados
-- Solo los registros que superan las compuertas G1, G2 y G3 del BPMN llegan
-- a esta tabla. Los rechazados quedan solo en stg_inmuebles_raw.
-- Relación 1:1 con stg_inmuebles_raw (un raw solo puede limpiar una vez).
-- ----------------------------------------------------------------------------
CREATE TABLE wrk_inmuebles_cleaned (
    id_cleaned    BIGINT        AUTO_INCREMENT PRIMARY KEY     COMMENT 'Identificador subrogado del registro saneado',
    id_raw        BIGINT        NOT NULL UNIQUE                COMMENT 'FK → stg_inmuebles_raw (1:1 obligatorio)',
    id_dataset    VARCHAR(36)   NOT NULL                       COMMENT 'FK → wrk_datasets_ingesta: lote ETL de origen',
    id_barrio     INT           NOT NULL                       COMMENT 'FK → cat_barrios: barrio normalizado',
    id_tipo       INT           NOT NULL                       COMMENT 'FK → cat_tipos_inmueble: tipología normalizada',
    tamano_m2     DECIMAL(10,2) NOT NULL                       COMMENT 'Área útil construida en m² (>0 y ≤50000)',
    habitaciones  SMALLINT      NOT NULL                       COMMENT 'Cantidad de habitaciones (1 a 20)',
    banos         SMALLINT      NOT NULL                       COMMENT 'Cantidad de baños (1 a 15)',
    estrato       SMALLINT      NOT NULL                       COMMENT 'Estrato socioeconómico validado (1 a 6)',
    precio_cop    DECIMAL(14,2) NOT NULL                       COMMENT 'Precio en pesos colombianos (>0)',
    anio_registro SMALLINT      NOT NULL                       COMMENT 'Año de publicación o registro (1900 a 2026)',
    es_valido     TINYINT(1)    DEFAULT 1 NOT NULL             COMMENT 'Flag de completitud: 1=válido, 0=incompleto',
    CONSTRAINT fk_cleaned_raw     FOREIGN KEY (id_raw)     REFERENCES stg_inmuebles_raw    (id_raw)     ON DELETE CASCADE  ON UPDATE CASCADE,
    CONSTRAINT fk_cleaned_dataset FOREIGN KEY (id_dataset) REFERENCES wrk_datasets_ingesta (id_dataset) ON DELETE CASCADE  ON UPDATE CASCADE,
    CONSTRAINT fk_cleaned_barrio  FOREIGN KEY (id_barrio)  REFERENCES cat_barrios          (id_barrio)  ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_cleaned_tipo    FOREIGN KEY (id_tipo)    REFERENCES cat_tipos_inmueble   (id_tipo)    ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_cleaned_estrato CHECK (estrato       BETWEEN 1 AND 6),
    CONSTRAINT chk_cleaned_tamano  CHECK (tamano_m2     > 0 AND tamano_m2  <= 50000.00),
    CONSTRAINT chk_cleaned_habs    CHECK (habitaciones  BETWEEN 1 AND 20),
    CONSTRAINT chk_cleaned_banos   CHECK (banos         BETWEEN 1 AND 15),
    CONSTRAINT chk_cleaned_precio  CHECK (precio_cop    > 0 AND precio_cop <= 50000000000.00),
    CONSTRAINT chk_cleaned_anio    CHECK (anio_registro BETWEEN 1900 AND 2026)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Capa working: registros que superaron las compuertas BPMN G1-G3 con tipos y dominios validados';

-- ----------------------------------------------------------------------------
-- 3.8 fct_features_analiticas — Variables Calculadas para Machine Learning
-- Relación 1:1 con wrk_inmuebles_cleaned. Todo registro limpio genera su
-- vector de features para entrenamiento y scoring de modelos predictivos.
-- ----------------------------------------------------------------------------
CREATE TABLE fct_features_analiticas (
    id_feature              BIGINT        AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador subrogado del vector de features',
    id_cleaned              BIGINT        NOT NULL UNIQUE            COMMENT 'FK → wrk_inmuebles_cleaned (1:1)',
    precio_unitario_m2      DECIMAL(14,2) NOT NULL                   COMMENT 'precio_cop / tamano_m2 — COP por metro cuadrado',
    puntaje_entorno         INT           NOT NULL                   COMMENT 'Suma ponderada de amenidades del entorno',
    bano_por_hab_ratio      DECIMAL(5,2)  NOT NULL                   COMMENT 'Ratio baños / habitaciones (≥ 0)',
    densidad_comercial      DECIMAL(8,4)  NOT NULL                   COMMENT 'Grandes superficies en radio / m² del barrio',
    parqueadero_ratio       DECIMAL(8,4)  NOT NULL                   COMMENT 'Cupos de parqueo disponibles / área total',
    factor_precio_millones  DECIMAL(12,4) DEFAULT 1.0000 NOT NULL    COMMENT 'Factor de escala para modelos en millones COP',
    CONSTRAINT fk_feature_cleaned FOREIGN KEY (id_cleaned)
        REFERENCES wrk_inmuebles_cleaned (id_cleaned) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_feature_ratio CHECK (bano_por_hab_ratio >= 0.0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Variables de feature engineering calculadas para cada registro limpio — insumo para modelos ML';


-- ============================================================================
-- GRUPO C: MASTER DATA MANAGEMENT (MDM) — GOLDEN RECORD
-- Registro maestro unificado que consolida la mejor versión de cada inmueble.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 3.9 mdm_inmuebles_maestros — Registro Maestro Consolidado (Golden Record)
-- Es la tabla central del MDM. El hash_duplicado garantiza la deduplicación:
-- SHA256(direccion_normalizada || tamano_m2 || id_barrio).
-- ----------------------------------------------------------------------------
CREATE TABLE mdm_inmuebles_maestros (
    id_maestro                    VARCHAR(36)   PRIMARY KEY    COMMENT 'UUID v4 — identificador único del inmueble maestro',
    id_barrio                     INT           NOT NULL       COMMENT 'FK → cat_barrios: ubicación final validada',
    id_tipo                       INT           NOT NULL       COMMENT 'FK → cat_tipos_inmueble: tipología consolidada',
    direccion_normalizada         VARCHAR(200)  NOT NULL       COMMENT 'Dirección en nomenclatura limpia estándar Bogotá',
    tamano_m2                     DECIMAL(10,2) NOT NULL       COMMENT 'Área consolidada en m² (> 0)',
    habitaciones                  SMALLINT      NOT NULL       COMMENT 'Número de habitaciones del golden record',
    banos                         SMALLINT      NOT NULL       COMMENT 'Número de baños del golden record',
    estrato                       SMALLINT      NOT NULL       COMMENT 'Estrato socioeconómico validado (1 a 6)',
    precio_ultimo_cop             DECIMAL(14,2) NOT NULL       COMMENT 'Último precio observado en COP (> 0)',
    precio_unitario_m2            DECIMAL(14,2) NOT NULL       COMMENT 'precio_ultimo_cop / tamano_m2',
    anio_construccion_referencia  SMALLINT      NULL           COMMENT 'Año de construcción aproximado (puede ser NULL si desconocido)',
    latitud_corregida             DECIMAL(10,7) NOT NULL       COMMENT 'Latitud calibrada del inmueble (WGS84)',
    longitud_corregida            DECIMAL(10,7) NOT NULL       COMMENT 'Longitud calibrada del inmueble (WGS84)',
    hash_duplicado                CHAR(64)      NOT NULL UNIQUE COMMENT 'SHA256 para detección de duplicados exactos',
    fecha_consolidacion           DATETIME      DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT 'Timestamp de creación o última actualización del golden record',
    CONSTRAINT fk_inmueble_barrio  FOREIGN KEY (id_barrio) REFERENCES cat_barrios       (id_barrio) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_inmueble_tipo    FOREIGN KEY (id_tipo)   REFERENCES cat_tipos_inmueble (id_tipo)  ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_maestro_estrato  CHECK (estrato            BETWEEN 1 AND 6),
    CONSTRAINT chk_maestro_tamano   CHECK (tamano_m2          > 0),
    CONSTRAINT chk_maestro_precio   CHECK (precio_ultimo_cop  > 0),
    CONSTRAINT chk_maestro_latitud  CHECK (latitud_corregida  BETWEEN  4.4500000 AND  4.8500000),
    CONSTRAINT chk_maestro_longitud CHECK (longitud_corregida BETWEEN -74.2500000 AND -73.9500000)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Golden Record del MDM: versión maestra, unificada y deduplicada de cada inmueble en Bogotá';

-- ----------------------------------------------------------------------------
-- 3.10 dim_entorno_urbano — Dimensión de Contexto Urbano por Inmueble
-- Relación 1:1 con mdm_inmuebles_maestros. Cada golden record tiene exactamente
-- un perfil de entorno que describe la infraestructura urbana circundante.
-- ----------------------------------------------------------------------------
CREATE TABLE dim_entorno_urbano (
    id_entorno           BIGINT        AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador subrogado del perfil de entorno',
    id_maestro           VARCHAR(36)   NOT NULL UNIQUE            COMMENT 'FK → mdm_inmuebles_maestros (1:1 obligatorio)',
    parques_cercanos     INT           DEFAULT 0 NOT NULL         COMMENT 'Parques en radio ≤ 1 km del inmueble (≥ 0)',
    vias_principales     INT           DEFAULT 0 NOT NULL         COMMENT 'Vías arteriales o troncales cercanas (≥ 0)',
    area_remocion_masa_m2 DECIMAL(10,2) DEFAULT 0.00 NOT NULL     COMMENT 'Área en zona de riesgo por remoción en masa (m²) (≥ 0)',
    grandes_superficies  INT           DEFAULT 0 NOT NULL         COMMENT 'Centros comerciales / hipermercados en radio 2 km (≥ 0)',
    colegios_cercanos    INT           DEFAULT 0 NOT NULL         COMMENT 'Colegios o instituciones educativas en radio 1 km (≥ 0)',
    hospitales_cercanos  INT           DEFAULT 0 NOT NULL         COMMENT 'Hospitales o clínicas en radio 2 km (≥ 0)',
    puntaje_amenidades   INT           DEFAULT 0 NOT NULL         COMMENT 'Score agregado ponderado de amenidades (suma de factores)',
    CONSTRAINT fk_entorno_maestro  FOREIGN KEY (id_maestro)
        REFERENCES mdm_inmuebles_maestros (id_maestro) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_entorno_parques  CHECK (parques_cercanos      >= 0),
    CONSTRAINT chk_entorno_vias     CHECK (vias_principales      >= 0),
    CONSTRAINT chk_entorno_riesgo   CHECK (area_remocion_masa_m2 >= 0.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Perfil de entorno urbano contextual: infraestructura y servicios cercanos al inmueble maestro';


-- ============================================================================
-- GRUPO D: CALIDAD, AUDITORÍA Y NOTIFICACIONES
-- Tablas de soporte operacional del pipeline ETL.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 3.11 log_rechazos_calidad — Log Granular de Registros Rechazados
-- Cada fila documenta un fallo en una compuerta BPMN (G1 a G4) con su
-- código de regla violada y el payload JSON del registro problemático.
-- ----------------------------------------------------------------------------
CREATE TABLE log_rechazos_calidad (
    id_rechazo       BIGINT      AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador subrogado del rechazo',
    id_dataset       VARCHAR(36) NOT NULL                   COMMENT 'FK → wrk_datasets_ingesta: lote en que ocurrió el fallo',
    compuerta_bpmn   VARCHAR(10) NOT NULL                   COMMENT 'Compuerta BPMN que detectó el fallo: G1, G2, G3 o G4',
    codigo_regla     VARCHAR(20) NOT NULL                   COMMENT 'Código de la regla de negocio violada (ej. RB-003)',
    motivo_error     TEXT        NOT NULL                   COMMENT 'Descripción técnica de la excepción detectada',
    payload_registro JSON        NULL                       COMMENT 'Carga útil del registro original en formato JSON (para trazabilidad)',
    fecha_rechazo    DATETIME    DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT 'Timestamp del evento de rechazo',
    CONSTRAINT fk_rechazo_dataset    FOREIGN KEY (id_dataset)
        REFERENCES wrk_datasets_ingesta (id_dataset) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_rechazo_compuerta CHECK (compuerta_bpmn IN ('G1','G2','G3','G4'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Log de auditoría: registros rechazados por violación de reglas en compuertas BPMN del pipeline';

-- ----------------------------------------------------------------------------
-- 3.12 rpt_limpieza_ejecucion — Balance Consolidado de Ejecución ETL
-- Un único reporte por dataset (UNIQUE en id_dataset) con los KPIs agregados
-- de cada ejecución del pipeline: total procesados, rechazados, tiempos, etc.
-- ----------------------------------------------------------------------------
CREATE TABLE rpt_limpieza_ejecucion (
    id_reporte                  BIGINT        AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador subrogado del reporte de ejecución',
    id_dataset                  VARCHAR(36)   NOT NULL UNIQUE            COMMENT 'FK → wrk_datasets_ingesta (1:1 por ejecución)',
    total_registros_raw         INT           NOT NULL                   COMMENT 'Total de registros leídos en la capa staging',
    total_registros_limpios     INT           NOT NULL                   COMMENT 'Total de registros que superaron las compuertas BPMN',
    total_rechazados            INT           NOT NULL                   COMMENT 'Total de registros descartados por violaciones',
    total_duplicados_eliminados INT           NOT NULL                   COMMENT 'Total de duplicados detectados y eliminados (hash)',
    total_nulos_imputados       INT           NOT NULL                   COMMENT 'Total de valores nulos tratados por imputación',
    tiempo_ejecucion_seg        DECIMAL(8,3)  NOT NULL                   COMMENT 'Latencia total del pipeline en segundos',
    fecha_generacion            DATETIME      DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT 'Timestamp de generación del reporte',
    CONSTRAINT fk_reporte_dataset FOREIGN KEY (id_dataset)
        REFERENCES wrk_datasets_ingesta (id_dataset) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='KPIs agregados de cada ejecución ETL: métricas de calidad, cobertura y rendimiento del pipeline';

-- ----------------------------------------------------------------------------
-- 3.13 log_notificaciones — Log de Notificaciones Despachadas
-- Registra el envío de alertas por correo al analista responsable al finalizar
-- cada pipeline, con el asunto, estado y timestamp de despacho.
-- CORRECCIÓN ACTIVIDAD 4: Se agrega CHECK sobre estado_envio (observación docente).
-- ----------------------------------------------------------------------------
CREATE TABLE log_notificaciones (
    id_notificacion   BIGINT       AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador subrogado de la notificación',
    id_dataset        VARCHAR(36)  NOT NULL                   COMMENT 'FK → wrk_datasets_ingesta: pipeline que disparó la alerta',
    email_destinatario VARCHAR(120) NOT NULL                  COMMENT 'Correo electrónico del analista destinatario',
    asunto            VARCHAR(200) NOT NULL                   COMMENT 'Asunto del mensaje de notificación',
    estado_envio      VARCHAR(30)  DEFAULT 'ENVIADO' NOT NULL COMMENT 'Estado del despacho: ENVIADO, FALLIDO o PENDIENTE',
    fecha_envio       DATETIME     DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT 'Timestamp de despacho de la notificación',
    CONSTRAINT fk_notificacion_dataset FOREIGN KEY (id_dataset)
        REFERENCES wrk_datasets_ingesta (id_dataset) ON DELETE CASCADE ON UPDATE CASCADE,
    -- CORRECCIÓN: CHECK faltante identificado en revisión de Actividad 4
    CONSTRAINT chk_notif_estado CHECK (estado_envio IN ('ENVIADO','FALLIDO','PENDIENTE'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Log de notificaciones: registro de alertas enviadas al analista al completar o rechazar cada pipeline';


-- ============================================================================
-- SECCIÓN 4: ÍNDICES DE RENDIMIENTO (ISO/IEC 25010 — Eficiencia de Desempeño)
-- ============================================================================
-- Los índices aceleran las consultas frecuentes del pipeline y los reportes.
-- Se crean índices sobre columnas usadas en JOINs, filtros WHERE y ORDER BY.
-- ============================================================================

-- Índices sobre la capa staging para búsquedas por dataset
CREATE INDEX idx_raw_dataset          ON stg_inmuebles_raw        (id_dataset);

-- Índices sobre la capa cleaning para los filtros operativos más comunes
CREATE INDEX idx_cleaned_dataset      ON wrk_inmuebles_cleaned     (id_dataset);
CREATE INDEX idx_cleaned_barrio       ON wrk_inmuebles_cleaned     (id_barrio);
CREATE INDEX idx_cleaned_estrato      ON wrk_inmuebles_cleaned     (estrato);
CREATE INDEX idx_cleaned_precio       ON wrk_inmuebles_cleaned     (precio_cop);
CREATE INDEX idx_cleaned_anio         ON wrk_inmuebles_cleaned     (anio_registro);

-- Índices sobre el golden record para búsquedas geoespaciales y de barrio
CREATE INDEX idx_maestro_barrio       ON mdm_inmuebles_maestros    (id_barrio);
CREATE INDEX idx_maestro_coords       ON mdm_inmuebles_maestros    (latitud_corregida, longitud_corregida);
CREATE INDEX idx_maestro_estrato      ON mdm_inmuebles_maestros    (estrato);

-- Índice compuesto para consultas de auditoría por dataset y compuerta BPMN
CREATE INDEX idx_rechazo_dataset_gw   ON log_rechazos_calidad      (id_dataset, compuerta_bpmn);


-- ============================================================================
-- SECCIÓN 5: CARGA INICIAL CON DATOS COMPLETAMENTE FICTICIOS (SEED DATA)
-- ============================================================================
-- TODOS los datos a continuación son 100% ficticios, generados con propósito
-- exclusivo de demostración y prueba académica. No representan personas,
-- empresas, inmuebles o transacciones reales.
-- Se usan dos datasets de ingesta para demostrar relaciones entre lotes.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 5.1 — 20 Localidades Oficiales de Bogotá D.C. (Datos públicos DANE)
-- Los nombres y códigos son de referencia pública; no constituyen dato personal.
-- ----------------------------------------------------------------------------
INSERT INTO cat_localidades (id_localidad, codigo_dane, nombre, zona_bogota) VALUES
( 1, '1101', 'Usaquén',            'Norte'),
( 2, '1102', 'Chapinero',          'Chapinero'),
( 3, '1103', 'Santa Fe',           'Centro'),
( 4, '1104', 'San Cristóbal',      'Sur'),
( 5, '1105', 'Usme',               'Sur'),
( 6, '1106', 'Tunjuelito',         'Sur'),
( 7, '1107', 'Bosa',               'Sur'),
( 8, '1108', 'Kennedy',            'Occidente'),
( 9, '1109', 'Fontibón',           'Occidente'),
(10, '1110', 'Engativá',           'Occidente'),
(11, '1111', 'Suba',               'Norte'),
(12, '1112', 'Barrios Unidos',     'Norte'),
(13, '1113', 'Teusaquillo',        'Centro'),
(14, '1114', 'Los Mártires',       'Centro'),
(15, '1115', 'Antonio Nariño',     'Sur'),
(16, '1116', 'Puente Aranda',      'Centro'),
(17, '1117', 'La Candelaria',      'Centro'),
(18, '1118', 'Rafael Uribe Uribe', 'Sur'),
(19, '1119', 'Ciudad Bolívar',     'Sur'),
(20, '1120', 'Sumapaz',            'Sur');

-- ----------------------------------------------------------------------------
-- 5.2 — 8 Barrios Ficticios de Prueba (nombres y coordenadas ficticios)
-- Cubren 5 localidades distintas para demostrar relaciones entre tablas.
-- ----------------------------------------------------------------------------
INSERT INTO cat_barrios (id_barrio, id_localidad, nombre_barrio, estrato_moda, latitud_centroide, longitud_centroide) VALUES
(1,  2, 'Chapinero Alto',    4, 4.6450000, -74.0580000),
(2,  1, 'Cedritos',          4, 4.7230000, -74.0320000),
(3, 11, 'Niza Sur',          5, 4.7100000, -74.0720000),
(4, 13, 'Galerías',          4, 4.6410000, -74.0750000),
(5,  8, 'Castilla',          3, 4.6480000, -74.1480000),
(6,  8, 'Tintal Sur',        2, 4.6320000, -74.1600000),
(7,  4, 'Altamira Sur',      2, 4.5710000, -74.0980000),
(8, 10, 'Santa Cecilia',     3, 4.6980000, -74.1010000);

-- ----------------------------------------------------------------------------
-- 5.3 — Catálogo de Tipos de Inmueble
-- ----------------------------------------------------------------------------
INSERT INTO cat_tipos_inmueble (id_tipo, codigo, descripcion) VALUES
(1, 'APARTAMENTO', 'Inmueble residencial en propiedad horizontal'),
(2, 'CASA',        'Inmueble unifamiliar o bifamiliar independiente'),
(3, 'ESTUDIO',     'Apartaestudio o monoambiente compacto'),
(4, 'PENTHOUSE',   'Inmueble exclusivo en último nivel de edificio');

-- ----------------------------------------------------------------------------
-- 5.4 — Catálogo de Fuentes de Origen (Fuentes ficticias de datos inmobiliarios)
-- ----------------------------------------------------------------------------
INSERT INTO cat_fuentes_origen (id_fuente, nombre_fuente, tipo_formato_default, estado) VALUES
(1, 'METROCUADRADO_MOCK',  'CSV',   'ACTIVO'),
(2, 'FINCARAIZ_MOCK',      'EXCEL', 'ACTIVO'),
(3, 'CATASTRO_OPEN_DATA',  'JSON',  'ACTIVO');

-- ----------------------------------------------------------------------------
-- 5.5 — Dos Lotes de Ingesta Ficticios (un lote exitoso, uno parcialmente rechazado)
-- Los IDs son UUIDs ficticios. Los emails son ficticios con dominio académico.
-- ----------------------------------------------------------------------------
INSERT INTO wrk_datasets_ingesta
    (id_dataset, id_fuente, nombre_archivo, hash_sha256, usuario_email, estado_pipeline)
VALUES
(
    'f47ac10b-58cc-4372-a567-0e02b2c3d479',
    1,
    'dataset_bogota_norte_mock_2026.csv',
    'a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef01',
    'ana.ficticia@unisalle.edu.co',
    'COMPLETADO'
),
(
    'a1b2c3d4-0000-4111-b222-c3d4e5f60000',
    2,
    'dataset_bogota_sur_mock_2026.xlsx',
    'b2c3d4e5f6a7890112345678abcdef0123456789abcdef0123456789abcdef02',
    'carlos.ficticio@unisalle.edu.co',
    'COMPLETADO'
);

-- ----------------------------------------------------------------------------
-- 5.6 — Registros Crudos en Staging (7 raw: 5 válidos + 2 rechazados por reglas)
-- Los rechazados representan errores reales del pipeline: estrato inválido
-- y precio con valor negativo.
-- ----------------------------------------------------------------------------
INSERT INTO stg_inmuebles_raw
    (id_raw, id_dataset, ubicacion_raw, tamano_raw, habitaciones_raw, banos_raw, estrato_raw, precio_raw, fecha_raw)
VALUES
-- Lote 1: 4 registros (3 válidos, 1 rechazado por estrato = 9)
(1, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 'Bogotá, Chapinero Alto, Cr 7 45-10', '65.5',  '2', '2', '4',   '380000000',  '2024'),
(2, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 'Bogotá, Cedritos, Cl 140 Kr 15 20',  '85.0',  '3', '2', '4',   '450000000',  '2024'),
(3, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 'Bogotá, Niza Sur, Kr 70 Cl 127 30',  '120.0', '4', '3', '5',   '750000000',  '2023'),
(4, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 'Bogotá, Chapinero Alto, Tv 39 63-52','45.0',  '1', '1', '9',   '210000000',  '2025'),  -- RECHAZO G2: estrato=9
-- Lote 2: 3 registros (2 válidos, 1 rechazado por precio negativo)
(5, 'a1b2c3d4-0000-4111-b222-c3d4e5f60000', 'Bogotá, Galerías, Kr 24 Cl 53 15',  '72.0',  '3', '2', '4',   '420000000',  '2024'),
(6, 'a1b2c3d4-0000-4111-b222-c3d4e5f60000', 'Bogotá, Castilla, Cl 40 Kr 80 12',  '58.0',  '2', '1', '3',   '195000000',  '2023'),
(7, 'a1b2c3d4-0000-4111-b222-c3d4e5f60000', 'Bogotá, Tintal Sur, Dg 40 Kr 90 8', '50.0',  '2', '1', '2',   '-50000000',  '2025'); -- RECHAZO G2: precio negativo

-- ----------------------------------------------------------------------------
-- 5.7 — Registros Limpios (5 cleaned: los que superaron las compuertas G1, G2 y G3)
-- Los id_raw 4 y 7 NO están aquí porque fueron rechazados en la compuerta G2.
-- ----------------------------------------------------------------------------
INSERT INTO wrk_inmuebles_cleaned
    (id_cleaned, id_raw, id_dataset, id_barrio, id_tipo, tamano_m2, habitaciones, banos, estrato, precio_cop, anio_registro, es_valido)
VALUES
(1, 1, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 1, 1,  65.50,  2, 2, 4, 380000000.00, 2024, 1),
(2, 2, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 2, 1,  85.00,  3, 2, 4, 450000000.00, 2024, 1),
(3, 3, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 3, 2, 120.00,  4, 3, 5, 750000000.00, 2023, 1),
(4, 5, 'a1b2c3d4-0000-4111-b222-c3d4e5f60000', 4, 1,  72.00,  3, 2, 4, 420000000.00, 2024, 1),
(5, 6, 'a1b2c3d4-0000-4111-b222-c3d4e5f60000', 5, 1,  58.00,  2, 1, 3, 195000000.00, 2023, 1);

-- ----------------------------------------------------------------------------
-- 5.8 — Features Analíticas calculadas para los 5 registros limpios
-- precio_unitario_m2 = precio_cop / tamano_m2 (calculado con datos ficticios)
-- ----------------------------------------------------------------------------
INSERT INTO fct_features_analiticas
    (id_feature, id_cleaned, precio_unitario_m2, puntaje_entorno, bano_por_hab_ratio, densidad_comercial, parqueadero_ratio, factor_precio_millones)
VALUES
(1, 1, 5801526.72, 8, 1.00, 0.0305, 0.0153, 1.0000),
(2, 2, 5294117.65, 6, 0.67, 0.0235, 0.0118, 1.0000),
(3, 3, 6250000.00, 9, 0.75, 0.0167, 0.0167, 1.0000),
(4, 4, 5833333.33, 7, 0.67, 0.0280, 0.0140, 1.0000),
(5, 5, 3362068.97, 5, 0.50, 0.0185, 0.0093, 1.0000);

-- ----------------------------------------------------------------------------
-- 5.9 — Golden Records en MDM (3 inmuebles maestros consolidados)
-- Los UUIDs, hashes y direcciones son completamente ficticios.
-- ----------------------------------------------------------------------------
INSERT INTO mdm_inmuebles_maestros
    (id_maestro, id_barrio, id_tipo, direccion_normalizada, tamano_m2, habitaciones, banos, estrato,
     precio_ultimo_cop, precio_unitario_m2, anio_construccion_referencia, latitud_corregida, longitud_corregida, hash_duplicado)
VALUES
(
    'b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6e', 1, 1,
    'kr 7 # 45-10 piso 4 ap 401', 65.50, 2, 2, 4,
    380000000.00, 5801526.72, 2018, 4.6450000, -74.0580000,
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
),
(
    'c2d3e4f5-a6b7-8c9d-0e1f-2a3b4c5d6e7f', 2, 1,
    'cl 140 # kr 15-20 ap 301',   85.00, 3, 2, 4,
    450000000.00, 5294117.65, 2015, 4.7230000, -74.0320000,
    '4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a'
),
(
    'd3e4f5a6-b7c8-9d0e-1f2a-3b4c5d6e7f8a', 3, 2,
    'kr 70 # cl 127-30 casa 15',  120.00, 4, 3, 5,
    750000000.00, 6250000.00, 2010, 4.7100000, -74.0720000,
    'ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d'
);

-- ----------------------------------------------------------------------------
-- 5.10 — Perfiles de Entorno Urbano para los 3 golden records
-- ----------------------------------------------------------------------------
INSERT INTO dim_entorno_urbano
    (id_entorno, id_maestro, parques_cercanos, vias_principales, area_remocion_masa_m2, grandes_superficies, colegios_cercanos, hospitales_cercanos, puntaje_amenidades)
VALUES
(1, 'b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6e', 3, 2, 0.00,   2, 2, 1, 8),
(2, 'c2d3e4f5-a6b7-8c9d-0e1f-2a3b4c5d6e7f', 2, 1, 0.00,   2, 1, 0, 6),
(3, 'd3e4f5a6-b7c8-9d0e-1f2a-3b4c5d6e7f8a', 4, 2, 0.00,   2, 2, 1, 9);

-- ----------------------------------------------------------------------------
-- 5.11 — Logs de Rechazo (2 rechazos: uno por estrato inválido, uno por precio)
-- Documenta los registros rechazados en la compuerta G2 del pipeline BPMN.
-- ----------------------------------------------------------------------------
INSERT INTO log_rechazos_calidad
    (id_rechazo, id_dataset, compuerta_bpmn, codigo_regla, motivo_error, payload_registro)
VALUES
(
    1,
    'f47ac10b-58cc-4372-a567-0e02b2c3d479',
    'G2',
    'RB-003',
    'Estrato fuera del dominio permitido [1-6]: valor recibido = 9',
    '{"id_raw": 4, "ubicacion_raw": "Bogotá, Chapinero Alto, Tv 39 63-52", "estrato_raw": "9", "precio_raw": "210000000"}'
),
(
    2,
    'a1b2c3d4-0000-4111-b222-c3d4e5f60000',
    'G2',
    'RB-004',
    'Precio en pesos colombianos con valor negativo: valor recibido = -50000000',
    '{"id_raw": 7, "ubicacion_raw": "Bogotá, Tintal Sur, Dg 40 Kr 90 8", "estrato_raw": "2", "precio_raw": "-50000000"}'
);

-- ----------------------------------------------------------------------------
-- 5.12 — Reportes de Ejecución (uno por dataset, como exige la restricción UNIQUE)
-- ----------------------------------------------------------------------------
INSERT INTO rpt_limpieza_ejecucion
    (id_reporte, id_dataset, total_registros_raw, total_registros_limpios, total_rechazados, total_duplicados_eliminados, total_nulos_imputados, tiempo_ejecucion_seg)
VALUES
(1, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 4, 3, 1, 0, 0, 0.452),
(2, 'a1b2c3d4-0000-4111-b222-c3d4e5f60000', 3, 2, 1, 0, 0, 0.318);

-- ----------------------------------------------------------------------------
-- 5.13 — Notificaciones Despachadas (una por dataset al completar el pipeline)
-- ----------------------------------------------------------------------------
INSERT INTO log_notificaciones
    (id_notificacion, id_dataset, email_destinatario, asunto, estado_envio)
VALUES
(1, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 'ana.ficticia@unisalle.edu.co',
   'Pipeline completado: 3/4 registros procesados — 1 rechazo en G2', 'ENVIADO'),
(2, 'a1b2c3d4-0000-4111-b222-c3d4e5f60000', 'carlos.ficticio@unisalle.edu.co',
   'Pipeline completado: 2/3 registros procesados — 1 rechazo en G2', 'ENVIADO');


-- ============================================================================
-- SECCIÓN 6: CONSULTAS DE VERIFICACIÓN (SELECT)
-- ============================================================================
-- Estas consultas permiten verificar la información almacenada y las relaciones
-- entre las tablas del modelo. Se ejecutan para comprobar que la carga inicial
-- fue exitosa y que las claves foráneas funcionan correctamente.
-- ============================================================================

-- Q1: Vista completa del Golden Record con Localidad, Barrio, Tipología y Entorno
-- Verifica: JOINs entre mdm_inmuebles_maestros, cat_barrios, cat_localidades,
--           cat_tipos_inmueble y dim_entorno_urbano.
SELECT
    m.id_maestro,
    l.nombre              AS localidad,
    b.nombre_barrio       AS barrio,
    b.estrato_moda        AS estrato_barrio,
    t.codigo              AS tipo_inmueble,
    m.direccion_normalizada,
    m.tamano_m2,
    m.habitaciones,
    m.banos,
    m.estrato,
    m.precio_ultimo_cop,
    m.precio_unitario_m2,
    e.puntaje_amenidades,
    e.colegios_cercanos,
    e.hospitales_cercanos
FROM mdm_inmuebles_maestros m
INNER JOIN cat_barrios         b ON m.id_barrio  = b.id_barrio
INNER JOIN cat_localidades     l ON b.id_localidad = l.id_localidad
INNER JOIN cat_tipos_inmueble  t ON m.id_tipo    = t.id_tipo
LEFT  JOIN dim_entorno_urbano  e ON m.id_maestro = e.id_maestro
ORDER BY l.nombre, b.nombre_barrio;

-- Q2: Trazabilidad completa del pipeline: desde el dataset de origen hasta features
-- Verifica: cadena raw → cleaned → features y metadatos del lote de ingesta.
SELECT
    d.nombre_archivo,
    d.estado_pipeline,
    d.usuario_email,
    r.ubicacion_raw,
    r.estrato_raw,
    c.tamano_m2,
    c.precio_cop,
    c.es_valido,
    f.precio_unitario_m2,
    f.bano_por_hab_ratio,
    f.puntaje_entorno
FROM wrk_datasets_ingesta    d
INNER JOIN stg_inmuebles_raw        r ON d.id_dataset = r.id_dataset
INNER JOIN wrk_inmuebles_cleaned    c ON r.id_raw      = c.id_raw
INNER JOIN fct_features_analiticas  f ON c.id_cleaned  = f.id_cleaned
ORDER BY d.nombre_archivo, r.id_raw;

-- Q3: Estadísticas de precio y tamaño por localidad (solo localidades con datos)
-- Verifica: agregaciones con GROUP BY y múltiples JOINs.
SELECT
    l.nombre                           AS localidad,
    COUNT(DISTINCT m.id_maestro)       AS total_inmuebles,
    ROUND(AVG(m.precio_ultimo_cop), 0) AS precio_promedio_cop,
    ROUND(AVG(m.tamano_m2), 2)         AS tamano_promedio_m2,
    ROUND(AVG(m.precio_unitario_m2),2) AS precio_unitario_promedio
FROM mdm_inmuebles_maestros m
INNER JOIN cat_barrios     b ON m.id_barrio   = b.id_barrio
INNER JOIN cat_localidades l ON b.id_localidad = l.id_localidad
GROUP BY l.id_localidad, l.nombre
ORDER BY precio_promedio_cop DESC;

-- Q4: Registros rechazados con detalle de compuerta y regla violada
-- Verifica: integridad de los logs de rechazo y relación con datasets.
SELECT
    d.nombre_archivo,
    rc.compuerta_bpmn,
    rc.codigo_regla,
    rc.motivo_error,
    rc.fecha_rechazo
FROM log_rechazos_calidad rc
INNER JOIN wrk_datasets_ingesta d ON rc.id_dataset = d.id_dataset
ORDER BY rc.fecha_rechazo DESC;

-- Q5: Balance del pipeline por dataset (KPIs de ejecución)
-- Verifica: reporte de limpieza y tasa de éxito del proceso ETL.
SELECT
    d.nombre_archivo,
    rp.total_registros_raw,
    rp.total_registros_limpios,
    rp.total_rechazados,
    ROUND(rp.total_registros_limpios * 100.0 / rp.total_registros_raw, 1) AS tasa_exito_pct,
    rp.tiempo_ejecucion_seg
FROM rpt_limpieza_ejecucion rp
INNER JOIN wrk_datasets_ingesta d ON rp.id_dataset = d.id_dataset
ORDER BY rp.fecha_generacion DESC;

-- Q6: Notificaciones enviadas con estado de despacho
SELECT
    n.id_notificacion,
    d.nombre_archivo,
    n.email_destinatario,
    n.asunto,
    n.estado_envio,
    n.fecha_envio
FROM log_notificaciones n
INNER JOIN wrk_datasets_ingesta d ON n.id_dataset = d.id_dataset
ORDER BY n.fecha_envio DESC;


-- ============================================================================
-- SECCIÓN 7: MANIPULACIÓN CONTROLADA DE DATOS (UPDATE y DELETE)
-- ============================================================================
-- Los UPDATE y DELETE se realizan con condiciones explícitas sobre claves
-- primarias para evitar afectar registros no previstos.
-- Se incluyen SELECT previos y posteriores para documentar el cambio.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- UPDATE 1: Corrección del estado del pipeline del primer dataset
-- Escenario: Se detectó que el analista marcó el dataset como COMPLETADO
-- pero requería re-validación. Se corrige el estado a VALIDANDO.
-- ----------------------------------------------------------------------------

-- Estado ANTES del UPDATE:
SELECT id_dataset, nombre_archivo, estado_pipeline
FROM wrk_datasets_ingesta
WHERE id_dataset = 'f47ac10b-58cc-4372-a567-0e02b2c3d479';

-- Ejecutar la actualización controlada:
UPDATE wrk_datasets_ingesta
SET    estado_pipeline = 'VALIDANDO'
WHERE  id_dataset = 'f47ac10b-58cc-4372-a567-0e02b2c3d479';

-- Estado DESPUÉS del UPDATE (debe mostrar VALIDANDO):
SELECT id_dataset, nombre_archivo, estado_pipeline
FROM wrk_datasets_ingesta
WHERE id_dataset = 'f47ac10b-58cc-4372-a567-0e02b2c3d479';

-- Revertir al estado original para no afectar las consultas posteriores:
UPDATE wrk_datasets_ingesta
SET    estado_pipeline = 'COMPLETADO'
WHERE  id_dataset = 'f47ac10b-58cc-4372-a567-0e02b2c3d479';

-- ----------------------------------------------------------------------------
-- UPDATE 2: Ajuste del precio de un inmueble maestro (renegociación ficticia)
-- Escenario: El precio del Golden Record en Chapinero Alto fue renegociado
-- a 395.000.000 COP. Se actualiza precio y precio unitario simultáneamente.
-- ----------------------------------------------------------------------------

-- Estado ANTES del UPDATE:
SELECT id_maestro, direccion_normalizada, precio_ultimo_cop, precio_unitario_m2
FROM mdm_inmuebles_maestros
WHERE id_maestro = 'b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6e';

-- Ejecutar la actualización controlada:
UPDATE mdm_inmuebles_maestros
SET    precio_ultimo_cop  = 395000000.00,
       precio_unitario_m2 = ROUND(395000000.00 / 65.50, 2)  -- = 6030534.35
WHERE  id_maestro = 'b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6e';

-- Estado DESPUÉS del UPDATE (debe mostrar nuevo precio):
SELECT id_maestro, direccion_normalizada, precio_ultimo_cop, precio_unitario_m2
FROM mdm_inmuebles_maestros
WHERE id_maestro = 'b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6e';

-- ----------------------------------------------------------------------------
-- DELETE controlado: Eliminar el registro raw rechazado (id_raw = 4)
-- Escenario: Se elimina un registro crudo inválido identificado por su PK.
-- Al no existir en wrk_inmuebles_cleaned (fue rechazado), no hay CASCADE.
-- ----------------------------------------------------------------------------

-- Confirmar que el registro existe y no está en cleaned:
SELECT id_raw, id_dataset, estrato_raw, precio_raw
FROM stg_inmuebles_raw
WHERE id_raw = 4;

-- Ejecutar el DELETE con condición explícita sobre la clave primaria:
DELETE FROM stg_inmuebles_raw
WHERE  id_raw = 4;

-- Confirmar que fue eliminado (debe retornar 0 filas):
SELECT id_raw FROM stg_inmuebles_raw WHERE id_raw = 4;


-- ============================================================================
-- SECCIÓN 8: PRUEBAS DE INTEGRIDAD REFERENCIAL Y RESTRICCIONES CHECK
-- ============================================================================
-- Estas sentencias demuestran que las restricciones de integridad funcionan.
-- TODAS están diseñadas para FALLAR con el error esperado.
-- En MySQL Workbench o phpMyAdmin, ejecutar cada bloque de forma aislada
-- y capturar el mensaje de error como evidencia.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- PRUEBA P-01: Violación de CHECK en estrato (valor fuera del rango [1,6])
-- Error esperado: ERROR 3819 (HY000): Check constraint 'chk_barrio_estrato' is violated.
-- ----------------------------------------------------------------------------
-- INSERT INTO cat_barrios (id_localidad, nombre_barrio, estrato_moda, latitud_centroide, longitud_centroide)
-- VALUES (1, 'Barrio Prueba Inválido', 9, 4.6500000, -74.0600000);

-- ----------------------------------------------------------------------------
-- PRUEBA P-02: Violación de UNIQUE en hash_duplicado (deduplicación MDM)
-- Error esperado: ERROR 1062 (23000): Duplicate entry 'e3b0c...' for key 'hash_duplicado'.
-- ----------------------------------------------------------------------------
-- INSERT INTO mdm_inmuebles_maestros
--     (id_maestro, id_barrio, id_tipo, direccion_normalizada, tamano_m2, habitaciones, banos, estrato,
--      precio_ultimo_cop, precio_unitario_m2, latitud_corregida, longitud_corregida, hash_duplicado)
-- VALUES
-- ('ffffffff-ffff-ffff-ffff-ffffffffffff', 1, 1, 'Dirección duplicada de prueba', 65.50, 2, 2, 4,
--  380000000.00, 5801526.72, 4.6450000, -74.0580000,
--  'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');

-- ----------------------------------------------------------------------------
-- PRUEBA P-03: Violación de FK RESTRICT — eliminar barrio con inmuebles asociados
-- Error esperado: ERROR 1451 (23000): Cannot delete or update a parent row:
--                a foreign key constraint fails.
-- ----------------------------------------------------------------------------
-- DELETE FROM cat_barrios WHERE id_barrio = 2;

-- ----------------------------------------------------------------------------
-- PRUEBA P-04: Violación de CHECK en estado_envio (valor fuera del dominio)
-- Error esperado: ERROR 3819 (HY000): Check constraint 'chk_notif_estado' is violated.
-- (CORRECCIÓN ACTIVIDAD 4: Este CHECK fue agregado en esta versión del script)
-- ----------------------------------------------------------------------------
-- INSERT INTO log_notificaciones (id_dataset, email_destinatario, asunto, estado_envio)
-- VALUES ('f47ac10b-58cc-4372-a567-0e02b2c3d479',
--         'prueba.invalido@ficticio.edu.co',
--         'Asunto de prueba de restricción',
--         'INVALIDO_NO_EXISTE');

-- ============================================================================
-- FIN DEL SCRIPT — sistema_data_wrangling / Actividad 4
-- Ejecutar siempre en base de datos local de laboratorio.
-- Todos los datos son 100% ficticios con fines académicos.
-- ============================================================================
