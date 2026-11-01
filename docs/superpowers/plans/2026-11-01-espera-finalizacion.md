# Plan: Integración Espera por Finalización y Tiempos de Intento

## 1. Secuencia de Implementación (TDD First)

### Fase 0: Preparación y Tests de Regresión (ANTES de cambios de producto)

| # | Test | Archivo | Qué Verifica |
|---|------|---------|--------------|
| T0.1 | `test_wait_result_returns_before_deadline_on_ready` | `test_bound_execution.py` | `_wait_result` retorna cuando `result.json` existe con delivery terminal, antes del deadline |
| T0.2 | `test_async_notify_does_not_turn_deadline_into_fixed_sleep` | `test_bound_execution.py` | Con notificación asíncrona simulada, espera no se convierte en sleep fijo de 300s |
| T0.3 | `test_host_without_notification_has_fallback` | `test_bound_execution.py` | Sin capacidad notificación, polling 20ms fallback funciona |
| T0.4 | `test_detached_worker_continues_after_client_timeout` | `test_bound_worker.py` | Worker detached sobrevive timeout del coordinador; resultado recuperable |
| T0.5 | `test_pending_uncertain_never_success_or_retry` | `test_bound_execution.py` | `delivery=pending/uncertain` → status=pending, uncertain=True, NUNCA ok/retry |
| T0.6 | `test_unrelated_session_attempt_provenance_rejected` | `test_bound_execution.py` | Recuperación rechaza `result.json` con task_id/attempt_id/session distintos |
| T0.7 | `test_two_attempts_same_session_separate_timings` | `test_availability_performance.py` | Dos intentos compartiendo sesión → dos `PerformanceSample` separados por `attempt_id` |
| T0.8 | `test_completed_vs_error_censored_separation` | `test_availability_performance.py` | `aggregate_samples` separa completed de error/interrupted/pending (censored) |
| T0.9 | `test_dedupe_recovery_and_observer_restart` | `test_availability_performance.py` | Recuperación completa campos faltantes; reinicio observer no resetea `observed_at` original |
| T0.10 | `test_legacy_unknown_malformed_timing` | `test_availability_performance.py` | Muestras legacy/sin timestamps/desconocidas → limitations, no crash |
| T0.11 | `test_comparable_grouping_insufficient_samples` | `test_availability_performance.py` | Agrupación por key+source+kind+role+context_bucket; N<3 → "insufficient" |
| T0.12 | `test_transport_tool_adapter_boundaries` | `test_bound_execution.py` / `test_bound_worker.py` | Fakes/procesos cortos propios; sin sondas de modelo |
| T0.13 | `test_supervisor_returns_early_while_process_still_alive` | `test_bound_execution.py` | Supervisor real (subprocess) escribe result.json y se queda vivo; coordinador retorna ok mientras proceso vive |

### Fase 1: Cambios en `session_worker.py`

| # | Cambio | Archivo | Detalle |
|---|--------|---------|---------|
| C1.1 | `launch_worker` retorna `tuple[TaskRecord, subprocess.Popen]` | `session_worker.py` | Línea ~288: `return record, process` en lugar de solo `record` |
| C1.2 | Actualizar type hint y docstring | `session_worker.py` | Reflejar nuevo retorno |

### Fase 2: Cambios en `bound_execution.py`

| # | Cambio | Archivo | Detalle |
|---|--------|---------|---------|
| C2.1 | `_launch_supervisor` captura y retorna `Popen` handle | `bound_execution.py` | Cambiar firma a `-> subprocess.Popen[bytes]`; desempaquetar tupla de `launch_worker` |
| C2.2 | `execute_bound` usa `_wait_result` (sondeo acotado) | `bound_execution.py` | Llamar `_wait_result` directamente; NO usar `communicate()` en handle supervisor |
| C2.3 | Mantener `_wait_result` como mecanismo principal | `bound_execution.py` | Sondeo 20 ms existente; retorno temprano en delivery terminal |
| C2.4 | Validación semántica en `_map_result`: `delivery`, `attempt_id`, `session_id`, `server_identity` | `bound_execution.py` | Usar `_map_result` con `terminal=True`; si falla → `_recover` |

### Fase 3: API Determinista de Timing (CLI)

| # | Cambio | Archivo | Detalle |
|---|--------|---------|---------|
| C3.1 | Subcomando `timing` en `delegate.py` | `delegate.py` | Nuevo parser subcommand; delega a `availability_performance.summarize_timing` |
| C3.2 | Función `summarize_timing(snapshot, project_key)` | `availability_performance.py` | Filtra `measurement_kind="task"`, `source="supervisor_clock"`; agrupa comparable; retorna lista `PerformanceResult` serializable |
| C3.3 | Integración en `doctor` opcional (flag `--timing`) | `delegate.py` | Si `--timing` incluye resumen en salida `doctor` |

### Fase 4: Documentación y Regla de Routing

| # | Cambio | Archivo | Detalle |
|---|--------|---------|---------|
| C4.1 | Añadir regla de routing a `docs/principios-aikit.md` o referencia skill | `skills/delegating-to-opencode/references/carga-opencode.md` | Regla breve (ver diseño §5.5) |
| C4.2 | Actualizar `README.md` si expone CLI nueva | `README.md` | Documentar `delegate timing` |

### Fase 5: Verificación Final

| # | Comando | Esperado |
|---|---------|----------|
| V1 | `uv run pytest` | All pass (incl. nuevos tests T0.1-T0.13) |
| V2 | `uv run ruff check .` | Clean |
| V3 | `uv run ruff format --check .` | Clean |
| V4 | `uv run mypy` | Clean |
| V5 | `python skills/delegating-to-opencode/scripts/delegate.py doctor --cwd .` | OK |
| V6 | `python skills/delegating-to-opencode/scripts/delegate.py timing --cwd .` | JSON determinista con median/sample_count/confidence |

## 2. Archivos a Modificar (Resumen)

| Archivo | Tipo Cambio |
|---------|-------------|
| `skills/delegating-to-opencode/scripts/session_worker.py` | Firma `launch_worker` + retorno handle |
| `skills/delegating-to-opencode/scripts/bound_execution.py` | `_launch_supervisor` retorna handle; `execute_bound` usa `_wait_result` + validación |
| `skills/delegating-to-opencode/scripts/availability_performance.py` | Nueva función `summarize_timing` (pura, sin I/O) |
| `skills/delegating-to-opencode/scripts/delegate.py` | Subcomando `timing` + integración opcional `doctor --timing` |
| `docs/superpowers/specs/2026-11-01-espera-finalizacion-design.md` | Diseño (actualizado a enfoque sondeo acotado) |
| `docs/superpowers/plans/2026-11-01-espera-finalizacion.md` | Este plan |
| `tests/test_bound_execution.py` | Tests T0.1, T0.2, T0.3, T0.5, T0.6, T0.12, T0.13 |
| `tests/test_bound_worker.py` | Test T0.4 |
| `tests/test_availability_performance.py` | Tests T0.7, T0.8, T0.9, T0.10, T0.11 |

## 3. Criterios de Aceptación por Test (RED → GREEN)

| Test | RED Inicial | GREEN Final |
|------|-------------|-------------|
| T0.1 | `_wait_result` sleep 300s fijo (mock) | Retorna < deadline cuando result.json ready |
| T0.2 | Deadline se agota aunque notificación llegue | Notificación (simulada via result.json early) despierta espera |
| T0.3 | Sin notificación → error | Polling 20ms funciona como fallback |
| T0.4 | Coordinator timeout mata worker | Worker detached termina; `recover_local_result` lee ok |
| T0.5 | `pending` → status ok | `pending` → status pending, uncertain=True |
| T0.6 | Recuperación adopta result ajeno | Recuperación rechaza con provenance_unavailable |
| T0.7 | Un sample por sesión | Dos samples con attempt_id distintos |
| T0.8 | Errores mezclados en mediana | Errores censored; solo completed en agregado exitoso |
| T0.9 | Observer restart resetea timestamps | `observed_at` = min(original, recovery) |
| T0.10 | Malformed → crash | Malformed → limitations, sample válida o None |
| T0.11 | Grupo heterogéneo → mediana única | Grupos comparables separados; N<3 → "insufficient" |
| T0.12 | Test requiere modelo real | Fakes/procesos cortos owned; sin inferencia |
| T0.13 | Coordinador espera a que hijo termine | Coordinador retorna ok en <1s mientras hijo vive (3s sleep) |

## 4. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| `launch_worker` change rompe callers existentes | Media | Alto | Mantener compatibilidad: tupla opcional; tests cubren ambos |
| `_wait_result` polling 20ms CPU en esperas largas | Baja | Bajo | Backoff adaptativo solo fallback; no crítico |
| Dedupe `PerformanceSample` colisiona por `event_id` fijo | Baja | Medio | `event_id="supervisor-task-total"` único por intento; verificado |
| CLI `timing` expone datos sin snapshot válido | Baja | Bajo | Manejo graceful: "no data" / "insufficient" en JSON |
| Pipe buffer bloquea hijo (stdout/stderr PIPE) | Media | Alto | Usar `DEVNULL` para stdout/stderr en tests con subprocess real |

## 4. Entregable Final

`.aikit/completion-wait-implementation/report.json` con:
- `status`: `DONE` | `DONE_WITH_CONCERNS` | `NEEDS_CONTEXT` | `BLOCKED`
- `inspected_coverage`: lista archivos/hashes vs artifacts privados
- `design_rulings`: decisiones técnicas tomadas (este plan + diseño)
- `criteria_tests`: mapeo criterio → test real + logs RED/GREEN
- `final_command`: comando exacto, cwd, exit_code, summary
- `timing_api_example`: salida JSON `delegate timing`
- `host_install_limits`: límites honestos (sin push universal, SSE volátil, etc.)

## 5. Fix Rounds

### Round 1 (2026-11-01)
- **Issue**: `execute_bound` usaba `supervisor_process.communicate(timeout)` esperando salida del proceso incluso cuando `result.json` ya listo.
- **Fix**: Revertido a `_wait_result` (sondeo 20 ms) que retorna temprano en delivery terminal.
- **Changes**: `bound_execution.py` (eliminar communicate), `test_bound_execution.py` (tests T0.1-T0.3, T0.5-T0.6, T0.12).
- **Verification**: 775 tests pass, ruff/mypy clean.

### Round 2 (2026-11-01)
- **Issue**: Test `test_supervisor_returns_early_while_process_still_alive` usaba mock (thread + object) en vez de subprocess real OS. Spec/plan describían enfoque `communicate()` ya descartado.
- **Fix**: 
  1. Test reescrito con `subprocess.Popen` real que escribe `result.json` vía `write_terminal` y duerme 3s.
  2. Usar `stdout=stderr=DEVNULL` para evitar bloqueo por buffer de pipe en Windows.
  3. Actualizar spec/plan a enfoque sondeo acotado (`_wait_result`), marcando `communicate()` como **rechazado**.
- **Changes**: 
  - `test_bound_execution.py`: nuevo test `test_supervisor_returns_early_while_process_still_alive` con subprocess real + DEVNULL.
  - `docs/superpowers/specs/2026-11-01-espera-finalizacion-design.md`: enfoque A = sondeo acotado; enfoque B/C = fallback/rechazado.
  - `docs/superpowers/plans/2026-11-01-espera-finalizacion.md`: actualizado a sondeo acotado; `communicate()` marcado como rechazado.
- **Verification**: 
  - `uv run pytest tests/test_bound_execution.py::test_supervisor_returns_early_while_process_still_alive -v` → PASSED (1.54s, coordinator returns in ~0.55s while child sleeps 3s).
  - `uv run pytest` → 776 passed.
  - `uv run ruff check . && uv run ruff format --check . && uv run mypy` → All clean.
- **File hashes**:
  - `skills/delegating-to-opencode/scripts/bound_execution.py`: `D191CECF80ED0749CD8B49B0C20AEA69C3A6A79BEEBD7E4455EAA735A3ACB366`
  - `tests/test_bound_execution.py`: `F53934784D931682EA4341234A8498BBAE918F2F1127AF154B648FDDA07B122A`

## 6. Presupuesto y Handoff

- **Presupuesto**: ~20 min implementación + tests + verificación
- **Revisión independiente**: Despachada por coordinador (no por implementador)
- **Fuentes congeladas**: Al final, sin cambios adicionales
- **Evidencia histórica**: Preservar reportes previos al corregir