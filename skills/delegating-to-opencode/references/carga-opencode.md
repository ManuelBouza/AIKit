# Carga de tarea para OpenCode

Contrato mínimo para delegar trabajo externalizable a OpenCode sin copiar la
conversación ni volcar logs.

## Contrato de tarea

Objetivo: una frase verificable.

Alcance: rutas permitidas o ámbito de exploración acotado; qué no tocar.

Aceptación: cambios esperados, pruebas/lint/tipos a ejecutar y criterio de éxito.

Límites: sin subdelegación, sin cambiar cuentas ni credenciales, sin datos que
no puedan externalizarse.

Presupuesto: intentos y tiempo razonables para la tarea; revisar parciales
antes de reintentar.

## Salida compacta

Archivos modificados o creados.

Pruebas: comando y resultado resumido.

Riesgos pendientes o cambios parciales.

## Catálogo

Consultarlo al seleccionar modelo y reutilizarlo en el mismo contexto mientras
no haya señal de cambio. No es caché garantizada ni cuota.

## Registro de coordinación

El registro es manual, sin backend: una entrada por intento y su resultado real.
`.aikit/delegaciones.jsonl` lo mantiene el coordinador: id de tarea, intento,
proveedor/modelo, variante o esfuerzo predeterminado, tarifa free/paid/unknown,
transporte cli/mcp/native, resultado y motivo si se vuelve a nativo. No inventes
modelos, tokens ni costes. Si el modelo nativo es desconocido, no inventes ID y
el motivo es obligatorio si hay retorno. Se cuentan tareas y ciclos, no
porcentaje de ahorro de tokens; no cuentes dos veces los reintentos como tareas
completadas. Distingue result/backend_status (ok/error) de review
(accepted/needs_corrections). Sin prompts, transcripciones, secretos, tokens ni
costes inventados.

## Revisión independiente

Contrato futuro `review.json`: `role: reviewer`, `session`, `snapshot`,
`verdict: accepted|needs_corrections`, `checks[]` (`id`, `command`, `cwd`,
`exit_code`, `summary`), `findings[]` (`severity: blocker|warning|info`,
`description`), `limitations[]`. El revisor recibe diseño, aceptación y archivos;
usa sesión nueva y ejecuta sus comprobaciones. Correcciones invalidan la
aceptación anterior. Si necesita otro diseño, devuelve la decisión a Codex sin
rediseñar. La utilidad de validación aún no existe hasta tarea 2.