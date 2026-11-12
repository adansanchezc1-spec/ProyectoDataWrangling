# Protocolo y registro de indagación y prueba de usabilidad

**Proyecto:** InmoInsight Bogotá  
**Versión:** 1.0  
**Estado:** Instrumento preparado; sesiones no realizadas.  
**Lugar para diligenciar:** sesión académica acordada con cada participante.

## 1. Convocatoria

Invitar voluntariamente a personas que hayan trabajado con datos, archivos de inmuebles, analítica inmobiliaria o consulta de inventarios. Buscar variedad de experiencia: al menos una persona cercana a la operación de datos y una consumidora/analista del resultado. No recopilar información de su empleador ni pedir archivos reales. La selección final depende de disponibilidad y autorización docente.

### Mensaje de invitación

> Estamos realizando una actividad académica de Interacción Humano-Computador sobre una interfaz para organizar y revisar datos inmobiliarios. Buscamos personas con experiencia relacionada con datos o análisis inmobiliario para una sesión de aproximadamente 30 minutos. Participar es voluntario; puedes omitir preguntas o retirarte en cualquier momento. Usaremos un prototipo con datos ficticios y reportaremos notas anónimas. No solicitaremos nombres, identificación ni información reservada. ¿Te interesaría participar?

## 2. Consentimiento verbal

Leer antes de iniciar y registrar únicamente Sí/No:

> Explicamos que esta sesión es parte de un proyecto académico. Evaluamos el prototipo, no tus capacidades. La participación es voluntaria y puedes detenerte u omitir cualquier pregunta. No solicitaremos datos sensibles. Registraremos acciones y comentarios bajo un código, sin nombre. Las notas se usarán para mejorar el diseño y se presentarán de forma anónima. ¿Aceptas participar con estas condiciones?

Consentimiento para participar: `Sí / No`  
Consentimiento independiente para audio (opcional; no requerido): `No solicitado / Sí / No`  
Si no acepta participar, agradecer y finalizar; no registrar respuestas.

## 3. Ficha anónima de contexto

Código aleatorio: `P__`  
Rol amplio (sin empresa): ____________________  
Experiencia relacionada (rango opcional): `menos de 1 año / 1–3 / más de 3 / prefiere no decir`  
Actividades relevantes: ____________________  
Frecuencia aproximada: `diaria / semanal / mensual / ocasional / otra: ____`  
Herramientas habituales: ____________________  
Dispositivo y sistema operativo: ____________________  
Entorno de uso (interrupciones/colaboración): ____________________  
Conectividad o restricciones de acceso relevantes: ____________________  
Preferencias/necesidades de accesibilidad que quiera compartir (opcional): ____________________

No anotar dirección, edad exacta, teléfono, correo, empleador, identificadores ni información financiera o médica.

## 4. Entrevista semiestructurada

Duración prevista: 15–20 minutos. Usar las preguntas abiertas del apartado 2 del `INFORME_FASE2_IHC.md`. Registrar ideas resumidas, no transcribir información identificable. Preguntas de profundización: “¿Puedes contarme un ejemplo reciente sin compartir datos privados?” y “¿Qué esperabas que ocurriera después?”.

### Registro de notas por tema

| Tema | Nota anónima (no incluir nombres ni datos sensibles) | Cita textual opcional, revisada para anonimato |
|---|---|---|
| Actividades y secuencia | | |
| Necesidades / información requerida | | |
| Dificultades y recuperación | | |
| Conocimientos y vocabulario | | |
| Dispositivo / entorno / frecuencia | | |
| Accesibilidad / conectividad | | |
| Expectativas y prioridades | | |

## 5. Guion de prueba moderada

Usar `docs/ihc/fase2/prototipo/index.html` y explicar que es una simulación con datos ficticios. No demostrar la solución antes de cada tarea. Leer el escenario literalmente y permitir que la persona piense en voz alta.

**Introducción:** “Gracias. Estamos probando el diseño, no tus habilidades. Realiza las tareas como lo harías normalmente. No hay consecuencias por equivocarte. Si algo no queda claro, puedes decirlo; registraré si pides ayuda.”

| Tarea | Escenario neutral | Éxito completo | Éxito parcial | Error/ayuda a registrar |
|---|---|---|---|---|
| T1. Seleccionar y revisar carga | “Debes iniciar una carga con un archivo disponible, revisar la información que presenta el sistema y llegar al resumen previo a ejecutarla. Detente cuando el prototipo indique que solo simula el procesamiento.” | Llega a confirmación y explica qué se verificó y qué no | Avanza con una pista o no distingue la vista previa ficticia | Formato, selección, interpretación, campos que cree obligatorios, solicitud de ayuda |
| T2. Comprender un rechazo | “Un registro de ejemplo no pasó una regla. Averigua qué dato causó el problema y qué harías para resolverlo sin cambiar información que no conoces.” | Identifica etapa, regla, valor observado y acción segura | Identifica causa, pero no el siguiente paso | Confusión por nombre técnico, lectura del mensaje, acción riesgosa |
| T3. Filtrar auditoría | “Busca los registros de la etapa de validación de valores y vuelve a mostrar la lista completa.” | Aplica filtro correcto, explica el resultado y restablece | Completa tras una pista o no logra restablecer | Filtros, número esperado, persistencia y solicitudes de ayuda |

Después de cada tarea: “¿Qué tan satisfecho/a quedaste con este recorrido?” escala 1 (nada) a 5 (muy). No guiar con lenguaje que sugiera una respuesta.

## 6. Registro de observación por participante

Código: `P__`  Fecha: __________  Facilitador/a: __________  Observador/a: __________  Consentimiento: `Sí / No`

| Tarea | Inicio | Fin | Duración (seg) | Resultado (C/P/NC) | Errores observables (n y descripción) | Ayudas (n y pista literal) | Duda/comentario anónimo | Satisfacción 1–5 |
|---|---|---|---:|---|---|---|---|---:|
| T1 | | | | | | | | |
| T2 | | | | | | | | |
| T3 | | | | | | | | |

Comentarios de cierre: ____________________________________________________

## 7. Consolidado de participantes

Completar tras las sesiones; no rellenar con valores estimados.

| Código | Perfil amplio | T1 C/P/NC | T2 C/P/NC | T3 C/P/NC | Restricción/contexto relevante anonimizado |
|---|---|---|---|---|---|
| P01 | | | | | |
| P02 | | | | | |
| P03 | | | | | |

### Resumen de métricas

| Medida | T1 | T2 | T3 | Método de cálculo/notas |
|---|---:|---:|---:|---|
| Finalización completa | | | | Completas / 3 intentos válidos × 100 |
| Parcial / no completada | | | | Reportar cada categoría por separado |
| Tiempo (mediana, rango) | | | | Segundos; señalar si hubo pista o resultado parcial |
| Errores observados | | | | Conteo total y tipo; definir antes de analizar |
| Solicitudes de ayuda | | | | Conteo y tipo de pista proporcionada |
| Satisfacción promedio (1–5) | | | | Promedio y distribución, n explícito |

Con n=3, interpretar como señal cualitativa de diseño, no como estimación estadística de toda la población usuaria.

## 8. Síntesis y trazabilidad

| Hallazgo (sin dato identificable) | Evidencia/códigos asociados | Necesidad | Requisito afectado | Prioridad | Cambio propuesto | Estado |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |

Eliminar notas identificables inmediatamente. Guardar solo agregados y citas anonimizadas en la entrega. No publicar formularios de consentimiento firmados.