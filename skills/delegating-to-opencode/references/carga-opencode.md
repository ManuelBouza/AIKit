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

Formato `review.json`: `role: reviewer`, `session`, `snapshot`,
`verdict: accepted|needs_corrections`, `checks[]` (`id`, `command`, `cwd`,
`exit_code`, `summary`), `findings[]` (`severity: blocker|warning|info`,
`description`), `limitations[]`. El revisor recibe diseño, aceptación y archivos;
usa sesión nueva y ejecuta sus comprobaciones. Correcciones invalidan la
aceptación anterior. Si necesita otro diseño, devuelve la decisión a Codex sin
rediseñar. `scripts/review_evidence.py` valida metadata, snapshot y checks
declarados, pero no ejecuta comandos ni demuestra autoría o calidad.

Si un subagente nativo usa la CLI, devuelve el JSON de stdout directamente al
coordinador; solo este persiste en una ruta permitida. Si falla el guardado,
recupera stdout y registra el problema: no repitas una inferencia ya terminada.
Reutiliza permisos conocidos solo en el mismo entorno/runtime/alcance. Si se sabe
que el sandbox bloquea la CLI, pide `exec_command` con `require_escalated` desde
el primer intento y justificación acotada; si cambió o se desconoce, usa antes un
preflight sin inferencia. No escales globalmente ni para eludir cuotas,
autenticación o privacidad. Si se deniega, informa código y motivo; no reintentes
la inferencia a ciegas ni pruebes permisos con modelos. Si MCP está disponible,
no elijas otra vía CLI solo por recordar un bloqueo antiguo.
