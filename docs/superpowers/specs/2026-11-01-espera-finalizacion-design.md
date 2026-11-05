# Diseño: Espera por Finalización y Tiempos de Intento en AIKit

## 1. Intención y Porqué

Integrar dos capacidades probadas empíricamente en el núcleo de delegación:

1. **Espera acotada por finalización mediante sondeo de `result.json`**: El supervisor (`session_worker.supervise`) ya escribe `result.json` con estado terminal (`completed`/`failed`/`interrupted`/`pending`) al salir. El coordinador (`bound_execution.execute_bound`) sondea este archivo cada 20 ms (`POLL_SECONDS=0.02`) y **retorna inmediatamente** cuando existe con estado no-`pending`. El timeout de 300 s es un *deadline*, no un *sleep* fijo. La evidencia (`tool-wait-probes.json`) muestra retorno a los ~20 s de un proceso de 35 s, y notificación asíncrona (`client_exited`) interrumpiendo `clock.sleep(300s)` a los 282 s.

2. **Observación de tiempos a nivel de intento real**: Particionar por `attempt_id`/`task_id` (no por sesión reutilizada), separar `completed` de `error`/`interrupted`/`pending` (censurados a la derecha), registrar `provider`/`model`/`variant`/`role`/`measurement_kind` y fuente. La infraestructura `PerformanceSample`/`PerformanceWindow` ya existe en `availability_performance.py` con deduplicación real por `(key, task_id, attempt_id, event_id, source, measurement_kind)`. El supervisor ya registra `task_seconds` (reloj del supervisor) como muestra `"supervisor_clock"`/`"task"` al final de `supervise()`.

**No se añade**: nueva infraestructura SSE, hooks de chat idle, monitor LLM/subagente, reprogramación global, instalación de skills/plugins, cambios en cuenta/estado global/checkout principal.

## 2. Metas, No-Metas, Anti-Metas

| Meta | No-Meta | Anti-Meta |
|------|---------|-----------|
| Coordinador usa sondeo acotado de `result.json` (20 ms) y valida `result.json` (delivery, attempt_id, session_id, server_identity) antes de declarar éxito | Reescribir manejo de procesos en el núcleo solo por el sleep diferido del chat | Asumir que salida de proceso = finalización backend; `pending`/`uncertain` nunca autoriza reintento |
| Reusar `PerformanceSample`/`PerformanceWindow` existente para tiempos por intento; exponer resumen determinista cachado (CLI `doctor` o subcomando puro) | Nuevo tool MCP solo por simetría | Inventar TTFT/TPS desde wall-time; mezclar intentos de distinta sesión/modelo/esfuerzo/rol |
| Cobertura TDD: ready antes de deadline, async-capable no convierte deadline en sleep fijo, fallback sin notificación, worker detached sobrevive timeout cliente, pending/uncertain no es éxito, proveniencia rechaza sesión/intento ajeno, dos intentos misma sesión = timings separados, completed vs error/censored separados, dedupe recuperación y reinicio observer, estado legacy/desconocido, agrupación comparable e "insuficiente" | Tests que fingan notificación host-only; espejar prosa | `or True`, skip/falso RED, hardcodear mediana inválida 33 min |

## 3. Restricciones

- **Compatibilidad hacia atrás**: `MCP 45s pending` semántica y firmas públicas `run` intactas.
- **Sin dependencias nuevas**: solo stdlib + código existente.
- **Windows**: pruebas con elevación acotada para `socketpair` donde proceda; procesos propios ocultos, sin flashes de consola.
- **Privacidad**: nada de prompts/razonamiento/args tools/paths/secrets/alias de cuenta inventados.
- **Bounded history**: `PerformanceWindow.max_samples=1000` ya aplicado.
- **Coordinador no redelega**: workers no redelegan; revisor en sesión nueva sin modificar entrega.

## 4. Enfoques Considerados

### Enfoque A: Sondeo acotado de `result.json` (_wait_result) + validación semántica (ELEGIDO)
- **Qué**: `bound_execution.execute_bound` lanza el supervisor detached y sondea `result.json` cada 20 ms vía `_wait_result`, retornando inmediatamente cuando el archivo existe con delivery terminal. Valida `delivery`/`attempt_id`/`session_id`/`server_identity` antes de declarar éxito.
- **Pros**: Cero infra nueva; retorna en escritura de `result.json` (probado ~0.5 s vs 300 s); preserva multitarea; compatible con `result.json` y reconciliación de procedencia; `_recover` ya existe para cuando falte `result.json` o falle validación.
- **Contras**: Sondeo en lugar de evento; sin visibilidad intermedia (permisos, streaming); requiere que supervisor escriba `result.json` atómicamente.
- **Despierta al coordinador**: `_wait_result` retorna en siguiente sondeo tras escritura de `result.json` → continuación inmediata en hilo del coordinador.

### Enfoque B: SSE local `/api/event` con filtro `types[]`
- **Qué**: Suscribirse a `session.execution.succeeded/failed/interrupted`, `session.idle` filtrado por `sessionID`.
- **Pros**: Estado terminal tiempo real desde servidor; `session.idle` punto seguro para siguiente turno; funciona para sesiones no propias.
- **Contras**: Stream volátil (overflow/desconexión pierde eventos); privacidad (span todas sesiones/ubicaciones); sin entrega garantizada (requiere reconciliación fallback); complejidad conexión/reconexión/dedupe; **NO probado para despertar chat Codex GUI** (solo durante turno de espera activo).
- **Despierta**: callback SSE en event loop del coordinador — SOLO si conexión viva y coordinador esperando activamente.

### Enfoque C: Polling adaptativo (fallback only)
- **Qué**: Intervalo 20 ms → backoff exponencial a máx 1 s.
- **Pros**: Simple, sin deps, reduce CPU en esperas largas, compatible con `result.json`.
- **Contras**: Aún polling; detección tardía = intervalo en momento de finalización; sin mejora para tareas cortas.
- **Despierta**: iteración loop polling — mismo que actual pero variable.

**Decisión**: Enfoque A primario para transporte CLI actual (sondeo acotado de `result.json` existente). Enfoque C solo fallback si `_wait_result` no disponible. Enfoque B útil para eventos pero NO reemplaza validación `result.json` ni es canal push universal para chat.

## 5. Partes Decididas

### 5.1 `session_worker.launch_worker` → devuelve `tuple[TaskRecord, subprocess.Popen]`
```python
def launch_worker(...) -> tuple[TaskRecord, subprocess.Popen[bytes]]:
    # ... existing code ...
    process = subprocess.Popen(...)
    threading.Thread(target=process.wait, daemon=True).start()
    return record, process  # NEW: return handle
```
- Mantener compatibilidad: si caller no espera 2-tupla, ignora segundo elemento.

### 5.2 `bound_execution.execute_bound` → usa `_wait_result` (sondeo acotado)
```python
# ANTES (hipotético communicate):
# supervisor_process = _launch_supervisor(...)
# supervisor_process.communicate(timeout=seconds)

# DESPUÉS (implementado):
_launch_supervisor(prepared, record, context=context)  # lanza supervisor detached
return _wait_result(context, record, seconds, agent=prepared.agent)
```
- `_wait_result` sondea `result.json` cada 20 ms (`POLL_SECONDS=0.02`) hasta deadline.
- Retorna inmediatamente cuando `result.json` existe con delivery ∈ {completed, failed, interrupted}.
- Valida `delivery`/`attempt_id`/`session_id`/`server_identity` vía `_map_result`.
- Si `result.json` no disponible o validación falla → `_recover` para reconciliación.

### 5.3 Timing observation — ya implementado en `session_worker.supervise` (líneas 781-793)
```python
if task_seconds is not None:
    sample = PerformanceSample(
        key,
        record.task_id,
        record.attempt_id,
        "supervisor_clock",
        "task",
        now,
        event_id="supervisor-task-total",
        role=record.role,
        task_seconds=task_seconds,
    )
    window = add_sample(window, sample)
```
- **Measurement kind**: `"task"` (reloj supervisor muro usuario→asistente terminal).
- **Source**: `"supervisor_clock"`.
- **Dedupe key**: `(key, task_id, attempt_id, "supervisor-task-total", "supervisor_clock", "task")` — único por intento.
- **Separación outcomes**: `_record_availability_outcome` solo registra si `delivery in {"completed", "failed"}` (línea 579). `pending`/`interrupted` censurados a la derecha — no absorben en exitosos.
- **Observer restart**: `observed_at = min(existing.observed_at, incoming.observed_at)` en `_merge_samples` — reinicio observer no resetea inicio real del intento.
- **Unknown timestamps**: quedan `None` (no se inventan).

### 5.4 API determinista de resumen de tiempos
Extender `delegate.doctor` o añadir subcomando `delegate timing` (CLI pura) que:
1. Lee `AvailabilitySnapshot` (ya tiene `performance_samples`).
2. Filtra por `measurement_kind="task"`, `source="supervisor_clock"`.
3. Agrupa por `PerformanceModelKey` + `role` (comparable: mismo proveedor/modelo/variante/cuenta, fuente/tipo, rol/contexto).
4. Para cada grupo: `aggregate_samples` → `PerformanceResult` con `median`, `sample_count`, `confidence` (low/medium/high/unknown), `limitations`.
5. Si `sample_count < 3` → `"insufficient for predictors"`.
6. Formato salida JSON determinista, cachado (snapshot ya atómico).

### 5.5 Regla de routing breve (documento de referencia skill)
> **Cuando el anfitrión expone esperas de finalización de proceso/tarea propias, úsalas con deadline máximo retornando anticipadamente al estar listo. Si una capacidad de notificación asíncrona está efectivamente publicada, notifica solo resultado/error/permiso/estado incierto significativo. No duermas 300 s fijos tras cada lanzamiento. Sin monitor LLM/subagente y preserva multitarea/interrupción de usuario. NO asumas `functions.exec/notify` en todo cliente ni promesa push universal GUI-idle. Runtime actual probó que notify interrumpe `clock.sleep` activo; background hooks no inician turnos idle. Evento observer dice `client_exited`, luego reconciliar resultado adaptador, attempt/session/owner, y entrega terminal antes de declarar éxito. `pending`/`uncertain` NUNCA permite inferencia duplicada. SSE OpenCode existente volátil/global; no nueva suscripción SSE ni infra servidor/plugin en esta primera integración. No interceptar agentes nativos/Superpowers.**

## 6. Queda al Constructor

- Implementar cambios en `session_worker.py` (retornar handle) y `bound_execution.py` (usar `_wait_result` + validación).
- Añadir tests TDD **antes** del parche de producto (ver plan).
- Exponer CLI `timing` en `delegate.py` (subcomando nuevo o extender `doctor`).
- Ejecutar `pytest`, `ruff check`, `ruff format --check`, `mypy` tras TODOS los edits finales.
- Computar hashes exactos actuales al final.
- Dejar fuentes congeladas; revisión independiente despachada por coordinador, no por implementador.