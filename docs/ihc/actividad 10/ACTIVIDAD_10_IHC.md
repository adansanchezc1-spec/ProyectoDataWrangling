# Actividad 10 — Foro de Discusión, Cierre e Interacción Académica

**Asignatura:** Interacción Humano-Computador (IHC)  
**Proyecto Base:** InmoInsight Bogotá — Sistema de Curaduría y Auditoría de Datos Inmobiliarios  
**Estudiante:** Adán Y. Sánchez Cubillos  
**Equipo de Proyecto:** Adán Y. Sánchez Cubillos & Sara Sofía Crespo Lerma  
**Fecha:** Noviembre de 2026  
**Fase:** CONTROL → EVALUACIÓN Y TRANSFERENCIA DE APRENDIZAJES  

---

## 📌 Guía Rápida para el Foro Institucional

Esta actividad consta de **dos momentos obligatorios**:
1. **Momento 1 — Aporte Individual:** Texto continuo de reflexión y síntesis crítica de entre 500 y 700 palabras (conteo verificado: **593 palabras** en el cuerpo principal).
2. **Momento 2 — Interacción con Dos Compañeros:** Dos réplicas académicas de entre 120 y 180 palabras cada una (conteo verificado: **164 palabras** y **168 palabras** respectivamente), con preguntas reflexivas y recomendaciones fundamentadas en IHC.

---

## MOMENTO 1: Publicación del Aporte Individual

### Título:
**Más allá de la interfaz: la convergencia del diseño centrado en el usuario y la prevención del error en sistemas de alta exigencia**

### Texto para Publicar en el Foro:

El diseño de interfaces efectivas trasciende la simple apariencia visual para convertirse en un engranaje sistemático donde el diseño centrado en el usuario (DCU) articula el prototipado, los patrones de interacción, la accesibilidad y la evaluación empírica. Durante el desarrollo de InmoInsight Bogotá —un sistema web para la curaduría y auditoría de datos residenciales—, experimentamos cómo el prototipado iterativo materializa el modelo mental del usuario, mientras que los patrones de diseño proporcionan soluciones ergonómicas comprobadas. A su vez, los principios de accesibilidad universal (WCAG 2.1) garantizan que la interacción sea perceptible y operable, y la evaluación de usabilidad actúa como el mecanismo de control empírico que valida si el artefacto satisface realmente las métricas de eficacia, eficiencia y satisfacción estipuladas por la norma ISO 9241-11.

En este marco, la decisión de diseño más trascendental del proyecto consistió en implementar una compuerta de validación visual estricta en tiempo real para el mapeo de columnas obligatorias. Al cargar lotes de datos inmobiliarios heterogéneos, los analistas y peritos solían omitir inadvertidamente atributos críticos como estrato o precio por metro cuadrado, corrompiendo la base maestra. Frente a ello, diseñamos un mecanismo que auto-detecta la correspondencia de las seis columnas mandatorias y bloquea de manera reactiva el botón de avance mediante un indicador dinámico ('6 de 6 obligatorias asignadas') y bordes semánticos de validación. Esta intervención eliminó la vulnerabilidad de la versión preliminar y aplicó rigurosamente la heurística de prevención de errores formulada por Nielsen (2024), resolviendo la necesidad crítica de certificar la integridad de los datos antes de ejecutar el costoso pipeline de procesamiento.

Asimismo, la fase de evaluación empírica con tres usuarios representativos reveló brechas significativas que desencadenaron una iteración sustancial. Durante la ejecución de tareas de auditoría forense, observamos que cuando un evaluador diagnosticaba una fila rechazada —como el predio REG-8942-04 descartado por superar el rango intercuartílico de precio—, se sentía forzado a reiniciar todo el flujo para reintentar la operación, perdiendo las configuraciones ya realizadas. La frustración observada justificó el rediseño integral de la pantalla de remediación: creamos un módulo de contingencia asistida que permite 'Cargar versión corregida' preservando el mapeo previo y los factores de ajuste, complementado con filtros facetados y chips interactivos removibles. Esta iteración redujo el tiempo mediano de auditoría a 1 minuto y 8 segundos, alcanzando una tasa de éxito del 100%.

El principal reto técnico y cognitivo radicó en la naturaleza del tipo de interfaz seleccionado: una aplicación web desktop-first orientada a la manipulación masiva de información tabular densa. La inspección simultánea de hasta 20 columnas generaba un alto riesgo de sobrecarga cognitiva y fatiga perceptual. Para resolverlo, descartamos entornos móviles o híbridos y adoptamos una arquitectura visual basada en tarjetas desacopladas, tipografía de alta legibilidad (Plus Jakarta Sans y JetBrains Mono), retroalimentación no intrusiva mediante notificaciones toast y un ratio de contraste superior a 5.5:1 que excede el nivel AA de las pautas WCAG 2.1. De este modo, garantizamos un área de trabajo amplia y descansada para analistas en jornadas continuas.

Como aprendizaje fundamental, este curso me demostró que la excelencia en ingeniería de software es estéril si el sistema impone barreras cognitivas que inducen al error humano. Como sostiene Norman (2013), cuando un usuario comete un error, el defecto reside en el diseño del sistema y no en la persona. En mis futuros proyectos de ciencia de datos y backend, no diseñaré arquitecturas basadas únicamente en la eficiencia del algoritmo, sino fundamentadas en los modelos conceptuales de los usuarios finales, integrando prototipos de alta fidelidad y pruebas de usabilidad desde las primeras fases del ciclo de vida.

---

### Referencias Consultadas (Normas APA 7.ª Edición):

- International Organization for Standardization. (2018). *Ergonomics of human-system interaction — Part 11: Usability: Definitions and concepts* (ISO Standard No. 9241-11:2018). https://www.iso.org/standard/63500.html
- Nielsen, J. (2024, January 30). *10 usability heuristics for user interface design*. Nielsen Norman Group. https://www.nngroup.com/articles/ten-usability-heuristics/
- Norman, D. A. (2013). *The design of everyday things: Revised and expanded edition*. Basic Books.
- World Wide Web Consortium. (2018). *Web content accessibility guidelines (WCAG) 2.1*. W3C Recommendation. https://www.w3.org/TR/WCAG21/

> **Métrica de Control:**  
> • Palabras en el cuerpo del aporte individual: **593 palabras** (Cumple con el rango solicitado: 500 – 700 palabras).

---

## MOMENTO 2: Interacción con los Compañeros

### 💬 Respuesta a Compañera (Proyecto Dotafora — Control de Inventario Móvil en Yopal)

**Texto para publicar en el foro:**

Me pareció muy acertado cómo aterrizaron el diseño de Dotafora a la realidad del mostrador en Yopal, sobre todo al tomarse en serio la restricción de los 30 segundos y el uso a una sola mano. La solución de anticipar el stock restante ('Hay 5 / Quedarán 3') es un ejemplo impecable de prevención de errores y visibilidad del estado que ahorra reprocesos sin entorpecer la atención al cliente.

Teniendo en cuenta ese ritmo acelerado y las constantes interrupciones del local, ¿cómo resolvieron o tienen previsto manejar el caso en que el vendedor seleccione por error una talla vecina y confirme la venta antes de percatarse?

Como sugerencia ligada a la heurística de control y libertad del usuario de Nielsen, les vendría muy bien complementar esa confirmación con una notificación efímera tipo snackbar con botón de 'Deshacer' durante unos segundos. En nuestro proyecto de analítica inmobiliaria vimos que ofrecer salidas de emergencia inmediatas le quita presión al usuario y evita descuadres posteriores en el inventario.

> **Métrica de Control:**  
> • Palabras de la Respuesta: **165 palabras** (Cumple estrictamente con el rango solicitado: 120 – 180 palabras).

---

### 💬 Respuesta a Compañero 2 (Enfoque: Plataforma Web / Accesibilidad e Inclusión WCAG)

**Texto para publicar en el foro:**

Me parece sumamente acertada tu reflexión respecto a concebir la accesibilidad (WCAG 2.1) como un pilar arquitectónico desde el inicio y no como una capa estética superficial añadida al final del ciclo de desarrollo. La decisión de estandarizar contrastes cromáticos y dotar de redundancia semántica a los estados de error mediante texto e iconos evita que los usuarios con deficiencias visuales o en condiciones lumínicas adversas queden excluidos de la interacción básica.

Considerando los desafíos que mencionas en plataformas web educativas, ¿qué criterios específicos adoptaron para garantizar la navegación integral mediante teclado y lectores de pantalla (como JAWS o NVDA) en los componentes dinámicos y modales de su aplicación?

Como aporte adicional, sugiero incorporar un indicador de foco visible prominente (outline de al menos 3 píxeles) y regiones ARIA en vivo (`aria-live="polite"`) para anunciar cambios de estado sin interrumpir al estudiante. En nuestro prototipo de curaduría de datos, esta práctica garantizó que los avisos emergentes fueran percibidos oportunamente por cualquier perfil, cumpliendo cabalmente con la norma ISO 9241-11.

> **Métrica de Control:**  
> • Palabras de la Respuesta 2: **168 palabras** (Cumple con el rango solicitado: 120 – 180 palabras).

