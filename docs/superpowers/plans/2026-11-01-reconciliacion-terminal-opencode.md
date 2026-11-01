# Reconciliación Terminal de OpenCode por Mensaje Persistido — Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconciliar `delivery` de `pending` a `completed` solo por lectura read-only del mensaje durable cuando falte `step_finish`/`step-finish` (`reason=stop`), sin relajar `EventStream` ni inventar terminal.

**Architecture:** Extender binding existente con `GET /api/session/:sessionID/message/:messageID`; añadir helper conservador en `session_backend`; integrarlo en `session_worker.supervise` tras `events.finish()` solo si `terminal=false` y sin error; reutilizar `bound_execution._map_result`/`_recover`. Persistencia atómica con locks existentes.

**Tech Stack:** Python 3.10+, pytest, Ruff, mypy, `uv`; transporte HTTP existente (`service_connection`), `session_store`, `session_stream`.

**Spec:** `docs/superpowers/specs/2026-11-01-reconciliacion-terminal-opencode-design.md` (commit 9f5f5e8)

## Global Constraints

- No nueva skill ni infraestructura paralela; reutilizar módulos existentes.
- Sin catálogo/cuota, sin inferencias adicionales, sin SSE global/hooks/monitor.
- Una sola lectura read-only por intento cuando falta marcador terminal.
- No aceptar idle/exit 0/texto como éxito; `server_state_unknown` no se suprime sin acreditación.
- `EventStream` conserva regla conservadora; no modificar parser para inventar terminal.
- Durante esta fase de planificación: no commit/push/install. En implementación futura, commits por tarea permitidos por el coordinador, sin push/install automático.
- Validación rutinaria sin catálogo ni `doctor`; `doctor` solo si el usuario lo pide expresamente.
- `build_plugin.py` requiere argumentos; verificar con `--help` o lectura del parser antes de ejecutar export.
- No prometer capacidades de tests sin nombre y assertions esperadas.

## Review Focus

Cinco tests asignados a revisión:
1. `tests/test_service_connection.py::test_managed_binding_session_message_get_maps_get_path`
2. `tests/test_session_backend.py::test_reconcile_terminal_message_accepts_stop_with_valid_ids`
3. `tests/test_session_backend.py::test_reconcile_terminal_message_rejects_foreign_or_old_ids`
4. `tests/test_session_worker.py::test_supervisor_reconciles_once_within_remaining_budget`
5. `tests/test_bound_execution.py::test_map_result_reuses_reconciled_completed_evidence`

- Correlación por IDs capturados del intento actual, no por cercanía temporal.
- `parent_id=null` sin vínculo fiable conserva `uncertain`.
- `finish=length/error/content-filter/interrupted/cancel/tool-calls/unknown` no son éxito.
- Presupuesto worker vs MCP 45 s: no cancelar backend al vencer cliente.
- Idempotencia y evidencia mínima sin credenciales/transcripciones.

---

### Task 1: Operación de lectura de mensaje en binding

**Files:**
- Modify: `skills/delegating-to-opencode/scripts/service_connection.py:34-43,94-136,297-316`
- Test: `tests/test_service_connection.py`

**Interfaces:**
- Extiende `ManagedBinding.request`:
```python
def request(self, operation, *, session_id=None, message_id=None, timeout=10.0, resume=None) -> ApiResponse
```
- Extiende `TrustedBinding.request` con `message_id: str | None = None`.
- Extiende `_operation_path(operation, session_id, message_id=None)`.
- `DEFAULT_OPERATIONS` añade `"session.message.get"`.
- Path: `GET /api/session/{session_id}/message/{message_id}`.

- [x] **Step 1: Write failing test**
```python
def test_managed_binding_session_message_get_maps_get_path():
    path, method = _operation_path("session.message.get", "ses_1", "msg_1")
    assert path == "/api/session/ses_1/message/msg_1"
    assert method == "GET"
    assert "session.message.get" in DEFAULT_OPERATIONS
```
- [x] **Step 2: Run** `uv run pytest tests/test_service_connection.py -q` → FAIL (RED).
- [x] **Step 3: Implement** operación en `_operation_path` y `DEFAULT_OPERATIONS`; pasar `message_id` en `request`.
- [x] **Step 4: Run** → PASS.
- [x] **Step 5: Commit** (solo en implementación futura) `feat: add read-only session message operation`

### Task 2: Helper conservador de reconciliación

**Estado:** completada y aceptada mediante revisión independiente. TDD: 35 fallos
antes de implementar; 127 pruebas focalizadas aprobadas después, junto con Ruff,
formato y mypy. Captura de metadata y evaluador disponibles; sin integración en
el supervisor ni cambios de persistencia. La tarea 3 permanece pendiente.

**Files:**
- Modify: `skills/delegating-to-opencode/scripts/session_backend.py`
- Test: `tests/test_session_backend.py`

**Interfaces:**
```python
@dataclass(frozen=True)
class TerminalReconciliation:
    accepted: bool
    outcome: Literal["completed", "partial", "failed", "uncertain", "pending"]
    finish: str | None
    completed_at: int | float | None
    assistant_message_id: str | None
    reason: str
    limitations: tuple[str, ...]

def reconcile_terminal_message(
    record: TaskRecord,
    binding: TrustedBinding,
    *,
    assistant_message_id: str | None,
    prompt_message_id: str | None = None,
    timeout: float,
    _clock: Callable[[], float] = time.monotonic,
) -> TerminalReconciliation
```

`session_stream` (solo metadata, no terminal):
- `EventStream` expone `assistant_message_id: str | None` capturado de `part.messageID` o `text part.messageID` del intento actual.
- Expone `assistant_message_mismatch: bool` si el ID observado no corresponde al intento actual.
- No cambia `terminal`; `terminal` sigue derivándose solo de `step_finish`/`step-finish` con `reason=stop`.
- Si el campo real no existe en eventos originales, helper retorna `accepted=False`, `outcome="uncertain"`, `reason="assistant_message_id_unavailable"` y documenta gate de solución; no acredita.

Correlación:
- Requiere propietario/sesión/cwd sin cambio y `assistant_message_id` capturado inequívocamente del intento actual.
- `parent_id=null` no autoriza usar último mensaje ni cercanía temporal.
- `prompt_message_id` solo se usa si está disponible; no se exige si la API no lo soporta.

Persistencia y compatibilidad:
- No añadir campos obligatorios a `TaskRecord` en esta tarea; evidencia saneada se persiste en `DeliveryObservation.source="durable_message"` y evidencia mínima en logs/observaciones existentes.
- Registros antiguos sin evidencia se tratan como `pending`/`uncertain` según estado actual; no se rechazan por ausencia de evidencia.
- Una actualización exitosa se hace bajo `lock_task`/`lock_session` existentes; si falla la escritura, conservar estado previo y registrar limitación.

- [ ] **Step 1: Write failing tests**
```python
def test_reconcile_terminal_message_accepts_stop_with_valid_ids():
    result = reconcile_terminal_message(record, binding, assistant_message_id="msg_1", timeout=5.0)
    assert result.accepted is True
    assert result.outcome == "completed"
    assert result.finish == "stop"
    assert result.assistant_message_id == "msg_1"

def test_reconcile_terminal_message_rejects_foreign_or_old_ids():
    result = reconcile_terminal_message(record, binding, assistant_message_id="msg_old", timeout=5.0)
    assert result.accepted is False
    assert result.outcome in {"uncertain", "pending"}
```
Además cubrir: `length` → `partial`; `error/content-filter/interrupted/cancel` → `failed`; `tool-calls/unknown` → nunca `completed`; API no disponible/timeout/propietario cambió → `pending`; mensaje incompleto sin `completed_at` → conservador.
- [ ] **Step 2: Run** `uv run pytest tests/test_session_backend.py -q` → FAIL.
- [ ] **Step 3: Implement** validación de identidad, `GET session.message.get`, aceptación estricta y evidencia saneada.
- [ ] **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** (solo en implementación futura) `feat: add conservative terminal reconciliation helper`

### Task 3: Integración en supervisor

**Files:**
- Modify: `skills/delegating-to-opencode/scripts/session_worker.py:495-560`
- Test: `tests/test_session_worker.py`

**Interfaces:**
- Consumes: `events.terminal`, `events.error`, `record.session`, binding, `assistant_message_id`.
- Produces: `delivery` reconciliado con `source="durable_message"` cuando aceptado; en caso contrario estado conservador previo.

- [ ] **Step 1: Write failing test**
```python
def test_supervisor_reconciles_once_within_remaining_budget():
    result = supervise(..., terminal=False, events_error=None, remaining_budget=3.0)
    assert reconciliation_calls == 1
    assert result.delivery.state == "completed" or result.delivery.state == "pending"
```
Además: si `uncertain`, mantiene `pending`; si presupuesto agotado, mantiene `pending` y permite reconciliación explícita posterior sin duplicar inferencia.
- [ ] **Step 2: Run** `uv run pytest tests/test_session_worker.py -q` → FAIL.
- [ ] **Step 3: Implement** tras `events.finish()`: si `not events.terminal and not events.error`, llamar helper con `timeout=min(remaining_budget, 10.0)`; `remaining_budget = end - now` con deadline del worker como autoridad; MCP 45 s es espera del cliente, no vida del supervisor; nunca interrumpir backend solo porque venció la espera del cliente; si aceptado, `delivery=completed source=durable_message`; persistir con `save_task`/locks; si helper lanza, añadir limitación y mantener `pending`.
- [ ] **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** (solo en implementación futura) `feat: reconcile terminal via durable message in supervisor`

### Task 4: Reutilizar contrato en bound_execution

**Files:**
- Modify: `skills/delegating-to-opencode/scripts/bound_execution.py:172-270`
- Test: `tests/test_bound_execution.py`

**Interfaces:**
- `_map_result` acepta `delivery="completed"` reconciliado por mensaje durable cuando identidades coinciden.
- `_recover` reusa evidencia persistida sin nueva inferencia.
- Conserva `result_mismatch` y comprobaciones de procedencia.

- [ ] **Step 1: Write failing test**
```python
def test_map_result_reuses_reconciled_completed_evidence():
    result = _map_result(record_with_delivery_completed_durable_message)
    assert result["delivery"]["state"] == "completed"
    assert result["delivery"]["source"] == "durable_message"
```
- [ ] **Step 2: Run** `uv run pytest tests/test_bound_execution.py -q` → FAIL.
- [ ] **Step 3: Implement** mínimo: tratar completed durable como completed terminal cuando `record`/result coinciden; preservar mismatch y procedencia; sin polling nuevo.
- [ ] **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** (solo en implementación futura) `feat: consume reconciled terminal in bound execution`

### Task 5: Documentación y validación de empaquetado

**Files:**
- Modify: `docs/balance-carga.md`, `README.md`, `skills/delegating-to-opencode/SKILL.md` (si aplica)
- Test: `tests/test_plugin_export.py`

- [ ] **Step 1: Update docs** describiendo trigger, casos negativos, semántica de presupuesto, campos de evidencia y compatibilidad con `pending`/`uncertain`.
- [ ] **Step 2: Run** `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, `git diff --check`.
- [ ] **Step 3: Verify package export** `python scripts/build_plugin.py --help` o lectura del parser; luego export a una ruta única bajo `.aikit/`, sin instalación.
- [ ] **Step 4: Commit** (solo en implementación futura) `docs: document terminal reconciliation contract`

### Task 6: Revisión independiente

- [ ] **Step 1: Fresh reviewer session** valida metadata (`role: reviewer`, `session`, `snapshot`, `verdict`, `checks[]`, `findings[]`, `limitations[]`) con `scripts/review_evidence.py`; el revisor no se limita a metadata, ejecuta comprobaciones reales sin modificar la entrega.
- [ ] **Step 2: Real minimal test once** solo con autorización futura; sin tests de inferencia en la suite.
- [ ] **Step 3: Export validation** sin instalación.

---

## Self-Review Notes

- Spec coverage: tabla de aceptación y correlación en Task 2; integración Task 3; reutilización Task 4; docs/export Task 5; revisión Task 6.
- Type consistency: `TerminalReconciliation` definido una sola vez en Task 2; Task 3/4 lo consumen. `ManagedBinding.request`/`TrustedBinding.request`/`_operation_path` actualizados en Task 1.
- Proporción: firmas y casos, sin cuerpos largos.
- Riesgo abierto: si discovery muestra que stdout no contiene `assistant_message_id` y la API solo devuelve mensaje completo por id, el gate conserva `uncertain` y no fabrica correlación; Task 2 incluye ese gate.
- Python mínimo del repositorio: 3.10, no elevar a 3.11.
- Ruta de captura prioritaria: `part.messageID` y `text part.messageID` del intento actual; no inventar terminal.
- `completed_at` usa timestamp numérico real de la API, no `str` arbitrario.
- Un solo outcome y evidencia saneada persistida bajo lock; compatibilidad con registros antiguos sin evidencia.
- No descartar negativos por stdout error/timeout/cancel; no promover por mensaje antiguo.
- Una lectura por intento con presupuesto restante del worker; MCP 45 s es espera del cliente. Si se agota el presupuesto, conservar estado; no afirmar un mecanismo posterior de reconciliación salvo que exista un camino determinista real o quede documentado fuera de alcance.
- Revisión final técnica por sesión nueva de OpenCode sin modificar entrega; coordinador valida metadata `review_evidence`; revisor no solo metadata. Prueba real mínima solo al ejecutar plan aprobado, una vez con presupuesto, sin instalar paquete a escondidas. Export validación sin instalar.
