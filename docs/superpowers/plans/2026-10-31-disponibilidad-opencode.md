# Disponibilidad real de cuentas OpenCode: plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Añadir registro local y consulta read-only de disponibilidad OpenCode, integrado con selección y preflight, sin inferencias de prueba.

**Architecture:** Reutilizar `HostContext`, binding HTTP, locks y atomicidad de `session_store`. Dividir en `availability_state.py`, `availability_refresh.py` y `availability_policy.py`. La selección del coordinador usa la tabla; la consulta solo ocurre en refresh planificado o fallo real.

**Tech Stack:** Python 3.10+, stdlib, pytest, Ruff, mypy, OpenCode 2.2.0 HTTP API.

**Spec:** `docs/superpowers/specs/2026-10-31-disponibilidad-opencode-design.md`

## Global Constraints

- Estado compartido en `HostContext.aikit_state`, fuera de Git.
- Ruta por defecto del equipo: `C:/Users/Manuel/.local/state/aikit/availability-state.json`; la biblioteca no fija rutas personales.
- Provider directo `openai` bloqueado.
- `quota_resume` permanece deshabilitado.
- Sin nueva skill ni modificar Superpowers.
- Tarea 4 de binding permanece pausada.
- Sin instalación, push ni commit.
- Sin inferencias de prueba ni consultas de catálogo por cada preparación.
- El runtime no elige automáticamente; solo usa modelo y motivo explícitos del coordinador.
- Prioridad actualizada por el usuario: Go de pago -> otros de pago conectados -> todos los gratuitos conectados -> Codex, siempre con modelo y esfuerzo adecuados y disponibilidad compatible. Sustituye la prioridad anterior de gratuitos primero.
- Incorporar el perfil de rendimiento real del spec: proveedor/modelo/esfuerzo, fecha, fuente y muestras comparables; preferencia dentro del mismo nivel, sin inferencias de prueba ni confundir lentitud con cuota.

## Review Focus

- `reset_at` pasado no marca disponible.
- Cuota compartida no habilita modelos no habilitados.
- Fallo de consulta conserva `last_valid_observation` completo.
- Cambio de cuenta no reutiliza certeza previa.
- Endpoint experimental fallido no inventa disponibilidad.
- Pending/EOF de cliente no reenvía trabajo vivo.

---

### Task 1: Compatibilidad de versión y capacidades

**Files:**
- Modify: `skills/delegating-to-opencode/scripts/service_identity.py`
- Test: `tests/test_service_identity.py`

**Interfaces:**
- Produces: `read_registration(context) -> ServiceRegistration` acepta versión no vacía y la registra; `CapabilitySnapshot(service_version, operations, schema_version, source)` documenta el contrato que `availability_refresh` validará contra OpenAPI.

- [ ] **Step 1: Write failing test** `test_registration_accepts_newer_minor_version` with version `2.3.0`.
- [ ] **Step 2: Run test** to verify failure.
- [ ] **Step 3: Implement** replace exact equality with non-empty version validation plus capability set.
- [ ] **Step 4: Run test** to verify pass.

### Task 2: Estado y serialización

**Files:**
- Create: `skills/delegating-to-opencode/scripts/availability_state.py`
- Test: `tests/test_availability_state.py`

**Interfaces:**
- Produces: `AvailabilityStatus`, `LimitScope`, `Precision`, `AccountAlias`, `ModelKey`, `PricingTier`, `ModelMetadata`, `CatalogContext`, `QuotaObservation`, `QueryAttempt`, `AvailabilityRecord`, `ModelEntry`, `DataSourceStatus`, `AvailabilitySnapshot`, `read_snapshot(path) -> AvailabilitySnapshot | None`, `write_snapshot(path, snapshot)`, `update_snapshot(path, mutate)`.

- [ ] **Step 1: Write failing tests** `test_state_roundtrip`, `test_invalid_json_keeps_no_partial_state`, `test_last_valid_observation_complete`.
- [ ] **Step 2: Run tests** to verify failure.
- [ ] **Step 3: Implement** dataclasses, JSON validation, path limits, locks and atomic replacement.
- [ ] **Step 4: Run tests** to verify pass.

### Task 3: Refresh de fuentes

**Files:**
- Create: `skills/delegating-to-opencode/scripts/availability_refresh.py`
- Modify: `skills/delegating-to-opencode/scripts/service_connection.py`
- Test: `tests/test_availability_refresh.py`

**Interfaces:**
- Consumes: `ManagedBinding.config_sources`, `model_catalog`, `verify_owner`.
- Produces: `refresh_go(binding, project, timeout) -> list[AvailabilityRecord]`, `refresh_integrations(binding, timeout) -> list[str]`, `refresh_catalog_metadata(binding, project, timeout) -> list[dict[str, Any]]`.

- [ ] **Step 1: Write failing tests** `test_go_refresh_whitelist`, `test_experimental_failure_returns_unknown`, `test_integration_list_sanitized`.
- [ ] **Step 2: Run tests** to verify failure.
- [ ] **Step 3: Implement** read-only calls to `/api/experimental/usage/limits`, `/api/integration` and `/api/model`; persist only whitelisted fields.
- [ ] **Step 4: Run tests** to verify pass.

### Task 4: Política y elegibilidad

**Files:**
- Create: `skills/delegating-to-opencode/scripts/availability_policy.py`
- Test: `tests/test_availability_policy.py`

**Interfaces:**
- Produces: `eligible_candidates(records, candidates) -> list[str]`, `record_outcome(record, result_code, observed_at) -> AvailabilityRecord`, `should_refresh(record, now) -> bool`.

- [ ] **Step 1: Write failing tests** `test_reset_past_requires_recheck`, `test_shared_scope_does_not_enable_model`, `test_outcome_preserves_last_valid`.
- [ ] **Step 2: Run tests** to verify failure.
- [ ] **Step 3: Implement** eligibility ordering and outcome recording without automatic selection.
- [ ] **Step 4: Run tests** to verify pass.

### Task 5: Enforcement CLI/MCP y supervisor

**Files:**
- Modify: `skills/delegating-to-opencode/scripts/delegate.py`
- Modify: `skills/delegating-to-opencode/scripts/mcp_server.py`
- Modify: `skills/delegating-to-opencode/scripts/session_worker.py`
- Test: `tests/test_bound_cli_mcp.py`

**Interfaces:**
- Consumes: `read_state`, `should_refresh`, `refresh_*`, `record_outcome`.
- Produces: preflight availability check before inference; durable outcome recording after completion.

- [ ] **Step 1: Write failing tests** `test_cli_preflight_no_external_call_when_fresh`, `test_mcp_pending_does_not_resend`, `test_supervisor_records_outcome`.
- [ ] **Step 2: Run tests** to verify failure.
- [ ] **Step 3: Implement** minimal enforcement in existing paths; no catalog calls in supervisor.
- [ ] **Step 4: Run tests** to verify pass.

### Task 6: Comando actualizador

**Files:**
- Modify: `skills/delegating-to-opencode/scripts/delegate.py` or create `skills/delegating-to-opencode/scripts/availability_cli.py`
- Test: `tests/test_availability_cli.py`

**Interfaces:**
- Produces: `availability refresh --cwd <path> --json` and `availability status --cwd <path> --json`, read-only, no profile IO, safe JSON.

- [ ] **Step 1: Write failing tests** `test_refresh_cli_json`, `test_status_cli_no_external_calls`, `test_missing_state_single_refresh`.
- [ ] **Step 2: Run tests** to verify failure.
- [ ] **Step 3: Implement** deterministic updater entrypoint with local access only.
- [ ] **Step 4: Run tests** to verify pass.

### Task 7: Exportación

**Files:**
- Modify: `scripts/build_plugin.py`
- Test: `tests/test_plugin_export.py`

**Interfaces:**
- Produces: exported package includes new availability modules and smoke imports.

- [ ] **Step 1: Write failing test** `test_export_imports_availability_modules`.
- [ ] **Step 2: Run test** to verify failure.
- [ ] **Step 3: Implement** allowlist update.
- [ ] **Step 4: Run test** to verify pass.

### Task 8: Documentación y routing

**Files:**
- Modify: `AGENTS.md`
- Modify: `config/codex/routing.md`
- Modify: `skills/delegating-to-opencode/SKILL.md`

**Interfaces:**
- Produces: concise rule and procedure reference.

- [ ] **Step 1: Update** concise rule and procedure reference.
- [ ] **Step 2: Run** `uv run ruff check .` and `uv run mypy`.

---

## Self-Review

Spec coverage: version compatibility, state, refresh, policy, enforcement, updater, export and docs are mapped.

Type consistency: availability types are centralized in `availability_state.py`.

Review focus: each failure mode has a named test.

Proportion: plan defines decisions and signatures, not implementation bodies.

## Seguimiento: primera unidad aceptada

- Unidad de compatibilidad de registro y snapshot aceptada por revisión independiente.
- APIs reales: `CapabilitySnapshot` es pasivo; `read_snapshot`, `write_snapshot`, `update_snapshot`, `empty_snapshot`, `state_path` y `record_with_unknown_alias` en `availability_state.py`. Las siguientes tareas consumen estos contratos, sustituyendo los nombres provisionales `read_state`/`write_state_atomic`.
- La validación efectiva de capacidades del servicio corresponde a la tarea de refresh; no se acredita todavía por aceptar una versión diferente.
- Fuente de aceptación: `.aikit/availability-note001/implementation/phase1-review.json`, 35 pruebas acotadas y Ruff/formato/mypy correctos; snapshot y sesión acreditados por `review_evidence.py`.
- Aún faltan refresh, política, perfil de rendimiento, CLI/MCP/supervisor, exportación, routing y automatización.

## Seguimiento: segunda unidad aceptada

- Refresh, política y perfil de rendimiento puro aceptados tras la ronda 1 de correcciones. Implementación inicial en OpenCode, correcciones en respaldo nativo por rate limit y revisión independiente nuevamente en OpenCode.
- Evidencia: `.aikit/availability-note001/implementation/phase2-review-fix1.json`; snapshot y sesión validados por `review_evidence.py`. 696 pruebas, Ruff/formato y mypy acotado del revisor pasan; el implementador también ejecutó mypy global de 53 fuentes.
- Contratos reales para la integración: `coalesced_refresh`, `RefreshBinding`, `should_refresh`, `sort_candidates`, `eligible_for_attempt`, `record_outcome`; rendimiento con `aggregate_comparable` y deduplicación por identidad estable.
- `QueryAttempt.attempt_id`, `ModelEntry.outcome_attempt_ids` y `PricingTier.context_size` son campos opcionales compatibles con schema 1.
- El cooldown permanece optativo, desactivado por defecto. La evaluación diaria se alinea con las 09:00 de Madrid; el reset pasado requiere verificación.
- Aún faltan integración CLI/MCP/supervisor, comando actualizador, exportación, routing y activación programada. No instalado globalmente.

## Seguimiento: integración CLI/MCP/supervisor aceptada

- Unidad de integración aceptada el 2026-11-01 tras FIX ROUND1: `.aikit/availability-note001/implementation/phase3-review-fix1.json`. Los 26 hashes y la sesión independiente real fueron validados por `review_evidence.py`.
- CLI, MCP y supervisor usan catálogo por contexto y admisión acreditada; las ejecuciones sucesivas con tabla válida no consultan catálogo, integraciones, OpenAPI ni cuota. La ausencia o cambio acreditado de contexto permite un refresh coalescente.
- El supervisor registra outcomes y muestras tipadas acotadas con identidad estable; recuperar el mismo evento no duplica las muestras. Cuota/saldo confirmados, rate limit, autenticación, presupuesto de salida y fallos de tarea se distinguen.
- Nuevos comandos: `delegate.py availability status|refresh --cwd <proyecto> --json`. Status solo lee el registro del host configurado; refresh usa únicamente el servicio registrado ya encendido. No configura el host ni arranca OpenCode.
- La exportación incluye los módulos nuevos. Política distribuida `prefer_free: false` para Go de pago -> otros de pago -> gratuitos; un override explícito se respeta.
- Compuertas de revisión: 726 pruebas, Ruff check, formato de 100 archivos y mypy de 57 fuentes correctos. Pruebas con transporte falso y procesos propios en Windows; no se acredita aún funcionamiento con el servicio real ni ramas POSIX.
- Ruling: los campos de contexto que el brief daba por existentes no estaban implementados; se añadieron como opcionales schema 1. Se conserva metadata por proyecto y un pin de admisión cuya equivalencia no se invalida por una generación de otro proyecto. La firma usa solo contrato público saneado, nunca secretos ni hashes de credenciales.
- Aún pendientes: regla/procedimiento en routing y skill, validación real del actualizador y configuración del host, y automatización diaria de Codex. No instalado, sin push; la tarea 4 de binding sigue pausada.

## Seguimiento: instrucciones alineadas con la tabla local

- El usuario priorizó actualizar skill y routing antes de continuar la primera tabla real. Fuente alineada en `SKILL.md`, `references/carga-opencode.md`, plantilla `config/codex/routing.md`, `AGENTS.md`, README y guía de orquestación. No se creó una skill adicional ni se modificó Superpowers.
- Revisión independiente aceptada: `.aikit/availability-note001/instructions/review.json`; seis hashes y sesión real acreditados por `review_evidence.py`. Ocho escenarios operativos acotados registrados por el revisor; baseline del autor documental, no prueba exhaustiva de agentes/modelos.
- Prioridad adecuada en todos los niveles: Go de pago -> otros de pago -> todos los gratuitos -> respaldo nativo. Tabla primero, refresh por disparadores, sin consultas por rutina ni promesa de cuota a partir del catálogo. Reanudación solo donde backend y adaptador la soporten.
- Advertencia factual del informe sobre disponibilidad de skill-creator corregida en metadata, preservando el original; sin cambiar la entrega revisada.
- No instalado ni propagado al entorno global. Host configurado solo en el proceso del primer refresco real: creó generación 1, pero integraciones/catálogo/cuotas devolvieron unavailable. No es una tabla de modelos utilizable. Bootstrap pausado por prioridad explícita del usuario; no se ejecutaron inferencias para probar modelos.
- Pendientes: diagnóstico del refresco real, configuración persistente del host, despliegue y automatización de Codex. Sin push; tarea 4 de binding continúa pausada.

## Seguimiento: primer registro real compartido publicado

- Causa del primer refresco fallido confirmada con contrato real: el cliente enviaba `directory` en lugar de `location[directory]`; integraciones y cuota usan envolturas `{location,data}`. Corregidos cliente y parsers con fixtures equivalentes al contrato real.
- FIX ROUND1 añade validación de procedencia de cuota: ubicación absoluta y canónicamente equivalente al proyecto, o fuente no disponible conservando observación histórica. Revisión independiente aceptada en `.aikit/availability-note001/bootstrap/review-fix1.json`; cinco hashes y sesión acreditados por `review_evidence.py`. Evidencia original: 726 pruebas; corrección acotada: 27 pruebas, Ruff y mypy correctos. El RED acotado original fue de firma, no reproducción conductual; límite documentado por el revisor.
- Publicado el registro real en la ubicación de usuario acordada, generación 2, el 2026-11-01T08:00:18Z: 872 modelos de 8 proveedores con modelos en este contexto, 71 gratuitos y 801 de pago. Refresco sin errores y consulta `status` local correcta. Catálogo no acredita cuota: los 872 modelos mantienen cuota individual desconocida; Go solo tiene observación agregada experimental.
- Guardadas `AIKIT_STATE` y `AIKIT_OPENCODE_REGISTRATION` a nivel de usuario, sin credenciales. Los procesos ya abiertos no heredan retroactivamente variables nuevas. El complemento instalado no se ha actualizado.
- Informacionales diferidos: `config_sources` recoge 238 proveedores soportados, no 238 conectados; ayudante `_quote` sin uso. No se exportó estado privado a Git.
- La 001 SIGUE ABIERTA: actualización programada diaria y acceso desatendido pendientes. La documentación oficial advierte que las tareas programadas usan el sandbox por defecto; no se crea una automatización activa sin validar acceso al registro fuera del proyecto.
- Prioridad explícita del usuario: terminar 001; después retomar tarea 4 del binding (paquete portable y evidencia integrada), antes de notas 008/005 u otras ideas. Tarea 4 no autoriza instalación ni push.

## Seguimiento: gratuidad condicionada y fuentes públicas

- Ampliación aprobada el 2026-11-01: la futura actualización diaria debe contrastar información pública en fuentes oficiales de los proveedores conectados, además del estado local de OpenCode. Contrato actualizado en el diseño original; diseño y plan específicos en `2026-11-01-gratuidad-publica-opencode-*`.
- `free_candidate` conserva su significado de tarifa publicada cero. Los hechos públicos tipados se guardan aparte con condiciones, procedencia y fechas; no acreditan plan ni cuota personal. CLI/doctor/MCP exponen la distinción y `availability import` incorpora artefactos validados sin consultar la web durante la ejecución normal.
- Corregidas importación estricta, procedencia por dominios oficiales independientes y pruebas de clasificación. Revisión FIX1 aceptada: `.aikit/availability-note001/public-terms/review-fix1.json`; doce hashes y sesión acreditados mediante `review_evidence.py`. Evidencia actual: 18 pruebas del módulo y 44 de superficies afectadas/exportación, Ruff y mypy correctos. La suite completa anterior al FIX1 pasó 739 casos; no se afirma una nueva ejecución completa posterior.
- Incorporados al estado compartido tres hechos Cloudflare como acceso condicional mediante franquicia, generación 3; se conservan 872 modelos y cuota individual desconocida. Los 71 modelos de tarifa publicada cero del catálogo no representan todo el acceso posible mediante franquicias.
- Preparado el flujo diario para enumerar proveedores con modelos y contrastar sus fuentes oficiales, con diagnósticos para nuevas fuentes no verificadas. Las entradas públicas de Google, Kilo, NVIDIA, OpenRouter y Z.ai fueron consultadas; eso verifica recuperación de fuentes, no sus cuotas personales ni todas sus condiciones de gratuidad.
- Se reutilizan skill y exportador existentes; sin nueva skill, cambios de Superpowers, instalación ni push. La 001 continúa abierta hasta validar el acceso desatendido y configurar la automatización diaria de Codex. Después se retoma la tarea 4 del binding antes de nuevas notas.
