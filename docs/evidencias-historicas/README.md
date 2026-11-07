# Extractos de evidencias históricas

Fecha de archivo: 2026-11-07. Estos cinco archivos conservan campos seleccionados
de evidencias localizadas en el worktree histórico `orquestacion-opencode`.
La selección prioriza la aceptación de reconciliación, el defecto DEF-001 y la
instalación y recarga históricas. El [inventario](../inventario-evidencias-locales.md)
registra las demás referencias y su localización observada.

Cada extracto identifica la ruta de origen y su SHA-256. Se omitieron campos no
seleccionados, en particular identificadores de sesión o tarea y rutas locales.
Los extractos no son copias íntegras y no sustituyen los originales para validar
sus contratos, sesiones, hashes o autoría. Las huellas permiten contrastarlos con
un original disponible, pero no autentican su procedencia.

- `reconciliacion-minima.json`: aceptación limitada de la prueba real mínima.
- `unidades-1-4-aceptacion.json`: aceptación de código y límites de revisión.
- `def001-recuperacion.json`: fallo inicial no diagnosticado y recuperación posterior.
- `instalacion-021.json`: alcance y límites de la instalación histórica.
- `recarga-021.json`: comprobación histórica del cliente tras la recarga.

Estos registros describen hechos informados en su momento: no prueban el estado
actual de una instalación ni autorizan ejecutar OpenCode. Los demás originales,
incluidos registros de disponibilidad y sesiones, no se han copiado; permanecen
fuera de Git en el worktree histórico cuando allí estén disponibles.
