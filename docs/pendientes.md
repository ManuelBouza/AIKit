# Registro de pendientes

**Corte:** 2026-11-04. Punto de reanudación documental; los estados describen evidencia disponible, no garantizan que el host instalado coincida con la fuente.

Este inventario acotado consolida el plan de reconciliación, documentación de `docs/`, README, `git log` y los informes de coordinación expresamente citados. No es una auditoría de toda la deuda histórica. Las notas viven en `notas/` del checkout principal, distinto de este worktree; se citan por número y nombre, sin copiar su contenido ni crear enlaces locales rotos.

## Prioridad y entregas

### REC-001 — Task 6: cierre global de reconciliación

- **Categoría/estado:** aceptación global de código de Unidades 1–4 completada. REV-001 corregido y aceptado; REV-002 resuelto por disposición documental aprobada; REV-003/004 implementados y aceptados en revisión global. La Task 6 original sigue incompleta por su prueba real mínima; la instalación permanece separada.
- **Evidencia actual:** [plan de evidencia](superpowers/plans/2026-11-03-evidencia-reconciliacion.md), [dictamen y seguimiento](revision-reconciliacion-2026-11-02.md), `.aikit/rev003004-unit4/report.json`, `report-bound.json` y `coordinator-acceptance.json`. Autor: **893 pruebas globales**, Ruff, formato y mypy; revisor independiente: **124 focales** y paridad de **42 archivos** del nuevo candidato. El comentario informativo de Unidad 3 está corregido.
- **Historia preservada:** Task 5 antigua `ed00065`, 849 aprobadas después de una ejecución con 848 y un PermissionError de causa no diagnosticada. Revisión inicial sobre `9a00248` encontró REV-001–004. Sus informes y fallos permanecen como evidencia histórica, no como estado del candidato nuevo.
- **Siguiente paso acotado:** ejecutar prueba real mínima de reconciliación contra el servicio existente de OpenCode; requiere autorización específica. No repetir suite global ni revisión técnica ya aceptadas por rutina.
- **Dependencia/autorización:** no instalar ni publicar como parte del cierre de código. La aceptación no acredita paridad con el host instalado ni resuelve DEF-001.

### DEF-001 — Fallo de arranque del supervisor

- **Categoría/estado:** defecto observado; causa no diagnosticada ni corregida. Un intento posterior de recuperación por CLI funcionó, pero no resuelve el fallo original.
- **Evidencia:** `.aikit/seleccion-modelo-requisitos/coordinator-recovery.json`: tarea `bda6addb-0184-4a7f-95e5-a1638ba0bcd5`, intento `d2315fe7-dc52-4df2-b3e3-ff4a448c7948`, `worker_failed`, sesión nula, sin archivo stdout ni proceso hallado; el fallo ocurrió antes de crear salida/sesión.
- **Siguiente paso acotado:** al retomar REC-001, valorar si este fallo impide ejecutar la revisión; diagnosticarlo solo si constituye un bloqueo, sin ampliar automáticamente el alcance.
- **Dependencia/autorización:** diagnóstico futuro autorizado por separado; no hay permiso de corregir o rediseñar ahora.

### ENT-002 — Candidato exportado y entorno instalado

- **Categoría/estado:** entrega incompleta; el candidato actualizado de fuente/exportación existe, pero no está instalado. No se ha comprobado aquí la identidad del host instalado.
- **Evidencia:** `.aikit/rev003004-unit4/dist/aikit`, candidato 0.2.0 de 42 archivos, paridad revisada por hashes y aceptación global de código. No se instaló ni activó. El candidato histórico de Task 5 es anterior a estos cambios; la aceptación de la exportación nueva no verifica el host instalado.
- **Siguiente paso acotado:** después de REC-001, contrastar fuente, candidato y host antes de decidir despliegue.
- **Dependencia/autorización:** instalación/actualización exige autorización propia; no se infiere del export ni de este registro.

### ENT-003 — Nota 001: disponibilidad de cuentas

- **Categoría/estado:** entrega incompleta; implementación documentada parcialmente y nota aún abierta. Estado de cada subentrega sujeto a contraste con su evidencia específica.
- **Evidencia:** [seguimiento de disponibilidad](superpowers/plans/2026-10-31-disponibilidad-opencode.md) registra unidades aceptadas de tabla, refresh, CLI/MCP/supervisor, instrucciones, registro, fuentes públicas y altas/bajas. También mantiene pendiente acceso desatendido y activación de actualización diaria de Codex. La automatización diaria acordada no tiene evidencia de creación/activación en las fuentes consultadas; esto no demuestra inexistencia universal. La tarea 4 de binding sigue pausada. Véase también [plan de fuentes públicas](superpowers/plans/2026-11-01-gratuidad-publica-opencode.md).
- **Siguiente paso acotado:** reconciliar qué subentregas de altas/bajas y documentación pública están efectivamente cerradas con sus reportes; mantener separado el pendiente de acceso desatendido/automatización diaria. Relacionar la nota 008 con la entrega existente, sin duplicar esperas ni reconciliación.
- **Dependencia/autorización:** respetar la prioridad existente y verificar acceso antes de activar automatización. No consultar servicios, instalar ni activar nada como parte del inventario.

## Ideas aparcadas

| ID estable | Categoría/estado verificable | Evidencia y siguiente paso acotado | Dependencia |
|---|---|---|---|
| IDEA-002 | Idea; nota 002 pendiente de debate. | `notas/002-opencode-como-subagente-acotado.md`; elegirla para debate explícito. | No autoriza implementación. |
| IDEA-003 | Idea; nota 003 pendiente de debate. | `notas/003-heuristica-coste-delegacion.md`; elegirla para debate explícito. | No autoriza implementación. |
| IDEA-004 | Idea; nota 004 pendiente de debate. | `notas/004-guardarrailes-privacidad-opencode.md`; elegirla para debate explícito. | No autoriza implementación. |
| IDEA-005 | Idea; nota 005 pendiente de debate. | `notas/005-prompts-concisos-opencode.md`; elegirla para debate explícito. | No autoriza implementación. |
| IDEA-006 | Idea; nota 006 pendiente de debate. | `notas/006-herramientas-skills-opencode.md`; elegirla para debate explícito. | No autoriza implementación. |
| IDEA-007 | Idea; nota 007 pendiente de debate. | `notas/007-separar-delegacion-de-aikit.md`; elegirla para debate explícito. | No autoriza implementación. |
| ENT-004 | Entrega incompleta de nota 008: espera pasiva implementada en fuentes según la nota; empaquetado/instalación y verificación en entorno nuevo pendientes. | `notas/008-espera-pasiva-opencode.md`; relacionar con ENT-002 y ENT-003 sin duplicar trabajo. | Instalación requiere autorización propia. |
| IDEA-009 | Idea en debate; uso local del método no equivale a activación global. | `notas/009-metodo-director-de-ideas.md`; retomar solo si se elige debatir su aplicación global. | No es requisito automático para cada tarea. |
| IDEA-010 | Idea/debate incompleto, aparcado tras requisitos parciales; investigación de esfuerzo solicitada por el usuario, sin política implementada. | [Requisitos de selección](superpowers/specs/2026-11-02-seleccion-modelo-esfuerzo-requisitos.md) e [investigación sobre esfuerzo](investigaciones/2026-11-04-esfuerzo-razonamiento.md); el algoritmo, suficiencia, representación, desempate, excepción OpenAI y pruebas siguen sin completar. Beam continuó en su misma sesión con `medium` para documentar y `low` para corregir texto; no es un experimento controlado de programación ni demuestra ahorro. | No priorizar su implementación antes de REC-001 ni interpretar la excepción redactada como permiso global/soporte. |

## Protocolo mínimo de reanudación

Propuesta documental, no automatización ni regla global: actualizar este registro al aparcar, retomar o cerrar un pendiente; cerrarlo solo con evidencia identificable y conservar el enlace a la entrega. Al reanudar, volver a contrastar el estado de fuente, candidato y host; no convertir historia o informes parciales en verificación actual. No se cubre aquí toda deuda histórica.
