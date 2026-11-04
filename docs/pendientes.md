# Registro de pendientes

**Corte:** 2026-11-04. Punto de reanudación documental; los estados describen evidencia disponible, no garantizan que el host instalado coincida con la fuente.

Este inventario acotado consolida el plan de reconciliación, documentación de `docs/`, README, `git log` y los informes de coordinación expresamente citados. No es una auditoría de toda la deuda histórica. Las notas viven en `notas/` del checkout principal, distinto de este worktree; se citan por número y nombre, sin copiar su contenido ni crear enlaces locales rotos.

## Prioridad y entregas

### REC-001 — Task 6: cierre de código y prueba real mínima

- **Categoría/estado:** cerrada con alcance explícito. Código de Unidades 1–4 aceptado independientemente; REV-001–004 resueltos según su disposición documentada. Prueba real mínima de CLI/API/helper autorizada y aceptada el 2026-11-04. No acredita supervisor completo, persistencia o recuperación en vivo; esos recorridos tienen pruebas deterministas y revisión técnica, no una demostración E2E real.
- **Evidencia:** [plan original](superpowers/plans/2026-11-01-reconciliacion-terminal-opencode.md), [seguimiento](revision-reconciliacion-2026-11-02.md), `.aikit/rev003004-unit4/coordinator-acceptance.json` y `.aikit/reconciliation-real-minimum/coordinator-acceptance.json`. Una inferencia Beam/Kilo low, gratuita; un GET durable; helper accepted/completed/stop. Primer comprobador pending conservado, reutilizados sus IDs sin repetir inferencia. Suite 893 del autor y 124 focales independientes siguen siendo evidencia separada.
- **Disposición:** coordinador acepta este mínimo acotado, sin afirmar pérdida de terminal ni éxito E2E del supervisor. Riesgo restante: fallo específico de integración en vivo no cubierto por este mínimo. DEF-001 y el host instalado no quedan verificados por este cierre.
- **Siguiente paso:** ENT-002, preparar paquete limpio y contrastar host antes de decidir instalación; no añade una nueva función ni otra batería de inferencias.

### DEF-001 — Fallo de arranque del supervisor

- **Categoría/estado:** defecto observado; causa no diagnosticada ni corregida. Un intento posterior de recuperación por CLI funcionó, pero no resuelve el fallo original.
- **Evidencia:** `.aikit/seleccion-modelo-requisitos/coordinator-recovery.json`: tarea `bda6addb-0184-4a7f-95e5-a1638ba0bcd5`, intento `d2315fe7-dc52-4df2-b3e3-ff4a448c7948`, `worker_failed`, sesión nula, sin archivo stdout ni proceso hallado; el fallo ocurrió antes de crear salida/sesión.
- **Siguiente paso acotado:** al retomar REC-001, valorar si este fallo impide ejecutar la revisión; diagnosticarlo solo si constituye un bloqueo, sin ampliar automáticamente el alcance.
- **Dependencia/autorización:** diagnóstico futuro autorizado por separado; no hay permiso de corregir o rediseñar ahora.

### ENT-002 — Actualización preparada, instalación pendiente

- **Categoría/estado:** versión 0.2.1 preparada; portable y candidato local0.2.1+host.1 validados, sin instalar ni recargar. Proyecto, lock y manifiesto fuente coherentes; sin cambios de dependencias o comportamiento.
- **Evidencia:** [plan de actualización y restauración](actualizacion-0.2.1.md), `.aikit/ent002-update-021/package-acceptance.json`, manifiestos de ambos paquetes y metadata de checks recuperada del backend. Cada distribución:42 archivos + catálogo, cero extras.12 pruebas de exportación aprobadas; lock offline correcto. Solo plugin.json y mcp.json difieren en el candidato local; se preservaron exactamente AIKIT_STATE y AIKIT_OPENCODE_REGISTRATION.
- **Host observado:** aikit@aikit-local registrado y habilitado0.2.0+host.1; caché/fuente anteriores conservadas. No confundir registro habilitado con runtime cargado en este chat.
- **Siguiente paso acotado:** instalar candidato0.2.1+host.1 según el plan, con respaldo selectivo previo, fuente nueva, runtime en installedPath y restauración al fallar; después el usuario recarga Codex y se comprueba carga real.
- **Dependencia/autorización:** requiere autorización propia de instalación; esta preparación no la ejecutó. Sin push ni cambios de otros plugins/cuentas. Prueba real previa limitada al helper; DEF-001 permanece separado.

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
