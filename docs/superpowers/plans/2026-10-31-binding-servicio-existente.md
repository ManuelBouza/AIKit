# Binding al servicio existente: plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Codex diseña y coordina; OpenCode ejecuta y revisa con el fallback autorizado.

**Goal:** ejecutar y controlar tareas propias sobre el servicio OpenCode ya encendido, sin autoarranque ni credenciales en los registros.

**Architecture:** fábrica de conexión autenticada e identidad verificable, registro de procedencia del host y supervisor existente. Un solo preflight y camino de envío para CLI/MCP. Ausencia, cambio de dueño o incertidumbre impiden nuevos envíos que dupliquen trabajo.

**Tech Stack:** Python >=3.10, biblioteca estándar, ctypes/Win32 para identidad y permisos, uv/pytest/Ruff/mypy; SDK MCP existente, sin runtime JavaScript nuevo.

**Spec:** `docs/superpowers/specs/2026-10-30-binding-servicio-existente-design.md`, aprobado el 31 de octubre de 2026.

## Restricciones globales

- Servicio existente; nunca `ensure`, `serve`, `--standalone`, start/restart/stop/upgrade o reconfiguración automática. Tampoco para consultar estado, catálogo o configuración.
- Solo loopback literal, puerto explícito válido y ruta raíz. Sin DNS, userinfo, query, fragmentos, redirects ni proxies en el endpoint base.
- Normal Basic auth de OpenCode; contraseña solo en RAM y entorno del hijo CLI. Nada en argv, manifiestos, logs, Git, artefactos o excepciones públicas.
- Prueba de propietario: registro estable, ID, PID, nacimiento real y versión; antes de cada request y tras respuesta. Primer adaptador Windows; otro SO sin prueba devuelve `process_identity_unavailable`.
- Token exacto: `aikit-owner-v1-` + SHA256 del array JSON compacto `[1, registration_id, canonical_url, pid, birth_filetime_decimal, version]`. FILETIME se serializa como cadena decimal; JSON usa `ensure_ascii=True`, separadores `,`/`:` y sin newline. Contraseña excluida.
- Nueva adquisición ante rotación; jamás adoptar otro servidor o repetir mutación. No prometer fencing, autoría criptográfica ni ejecución exactamente una vez.
- Reutilizar certificados, modelos y variantes actuales. Bloquear `openai` directo y subdelegación; `quota_resume` continúa pendiente de su propio contrato.
- Capacidad primero, Free adecuado antes de Go. Anunciar objetivo/modelo/esfuerzo/tarifa antes de cada inferencia; no probar permisos con modelos ni hacer consultas privadas que puedan recuperar claims.
- Control solo tras cotejar host/proyecto/sesión/rol/binding. Sesiones legadas privadas no se adoptan. Incierto conserva contexto y bloquea duplicación; sin intento vivo/incierto se permite fallback nativo.
- No modificar Superpowers ni interceptar agentes. No instalación, push ni escritura real de nuevo estado del perfil en este plan sin el alcance de instalación correspondiente; pruebas usan host temporal.

## Focos de revisión

1. Servicio desaparece entre descubrimiento y envío: error sin autoarranque ni otra inferencia (tareas 1 y 3).
2. Registro cambia de clave o conserva PID reutilizado: invalidación aunque la URL sea idéntica (tarea 1).
3. Caída entre escritura del host y proyecto: estado incierto, bytes previos intactos, sin reconstruir autoridad (tarea 2).
4. Respuesta perdida después de admisión: mismo intento, sin reenviar por CLI/MCP ni fallback paralelo (tarea 3).
5. Paquete limpio omite dependencia o filtra registros: smoke test de exportación sin perfil/modelos (tarea 4).

## Mapa de archivos e interfaces

En `skills/delegating-to-opencode/scripts/` crear:

- `service_identity.py`: `HostContext`, lectura acotada del registro oficial, rutas/permisos, nacimiento y token.
- `service_connection.py`: `ManagedBinding` que implementa `session_backend.TrustedBinding`, HTTP autenticado sin descubrimiento implícito y entorno del hijo.
- `host_registry.py`: procedencia validada/atómica/bloqueada, separada de datos del proyecto.
- `bound_execution.py`: reserva y ejecución sobre el supervisor; recuperación local de resultado sin otro envío.

`delegate.py` conserva selección/certificado y produce la preparación ligada; no crear otro parser de políticas. `session_worker.py` incorpora procedencia y credenciales solo dentro del supervisor. `session_backend.py` conserva su algoritmo y recibe el binding real validado; no duplicar asentamiento/ACK.

Tipos nuevos compartidos:

- `HostContext(opencode_registration: Path, aikit_state: Path, expected_version: str)`, resuelto una vez desde configuración confiable del host/canal; nunca desde JSON o prompts de tarea. Canal 2.2.0 acreditado; variantes de canal/versión no acreditadas fallan sin arrancar.
- `ServiceRegistration`: ID, URL canónica, PID, versión y credencial privada con `repr`/serialización redaccionados. Máximo 64 KiB y profundidad 8.
- `ProcessBirth`: PID, FILETIME bruto y `started_at` UTC derivado de él; nunca datetime.now como nacimiento.
- `BoundLaunch`: argv sin credenciales, binding, cwd, tarea, modelo, variante, motivo, rol, agente y timeout. Solo en memoria; argv (puede contener el prompt), texto y binding excluidos de repr/serialización de metadatos.
- `HostAttempt`: esquema 1 con los campos de la especificación y `agent: build|plan`, separado de `role: implementer|reviewer`. No inferir rol a partir del agente.
- `ServiceError` y `RegistryError`: códigos estables/mensajes fijos sin cuerpo remoto ni registro del usuario.

## Tarea 1: descubrimiento e identidad y conexión real sin arranque

**Archivos:** crear `service_identity.py`, `service_connection.py`, `tests/test_service_identity.py` y `tests/test_service_connection.py`; añadir módulos a `pyproject.toml:mypy.files`.

**Interfaces:** `resolve_host_context() -> HostContext` en `service_identity.py` lee solo configuración confiable del host; `discover_existing(context: HostContext, *, timeout: float = 10.0) -> ManagedBinding` en `service_connection.py`. `ManagedBinding.expected_owner`, `operations`, `verify_owner(timeout=...)` y `request(operation, session_id=..., timeout=..., resume=...)` respetan el protocolo existente. Métodos adicionales `config_sources(project: Path, *, timeout: float) -> object`, `model_catalog(project: Path, *, timeout: float) -> object` y `child_environment(base: Mapping[str, str]) -> dict[str, str]`; `close() -> None` invalida la instancia.

- [ ] Escribir tests rojos con registro temporal y servidor HTTP falso: ausencia no llama Popen, URL con DNS/redirect/proxy/userinfo/ruta extra/URI sin `//` rechazada antes de enviar; 401 no reintenta ni publica cuerpo. Comprobar límites de tamaño, profundidad, Unicode y enteros extremos.
- [ ] Añadir pruebas de registro/clave/version rotados durante GET, PID igual con FILETIME distinto, nacimiento desconocido, token determinista, credencial excluida y `close` sin reutilización. Preflight y requests no alteran el entorno padre.
- [ ] Ejecutar `uv run pytest tests/test_service_identity.py tests/test_service_connection.py -q`; registrar fallo esperado por interfaces ausentes.
- [ ] Implementar ruta oficial del registro según fuente 2.2.0 y contexto confiable; rechazar enlaces/reparse y entradas de origen no acreditado. En Windows comprobar propietario y permisos con API de seguridad del SO: no aceptar modificaciones por identidades ajenas a usuario/SYSTEM/Administradores. No reparar ACL ni pedir privilegios de depuración; si no se acredita, devolver `registration_untrusted`. Para el nuevo estado del host las ACL también impiden lectura ajena no autorizada. Registrar qué comprobación se ejecuta, no tratar chmod POSIX como prueba de ACL Windows.
- [ ] Implementar OpenProcess con consulta limitada, GetProcessTimes y cierre de handles; usar FILETIME en token y UTC en OwnerIdentity. HTTP con ProxyHandler vacío, redirects rechazados y autenticación normal; presupuesto monotónico total 10 s para adquisición y restante por petición. Limitar body a 8 MiB/profundidad 128 y traducir errores de parsing sin mostrarlo.
- [ ] Implementar mapeo cerrado de operaciones v2.2.0, incluido `config.get`/`GET /api/config` y `GET /api/model` con `location[directory]` explícito. No construir paths desde datos de registro de tarea. No añadir modelo/permisos mutadores ni consumidor de logs.
- [ ] Pasar tests, Ruff y mypy de los cambios; revisor nuevo independiente antes de commit `feat: conectar al servicio existente sin autoarranque`.

## Seguimiento de revisión independiente (Tarea 1)

- Revisión final: `.aikit/binding-task1/review-final.json`, verdict `accepted`.
- Checks finales: `uv run pytest` 554 passed; `uv run ruff check .` OK;
  `uv run ruff format --check .` OK; `uv run mypy` OK.
- Evidencia: ACL real con `icacls` sobre archivo temporal propio; deadline total
  verificado para cabeceras y cuerpo lentos (0,503 s para 0,5 s); verify_owner
  antes y después; representación sin credencial.
- Desvío histórico TDD: no hay evidencia independiente del ciclo rojo inicial;
  las garantías se acreditan por la suite verde actual y sondas propias.
- No se acreditan tareas 2-4 ni integración real con servicio.

## Tarea 2: procedencia del host y supervisor ligado

**Archivos:** crear `host_registry.py`, `tests/test_host_registry.py` y `tests/test_bound_worker.py`; modificar `session_worker.py`. Reutilizar `session_store.py` sin cambiar su esquema salvo necesidad documentada.

**Interfaces:** `load_host_task(context: HostContext, task_id: str) -> HostTask`; `reserve_host_attempt(context: HostContext, record: TaskRecord, *, agent: str) -> HostAttempt`; `record_host_session(context: HostContext, record: TaskRecord, session_id: str) -> None`; `verify_provenance(context: HostContext, record: TaskRecord) -> HostAttempt`. `HostTask` contiene esquema 1, UUID de tarea/intento actual, raíz canónica, rol e historial de `HostAttempt`.

- [ ] Escribir pruebas rojas de dos procesos reservando un intento, host ausente/corrupto/futuro, ID o raíz desplazados, rol/binding/sesión discrepantes, symlink/reparse y datos JSON de tipos erróneos. Afirmar que no se repara el host desde el proyecto ni se elimina incertidumbre por antigüedad.
- [ ] Añadir pruebas de caída/fallo en cada frontera: host reservado → proyecto, cliente arrancado → sesión, host con sesión → proyecto. Bytes anteriores se conservan; captura de resultado no causa otra inferencia. Registro nunca contiene contraseña, prompt ni conversación.
- [ ] Ejecutar `uv run pytest tests/test_host_registry.py tests/test_bound_worker.py -q`; confirmar rojo.
- [ ] Implementar bloqueos de SO por tarea y reemplazo atómico en mismo directorio dentro de `<aikit_state>/tasks/`. Canonicalizar raíz con Path.resolve validado y normcase en Windows. Reutilizar validadores y garantías del almacén en vez de otra política de rutas.
- [ ] Integrar orden del diseño: host antes de proyecto y antes de envío; sesión observada primero host y luego proyecto. No prometer transacción entre volúmenes. Cualquier escritura fallida deja intento incierto y salida recuperable; no borra reservas.
- [ ] El supervisor independiente vuelve a adquirir el mismo token desde el registro oficial; la clave no se transmite por manifiesto/argv. Compara procedencia, revalida configuración antes del envío y construye `--server` explícito con env del hijo. Identidades de cliente/supervisor se acreditan con el mismo módulo SO o quedan desconocidas. Callback de interrupción cierra sobre binding validado y procedencia, reutilizando `interrupt_session`.
- [ ] Mantener seams de procesos falsos solo desde código de tests, sin flags/env de bypass. Probar que el padre puede terminar y que otro cliente puede consultar la procedencia ya publicada, sin adoptar un servidor reiniciado ni una sesión ajena.
- [ ] Pasar pruebas afectadas, revisar independientemente y commit `feat: registrar procedencia del host para sesiones propias`.

## Seguimiento de revisión independiente (Tarea 2)

- Revisión final: `.aikit/binding-task2/review.json`, verdict `accepted`.
- Checks finales: `uv run pytest` 591 passed; `uv run ruff check .` OK;
  `uv run ruff format --check .` OK; `uv run mypy` OK.
- Evidencia: host privado con bloqueo SO, escritura atómica y validación estricta.
- No se acreditan tareas 3-4 ni integración real con servicio.

## Tarea 3: preflight común y envío CLI/MCP sobre el supervisor

**Archivos:** crear `bound_execution.py`, `tests/test_bound_execution.py` y `tests/test_bound_cli_mcp.py`; modificar `delegate.py`, `session_worker.py`, `mcp_server.py`, `tests/fakes.py` y pruebas de CLI/catálogo/ejecución afectadas. Actualizar también `scripts/build_plugin.py` y su smoke de exportación cuando las nuevas dependencias pasen a ser imports del camino público. No alterar el algoritmo del parser `restrictions.py`.

**Interfaces:** `_prepare_run(cwd: Path | str, task_loader: Callable[[], str], model: str | None, variant: str | None, reason: str | None, agent: str, timeout: float, *, role: Role = "implementer", context: HostContext | None = None) -> BoundLaunch` reutiliza validadores de `delegate.py` en orden del diseño; es interno y se actualizan sus consumidores actuales del tuple. `bound_execution.execute_bound(prepared: BoundLaunch, *, context: HostContext) -> dict[str, Any]` crea/reserva tarea y utiliza el supervisor, sin un segundo bucle de inferencia. `recover_local_result(context: HostContext, record: TaskRecord) -> dict[str, Any]` no envía prompts. La dataclass `BoundLaunch` vive en `service_connection.py` para evitar imports circulares con la entrada CLI ejecutada como `__main__`.

- [ ] Escribir pruebas rojas: certificado inválido corta antes de catálogo/envío; configuración y catálogo comparten binding/proyecto; fallo/reinicio entre checks y envío no llama modelo ni ensure. Instrumentar subprocess para que cualquier `serve`, descubrimiento implícito o `--standalone` falle el test.
- [ ] Añadir compatibilidad: argumentos literales, variantes publicadas, errores sin secretos, `plan` y `build` preservados; API CLI/MCP comparte camino y restricciones. Agregar `role` opcional explícito (`implementer` por defecto) para procedencia; no convertir `--agent plan` automáticamente en rol reviewer. La interfaz de sesiones pública completa sigue perteneciendo al plan original.
- [ ] Añadir pruebas de respuesta perdida tras envío, caída de cliente con supervisor vivo, EOF sin terminal, resultado terminado recuperable y estado incierto que no produce otro intento por fallback. Afirmar que el servicio compartido nunca se termina, incluso al parar el cliente propio.
- [ ] Ejecutar `uv run pytest tests/test_bound_execution.py tests/test_bound_cli_mcp.py -q` y verificar rojo previo.
- [ ] Migrar las consultas a binding existente. Para envío: config.get → certificado → catálogo → selección → reserva → comprobación fresca → envío. `doctor` sigue siendo consulta sin certificado obligatorio, como hoy: verifica conexión/identidad, consulta catálogo del proyecto y filtra proveedor directo OpenAI, sin enviar prompts. Probar explícitamente doctor en proyecto sin políticas y rechazo del envío equivalente. No ejecutar CONFIG_CHECK_ARGS privado; conservar el validador de fuentes efectivas, sin certificar desde opencode.json aislado. Servicio apagado devuelve `service_unavailable` y el coordinador decide fallback sin arrancarlo.
- [ ] Mantener firmas públicas existentes; añadir `role` como keyword opcional en funciones y campo opcional en CLI/MCP. Añadir seguimiento task_id/attempt_id sin retirar campos de éxito. Una espera agotada o posible admisión devuelve `pending/uncertain`, nunca éxito ni cancelación por haber terminado el cliente. El wrapper síncrono espera el límite existente; MCP limita espera a 45 s y devuelve seguimiento. No implementar todavía resume/adopción ni reenvío de admisiones.
- [ ] Congelar fuentes, pasar suite y controles; revisión independiente y commit `feat: unificar delegacion ligada para CLI y MCP`.

## Seguimiento de revisión independiente (Tarea 3)

- Revisión final: `.aikit/binding-task3/review-final.json`, verdict `accepted`.
- Checks finales: `uv run pytest` 629 passed; `uv run ruff check .` OK;
  `uv run ruff format --check .` OK; `uv run mypy` OK.
- Hallazgo anterior ADDRESSED: hueco transitorio ReplaceFileW corregido con
  FileRenameInfoEx por handle.
- No se acreditan tareas 4 ni integración real con servicio.

## Tarea 4: paquete portable y evidencia integrada

**Archivos:** modificar `scripts/build_plugin.py`, `tests/test_plugin_export.py`, `README.md`, `docs/sesiones-opencode.md`, skill/referencias pertinentes, `pyproject.toml`, `uv.lock`, `plugin.json` y plan de sesiones original para ajustar dependencias ya cubiertas. Evidencia privada en `.aikit/validation-managed-binding/`.

- [ ] Ampliar la prueba de exportación limpia que acompaña los imports de tarea 3: CLI sin modelos e importación MCP; todas las dependencias presentes; ningún `.aikit`, perfil, registro o credencial exportado. Comprobar cero arranques cuando falta servicio y cero acceso al perfil real al inyectar host temporal.
- [ ] Ejecutar `uv run pytest tests/test_plugin_export.py -q`. Si una garantía nueva falla, registrar rojo y corregir antes de continuar; si ya pasa, conservar esa evidencia sin fabricar una regresión. Revisar lista permitida, tipos y documentación. Versión coherente `0.2.0` en manifiestos/proyecto/lock, sin duplicar migración cuando se retome el plan original.
- [ ] Con fuentes congeladas, ejecutar `uv sync --locked`, `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`. Entorno conocido: suite pytest requiere escalación acotada por socketpair local de asyncio/AnyIO; no repetir atasco normal. Una sola suite viva, UV_CACHE_DIR local por proceso permitido.
- [ ] Ejecutar escenario integral con servicio falso local: registro estable/rotado, dos lanzadores, desconexión de cliente, recuperación de resultado y detención del cliente propio sin afectar otro trabajo. Comprobar que el proceso de servicio permanece vivo.
- [ ] Si hay servicio real ya encendido y configuración segura: seleccionar un Free suficiente y anunciar objetivo/modelo/esfuerzo/tarifa; crear una tarea mínima propia, registrar procedencia y verificar observación/cierre en su dueño real. Usar `HostContext` de prueba con estado temporal fuera del proyecto, sin inicializar el perfil instalado; conservarlo si el intento queda incierto. No usar sesiones históricas o trabajos del usuario. Ante cuota/rechazo revisar sesión y parciales antes de reselect; no testear todos los modelos a ciegas.
- [ ] Revisor independiente valida snapshot y entrega `review.json` con comandos/códigos reales. Codex valida metadata usando `scripts/review_evidence.py`, sin repetir revisión técnica. Documentar Windows probado y capacidades no acreditadas; no afirmar control real por tests falsos.
- [ ] Commit `feat: empaquetar binding verificado al servicio existente`. No instalar ni hacer push. Si la prueba real no puede ejecutarse, publicar únicamente el límite observado en el informe, sin marcarla pasada.

## Relación con el plan de sesiones y autorrevisión

Este plan implementa la puerta surgida en etapa 3. La etapa 4 original depende de
su aceptación; la etapa 5 reutilizará wrappers, role, espera y empaquetado aquí
resueltos, sin crear caminos alternativos. La excepción OpenAI y lector de
admisiones/inbox continúan en sus contratos pendientes. No se reimplementan las
etapas 1–3 ya aceptadas ni se repiten sus pruebas salvo regresiones afectadas.

Cobertura revisada: descubrimiento/auth/identidad y URLs (tarea 1); host separado,
doble escritura, roles y procedencia (2); preflight/camino único/incertidumbre (3);
portabilidad y prueba real (4). Los cinco focos tienen pruebas asignadas. Se
conservan nombres del protocolo existente y se actualiza la devolución interna
de `_prepare_run` explícitamente; el ejecutor no debe adivinar otra interfaz.

Método preservado: ejecución técnica en OpenCode con modelo/esfuerzo adecuados,
Free primero cuando suficiente; revisión independiente y correcciones en contexto
del implementador. Codex conserva arquitectura. Pendiente de revisión del usuario
antes de ejecutar; el plan no autoriza despliegue, servicios ni cambios de cuenta.
