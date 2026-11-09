---
title: 'Director de Ideas de AIKit'
type: 'feature'
created: '2026-11-09'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent">

## Intent

**Problem:** Las ideas necesitan resolver ambigüedades relevantes y alcanzar una comprensión compartida antes de materializarse.

**Approach:** Crear una skill independiente de BMAD para madurar ideas, incluirla en el complemento AIKit y añadir una instrucción breve en el AGENTS.md de este proyecto. Respetar las autorizaciones existentes y no imponer el proceso en tareas claras.

</frozen-after-approval>

## Implementation Notes

- La nota 009 contiene el diseño autorizado y casos de aceptación; conservar estado y evidencia.
- `scripts/build_aikit.py` usa inclusión explícita. La skill debe formar parte del paquete sin OpenCode.
- El cambio de instrucciones se limita al proyecto; no actualizar el perfil global.
- Validar estructura de la skill y exportación; no confundir esas pruebas con selección automática en sesiones reales.
- Implementados skill, exportador, instrucción local, documentación y trazabilidad.
- `quick_validate.py`: válido. `uv run pytest tests/test_build_aikit.py -q`: 13 pruebas aprobadas en Windows con TEMP/TMP/UV_CACHE_DIR locales.
- Un evaluador analizó tres escenarios sobre el texto, sin ejecutar selección real; quedan pendientes las pruebas reales de descubrimiento y convivencia con y sin BMAD.

## Review Triage Log

- Medio: la fuente bajo `packaging` no es catálogo de skills; se añadió en `AGENTS.md` una instrucción de lectura explícita cuando no se descubre.
- Medio: la evidencia de exportación no verifica comportamiento real; se reconoce la limitación y queda pendiente su validación en sesión real.
- Medio: la comprensión compartida precisaba contraste cuando no constaba; se incorporó a la skill.
- Bajo: afirmaciones históricas podían confundirse con el estado actual; se marcaron como históricas.
- Bajo: faltaba enlace desde la nota a esta especificación; se añadió.
