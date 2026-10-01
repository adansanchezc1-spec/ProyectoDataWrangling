# 03. Diccionario de Metadatos y Registro de Elementos (ISO/IEC 11179)
**Estándar**: ISO/IEC 11179 (Information Technology — Metadata Registries / MDR) · ISO/IEC 25012 · MySQL 8.0+ / 8.4+ LTS  
**Fase PDCO**: `PLAN → DEVELOPMENT` | **SDLC Stage**: Detailed Database Design  
**Proyecto**: Sistema Data Wrangling & MDM Inmobiliario (Bogotá Real Estate)  

---

## 1. Convenciones de Nomenclatura y Estructura ISO/IEC 11179

De acuerdo con el estándar **ISO/IEC 11179-5 (Naming and identification principles)**, todos los elementos de datos se estructuran siguiendo la tríada:
$$\text{Objeto de Negocio} + \text{Término de Propiedad} + \text{Término de Representación}$$

### Términos de Representación Estándar
- `Identifier`: Clave unívoca subrogada o natural (`id_...`, `hash_...`).
- `Code`: Código estándar alfanumérico o categórico (`codigo_...`, `compuerta_...`).
- `Name`: Denominación textual en lenguaje natural (`nombre_...`).
- `Quantity`: Valor numérico entero discreto (`habitaciones`, `banos`, `parques_cercanos`).
- `Measure`: Medida física continua o métrica calculada (`tamano_m2`, `latitud_...`).
- `Amount`: Valor monetario en divisa (`precio_cop`, `precio_ultimo_cop`).
- `Ratio`: Proporción matemática adimensional (`bano_por_hab_ratio`, `parqueadero_ratio`).
- `Date / DateTime`: Marca temporal (`fecha_ingesta`, `created_at`).
- `Status / Indicator`: Estado de máquina o bandera booleana (`estado_pipeline`, `es_valido`).

---

## 2. Diccionario de Metadatos por Entidad

### 2.1 Tabla: `cat_localidades` (Catálogo de Localidades)
| Elemento de Datos | Término Repr. | Tipo SQL (MySQL / ISO 9075) | Nulable | PK/FK/UK | Dominio / Regla de Negocio | Descripción Semántica |
|---|---|---|---|---|---|---|
| `id_localidad` | Identifier | `INT AUTO_INCREMENT` | NO | PK | Auto-incremental $\ge 1$ | Identificador subrogado de la localidad. |
| `codigo_dane` | Code | `VARCHAR(10)` | NO | UK | Códigos DANE oficiales (`1101` a `1120`) | Código territorial oficial según DANE. |
| `nombre` | Name | `VARCHAR(100)` | NO | - | Texto no vacío (ej. "Usaquén", "Chapinero") | Nombre oficial de la localidad. |
| `zona_bogota` | Name | `VARCHAR(50)` | NO | - | `{'Norte', 'Sur', 'Centro', 'Occidente'}` | Macro-sectorización urbana en Bogotá. |
| `created_at` | DateTime | `DATETIME` | NO | - | `DEFAULT CURRENT_TIMESTAMP` | Fecha de creación del registro. |

---

### 2.2 Tabla: `cat_barrios` (Catálogo de Barrios y Comunas)
| Elemento de Datos | Término Repr. | Tipo SQL (MySQL / ISO 9075) | Nulable | PK/FK/UK | Dominio / Regla de Negocio | Descripción Semántica |
|---|---|---|---|---|---|---|
| `id_barrio` | Identifier | `INT AUTO_INCREMENT` | NO | PK | Auto-incremental $\ge 1$ | Identificador subrogado del barrio. |
| `id_localidad` | Identifier | `INT` | NO | FK | `REFERENCES cat_localidades` | Clave foránea a la localidad contenedora. |
| `nombre_barrio` | Name | `VARCHAR(120)` | NO | - | Texto alfanumérico limpio | Nombre formal del barrio o UPZ. |
| `estrato_moda` | Quantity | `SMALLINT` | NO | - | `BETWEEN 1 AND 6` (RB-002) | Estrato socioeconómico predominante del barrio. |
| `latitud_centroide`| Measure | `DECIMAL(10,7)` | NO | - | `BETWEEN 4.4500000 AND 4.8500000` (RB-001) | Coordenada geográfica latitud (WGS84). |
| `longitud_centroide`| Measure | `DECIMAL(10,7)` | NO | - | `BETWEEN -74.2500000 AND -73.9500000` (RB-001) | Coordenada geográfica longitud (WGS84). |
| `created_at` | DateTime | `DATETIME` | NO | - | `DEFAULT CURRENT_TIMESTAMP` | Fecha de registro en el catálogo. |

---

### 2.3 Tabla: `cat_tipos_inmueble` (Catálogo de Tipologías)
| Elemento de Datos | Término Repr. | Tipo SQL (MySQL / ISO 9075) | Nulable | PK/FK/UK | Dominio / Regla de Negocio | Descripción Semántica |
|---|---|---|---|---|---|---|
| `id_tipo` | Identifier | `INT AUTO_INCREMENT` | NO | PK | Auto-incremental $\ge 1$ | Identificador del tipo de inmueble. |
| `codigo` | Code | `VARCHAR(30)` | NO | UK | `{'APARTAMENTO', 'CASA', 'ESTUDIO', 'LOTE'}` | Código mnemotécnico tipológico. |
| `descripcion` | Name | `VARCHAR(100)` | NO | - | Texto descriptivo | Descripción extendida del tipo de bien. |

---

### 2.4 Tabla: `cat_fuentes_origen` (Fuentes Externas de Datos)
| Elemento de Datos | Término Repr. | Tipo SQL (MySQL / ISO 9075) | Nulable | PK/FK/UK | Dominio / Regla de Negocio | Descripción Semántica |
|---|---|---|---|---|---|---|
| `id_fuente` | Identifier | `INT AUTO_INCREMENT` | NO | PK | Auto-incremental $\ge 1$ | Identificador de la fuente origen. |
| `nombre_fuente` | Name | `VARCHAR(80)` | NO | UK | Texto unívoco (ej. "MetroCuadrado") | Nombre de la entidad proveedora. |
| `tipo_formato_default`| Code | `VARCHAR(20)` | NO | - | `{'CSV', 'EXCEL', 'JSON'}` (RB-004) | Formato por defecto del archivo fuente. |
| `estado` | Status | `VARCHAR(20)` | NO | - | `{'ACTIVO', 'INACTIVO'}` | Estado operativo de la fuente. |

---

### 2.5 Tabla: `wrk_datasets_ingesta` (Lotes de Ingesta ETL)
| Elemento de Datos | Término Repr. | Tipo SQL (MySQL / ISO 9075) | Nulable | PK/FK/UK | Dominio / Regla de Negocio | Descripción Semántica |
|---|---|---|---|---|---|---|
| `id_dataset` | Identifier | `VARCHAR(36)` | NO | PK | Formato UUIDv4 canónico | Identificador universal del lote ETL. |
| `id_fuente` | Identifier | `INT` | NO | FK | `REFERENCES cat_fuentes_origen` | Fuente de procedencia del dataset. |
| `nombre_archivo` | Name | `VARCHAR(255)` | NO | - | Nombre físico del archivo cargado | Nombre original del fichero. |
| `hash_sha256` | Identifier | `CHAR(64)` | NO | - | Cadena SHA-256 (64 hex) (ISO 8000) | Hash criptográfico de integridad del archivo. |
| `usuario_email` | Name | `VARCHAR(120)` | NO | - | Formato email válido (RB-006) | Correo del usuario que inició la carga. |
| `estado_pipeline`| Status | `VARCHAR(30)` | NO | - | `{'CARGADO', 'VALIDANDO', 'COMPLETADO', 'RECHAZADO'}` | Estado de avance en el workflow BPMN. |
| `fecha_ingesta` | DateTime | `DATETIME` | NO | - | `DEFAULT CURRENT_TIMESTAMP` | Timestamp de recepción del lote. |

---

### 2.6 Tabla: `stg_inmuebles_raw` (Capa Staging Cruda)
| Elemento de Datos | Término Repr. | Tipo SQL (MySQL / ISO 9075) | Nulable | PK/FK/UK | Dominio / Regla de Negocio | Descripción Semántica |
|---|---|---|---|---|---|---|
| `id_raw` | Identifier | `BIGINT AUTO_INCREMENT` | NO | PK | Auto-incremental $\ge 1$ | Identificador del registro crudo. |
| `id_dataset` | Identifier | `VARCHAR(36)` | NO | FK | `REFERENCES wrk_datasets_ingesta` | Lote de ingesta al que pertenece la fila. |
| `ubicacion_raw` | Text | `TEXT` | SÍ | - | Cadena cruda sin transformar | Valor original de la columna ubicación. |
| `tamano_raw` | Text | `TEXT` | SÍ | - | Cadena cruda sin transformar | Valor original de tamaño / m². |
| `habitaciones_raw`| Text | `TEXT` | SÍ | - | Cadena cruda sin transformar | Valor original de habitaciones. |
| `banos_raw` | Text | `TEXT` | SÍ | - | Cadena cruda sin transformar | Valor original de baños. |
| `estrato_raw` | Text | `TEXT` | SÍ | - | Cadena cruda sin transformar | Valor original de estrato. |
| `precio_raw` | Text | `TEXT` | SÍ | - | Cadena cruda sin transformar | Valor original de precio. |
| `fecha_raw` | Text | `TEXT` | SÍ | - | Cadena cruda sin transformar | Valor original de fecha/año. |
| `fecha_extraccion`| DateTime | `DATETIME` | NO | - | `DEFAULT CURRENT_TIMESTAMP` | Timestamp de persistencia en staging. |

---

### 2.7 Tabla: `wrk_inmuebles_cleaned` (Registros Limpios y Saneados)
| Elemento de Datos | Término Repr. | Tipo SQL (MySQL / ISO 9075) | Nulable | PK/FK/UK | Dominio / Regla de Negocio | Descripción Semántica |
|---|---|---|---|---|---|---|
| `id_cleaned` | Identifier | `BIGINT AUTO_INCREMENT` | NO | PK | Auto-incremental $\ge 1$ | Identificador del registro limpio. |
| `id_raw` | Identifier | `BIGINT` | NO | FK/UK | `REFERENCES stg_inmuebles_raw` | Registro crudo de origen ($1:1$). |
| `id_dataset` | Identifier | `VARCHAR(36)` | NO | FK | `REFERENCES wrk_datasets_ingesta` | Lote de procesamiento. |
| `id_barrio` | Identifier | `INT` | NO | FK | `REFERENCES cat_barrios` (RB-001) | Barrio normalizado en Bogotá. |
| `id_tipo` | Identifier | `INT` | NO | FK | `REFERENCES cat_tipos_inmueble` | Tipología validada. |
| `tamano_m2` | Measure | `DECIMAL(10,2)` | NO | - | `> 0 AND <= 50000.00` (RB-005) | Área construida en metros cuadrados. |
| `habitaciones` | Quantity | `SMALLINT` | NO | - | `BETWEEN 1 AND 20` (RB-005) | Número de habitaciones del inmueble. |
| `banos` | Quantity | `SMALLINT` | NO | - | `BETWEEN 1 AND 15` (RB-005) | Número de baños completos y sociales. |
| `estrato` | Quantity | `SMALLINT` | NO | - | `BETWEEN 1 AND 6` (RB-002) | Estrato socioeconómico validado. |
| `precio_cop` | Amount | `DECIMAL(14,2)` | NO | - | `> 0 AND <= 50000000000.00` (RB-005) | Precio en pesos colombianos (COP). |
| `anio_registro` | Quantity | `SMALLINT` | NO | - | `BETWEEN 1900 AND 2026` (RF-011) | Año del registro inmobiliario para ML. |
| `es_valido` | Indicator| `BOOLEAN` | NO | - | `DEFAULT TRUE` | Bandera de aptitud para consumo analítico. |

---

### 2.8 Tabla: `fct_features_analiticas` (Variables Derivadas para ML)
| Elemento de Datos | Término Repr. | Tipo SQL (MySQL / ISO 9075) | Nulable | PK/FK/UK | Dominio / Regla de Negocio | Descripción Semántica |
|---|---|---|---|---|---|---|
| `id_feature` | Identifier | `BIGINT AUTO_INCREMENT` | NO | PK | Auto-incremental $\ge 1$ | Identificador del vector de features. |
| `id_cleaned` | Identifier | `BIGINT` | NO | FK/UK | `REFERENCES wrk_inmuebles_cleaned` | Registro limpio asociado ($1:1$). |
| `precio_unitario_m2`| Amount | `DECIMAL(14,2)` | NO | - | `precio_cop / tamano_m2` | Precio normalizado por metro cuadrado. |
| `puntaje_entorno` | Quantity | `INT` | NO | - | `parques + colegios + hospitales` | Score agregado de amenidades. |
| `bano_por_hab_ratio`| Ratio | `DECIMAL(5,2)` | NO | - | `banos / habitaciones >= 0.0` | Proporción de baños por habitación. |
| `densidad_comercial`| Ratio | `DECIMAL(8,4)` | NO | - | `grandes_superficies / tamano_m2` | Coeficiente comercial relativo. |
| `parqueadero_ratio`| Ratio | `DECIMAL(8,4)` | NO | - | `parqueaderos / tamano_m2` | Ratio de estacionamientos por m². |
| `factor_precio_millones`| Ratio | `DECIMAL(12,4)` | NO | - | `DEFAULT 1.0000` | Factor de escala para modelos de regresión. |

---

### 2.9 Tabla: `mdm_inmuebles_maestros` (Master Data Management - Golden Record)
| Elemento de Datos | Término Repr. | Tipo SQL (MySQL / ISO 9075) | Nulable | PK/FK/UK | Dominio / Regla de Negocio | Descripción Semántica |
|---|---|---|---|---|---|---|
| `id_maestro` | Identifier | `VARCHAR(36)` | NO | PK | Formato UUIDv4 canónico | Identificador maestro único del inmueble. |
| `id_barrio` | Identifier | `INT` | NO | FK | `REFERENCES cat_barrios` | Barrio Bogotá consolidado. |
| `id_tipo` | Identifier | `INT` | NO | FK | `REFERENCES cat_tipos_inmueble` | Tipología consolidada. |
| `direccion_normalizada`| Name | `VARCHAR(200)` | NO | - | Nomenclatura vial estandarizada | Dirección limpia y geocodificada. |
| `tamano_m2` | Measure | `DECIMAL(10,2)` | NO | - | `> 0.00` | Área útil consolidada. |
| `habitaciones` | Quantity | `SMALLINT` | NO | - | `BETWEEN 1 AND 20` | Habitaciones consolidadas. |
| `banos` | Quantity | `SMALLINT` | NO | - | `BETWEEN 1 AND 15` | Baños consolidados. |
| `estrato` | Quantity | `SMALLINT` | NO | - | `BETWEEN 1 AND 6` | Estrato socioeconómico definitivo. |
| `precio_ultimo_cop`| Amount | `DECIMAL(14,2)` | NO | - | `> 0.00` | Última cotización registrada en COP. |
| `precio_unitario_m2`| Amount | `DECIMAL(14,2)` | NO | - | `> 0.00` | Precio histórico por m². |
| `anio_construccion_referencia`| Quantity | `SMALLINT` | SÍ | - | `BETWEEN 1900 AND 2026` | Año estimado de edificación. |
| `latitud_corregida`| Measure | `DECIMAL(10,7)` | NO | - | `BETWEEN 4.4500000 AND 4.8500000` | Latitud corregida espacialmente. |
| `longitud_corregida`| Measure | `DECIMAL(10,7)` | NO | - | `BETWEEN -74.2500000 AND -73.9500000`| Longitud corregida espacialmente. |
| `hash_duplicado` | Identifier | `CHAR(64)` | NO | UK | SHA-256 (RB-003 / ISO 8000) | Clave única de deduplicación semántica. |
| `fecha_consolidacion`| DateTime | `DATETIME` | NO | - | `DEFAULT CURRENT_TIMESTAMP` | Fecha de consolidación en el MDM. |

---

### 2.10 Tabla: `dim_entorno_urbano` (Dimensión de Contexto Espacial)
| Elemento de Datos | Término Repr. | Tipo SQL (MySQL / ISO 9075) | Nulable | PK/FK/UK | Dominio / Regla de Negocio | Descripción Semántica |
|---|---|---|---|---|---|---|
| `id_entorno` | Identifier | `BIGINT AUTO_INCREMENT` | NO | PK | Auto-incremental $\ge 1$ | Identificador del registro de entorno. |
| `id_maestro` | Identifier | `VARCHAR(36)` | NO | FK/UK | `REFERENCES mdm_inmuebles_maestros` | Inmueble maestro asociado ($1:1$). |
| `parques_cercanos` | Quantity | `INT` | NO | - | `DEFAULT 0 AND >= 0` | Cantidad de parques en radio de 1 km. |
| `vias_principales` | Quantity | `INT` | NO | - | `DEFAULT 0 AND >= 0` | Vías arteriales en proximidad. |
| `area_remocion_masa_m2`| Measure | `DECIMAL(10,2)` | NO | - | `DEFAULT 0.00 AND >= 0.00` | Área en zona de riesgo geológico (m²). |
| `grandes_superficies`| Quantity | `INT` | NO | - | `DEFAULT 0 AND >= 0` | Centros comerciales y supermercados. |
| `colegios_cercanos`| Quantity | `INT` | NO | - | `DEFAULT 0 AND >= 0` | Instituciones educativas en radio 1 km. |
| `hospitales_cercanos`| Quantity | `INT` | NO | - | `DEFAULT 0 AND >= 0` | Centros de salud y hospitales en radio 2 km. |
| `puntaje_amenidades`| Quantity | `INT` | NO | - | `DEFAULT 0 AND >= 0` | Índice global ponderado de amenidades. |

---

### 2.11 Tabla: `log_rechazos_calidad` (Auditoría de Rechazos BPMN)
| Elemento de Datos | Término Repr. | Tipo SQL (MySQL / ISO 9075) | Nulable | PK/FK/UK | Dominio / Regla de Negocio | Descripción Semántica |
|---|---|---|---|---|---|---|
| `id_rechazo` | Identifier | `BIGINT AUTO_INCREMENT` | NO | PK | Auto-incremental $\ge 1$ | Identificador del evento de rechazo. |
| `id_dataset` | Identifier | `VARCHAR(36)` | NO | FK | `REFERENCES wrk_datasets_ingesta` | Lote de origen donde falló la validación. |
| `compuerta_bpmn` | Code | `VARCHAR(10)` | NO | - | `{'G1', 'G2', 'G3', 'G4'}` | Gateway BPMN 2.0 donde se detectó el fallo. |
| `codigo_regla` | Code | `VARCHAR(20)` | NO | - | `{'RB-001', 'RB-002', ..., 'RB-005'}` | Regla de negocio infringida. |
| `motivo_error` | Text | `TEXT` | NO | - | Texto explicativo del fallo | Detalle técnico del error. |
| `payload_registro`| Text | `JSON` | SÍ | - | Documento JSON nativo | Valores crudos del registro rechazado. |
| `fecha_rechazo` | DateTime | `DATETIME` | NO | - | `DEFAULT CURRENT_TIMESTAMP` | Timestamp exacto del descarte. |

---

### 2.12 Tabla: `rpt_limpieza_ejecucion` (Balance Agregado de Limpieza)
| Elemento de Datos | Término Repr. | Tipo SQL (MySQL / ISO 9075) | Nulable | PK/FK/UK | Dominio / Regla de Negocio | Descripción Semántica |
|---|---|---|---|---|---|---|
| `id_reporte` | Identifier | `BIGINT AUTO_INCREMENT` | NO | PK | Auto-incremental $\ge 1$ | Identificador del balance de ejecución. |
| `id_dataset` | Identifier | `VARCHAR(36)` | NO | FK/UK | `REFERENCES wrk_datasets_ingesta` | Lote de ingesta evaluado ($1:1$). |
| `total_registros_raw`| Quantity | `INT` | NO | - | `total_registros_raw >= 0` | Total de filas leídas en la fuente. |
| `total_registros_limpios`| Quantity | `INT` | NO | - | `total_registros_limpios >= 0` | Total de filas aptas y normalizadas. |
| `total_rechazados`| Quantity | `INT` | NO | - | `total_rechazados >= 0` | Total de registros descartados por reglas. |
| `total_duplicados_eliminados`| Quantity | `INT` | NO | - | `total_duplicados >= 0` (RB-003) | Total de duplicados detectados y suprimidos. |
| `total_nulos_imputados`| Quantity | `INT` | NO | - | `total_nulos >= 0` | Total de valores nulos corregidos/imputados. |
| `tiempo_ejecucion_seg`| Measure | `DECIMAL(8,3)` | NO | - | Latencia en segundos $> 0.000$ | Tiempo de procesamiento CPU/I-O. |
| `fecha_generacion`| DateTime | `DATETIME` | NO | - | `DEFAULT CURRENT_TIMESTAMP` | Timestamp de generación del reporte. |

---

### 2.13 Tabla: `log_notificaciones` (Auditoría de Envíos de Correo)
| Elemento de Datos | Término Repr. | Tipo SQL (MySQL / ISO 9075) | Nulable | PK/FK/UK | Dominio / Regla de Negocio | Descripción Semántica |
|---|---|---|---|---|---|---|
| `id_notificacion` | Identifier | `BIGINT AUTO_INCREMENT` | NO | PK | Auto-incremental $\ge 1$ | Identificador de la notificación. |
| `id_dataset` | Identifier | `VARCHAR(36)` | NO | FK | `REFERENCES wrk_datasets_ingesta` | Lote asociado al evento. |
| `email_destinatario`| Name | `VARCHAR(120)` | NO | - | Formato con `@` (RB-006) | Dirección de correo receptora. |
| `asunto` | Name | `VARCHAR(200)` | NO | - | Texto del asunto | Resumen de notificación enviado. |
| `estado_envio` | Status | `VARCHAR(30)` | NO | - | `{'ENVIADO', 'FALLIDO', 'SIMULADO'}` | Estado del despacho del correo. |
| `fecha_envio` | DateTime | `DATETIME` | NO | - | `DEFAULT CURRENT_TIMESTAMP` | Timestamp de despacho del mensaje. |
