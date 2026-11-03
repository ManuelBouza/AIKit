# Evidencia de reconciliación terminal — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persistir una observación diagnóstica acotada por intento para toda reconciliación, sin confundirla con la entrega final, y permitir que recuperación local use evidencia exitosa solo cuando el registro, el artefacto y la procedencia actuales coincidan.

**Architecture:** Añadir una propiedad opcional al `TaskRecord` y un marcador interno de respuesta HTTP al helper; primero desplegar parser/recuperación que aceptan legacy y entienden el lifecycle. Después, el supervisor escribe `record.json` provisional, publica `result.json` con el reemplazo atómico existente, registra la observación host por mecanismos actuales y confirma el estado final en el registro. `record.json` es el único punto de commit local; no se promete transacción entre tres archivos.

**Tech Stack:** Python 3.10+, dataclasses tipadas, JSON existente, pytest, Ruff, mypy, `session_store` y locks actuales; SHA-256 de la biblioteca estándar.

**Spec:** `docs/superpowers/specs/2026-11-03-evidencia-reconciliacion-design.md` (aprobado el 2026-11-03; commit `27daa45`).

**Estado:** Unidades 1 y 2 ejecutadas y aceptadas independientemente el 2026-11-03. Unidades 3–4 pendientes; no habilitar el escritor antes del lector compatible.

## Global Constraints

- No cambiar el JSON público de resultado ni la semántica actual de `delivery`.
- Una observación negativa se conserva como diagnóstico; solo los gates existentes pueden producir `delivery=completed`.
- Máximo una lectura `session.message.get`; no añadir inferencias, sondeos, reintentos, monitor ni llamadas de catálogo/cuota.
- Timeout por proceso y presupuesto restante actual del worker; no sumar preflight, reiniciar deadline ni cambiar cancelación.
- Usar `lock_task`, `save_task` y `_atomic_replace` existentes; no añadir locks, base de datos, sidecar o servicio.
- No anidar `lock_task` con el lock host: guardar la barrera bajo lock de tarea y después usar `record_host_observation`, fuera de ese lock, según el flujo existente.
- El campo `reconciliation` es opcional para registros legacy. No prometer que escritores antiguos preservan claves nuevas; actualizar lector antes de habilitar escritores.
- `_record_to_json` omite `reconciliation` cuando vale `None`; serializador/parser nuevos aceptan exactamente forma legacy y extendida, sin publicar la clave mientras el writer del supervisor siga deshabilitado.
- No persistir bodies, errores del proveedor, transcripciones, credenciales, passwords, configuración ni texto arbitrario de excepción.
- No instalar. Si los archivos fuente empaquetados cambian, validar export en ruta nueva bajo `.aikit/`; no instalar ni ejecutar la prueba real mínima sin autorización específica.
- No exportar ni desplegar snapshot intermedio entre lector y writer; exportar solo cuando ambas unidades estén coordinadas.
- Preservar coordinador, workers y revisión independiente; cada revisor usa sesión distinta de la de implementación.

## Review Focus

1. **Legacy vs clave exacta:** registros v1 sin `reconciliation` continúan leyéndose; presencia malformada nunca promueve entrega. Test propietario: Unidad 1, `test_legacy_record_without_reconciliation_loads`; Unidad 2, `test_malformed_reconciliation_is_not_usable`.
2. **Respuesta real vs error local:** timeout/precheck/excepción no se registran como respuesta durable; una respuesta HTTP por sí sola tampoco acredita identidad o éxito; códigos no filtran texto. Test propietario: Unidad 1, `test_reconciliation_marks_only_received_response`; Unidad 3, `test_local_precheck_failure_persists_no_remote_outcome`.
3. **Barrera y stale attempt:** un completed válido se reutiliza; si una invalidación no se puede guardar, no se hace GET ni se publica un nuevo completed. Test propietario: Unidad 3, `test_failed_pending_barrier_does_not_reconcile`.
4. **Artefactos y commit:** bytes/digest corresponden exactamente; crash o fallo entre result, host y commit no recupera completed. Test propietario: Unidad 3, `test_result_digest_covers_exact_atomic_bytes` y `test_commit_failure_keeps_recovery_pending`.
5. **Recovery de identidad vigente:** owner/attempt/session/digest incorrectos no acreditan éxito y recovery no consulta backend. Test propietario: Unidad 2, `test_recover_rejects_stale_reconciliation_evidence`; preservar también CLI-terminal y legacy válidos.

## Mapa de archivos

- `skills/delegating-to-opencode/scripts/session_store.py`: tipo inmutable, validación/serialización de la clave opcional y lectura legacy.
- `skills/delegating-to-opencode/scripts/session_backend.py`: `response_observed` interno para distinguir respuesta HTTP real de resultado local del helper.
- `skills/delegating-to-opencode/scripts/bound_execution.py`: carga de bytes actuales, validación lifecycle/identity/digest y gate de recovery sin GET.
- `skills/delegating-to-opencode/scripts/session_worker.py`: barrera provisional, observación, publicación atómica del resultado y último commit.
- Tests: ampliar `tests/test_session_store.py`, `tests/test_terminal_reconciliation.py`, `tests/test_bound_reconciliation.py` y `tests/test_host_registry.py`; crear `tests/test_reconciliation_evidence.py` corto para fallos de supervisor/publicación, reutilizando `prepare`, `run_fake`, `worker`, `FakeBinding` y seeders existentes.
- `docs/balance-carga.md`: explicar lifecycle observado vs entrega final y límites de recuperación.

## Unidad 1: esquema opcional y provenance del helper

**Archivos:** modificar `session_store.py`, `session_backend.py`; tests en `tests/test_session_store.py` y `tests/test_terminal_reconciliation.py`.

**Interfaces que produce:**

```python
ReconciliationPhase = Literal["not_attempted", "local_failure", "response_observed"]
ReconciliationIdentity = Literal["unverified", "verified", "invalidated"]
ReconciliationLifecycle = Literal["provisional", "committed", "invalidated"]
ReconciliationSource = Literal["local", "durable_message"]
ReconciliationOutcome = Literal[
    "completed", "partial", "failed", "uncertain", "pending"
]
TerminalFinish = Literal[
    "stop",
    "length",
    "error",
    "content-filter",
    "interrupted",
    "cancel",
    "tool-calls",
    "unknown",
]


@dataclass(frozen=True)
class ReconciliationObservation:
    attempt_id: str
    session_id: str | None
    assistant_message_id: str | None
    observed_at: str
    generation: int
    phase: ReconciliationPhase
    identity: ReconciliationIdentity
    lifecycle: ReconciliationLifecycle
    source: ReconciliationSource
    accepted: bool | None
    outcome: ReconciliationOutcome | None
    reason: ReconciliationReason
    finish: TerminalFinish | None
    completed_at: int | float | None
    limitations: tuple[ReconciliationReason, ...]
    result_sha256: str | None


@dataclass
class TaskRecord:
    # campos actuales sin cambio
    reconciliation: ReconciliationObservation | None = None


@dataclass(frozen=True)
class TerminalReconciliation:
    # campos actuales sin cambio
    response_observed: bool = False
```

`ReconciliationReason` es un `Literal` formado por razones ya emitidas por `reconcile_terminal_message`: `accepted`, `assistant_message_id_unavailable`, `assistant_message_id_mismatch`, `backend_timeout`, `backend_unavailable`, `budget_exhausted`, `finish_cancel`, `finish_content-filter`, `finish_error`, `finish_interrupted`, `finish_length`, `invalid_completed_at`, `invalid_response`, `invalid_role`, `message_error`, `missing_completed_at`, `missing_finish`, `non_final_finish`, `operation_unavailable`, `owner_mismatch`, `owner_unverified`, `parent_id_null_not_correlated`, `parent_id_unavailable`, `parent_message_mismatch`, `prior_delivery_not_success`, `record_changed`, `session_mismatch`, `session_unknown`, `unknown_finish`; añadir solo códigos locales existentes necesarios: `owner_verification_failed`, `reconciliation_failed`, `record_save_failed`, `result_save_failed`, `provenance_unavailable`, `deadline_exceeded`, `result_mismatch`. Finish remoto fuera de `TerminalFinish` se normaliza a `None` con `reason=unknown_finish`; nunca guardar texto arbitrario.

- [x] **Paso 1: RED de compatibilidad de almacenamiento.** `test_legacy_record_without_reconciliation_loads` afirma `record.reconciliation is None` y que serializar legacy omite la clave; `test_reconciliation_record_round_trips_and_validates` comprueba round-trip, generation positiva, timestamp zonado y digest SHA-256; `test_malformed_reconciliation_is_not_usable` muta enum/ID/digest y verifica `invalid_record`, nunca aceptación.
- [x] **Paso 2: Ejecutar tests de almacenamiento para comprobar RED.** `uv run pytest tests/test_session_store.py -q`; esperado: ausencia de parser/serializador opcional o rechazo de fixture nueva, nunca import error.
- [x] **Paso 3: Implementar el campo.** Extender `TaskRecord`, `_RECORD_KEYS`, `_record_from_json`, `_record_to_json` y `_validate_record`: aceptar exactamente set legacy o set legacy + `reconciliation`; ausencia => `None`; al serializar `None`, no insertar la clave. Validar formatos y enums; no cambiar versión ni migrar masivamente.
- [x] **Paso 4: GREEN almacenamiento.** Ejecutar `uv run pytest tests/test_session_store.py -q`; esperado: legacy y nueva forma pasan, forma malformada fail-closed.
- [x] **Paso 5: Escribir test RED de provenance HTTP.** `test_reconciliation_marks_only_received_response`: early exits y request que lanza conservan `response_observed=False`; `ApiResponse` real pone `True`, incluso con status no-success.
- [x] **Paso 6: Ejecutar RED.** `uv run pytest tests/test_terminal_reconciliation.py -q`; esperado: assertion fallida por el marcador ausente, no error de import.
- [x] **Paso 7: Implementar el marcador.** Añadir `response_observed: bool = False` al final de `TerminalReconciliation`; activarlo solo después de retornar `request`. Un HTTP 500 puede tener `True` y `accepted=False`; el flag no acredita identidad ni éxito.
- [x] **Paso 8: GREEN focal.** Ejecutar `uv run pytest tests/test_session_store.py tests/test_terminal_reconciliation.py -q`; esperado: ambas áreas pasan.
- [x] **Paso 9: Revisión y versionado futuro.** Revisión independiente de esquema/saneamiento; tras aprobación del coordinador, `git add` solo los archivos de Unidad 1 y `git commit -m "feat: model reconciliation evidence safely"`; sin push ni instalación.


**Cierre de Unidad 1:** implementador 866 pruebas globales; revisor independiente 175 focales y reproducción adicional, sin hallazgos. Casos de almacenamiento en "tests/test_reconciliation_observation_store.py" para mantener archivos acotados. Evidencia y límites en [el seguimiento](../../revision-reconciliacion-2026-11-02.md). Las interfaces posteriores aún no se publican desde el supervisor.

## Unidad 2: lector de recuperación y compatibilidad

**Archivos:** modificar `bound_execution.py`; tests en `tests/test_bound_reconciliation.py` y fixture legacy en `tests/test_session_store.py` si hace falta.

**Interfaces que produce:**

```python
def _read_result_snapshot(
    record: TaskRecord,
) -> tuple[bytes, dict[str, Any]] | None: ...
def _reconciliation_matches_result(record: TaskRecord, result_bytes: bytes) -> bool: ...
```

- [x] **Paso 1: Escribir tests RED de reader.** `test_recover_legacy_record_without_observation_uses_existing_gates`, `test_recover_rejects_stale_reconciliation_evidence`, `test_recover_does_not_complete_malformed_observation` y `test_recover_rejects_digest_mismatch_without_backend_read`. Legacy válido conserva el gate antiguo; metadata presente requiere lifecycle/identity/accepted/outcome/IDs/digest correctos.
- [x] **Paso 2: Ejecutar RED.** `uv run pytest tests/test_bound_reconciliation.py -q`; esperado: fallos de comportamiento por falta de validación de observación, no fallos de import.
- [x] **Paso 3: Implementar snapshot de resultado.** Añadir `def _read_result_snapshot(record: TaskRecord) -> tuple[bytes, dict[str, Any]] | None`; reutilizar `_read_artifact` y límite existente, parsear una vez, entregar bytes exactos y payload. Mantener `_read_result` como adaptador dict para sus demás consumidores.
- [x] **Paso 4: Implementar gate de `_recover`.** Si `reconciliation is None`, conservar reglas legacy. Si está presente, `completed` solo pasa con intento/sesión/owner vigentes y generation positiva en el registro actual, lifecycle `committed`, identity `verified`, `accepted=True`, outcome `completed`, IDs consistentes, host terminal actual y digest de bytes coincidente. Metadata negativa/provisional/invalidada/stale/malformada retorna pending saneado; nunca consultar binding/backend.
- [x] **Paso 5: GREEN y revisión.** Repetir `uv run pytest tests/test_bound_reconciliation.py -q`; comprobar status/delivery pending, `result_mismatch`, ningún request backend en discrepancias y CLI-terminal normal sin observación. Revisión independiente de compatibilidad.
- [x] **Paso 6: Versionar tras aprobación.** `git add` solo archivos de Unidad 2 y `git commit -m "fix: gate reconciliation recovery on committed evidence"`; no instalar/exportar.


**Cierre de Unidad 2:** 875 pruebas globales del implementador; 186 focales y tres reproducciones del revisor, dictamen accepted. El bloqueo por fuente de entrega se reprodujo, corrigió y revisó en la misma sesión independiente. Generation se valida positiva en el registro actual: no existe copia externa para contrastarla; el enlace usa intento, sesión y digest. No se afirma esa comparación independiente ni autenticidad criptográfica. Detalle en [el seguimiento](../../revision-reconciliacion-2026-11-02.md). Unidades 3 y 4 no iniciadas.

## Unidad 3: protocolo del supervisor y publicación ordenada

**Archivos:** modificar `session_worker.py`; crear `tests/test_reconciliation_evidence.py`; reutilizar tests de `host_registry.py` para confirmar la reversión existente.

**Interfaces que produce:**

```python
def _write_result_atomic(
    attempt_directory: Path, report: dict[str, Any]
) -> tuple[bytes, str]: ...
def _result_sha256(payload: bytes) -> str: ...
```

`_write_result_atomic` serializa exactamente el JSON público actual con `ensure_ascii=True`, escribe bytes en temporal único en el directorio del intento, hace flush/`fsync`, llama `session_store._atomic_replace(temp, result.json)` y devuelve esos bytes/digest; limpia solo el temporal propio. No reescribe `result.json` después del commit. El writer nuevo solo se activa tras completar Unidad 1.

- [ ] **Paso 1: Escribir tests RED del protocolo.** En `tests/test_reconciliation_evidence.py`, reutilizar fixtures y mantenerlo compacto. Nombres/asserts observables: `test_pending_save_failure_prevents_get_or_new_completed` (record previo intacto, cero message GET); `test_result_write_failure_keeps_record_provisional`; `test_host_observation_failure_blocks_commit`; `test_last_owner_check_failure_blocks_commit`; `test_commit_save_failure_recovery_stays_pending`; `test_crash_after_host_terminal_before_commit_stays_pending`; `test_postcommit_result_rewrite_fails_digest_gate`; `test_negative_outcome_commits_diagnostic_without_promoting_delivery`; `test_cli_terminal_completion_needs_no_reconciliation_observation`. En todos: report/record y forma JSON pública actual; evitar asserts solo de contador de llamadas.
- [ ] **Paso 2: Ejecutar RED.** `uv run pytest tests/test_reconciliation_evidence.py -q`; esperado: fallos de comportamiento del lifecycle/publicación, no errores de import.
- [ ] **Paso 3: Implementar `_write_result_atomic`.** Serializar la forma pública actual; `tempfile.mkstemp` en el directorio del intento, escribir bytes exactos, flush/`fsync`, reutilizar `_atomic_replace`, limpiar solo temporal propio y devolver `(payload, sha256)`.
- [ ] **Paso 4: GREEN del writer.** Repetir su test focal y confirmar bytes idénticos, hash calculado sobre esos bytes y conservación del destino previo si `_atomic_replace` falla.
- [ ] **Paso 5: Implementar barrera/protocolo en `supervise`.** Completed vigente se reutiliza. Reevaluación aprobada: bajo `lock_task`, releer registro vigente, validar identidad y guardar provisional/pending antes de GET; fuera de ese lock, demover host con `terminal=False`. Si falla la barrera, parar. Tras helper, persistir diagnóstico provisional solo si una nueva lectura bajo lock confirma todavía task/attempt/server/session/generation; actualizar el registro actual sin copiar otros campos desde un snapshot stale. Para éxito, escribir artefacto candidato, observar host terminal solo después de gates, hacer último owner-check y repetir la comparación antes del commit atómico; para negativos, preservar delivery y commitear solo diagnóstico. Nunca reescribir artefacto tras commit sin barrera y nueva generation/digest.
- [ ] **Paso 6: GREEN y focal vecina.** `uv run pytest tests/test_reconciliation_evidence.py tests/test_worker_reconciliation.py tests/test_host_registry.py -q`; no más de un GET por intento, recuperación sin GET y todos los fallos frontera pending.
- [ ] **Paso 7: Revisión independiente.** Revisor de lifecycle/rollback en sesión distinta, antes de pasar a validación global.
- [ ] **Paso 8: Versionar tras aprobación.** `git add` solo archivos de Unidad 3 y `git commit -m "feat: persist reconciliation evidence safely"`; sin push ni instalación.

## Unidad 4: validación global, documentación y revisión de entrega

**Archivos:** `docs/balance-carga.md`, tests existentes `test_bound_reconciliation.py` y `test_reconciliation_evidence.py`; ajustes de producción solo si los checks encuentran un fallo que siga dentro del diseño aprobado.

**Interfaces consumidas:** `ReconciliationObservation`, `TerminalReconciliation.response_observed`, `_write_result_atomic`, `_read_result_snapshot` y `record_host_observation` existentes.

- [ ] **Paso 1: Asegurar casos restantes.** Ejecutar `uv run pytest tests/test_bound_reconciliation.py tests/test_reconciliation_evidence.py -q`; completar únicamente asserts que falten de legacy, `result_mismatch`, negative committed y no-GET local.
- [ ] **Paso 2: Documentar contrato.** Actualizar `docs/balance-carga.md`: estado del registro, distinción outcome/delivery, lifecycle/commit, SHA, gates host y límites multiartefacto; no cambiar JSON público.
- [ ] **Paso 3: Validación final una vez.** Ejecutar `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy` y `git diff --check`; guardar logs/exit codes. Solo repetir suite si hay cambio funcional o fallo con causa/reason registrado; no repetir por formato-only.
- [ ] **Paso 4: Exportar candidato si cambió source empaquetado.** Usar `scripts/build_plugin.py` con destino único bajo `.aikit/`, comprobar hashes/paridad y registrar resultado; no instalar ni recargar host.
- [ ] **Paso 5: Revisión global independiente.** Sesión nueva distinta del implementador; snapshot final, análisis técnico, checks reales sin modificar entrega y metadata `review_evidence.py` validada por coordinador. No autorrevisión ni duplicar revisión técnica.
- [ ] **Paso 6: Cierre de esta implementación y commit futuro.** Registrar la aceptación global de código y actualizar REC-001, sin dar por terminada la tarea 6 original mientras falte su prueba real mínima autorizada. La instalación conserva su autorización separada. Tras aceptación del coordinador, `git add` solo los archivos del alcance y `git commit -m "feat: finalize durable reconciliation diagnostics"`; sin push.

## Gates de implementación ya comprobados en fuente

- El host se puede hacer conservador con `record_host_observation(..., terminal=False)`: el estado pasa a `uncertain`; `_write_host` publica bajo su lock con temporal/`fsync`/`_atomic_replace`. La prueba futura debe demostrar que `_recover` no lo trata como terminal.
- El `result.json` actual usa `open_artifact(..., "xb")`, no reemplazo atómico. Reutilizar `session_store._atomic_replace` es posible porque recibe archivos regulares hermanos, y `host_registry._write_host` ya demuestra el patrón de temporal seguro. El writer futuro debe comprobar lectores abiertos y ACL en Windows mediante fallos observables; no crear APIs/infra paralelas.
- La semántica pública no cambia: `bound_execution._recover` usa fase host `terminal_observed`; un `record.json` committed, digest actual y owner/provenance son gates adicionales, no sustitutos de esa fase.

## Autorrevisión del plan

- **Cobertura:** esquema/helper, recovery reader, writer/lifecycle, digest/legacy, fallos de cada frontera, documentación, validación global y revisión independiente tienen dueño y tests.
- **Secuencia segura:** Unidad 1 añade serialización/parser; Unidad 2 entrega recovery reader compatible; Unidad 3 habilita writer; Unidad 4 valida. Nunca se publica writer antes del reader. Unidad 3 mantiene barrera provisional hasta último save del record.
- **Tipos:** los campos de `ReconciliationObservation`, alias, `response_observed`, writer y reader coinciden en las cuatro unidades; los errores usan códigos literales existentes y no texto arbitrario.
- **Review Focus:** cada uno de los cinco riesgos tiene test explícito asignado arriba; estos tests no se ejecutaron al redactar el plan.
- **Proporción:** cuatro unidades acopladas; sin infraestructura o refactor ajeno a REV-003/004.
