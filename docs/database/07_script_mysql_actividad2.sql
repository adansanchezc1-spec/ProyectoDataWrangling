-- ============================================================================
-- ACTIVIDAD 2: IMPLEMENTACIÓN DE BASE DE DATOS RELACIONAL
-- SISTEMA DATA WRANGLING & MASTER DATA MANAGEMENT (MDM) INMOBILIARIO BOGOTÁ
-- MOTOR SGBD: MySQL Server 8.0+ / 8.4+ LTS (XAMPP / phpMyAdmin / MySQL Workbench)
-- AUTOR: Adán Y. Sánchez Cubillos (Universidad de La Salle)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS sistema_data_wrangling 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE sistema_data_wrangling;

-- Desactivar temporalmente revisión de FKs para creación limpia
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS log_notificaciones;
DROP TABLE IF EXISTS rpt_limpieza_ejecucion;
DROP TABLE IF EXISTS log_rechazos_calidad;
DROP TABLE IF EXISTS dim_entorno_urbano;
DROP TABLE IF EXISTS mdm_inmuebles_maestros;
DROP TABLE IF EXISTS fct_features_analiticas;
DROP TABLE IF EXISTS wrk_inmuebles_cleaned;
DROP TABLE IF EXISTS stg_inmuebles_raw;
DROP TABLE IF EXISTS wrk_datasets_ingesta;
DROP TABLE IF EXISTS cat_fuentes_origen;
DROP TABLE IF EXISTS cat_tipos_inmueble;
DROP TABLE IF EXISTS cat_barrios;
DROP TABLE IF EXISTS cat_localidades;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- 1. TABLAS DE CATÁLOGO Y DATOS DE REFERENCIA (REFERENCE DATA)
-- ============================================================================

-- 1.1 Catálogo de Localidades de Bogotá
CREATE TABLE cat_localidades (
    id_localidad INT AUTO_INCREMENT PRIMARY KEY,
    codigo_dane VARCHAR(10) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    zona_bogota VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 1.2 Catálogo de Barrios y Comunas
CREATE TABLE cat_barrios (
    id_barrio INT AUTO_INCREMENT PRIMARY KEY,
    id_localidad INT NOT NULL,
    nombre_barrio VARCHAR(120) NOT NULL,
    estrato_moda SMALLINT NOT NULL,
    latitud_centroide DECIMAL(10, 7) NOT NULL,
    longitud_centroide DECIMAL(10, 7) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_barrio_localidad FOREIGN KEY (id_localidad)
        REFERENCES cat_localidades (id_localidad) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_barrio_estrato CHECK (estrato_moda BETWEEN 1 AND 6),
    CONSTRAINT chk_barrio_latitud CHECK (latitud_centroide BETWEEN 4.4500000 AND 4.8500000),
    CONSTRAINT chk_barrio_longitud CHECK (longitud_centroide BETWEEN -74.2500000 AND -73.9500000)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 1.3 Catálogo de Tipos de Inmueble
CREATE TABLE cat_tipos_inmueble (
    id_tipo INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(30) NOT NULL UNIQUE,
    descripcion VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 1.4 Catálogo de Fuentes de Origen
CREATE TABLE cat_fuentes_origen (
    id_fuente INT AUTO_INCREMENT PRIMARY KEY,
    nombre_fuente VARCHAR(80) NOT NULL UNIQUE,
    tipo_formato_default VARCHAR(20) NOT NULL,
    estado VARCHAR(20) DEFAULT 'ACTIVO' NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 2. TABLAS TRANSACCIONALES Y DE PIPELINE ETL
-- ============================================================================

-- 2.1 Ingesta de Datasets
CREATE TABLE wrk_datasets_ingesta (
    id_dataset VARCHAR(36) PRIMARY KEY,
    id_fuente INT NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    hash_sha256 CHAR(64) NOT NULL,
    usuario_email VARCHAR(120) NOT NULL,
    estado_pipeline VARCHAR(30) DEFAULT 'CARGADO' NOT NULL,
    fecha_ingesta DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_ingesta_fuente FOREIGN KEY (id_fuente)
        REFERENCES cat_fuentes_origen (id_fuente) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_ingesta_estado CHECK (
        estado_pipeline IN ('CARGADO', 'EXTRAYENDO', 'VALIDANDO', 'TRANSFORMANDO', 'PERFILANDO', 'COMPLETADO', 'RECHAZADO')
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.2 Capa Staging Cruda (Raw Data)
CREATE TABLE stg_inmuebles_raw (
    id_raw BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_dataset VARCHAR(36) NOT NULL,
    ubicacion_raw TEXT,
    tamano_raw TEXT,
    habitaciones_raw TEXT,
    banos_raw TEXT,
    estrato_raw TEXT,
    precio_raw TEXT,
    fecha_raw TEXT,
    fecha_extraccion DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_raw_dataset FOREIGN KEY (id_dataset)
        REFERENCES wrk_datasets_ingesta (id_dataset) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.3 Capa Working Saneada (Cleaned Data)
CREATE TABLE wrk_inmuebles_cleaned (
    id_cleaned BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_raw BIGINT NOT NULL UNIQUE,
    id_dataset VARCHAR(36) NOT NULL,
    id_barrio INT NOT NULL,
    id_tipo INT NOT NULL,
    tamano_m2 DECIMAL(10, 2) NOT NULL,
    habitaciones SMALLINT NOT NULL,
    banos SMALLINT NOT NULL,
    estrato SMALLINT NOT NULL,
    precio_cop DECIMAL(14, 2) NOT NULL,
    anio_registro SMALLINT NOT NULL,
    es_valido TINYINT(1) DEFAULT 1 NOT NULL,
    CONSTRAINT fk_cleaned_raw FOREIGN KEY (id_raw)
        REFERENCES stg_inmuebles_raw (id_raw) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_cleaned_dataset FOREIGN KEY (id_dataset)
        REFERENCES wrk_datasets_ingesta (id_dataset) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_cleaned_barrio FOREIGN KEY (id_barrio)
        REFERENCES cat_barrios (id_barrio) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_cleaned_tipo FOREIGN KEY (id_tipo)
        REFERENCES cat_tipos_inmueble (id_tipo) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_cleaned_estrato CHECK (estrato BETWEEN 1 AND 6),
    CONSTRAINT chk_cleaned_tamano CHECK (tamano_m2 > 0 AND tamano_m2 <= 50000.00),
    CONSTRAINT chk_cleaned_habs CHECK (habitaciones BETWEEN 1 AND 20),
    CONSTRAINT chk_cleaned_banos CHECK (banos BETWEEN 1 AND 15),
    CONSTRAINT chk_cleaned_precio CHECK (precio_cop > 0 AND precio_cop <= 50000000000.00),
    CONSTRAINT chk_cleaned_anio CHECK (anio_registro BETWEEN 1900 AND 2026)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.4 Features Analíticas (Feature Engineering para ML)
CREATE TABLE fct_features_analiticas (
    id_feature BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_cleaned BIGINT NOT NULL UNIQUE,
    precio_unitario_m2 DECIMAL(14, 2) NOT NULL,
    puntaje_entorno INT NOT NULL,
    bano_por_hab_ratio DECIMAL(5, 2) NOT NULL,
    densidad_comercial DECIMAL(8, 4) NOT NULL,
    parqueadero_ratio DECIMAL(8, 4) NOT NULL,
    factor_precio_millones DECIMAL(12, 4) DEFAULT 1.0000 NOT NULL,
    CONSTRAINT fk_feature_cleaned FOREIGN KEY (id_cleaned)
        REFERENCES wrk_inmuebles_cleaned (id_cleaned) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_feature_ratio CHECK (bano_por_hab_ratio >= 0.0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 3. TABLAS DE MASTER DATA MANAGEMENT (MDM - GOLDEN RECORD)
-- ============================================================================

-- 3.1 Registro Maestro Consolidado de Inmuebles
CREATE TABLE mdm_inmuebles_maestros (
    id_maestro VARCHAR(36) PRIMARY KEY,
    id_barrio INT NOT NULL,
    id_tipo INT NOT NULL,
    direccion_normalizada VARCHAR(200) NOT NULL,
    tamano_m2 DECIMAL(10, 2) NOT NULL,
    habitaciones SMALLINT NOT NULL,
    banos SMALLINT NOT NULL,
    estrato SMALLINT NOT NULL,
    precio_ultimo_cop DECIMAL(14, 2) NOT NULL,
    precio_unitario_m2 DECIMAL(14, 2) NOT NULL,
    anio_construccion_referencia SMALLINT NULL,
    latitud_corregida DECIMAL(10, 7) NOT NULL,
    longitud_corregida DECIMAL(10, 7) NOT NULL,
    hash_duplicado CHAR(64) NOT NULL UNIQUE,
    fecha_consolidacion DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_inmueble_barrio FOREIGN KEY (id_barrio)
        REFERENCES cat_barrios (id_barrio) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_inmueble_tipo FOREIGN KEY (id_tipo)
        REFERENCES cat_tipos_inmueble (id_tipo) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_maestro_estrato CHECK (estrato BETWEEN 1 AND 6),
    CONSTRAINT chk_maestro_tamano CHECK (tamano_m2 > 0),
    CONSTRAINT chk_maestro_precio CHECK (precio_ultimo_cop > 0),
    CONSTRAINT chk_maestro_latitud CHECK (latitud_corregida BETWEEN 4.4500000 AND 4.8500000),
    CONSTRAINT chk_maestro_longitud CHECK (longitud_corregida BETWEEN -74.2500000 AND -73.9500000)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3.2 Dimensión de Entorno Urbano Contextual
CREATE TABLE dim_entorno_urbano (
    id_entorno BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_maestro VARCHAR(36) NOT NULL UNIQUE,
    parques_cercanos INT DEFAULT 0 NOT NULL,
    vias_principales INT DEFAULT 0 NOT NULL,
    area_remocion_masa_m2 DECIMAL(10, 2) DEFAULT 0.00 NOT NULL,
    grandes_superficies INT DEFAULT 0 NOT NULL,
    colegios_cercanos INT DEFAULT 0 NOT NULL,
    hospitales_cercanos INT DEFAULT 0 NOT NULL,
    puntaje_amenidades INT DEFAULT 0 NOT NULL,
    CONSTRAINT fk_entorno_maestro FOREIGN KEY (id_maestro)
        REFERENCES mdm_inmuebles_maestros (id_maestro) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_entorno_parques CHECK (parques_cercanos >= 0),
    CONSTRAINT chk_entorno_vias CHECK (vias_principales >= 0),
    CONSTRAINT chk_entorno_riesgo CHECK (area_remocion_masa_m2 >= 0.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 4. TABLAS DE CALIDAD, AUDITORÍA Y NOTIFICACIONES
-- ============================================================================

-- 4.1 Log de Rechazos Granulares por Compuerta BPMN
CREATE TABLE log_rechazos_calidad (
    id_rechazo BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_dataset VARCHAR(36) NOT NULL,
    compuerta_bpmn VARCHAR(10) NOT NULL,
    codigo_regla VARCHAR(20) NOT NULL,
    motivo_error TEXT NOT NULL,
    payload_registro JSON NULL,
    fecha_rechazo DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_rechazo_dataset FOREIGN KEY (id_dataset)
        REFERENCES wrk_datasets_ingesta (id_dataset) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_rechazo_compuerta CHECK (compuerta_bpmn IN ('G1', 'G2', 'G3', 'G4'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4.2 Balance Consolidado de Limpieza por Dataset
CREATE TABLE rpt_limpieza_ejecucion (
    id_reporte BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_dataset VARCHAR(36) NOT NULL UNIQUE,
    total_registros_raw INT NOT NULL,
    total_registros_limpios INT NOT NULL,
    total_rechazados INT NOT NULL,
    total_duplicados_eliminados INT NOT NULL,
    total_nulos_imputados INT NOT NULL,
    tiempo_ejecucion_seg DECIMAL(8, 3) NOT NULL,
    fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_reporte_dataset FOREIGN KEY (id_dataset)
        REFERENCES wrk_datasets_ingesta (id_dataset) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4.3 Log de Notificaciones Despachadas
CREATE TABLE log_notificaciones (
    id_notificacion BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_dataset VARCHAR(36) NOT NULL,
    email_destinatario VARCHAR(120) NOT NULL,
    asunto VARCHAR(200) NOT NULL,
    estado_envio VARCHAR(30) DEFAULT 'ENVIADO' NOT NULL,
    fecha_envio DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_notificacion_dataset FOREIGN KEY (id_dataset)
        REFERENCES wrk_datasets_ingesta (id_dataset) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 5. ÍNDICES DE RENDIMIENTO (ISO/IEC 25010)
-- ============================================================================
CREATE INDEX idx_raw_dataset ON stg_inmuebles_raw (id_dataset);
CREATE INDEX idx_cleaned_dataset ON wrk_inmuebles_cleaned (id_dataset);
CREATE INDEX idx_cleaned_barrio ON wrk_inmuebles_cleaned (id_barrio);
CREATE INDEX idx_cleaned_estrato ON wrk_inmuebles_cleaned (estrato);
CREATE INDEX idx_cleaned_precio ON wrk_inmuebles_cleaned (precio_cop);
CREATE INDEX idx_maestro_barrio ON mdm_inmuebles_maestros (id_barrio);
CREATE INDEX idx_maestro_coords ON mdm_inmuebles_maestros (latitud_corregida, longitud_corregida);
CREATE INDEX idx_rechazo_dataset_compuerta ON log_rechazos_calidad (id_dataset, compuerta_bpmn);

-- ============================================================================
-- 6. INSERCIÓN DE DATOS DE PRUEBA FICTICIOS (SEED DATA & TEST DATA)
-- ============================================================================

-- 6.1 Catálogo de 20 Localidades Oficiales de Bogotá
INSERT INTO cat_localidades (id_localidad, codigo_dane, nombre, zona_bogota) VALUES
(1, '1101', 'Usaquén', 'Norte'),
(2, '1102', 'Chapinero', 'Chapinero'),
(3, '1103', 'Santa Fe', 'Centro'),
(4, '1104', 'San Cristóbal', 'Sur'),
(5, '1105', 'Usme', 'Sur'),
(6, '1106', 'Tunjuelito', 'Sur'),
(7, '1107', 'Bosa', 'Sur'),
(8, '1108', 'Kennedy', 'Occidente'),
(9, '1109', 'Fontibón', 'Occidente'),
(10, '1110', 'Engativá', 'Occidente'),
(11, '1111', 'Suba', 'Norte'),
(12, '1112', 'Barrios Unidos', 'Norte'),
(13, '1113', 'Teusaquillo', 'Centro'),
(14, '1114', 'Los Mártires', 'Centro'),
(15, '1115', 'Antonio Nariño', 'Sur'),
(16, '1116', 'Puente Aranda', 'Centro'),
(17, '1117', 'La Candelaria', 'Centro'),
(18, '1118', 'Rafael Uribe Uribe', 'Sur'),
(19, '1119', 'Ciudad Bolívar', 'Sur'),
(20, '1120', 'Sumapaz', 'Sur');

-- 6.2 Catálogo de Barrios Ficticios de Prueba
INSERT INTO cat_barrios (id_barrio, id_localidad, nombre_barrio, estrato_moda, latitud_centroide, longitud_centroide) VALUES
(1, 2, 'Chapinero Alto', 4, 4.6450000, -74.0580000),
(2, 1, 'Cedritos', 4, 4.7230000, -74.0320000),
(3, 11, 'Niza Sur', 5, 4.7100000, -74.0720000),
(4, 13, 'Galerías', 4, 4.6410000, -74.0750000),
(5, 8, 'Castilla', 3, 4.6480000, -74.1480000);

-- 6.3 Catálogo de Tipos de Inmueble
INSERT INTO cat_tipos_inmueble (id_tipo, codigo, descripcion) VALUES
(1, 'APARTAMENTO', 'Inmueble residencial en propiedad horizontal'),
(2, 'CASA', 'Inmueble unifamiliar o bifamiliar independiente'),
(3, 'ESTUDIO', 'Apartaestudio o monoambiente compacto'),
(4, 'PENTHOUSE', 'Inmueble exclusivo en último nivel');

-- 6.4 Catálogo de Fuentes de Origen
INSERT INTO cat_fuentes_origen (id_fuente, nombre_fuente, tipo_formato_default, estado) VALUES
(1, 'METROCUADRADO_MOCK', 'CSV', 'ACTIVO'),
(2, 'FINCARAIZ_MOCK', 'EXCEL', 'ACTIVO'),
(3, 'CATASTRO_OPEN_DATA', 'JSON', 'ACTIVO');

-- 6.5 Ingesta de un Lote de Prueba (Ficticio)
INSERT INTO wrk_datasets_ingesta (
    id_dataset, id_fuente, nombre_archivo, hash_sha256, usuario_email, estado_pipeline
) VALUES (
    'f47ac10b-58cc-4372-a567-0e02b2c3d479', 1, 'dataset_vivienda_bogota_mock_2026.csv', 
    'a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0', 
    'estudiante.prueba@unisalle.edu.co', 'COMPLETADO'
);

-- 6.6 Datos Crudos en Staging (Raw)
INSERT INTO stg_inmuebles_raw (id_raw, id_dataset, ubicacion_raw, tamano_raw, habitaciones_raw, banos_raw, estrato_raw, precio_raw, fecha_raw) VALUES
(1, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 'Bogota, Chapinero Alto', '65.5', '2', '2', '4', '380000000', '2024'),
(2, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 'Bogota, Cedritos', '85.0', '3', '2', '4', '450000000', '2024'),
(3, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 'Bogota, Niza Sur', '120.0', '4', '3', '5', '750000000', '2023');

-- 6.7 Datos Limpios y Normalizados (Working Cleaned)
INSERT INTO wrk_inmuebles_cleaned (
    id_cleaned, id_raw, id_dataset, id_barrio, id_tipo, tamano_m2, habitaciones, banos, estrato, precio_cop, anio_registro, es_valido
) VALUES
(1, 1, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 1, 1, 65.50, 2, 2, 4, 380000000.00, 2024, 1),
(2, 2, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 2, 1, 85.00, 3, 2, 4, 450000000.00, 2024, 1),
(3, 3, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 3, 2, 120.00, 4, 3, 5, 750000000.00, 2023, 1);

-- 6.8 Features Analíticas para Machine Learning
INSERT INTO fct_features_analiticas (
    id_feature, id_cleaned, precio_unitario_m2, puntaje_entorno, bano_por_hab_ratio, densidad_comercial, parqueadero_ratio, factor_precio_millones
) VALUES
(1, 1, 5801526.72, 8, 1.00, 0.0305, 0.0153, 1.0000),
(2, 2, 5294117.65, 6, 0.67, 0.0235, 0.0118, 1.0000),
(3, 3, 6250000.00, 9, 0.75, 0.0167, 0.0167, 1.0000);

-- 6.9 Consolidación en Master Data Management (Golden Record)
INSERT INTO mdm_inmuebles_maestros (
    id_maestro, id_barrio, id_tipo, direccion_normalizada, tamano_m2, habitaciones, banos, estrato, 
    precio_ultimo_cop, precio_unitario_m2, anio_construccion_referencia, latitud_corregida, longitud_corregida, hash_duplicado
) VALUES
('b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6e', 1, 1, 'kr 7 cl 45 10', 65.50, 2, 2, 4, 380000000.00, 5801526.72, 2018, 4.6450000, -74.0580000, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
('c2d3e4f5-a6b7-8c9d-0e1f-2a3b4c5d6e7f', 2, 1, 'cl 140 kr 15 20', 85.00, 3, 2, 4, 450000000.00, 5294117.65, 2015, 4.7230000, -74.0320000, '4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a'),
('d3e4f5a6-b7c8-9d0e-1f2a-3b4c5d6e7f8a', 3, 2, 'kr 70 cl 127 30', 120.00, 4, 3, 5, 750000000.00, 6250000.00, 2010, 4.7100000, -74.0720000, 'ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d');

-- 6.10 Dimensión de Entorno Urbano
INSERT INTO dim_entorno_urbano (
    id_entorno, id_maestro, parques_cercanos, vias_principales, area_remocion_masa_m2, grandes_superficies, colegios_cercanos, hospitales_cercanos, puntaje_amenidades
) VALUES
(1, 'b1c2d3e4-f5a6-7b8c-9d0e-1f2a3b4c5d6e', 3, 2, 0.00, 2, 2, 1, 8),
(2, 'c2d3e4f5-a6b7-8c9d-0e1f-2a3b4c5d6e7f', 2, 1, 0.00, 2, 1, 0, 6),
(3, 'd3e4f5a6-b7c8-9d0e-1f2a-3b4c5d6e7f8a', 4, 2, 0.00, 2, 2, 1, 9);

-- 6.11 Balance de Limpieza (Reporte de Ejecución)
INSERT INTO rpt_limpieza_ejecucion (
    id_reporte, id_dataset, total_registros_raw, total_registros_limpios, total_rechazados, total_duplicados_eliminados, total_nulos_imputados, tiempo_ejecucion_seg
) VALUES (
    1, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 3, 3, 0, 0, 0, 0.452
);

-- 6.12 Log de Notificación Despachada
INSERT INTO log_notificaciones (
    id_notificacion, id_dataset, email_destinatario, asunto, estado_envio
) VALUES (
    1, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 'estudiante.prueba@unisalle.edu.co', 
    'Éxito: Dataset procesado y cargado a MDM (3 registros)', 'ENVIADO'
);

-- ============================================================================
-- 7. CONSULTAS DE PRUEBA Y COMPROBACIÓN (QUERIES DE VERIFICACIÓN)
-- ============================================================================

-- Consulta 1: Vista consolidada del Golden Record con Localidad, Barrio y Tipología
SELECT 
    m.id_maestro,
    l.nombre AS localidad,
    b.nombre_barrio AS barrio,
    t.codigo AS tipo_inmueble,
    m.direccion_normalizada,
    m.tamano_m2,
    m.habitaciones,
    m.banos,
    m.estrato,
    m.precio_ultimo_cop,
    m.precio_unitario_m2,
    e.puntaje_amenidades
FROM mdm_inmuebles_maestros m
INNER JOIN cat_barrios b ON m.id_barrio = b.id_barrio
INNER JOIN cat_localidades l ON b.id_localidad = l.id_localidad
INNER JOIN cat_tipos_inmueble t ON m.id_tipo = t.id_tipo
LEFT JOIN dim_entorno_urbano e ON m.id_maestro = e.id_maestro;

-- Consulta 2: Trazabilidad completa desde el dataset de origen hasta el registro limpio y features
SELECT 
    d.nombre_archivo,
    d.usuario_email,
    r.ubicacion_raw,
    c.tamano_m2,
    c.precio_cop,
    f.precio_unitario_m2,
    f.bano_por_hab_ratio
FROM wrk_datasets_ingesta d
INNER JOIN stg_inmuebles_raw r ON d.id_dataset = r.id_dataset
INNER JOIN wrk_inmuebles_cleaned c ON r.id_raw = c.id_raw
INNER JOIN fct_features_analiticas f ON c.id_cleaned = f.id_cleaned;
