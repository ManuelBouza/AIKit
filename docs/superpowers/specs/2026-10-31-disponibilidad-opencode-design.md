# Diseño: disponibilidad real de cuentas OpenCode

Estado: borrador para aprobación del usuario. No implementa código.

## Decisiones cerradas

- Solo cuentas OpenCode, no Codex.
- Si no hay API de consulta, se permite un único intento de tarea real ya autorizada, nunca una inferencia de prueba.
- Fuente inaccesible no acredita cuota cero ni reset.
- Se conserva la última observación válida separada del último intento fallido.
- Se mantiene capacidad primero: Free adecuado -> Go -> otros -> Codex nativo sin opción adecuada.
- No se pregunta al usuario por cada fallo.
- `reset_at` pasado exige reconsulta; no implica disponibilidad.
- Scope compartido desconocido no autoriza ampliar el bloqueo.
- Cambio de cuenta o conexión invalida la certeza previa sin persistir secretos.
- Provider directo `openai` sigue bloqueado y `quota_resume` no cambia.

## Fuente oficial verificada

OpenCode 2.2.0 expone `GET /api/experimental/usage/limits`, con `location` opcional. La respuesta observada el 2026-10-31T14:53:45.967746Z incluye Go con `rolling`, `weekly` y `monthly`, cada uno con `percent`, `limited` y `resetsAt`. El schema incluye `workspace`, `go` y `budgets`. Los campos `workspace.id`, `name` y `usageURL` no se persisten. Los datos guardados son solo Go en lista blanca.

El endpoint es experimental y versionado; si falla o cambia el contrato, el estado debe quedar `unknown`, no disponible.

## Propuesta

A. Usar la API oficial de Go más un registro mínimo para otros proveedores.

Ventajas: fuente oficial, datos estructurados, sin dependencia inicial de plugin.

Límites: otros proveedores quedan `unknown` o error hasta que exista fuente verificada. El plugin `opencode-quota` se evalúa después por trust, privacidad y compatibilidad, sin instalarlo ahora.

## Estado compartido

Ubicación: `HostContext.aikit_state`, compartido entre proyectos y fuera de Git. Se reutilizan locks y reemplazo atómico de `session_store`. No se crea infraestructura paralela.

TTL propuesto (no aprobado por el usuario): 15 minutos para observación válida; 5 minutos de cooldown para error sin reset. Al llegar `reset_at`, reconsultar y no asumir disponibilidad.
## Esquema mínimo

```json
{
  "provider": "string",
  "account_alias": "string sin PII",
  "model": "string",
  "limit_scope": "model|account|shared_group|unknown",
  "status": "available|exhausted|unknown|error",
  "observed_at": "ISO-8601 UTC",
  "last_valid_observation": {
    "status": "string",
    "observed_at": "ISO-8601 UTC",
    "source": "string",
    "limit_scope": "string",
    "reset_at": "ISO-8601 UTC|null",
    "precision": "confirmed|estimated|unavailable"
  },
  "last_query_attempt": {
    "at": "ISO-8601 UTC",
    "result": "string",
    "error_code": "string|null"
  },
  "reset_at": "ISO-8601 UTC|null",
  "precision": "confirmed|estimated|unavailable",
  "next_check_at": "ISO-8601 UTC",
  "shared_scope_known": false
}
```

`last_valid_observation` completo es obligatorio; no basta con `last_valid_at`.

## Alias y privacidad

El alias debe derivarse de un identificador público de la fuente o de un alias local. No se persisten credenciales, hashes de credenciales, `workspace.id`, `name`, `usageURL`, tokens, configuración completa ni PII. Si no hay identidad acreditable, no se reutiliza certeza entre cuentas.

## Reglas de interpretación

- Catálogo confirma presencia, no cuota.
- Una inferencia exitosa es observación reciente, no garantía futura.
- El código solo bloquea el modelo o grupo para el que la fuente acredita el ámbito.
- Un error de un modelo Go no implica agotamiento de todo Go.
- Si no hay cobertura de binding para el grupo, se registra una observación agregada separada y los modelos no cubiertos quedan `unknown`.
- Errores de cuota, rate limit, servicio, autenticación y `max_output` no asequible se separan; ninguno implica cuota cero universal.

## Enforcement mínimo

Regla breve en AGENTS/routing, procedimiento en la skill y comprobación mínima en el camino CLI/MCP existente antes de inferir, reutilizando preflight y supervisor actuales. No se duplica infraestructura ni se interceptan subagentes nativos o Superpowers.

## APIs propuestas

- `read_availability(state, key)`
- `refresh_availability(binding, key)`
- `decide_candidate(state, policy, candidates)`
- `record_inference_outcome(state, key, result)`

## CLI/MCP

La consulta de disponibilidad no ejecuta inferencia. La salida saneada incluye fuente, fecha de observación, frescura, próxima comprobación, `reset_at` en UTC y hora local, y estado. `quota_resume` permanece deshabilitado en esta nota; la frase anterior solo conserva el contrato existente para una futura habilitación separada.
## Criterios de aceptación

- Tests con transporte falso para timestamps, scopes, fallos de cache, concurrencia, identidad, CLI/MCP, intentos pendientes y exportación limpia.
- No hay secretos, PII ni estado mutable en el paquete exportado.
- Los estados desconocidos usan un único intento real autorizado, registrado una vez con IDs existentes.
- No se implementa hasta aprobación del usuario.
