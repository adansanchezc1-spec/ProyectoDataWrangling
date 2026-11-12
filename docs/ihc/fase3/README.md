# Paquete de Entrega — Fase 3: IHC

**Proyecto:** InmoInsight Bogotá — Curaduría y Auditoría de Datos Inmobiliarios  
**Asignatura:** Interacción Humano-Computador  
**Equipo:** Adán Y. Sánchez Cubillos & Sara Sofía Crespo Lerma  
**Fecha:** 20 de Octubre de 2026  
**Estado:** Prototipo Navegable de Alta Fidelidad y Evaluación Empírica con Usuarios Concluidas.

---

## 📦 Artefactos del Paquete de Fase 3

1. **[Informe Académico Completo de la Fase 3](INFORME_FASE3_IHC.md):**
   - Revisión formal de las Fases 1 y 2.
   - Justificación técnica del tipo de interfaz web desktop-first.
   - Arquitectura de navegación y diagramas de secuencia de los **dos recorridos críticos**.
   - Catálogo de las **13 pantallas de alta fidelidad**.
   - Sistema de diseño (tokens, tipografía, paleta esmeralda/oro, componentes).
   - Patrones de diseño aplicados y auditoría de accesibilidad WCAG 2.1 AA.
   - Evaluación de usabilidad con 3 usuarios (**Usuario 1**, **Usuario 2**, **Usuario 3**) con métricas de tiempo, eficacia y satisfacción (ISO 9241-11).
   - Matriz de 5 oportunidades de mejora y evidencia de las **3 mejoras implementadas** (Antes vs. Después).

2. **[Prototipo Navegable de Alta Fidelidad](prototipo/index.html):**
   - Archivo autónomo HTML5/CSS3/JavaScript sin librerías externas pesadas.
   - 13 pantallas interactivas conectadas mediante router ligero local.
   - Simulación del pipeline con barra de progreso reactiva, consola de logs y las 4 compuertas de calidad.
   - Mapeador de columnas con auto-detección heurística y validación estricta de los 6 atributos obligatorios.
   - Bandeja de auditoría con buscador en tiempo real, filtros combinados y chips dinámicos.

---

## 🚀 Cómo Ejecutar y Probar el Prototipo

1. Abra el archivo [`prototipo/index.html`](prototipo/index.html) directamente con doble clic en Google Chrome, Microsoft Edge, Mozilla Firefox o Safari.
2. No requiere servidor web, conexión a Internet ni instalación de Node.js o Python.
3. Para probar el **Recorrido Crítico 1 (Ingesta y Validación):**
   - En el Dashboard, haga clic en `Cargar Nuevo Lote`.
   - En la dropzone, haga clic para simular la carga del archivo CSV.
   - Avance a la previsualización y luego a la pantalla de mapeo de columnas (compruebe cómo el botón se bloquea si deselecciona una columna).
   - Configure los parámetros y confirme en el modal reversible.
   - Observe la ejecución animada del pipeline de 4 etapas y navegue al reporte final de resultados.
4. Para probar el **Recorrido Crítico 2 (Auditoría y Remediación):**
   - En el menú lateral o desde el resumen de lote, ingrese a `Bandeja de Auditoría`.
   - Utilice el buscador escribiendo *"Chapinero"* o filtre por la compuerta *G3*.
   - Haga clic en `Diagnosticar →` en el registro `REG-8942-04`.
   - Analice la regla de negocio violada y pulse `Gestionar Acción de Recuperación →`.
   - Pruebe la acción `Reintentar Lote Corregido` para constatar cómo el sistema preserva los parámetros y columnas previas.

---

## 🎨 Sistema de Diseño y Accesibilidad
- **Paleta Cromática:** Primario Esmeralda Bogotá (`#10523A`), Acento Oro (`#D6A64A`), Superficies limpias (`#FFFFFF`, `#F4F7F5`).
- **Accesibilidad:** Ratio de contraste de texto superior a 5.5:1 (Supera el estándar WCAG 2.1 AA), foco visible dorado de 3px, soporte de navegación por teclado y redundancia visual con etiquetas e iconos en todos los estados.
