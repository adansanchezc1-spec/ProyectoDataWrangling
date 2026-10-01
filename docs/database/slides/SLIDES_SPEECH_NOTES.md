# Guion de Sustentación Académica y Notas de Oratoria
## Actividad 2: Implementación de Base de Datos Relacional Normalizada (BCNF & MDM)
**Proyecto**: Sistema de Data Wrangling y Master Data Management Inmobiliario de Bogotá D.C.  
**Autores / Expositores**: Adán Yesid Sánchez Cubillos, Juan Sebastián Marles Montes y Andrés Felipe Pineda Pardo  
**Institución**: Universidad de La Salle — Facultad de Ingeniería  
**Materia / Asignatura**: Bases de datos  
**Docente**: Prof. Celso Javier Rodriguez Pizza  
**Tiempo Total Estimado**: 10 a 12 minutos (~1 minuto por diapositiva)  
**SGBD**: MySQL Server 8.0+ / 8.4+ LTS (Motor Transaccional Relacional InnoDB)  

---

## Estrategia de Reparto y Turnos de Exposición

| Expositor | Enfoque de la Presentación | Diapositivas Asignadas |
|---|---|---|
| **Adán Yesid Sánchez Cubillos** | Contextualización de negocio, pipeline BPMN 2.0, arquitectura conceptual EER en 4 cuadrantes DAMA y proceso de abstracción vs. antipatrón God Table. | **Slides 01, 02, 03, 04** |
| **Juan Sebastián Marles Montes** | Diagrama lógico relacional (Workbench), demostración matemática BCNF, diccionario ISO/IEC 11179 e implementación física en MySQL. | **Slides 05, 06, 07, 08** |
| **Andrés Felipe Pineda Pardo** | Terminal de pruebas de integridad (códigos 1062, 3819, 1451), arquitectura desacoplada (SOLID-DIP), matriz de seguridad y conclusiones normativas. | **Slides 09, 10, 11** |

---

## Slide por Slide: Guion de Defensa Técnica

### Slide 01 — Portada Tech Ejecutiva & Presentación Institucional
- **Expositor**: Adán Yesid Sánchez Cubillos
- **Tiempo**: 0:45 min
- **Discurso Sugerido**:
  > *"Muy buenos días profesor Celso Javier Rodriguez Pizza y compañeros. Junto con mis compañeros Juan Sebastián Marles Montes y Andrés Felipe Pineda Pardo, presentamos la sustentación de la Actividad 2: Diseño e Implementación de Base de Datos Relacional Normalizada para nuestro Sistema de Data Wrangling y Master Data Management Inmobiliario de Bogotá D.C.*  
  > *Este desarrollo da respuesta al ciclo SDLC bajo estándares internacionales: SWEBOK v4 en ingeniería de software, DAMA-DMBOK v2 en gobernanza y gestión de datos, ISO/IEC 11179 en metadatos, ISO/IEC 25012 en calidad de datos y con implementación física exclusiva sobre MySQL Server 8.4 LTS con motor transaccional InnoDB."*
- **Puntos Clave en Pantalla**:
  - Resaltar la acreditación BCNF, la trazabilidad del pipeline ETL y la articulación académica formal.

---

### Slide 02 — Caos de Datos Inmobiliarios en Bogotá y Pipeline BPMN 2.0
- **Expositor**: Adán Yesid Sánchez Cubillos
- **Tiempo**: 1:10 min
- **Discurso Sugerido**:
  > *"En Bogotá D.C., los datos del mercado inmobiliario provienen de portales comerciales masivos y fuentes catastrales abiertas en formatos no estructurados: CSV, Excel y JSON. Estos datasets exhiben patologías severas: direcciones inconsistentes, precios almacenados como cadenas de texto con caracteres especiales, y registros que violan las reglas de negocio, tales como inmuebles fuera de la cobertura geográfica de Bogotá (RB-001), estratos socioeconómicos inválidos fuera del rango 1 a 6 (RB-002) y duplicaciones masivas provocadas por publicaciones concurrentes (RB-003).*  
  > *Para gobernar este proceso, diseñamos un pipeline BPMN 2.0 con 4 compuertas de control de calidad innegociables: G1 valida la integridad física del archivo de entrada; G2 audita la presencia de columnas canónicas obligatorias; G3 normaliza tipos, filtra geometrías de Bogotá y valida estratos; y G4 ejecuta el feature engineering, valida consistencia física y deduplica registros mediante hashing criptográfico antes de consolidar el Golden Record."*
- **Términos Técnicos a Enfatizar**:
  - *Data Wrangling*, *Gateways de Calidad G1-G4*, *Reglas de Negocio RB-001 a RB-006*.

---

### Slide 03 — Diagrama Conceptual Entidad-Relación Extendido (EER - DAMA-DMBOK)
- **Expositor**: Adán Yesid Sánchez Cubillos
- **Tiempo**: 1:15 min
- **Discurso Sugerido**:
  > *"A partir del análisis de requerimientos funcionales, modelamos el Diagrama Conceptual EER compuesto por 13 entidades, estructuradas de manera rigurosa en los 4 cuadrantes del marco DAMA-DMBOK v2:*  
  > *1. Datos de Referencia: Localidades, barrios, tipos de inmueble y fuentes de origen, que normalizan y desacoplan la taxonomía territorial.*  
  > *2. Pipeline y Staging: El catálogo de datasets de ingesta, la capa de staging crudo inmutable y la capa working de inmuebles depurados con su vector de variables de ingeniería.*  
  > *3. Master Data (MDM): Nuestra entidad central `mdm_inmuebles_maestros`, que consolida el registro de verdad única o Golden Record, respaldado por la dimensión de entorno urbano contextual.*  
  > *4. Auditoría y Soporte: Registro forense de rechazos en `log_rechazos_calidad`, balance cuantitativo de lotes y logs de notificaciones por email.*  
  > *Todas las relaciones están tipificadas mediante cardinalidad Crow's Foot (1:1, 1:N, N:M descompuesta)."*
- **Términos Técnicos a Enfatizar**:
  - *Cuadrantes DAMA-DMBOK*, *Golden Record*, *Cardinalidad Crow's Foot*, *Entidades Fuertes y Débiles*.

---

### Slide 04 — Abstracción de Entidades vs. Antipatrón "God Table"
- **Expositor**: Adán Yesid Sánchez Cubillos
- **Tiempo**: 1:00 min
- **Discurso Sugerido**:
  > *"Una decisión clave de ingeniería fue rechazar tajantemente el antipatrón de la 'God Table' o tabla plana desnormalizada de 25 columnas. Almacenar todo en una única tabla ocasiona anomalías de actualización destructivas: si cambia el nombre o código de un barrio, se requeriría bloquear y actualizar potencialmente millones de registros. Además, se violaría la norma ISO 8000 al destruir el linaje del dato crudo original y el principio SOLID de Responsabilidad Única.*  
  > *Nuestra arquitectura garantiza inmutabilidad absoluta: el dato crudo en `stg_inmuebles_raw` jamás se modifica ni se sobreescribe; el registro limpio se transforma en la capa working; y únicamente los datos certificados por las compuertas se integran al MDM maestro."*
- **Paso de Testigo**:
  > *"A continuación, le cedo la palabra a mi compañero Juan Sebastián Marles Montes, quien sustentará el modelo lógico relacional, la demostración matemática BCNF y la especificación en MySQL."*

---

### Slide 05 — Diagrama Lógico Relacional (MySQL Workbench Schema & Conexiones)
- **Expositor**: Juan Sebastián Marles Montes
- **Tiempo**: 1:20 min
- **Discurso Sugerido**:
  > *"Muchas gracias, Adán. En esta diapositiva presentamos el Diagrama Lógico Relacional completo, diseñado según la convención oficial y rigurosa de MySQL Workbench.*  
  > *El esquema formaliza las 13 tablas relacionales con sus claves primarias (PK), foráneas (FK) y alternas (UQ), tipadas rigurosamente según los motores relacionales modernos.*  
  > *Observen la distribución arquitectónica y las líneas de conexión declarativas:*  
  > *1. En el extremo superior derecho, `CAT_FUENTES_ORIGEN` se conecta con cardinalidad 1 a N a `WRK_DATASETS_INGESTA` mediante la relación **'originates'**.*  
  > *2. Desde `WRK_DATASETS_INGESTA` parten cuatro conectores de control: hacia `STG_INMUEBLES_RAW` con la relación **'ingests'**; hacia `LOG_NOTIFICACIONES` mediante **'sends_notifications'**; hacia `LOG_RECHAZOS_CALIDAD` con **'logs_rejections'**; y hacia `RPT_LIMPIEZA_EJECUCION` mediante **'generates_reports'**.*  
  > *3. El flujo transaccional fluye desde `STG_INMUEBLES_RAW` hacia `WRK_INMUEBLES_CLEANED` a través de la relación **'cleans'**.*  
  > *4. En el dominio territorial a la izquierda, `CAT_LOCALIDADES` contiene a `CAT_BARRIOS` mediante la relación **'contains'**; a su vez, `CAT_BARRIOS` referencia tanto al registro maestro mediante **'defines_master_record'** como a la capa working.*  
  > *5. `CAT_TIPOS_INMUEBLE` clasifica a los inmuebles saneados (**'classifies'**) y tipifica al maestro (**'defines_master_type'**).*  
  > *6. En la base del modelo, observamos dos relaciones 1 a 1 de extensión dimensional: `WRK_INMUEBLES_CLEANED` genera las variables analíticas en `FCT_FEATURES_ANALITICAS` mediante **'produces_features'**, y nuestro Golden Record en `MDM_INMUEBLES_MAESTROS` se expande con `DIM_ENTORNO_URBANO` mediante **'enriches_urban_context'**.*  
  > *En pantalla disponemos de controles de zoom interactivo y un botón para abrir la captura nativa directa de MySQL Workbench."*
- **Términos Técnicos a Enfatizar**:
  - *Primary Keys (PK)*, *Foreign Keys (FK)*, *Unique Constraints (UQ)*, *Conectores Ortogonales*, *Cardinalidades 1:N y 1:1*.

---

### Slide 06 — Demostración Matemática de Normalización BCNF
- **Expositor**: Juan Sebastián Marles Montes
- **Tiempo**: 1:15 min
- **Discurso Sugerido**:
  > *"Demostramos formalmente el tránsito de normalización desde 1NF hasta Forma Normal de Boyce-Codd (BCNF).*  
  > *En Primera Forma Normal (1NF), eliminamos dominios no atómicos descomponiendo cadenas complejas de dirección en identificadores atómicos de localidad, barrio y nomenclatura.*  
  > *En Segunda Forma Normal (2NF), eliminamos dependencias parciales respecto a claves compuestas empleando identificadores subrogados unívocos.*  
  > *En Tercera Forma Normal (3NF), eliminamos la transitividad territorial: el inmueble referencia únicamente a su barrio, y el barrio a su localidad.*  
  > *Y en BCNF, demostramos matemáticamente que para toda Dependencia Funcional no trivial X tiende a Y, el determinante X es superclave estricta del esquema. Esta descomposición es Lossless Join Decomposition y preserva la totalidad de las dependencias funcionales."*
- **Términos Técnicos a Enfatizar**:
  - *Dependencia Funcional (DF)*, *Superclave Estricta*, *Lossless Join Decomposition*, *Forma Normal de Boyce-Codd*.

---

### Slide 07 — Diccionario de Metadatos y Estándar ISO/IEC 11179
- **Expositor**: Juan Sebastián Marles Montes
- **Tiempo**: 1:10 min
- **Discurso Sugerido**:
  > *"Cada elemento de datos ha sido formalmente catalogado bajo el estándar internacional ISO/IEC 11179-5, aplicando la estructura canónica: Objeto de Negocio + Término de Propiedad + Término de Representación.*  
  > *Estandarizamos el tipado estricto en MySQL:*  
  > *Identificadores subrogados de alto rendimiento en enteros autoincrementables; UUIDs canónicos de 36 caracteres en VARCHAR(36) para compatibilidad universal; coordenadas geográficas con precisión submétrica en DECIMAL(10,7); valores monetarios en DECIMAL(14,2) para impedir desbordamientos o imprecisiones de punto flotante; y el tipo nativo JSON para almacenar la carga cruda en el registro de rechazos.*  
  > *Cada atributo mapea directamente a las reglas de negocio del proyecto."*
- **Términos Técnicos a Enfatizar**:
  - *ISO/IEC 11179-5*, *Tipado Fuerte*, *Metadata Registries*, *Precisión Numérica*.

---

### Slide 08 — Implementación Física en SGBD MySQL (InnoDB & utf8mb4)
- **Expositor**: Juan Sebastián Marles Montes
- **Tiempo**: 1:15 min
- **Discurso Sugerido**:
  > *"En la capa física, implementamos el esquema exclusivamente en MySQL Server 8.4 LTS con motor InnoDB.*  
  > *Configuramos el conjunto de caracteres `utf8mb4` con colación `utf8mb4_unicode_ci`, garantizando total fidelidad tipográfica con acentos, caracteres en español y nomenclaturas de Bogotá.*  
  > *A nivel de integridad referencial, aplicamos políticas diferenciadas: `ON DELETE RESTRICT` para blindar los catálogos maestros territoriales impidiendo borrados accidentales, y `ON DELETE CASCADE` para lotes de trabajo transitorios.*  
  > *Asimismo, aprovechamos las restricciones CHECK nativas evaluadas en tiempo de ejecución por MySQL desde la versión 8.0.16, e indexamos B-Tree clustered y secundarios sobre claves foráneas y hashes de búsqueda para garantizar latencias P95 menores a 20 milisegundos."*
- **Paso de Testigo**:
  > *"A continuación, cedo la palabra a mi compañero Andrés Felipe Pineda Pardo, quien presentará las pruebas de integridad en terminal, la arquitectura de persistencia y las conclusiones del proyecto."*

---

### Slide 09 — Evidencias de Pruebas de Integridad con Datos Sintéticos
- **Expositor**: Andrés Felipe Pineda Pardo
- **Tiempo**: 1:20 min
- **Discurso Sugerido**:
  > *"Muchas gracias, Juan Sebastián. Un principio ético y normativo fundamental de nuestro proyecto es la privacidad de la información: la totalidad de las pruebas de integridad fueron ejecutadas con datos sintéticos generados algorítmicamente, sin utilizar datos personales ni sensibles de ciudadanos.*  
  > *En la diapositiva visualizamos la terminal de ejecución en MySQL con tres validaciones críticas:*  
  > *Prueba 1: Inserción de un inmueble con hash duplicado SHA-256. El motor activó la restricción UNIQUE 'uq_inmueble_hash' y bloqueó la transacción arrojando el Error 1062, validando exitosamente la regla RB-003.*  
  > *Prueba 2: Inserción de un inmueble con estrato socioeconómico 7. El motor disparó la restricción CHECK 'chk_cleaned_estrato' y canceló la operación con el Error 3819, dando cumplimiento estricto a RB-002.*  
  > *Prueba 3: Intento de borrado de una localidad con barrios activos asociados. La política ON DELETE RESTRICT bloqueó el borrado arrojando el Error 1451, protegiendo la integridad referencial del modelo."*
- **Términos Técnicos a Enfatizar**:
  - *Códigos de Error 1062, 3819, 1451*, *Datos Sintéticos*, *Integridad Referencial Forzada*.

---

### Slide 10 — Persistencia Desacoplada (SOLID-DIP) y Matriz de Seguridad
- **Expositor**: Andrés Felipe Pineda Pardo
- **Tiempo**: 1:10 min
- **Discurso Sugerido**:
  > *"En el diseño del software, implementamos el Principio de Inversión de Dependencias (SOLID-DIP) a través del Repository Pattern. Nuestra capa de servicios y las entidades del dominio interactúan exclusivamente con interfaces abstractas como `IDataRepository`. Esto significa que la aplicación no depende directamente de MySQL: si en el futuro se incorpora un nuevo conector, el núcleo del pipeline no sufre ninguna modificación.*  
  > *En el ámbito de la seguridad, aplicamos:*  
  > *1. Principio de Mínimo Privilegio (PoLP): el usuario de la aplicación solo posee permisos DML (SELECT, INSERT, UPDATE) sobre las tablas estrictamente requeridas, sin permisos de administración DDL.*  
  > *2. Protección total contra SQL Injection mediante sentencias preparadas y consultas parametrizadas.*  
  > *3. Trazabilidad criptográfica mediante hashes SHA-256 para cada lote y registro consolidado."*
- **Términos Técnicos a Enfatizar**:
  - *Dependency Inversion Principle (DIP)*, *Repository Pattern*, *Principle of Least Privilege (PoLP)*, *Sentencias Preparadas*.

---

### Slide 11 — Conclusiones, Estándares Internacionales y Roadmap SDLC
- **Expositor**: Andrés Felipe Pineda Pardo (con cierre conjunto)
- **Tiempo**: 1:10 min
- **Discurso Sugerido**:
  > *"Para concluir nuestra sustentación, este entregable certifica el cumplimiento riguroso de siete estándares internacionales de referencia: SWEBOK v4 en ingeniería y diseño, DAMA-DMBOK v2 en gobernanza de datos maestros, ISO 9075 en lenguaje SQL estandarizado, ISO/IEC 11179 en registro de metadatos, ISO/IEC 25012 en calidad de datos, ISO 8000 en linaje e inmutabilidad, y los principios SOLID de arquitectura de software.*  
  > *Transformamos fuentes no estructuradas, dispersas y patológicas de Bogotá en un modelo relacional BCNF de alta fidelidad, auditable y listo para abastecer pipelines analíticos y modelos predictivos.*  
  > *En la siguiente etapa del ciclo SDLC, avanzaremos en la implementación concreta de `mysql_repository.py` y la suite automatizada de pruebas unitarias.*  
  > *Agradecemos su atención y quedamos a total disposición del profesor Celso Javier Rodriguez Pizza para resolver cualquier inquietud."*

---

## Banco de Preguntas Docentes Preparadas (Defensa Técnica)

### P1: ¿Por qué eligieron BCNF en lugar de detenerse en 3NF?
- **Responde**: Juan Sebastián Marles Montes
- **Respuesta**: *"Porque en 3NF aún se toleran anomalías de actualización y redundancia cuando existen múltiples claves candidatas compuestas que se solapan entre sí. Al alcanzar la Forma Normal de Boyce-Codd, garantizamos que toda determinante en el esquema sea obligatoriamente una superclave estricta, erradicando al 100% las redundancias sin incurrir en pérdida de dependencias funcionales."*

### P2: ¿Por qué se utilizó MySQL de forma exclusiva y qué ventajas aporta InnoDB?
- **Responde**: Andrés Felipe Pineda Pardo
- **Respuesta**: *"MySQL Server 8.4 LTS con motor InnoDB provee cumplimiento ACID completo con transacciones atómicas y bloqueo a nivel de fila (row-level locking). Desde la versión 8.0.16, MySQL evalúa y fuerza de manera estricta las restricciones CHECK declarativas, soporta tipos JSON nativos con validación binaria interna, y permite administrar de forma homogénea las colaciones `utf8mb4_unicode_ci` y las políticas de integridad referencial requeridas en el estándar de la cátedra."*

### P3: ¿Cómo garantiza la base de datos la inmutabilidad y el linaje de los datos originales?
- **Responde**: Adán Yesid Sánchez Cubillos
- **Respuesta**: *"A través del aislamiento de capas en el diseño del modelo. La tabla `stg_inmuebles_raw` opera bajo el principio 'Append-Only': solo admite inserciones y lecturas. El proceso de Data Wrangling lee de staging y genera los registros saneados en la capa working. Si en cualquier momento se requiere una auditoría forense bajo ISO 8000, el dato original permanece inalterado exactamente como provino del archivo fuente."*

### P4: ¿Cuál es el rol del campo `hash_duplicado` en `mdm_inmuebles_maestros`?
- **Responde**: Juan Sebastián Marles Montes / Andrés Felipe Pineda Pardo
- **Respuesta**: *"Es una clave alterna con restricción UNIQUE generada mediante una función hash SHA-256 sobre la concatenación normalizada de dirección, área en m² y código de barrio. Esto permite que el motor de base de datos rechace automáticamente en tiempo O(log n) cualquier publicación duplicada entre portales comerciales con variaciones cosméticas, satisfaciendo de forma algorítmica la regla de negocio RB-003."*
