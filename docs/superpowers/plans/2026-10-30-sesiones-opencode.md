# Seguimiento y recuperación de sesiones OpenCode: plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. En AIKit, el ejecutor técnico es OpenCode y Codex conserva diseño y coordinación.

**Goal:** conservar sesión y resultados, observar actividad y continuar trabajo incompleto sin duplicar inferencias ni efectos conocidos.

**Architecture:** ampliar el núcleo compartido CLI/MCP con registro persistente y supervisor local. Separar espera del cliente, ejecución y entrega. Consultar/controlar únicamente el servidor identificado; capacidades desconocidas se devuelven como limitaciones, nunca como permiso para repetir trabajo.

**Tech Stack:** Python >=3.10 tipado, biblioteca estándar para CLI, SDK MCP existente, uv, pytest, Ruff y mypy. Windows y rutas portables; sin nuevas dependencias de ejecución.

**Spec:** `docs/superpowers/specs/2026-10-30-sesiones-opencode-design.md`, aprobado el 30 de octubre de 2026.

## Restricciones globales

- Codex conserva diseño, contratos, plan y selección de modelo. OpenCode implementa, prueba y revisa; workers no redelegan.
- Capacidad primero: Free adecuado, Go, otras alternativas adecuadas, Codex si falta disponibilidad/capacidad. Bloquear proveedor directo `openai` salvo recuperación de sesión existente por cuota agotada: en ese caso OpenAI adecuado dentro de OpenCode precede al retorno nativo, para conservar contexto.
- Anunciar objetivo, modelo, variante publicada o predeterminada y tarifa antes de cada inferencia, incluso continuación. No inferir para probar permisos.
- Implementador conserva sesión; revisor independiente usa otra. No interceptar subagentes ni alterar Superpowers; ampliar la skill existente.
- No usar `--auto`, `--continue`, sesiones inexistentes como continuación, ni terminación global de procesos.
- Un cliente terminado, silencio, archivos escritos o consulta al servidor equivocado no prueban entrega terminada.
- Sin identidad/estado suficiente: observar y reconciliar; no reenviar ni retornar a ejecución nativa paralela.
- Todas las evidencias locales quedan en `.aikit/`; no exportar credenciales, configuración completa ni conversaciones. Sin instalación ni push en este plan.

## Focos de revisión

1. Registro corrupto o versión futura: no inferir ni matar procesos; errores explícitos (tareas 1 y 4).
2. PID reutilizado o servidor reiniciado: invalidar propiedad anterior (tareas 1 y 3).
3. Cliente cancelado, supervisor vivo: recuperar resultado sin reiniciar (tareas 2 y 5).
4. Prompt aceptado con respuesta perdida: reconciliar antes de otro envío (tareas 3 y 4).
5. Sesión manipulada desde otro cliente: comprobar estado actual y no confiar solo en bloqueo local (tareas 3 y 4).

## Archivos y responsabilidades

En `skills/delegating-to-opencode/scripts/`, crear:

- `session_store.py`: tipos, registro atómico, confinamiento y bloqueo entre procesos.
- `session_worker.py`: supervisor de la CLI, lectura incremental y plazos.
- `session_backend.py`: consultas/control API verificados y capacidades disponibles.
- `session_service.py`: operaciones de tarea y reconciliación; sin selección automática de modelo.

`delegate.py` conserva catálogo, política y entrada CLI; `mcp_server.py` expone el mismo servicio. No copiar las restricciones a una segunda implementación.
Crear pruebas por responsabilidad: `tests/test_session_store.py`, `test_session_worker.py`, `test_session_backend.py`, `test_session_service.py` y `test_session_cli_mcp.py`.
Ampliar los falsos existentes sin invalidar sus comprobaciones de argumentos o secretos.

## Contrato entre módulos

`session_store.py` define dataclasses y un `TypedDict` público:

- `TaskRecord`: versión 1, IDs UUID, rol `implementer|reviewer`, cwd canónico, selección de modelo/motivo/tarifa, sesión opcional, identidad de servidor opcional, identidad cliente/supervisor opcional, plazos, observaciones fechadas y cursor opcional. Un PID siempre va unido a identidad de arranque comprobable. Una recuperación OpenAI registra autorización de alcance `quota_resume`, evidencia sanitizada del agotamiento, modelo anterior y nuevo, y motivo de no usar alternativas adecuadas; no guarda tokens de autenticación.
- `ExecutionObservation`: estado `active|waiting|retrying|idle|unknown`, fuente y fecha. `waiting` incluye motivo permiso/entrada cuando consta.
- `DeliveryObservation`: estado `pending|partial|completed|failed|interrupted`, fuente y fecha.
- `TaskReply`: `status: ok|pending|error`, `task_id`, `attempt_id`, sesión opcional, observaciones, capacidades, limitaciones y código opcional. Solo `completed` acreditado produce entrega satisfactoria.
- `StoreError`: excepción tipada con código estable y mensaje sin datos sensibles.

`session_backend.py` define `BackendCapabilities`, `SessionInspection` y `InterruptOutcome` tipados. Incluyen identidad del servidor observada, sesión/directorio, actividad, entrada pendiente, cursor/evidencia terminal y limitaciones. Ninguna API inventada se convierte en capacidad disponible.

Funciones del almacén: `load_task(root: Path, task_id: str) -> TaskRecord`, `save_task(root: Path, record: TaskRecord) -> None`, `lock_task(root: Path, task_id: str) -> ContextManager[None]` y `lock_session(root: Path, session_id: str) -> ContextManager[None]`.
Las rutas se derivan de identificadores validados, nunca de rutas incluidas en un JSON no fiable.

## Tarea 1: registro persistente y exclusión

**Archivos:** crear `session_store.py` y `tests/test_session_store.py`; modificar la lista `files` de mypy en `pyproject.toml`.

**Interfaces:** produce los tipos y funciones anteriores. Registro en `<cwd>/.aikit/sessions/<task_id>/record.json`; intento actual y anteriores se conservan por ID.

- [x] Escribir pruebas: ida/vuelta preserva selección e IDs; `session=None` es válido al arrancar; versión futura/corrupción falla sin sobrescribir; caída antes de reemplazo conserva JSON anterior; traversal, enlaces y rutas Windows absolutas se rechazan.
- [x] Añadir prueba con dos procesos reales sin inferencia: solo uno adquiere el bloqueo; tras salir el propietario se libera; un PID vivo diferente no acredita propiedad por número solamente.
- [x] Ejecutar `uv run pytest tests/test_session_store.py -q`; comprobar fallos por la capacidad ausente.
- [x] Implementar escritura temporal en el mismo directorio y reemplazo atómico, bloqueos del sistema operativo (`msvcrt`/`fcntl`) y validación de esquema/identidad. No borrar registros ni recuperar bloqueos por antigüedad.
- [x] Repetir el comando: todas las pruebas pasan; ejecutar Ruff y mypy sobre los archivos afectados.
- [x] Revisión independiente y commit `feat: registrar tareas y sesiones de OpenCode`.

## Tarea 2: supervisor y resultados parciales recuperables

**Archivos:** crear `session_worker.py`, `tests/test_session_worker.py`; modificar `delegate.py`, `tests/fakes.py`, `tests/test_policy_process.py` y `tests/test_execution.py`.

**Interfaces:** `session_worker.supervise(root: Path, task_id: str) -> int`; `session_service` consumirá después `launch_worker(root: Path, task_id: str) -> TaskRecord`. Para interrupción, el worker recibe un callback `Callable[[TaskRecord], bool | None]`: confirmado, no confirmado o no disponible. Hasta tarea 3, el callback real devuelve `None`; los tests inyectan el falso. El módulo worker tendrá entrada privada por `python -m` o ruta resuelta desde la instalación, sin depender del checkout.

- [x] Escribir pruebas con ejecutable Python falso: emite sesión antes de acabar, emite salida fragmentada, llena stderr, excede el tamaño de una línea, termina con error y produce JSON inválido. Comprobar captura temprana sin deadlock ni crecimiento ilimitado.
- [x] Añadir pruebas: se desconecta el cliente y el supervisor conserva progreso; falla el guardado final y stdout sigue devolviendo resultado; espera agotada no mata; salida cliente cero sin terminal no se declara completada.
- [x] Ejecutar `uv run pytest tests/test_session_worker.py tests/test_policy_process.py tests/test_execution.py -q`; comprobar los fallos nuevos antes de cambiar código.
- [x] Implementar lectura concurrente de stdout/stderr, captura incremental del ID y diario de metadatos. Limitar línea a 1 MiB, cola de diagnóstico en memoria a 64 KiB y salida parcial persistida a 1 MiB por flujo; marcar truncamiento sin ocultarlo ni publicar texto crudo en errores.
- [x] Crear supervisor independiente del tiempo de vida del cliente. Windows: proceso sin ventana visible y handles no heredados innecesarios; POSIX: sesión propia. No registrar credenciales ni prompt en el manifiesto del supervisor. Persistir identidad comprobable o marcarla desconocida.
- [x] El límite de ejecución permanece finito (máximo 3600 s); la espera del cliente será independiente. Al límite, pedir interrupción mediante la interfaz de tarea 3 y esperar hasta 10 s. Sin capacidad o confirmación, registrar estado desconocido; no afirmar cancelación. No habilitar terminación forzada automática.
- [x] Pasar las pruebas nuevas y existentes; revisar independientemente y commit `feat: conservar progreso y resultados del worker OpenCode`.

## Tarea 3: verificar e integrar capacidades del servidor propietario

**Archivos:** crear `session_backend.py`, `tests/test_session_backend.py` y `docs/sesiones-opencode.md`.

**Interfaces:** `inspect_session(record: TaskRecord) -> SessionInspection` y `interrupt_session(record: TaskRecord) -> InterruptOutcome`; consultas acotadas a 10 s. No hacen inferencia.

- [ ] Preflight factual sin inferencia: registrar versión, ayuda y operaciones API instaladas. Investigar cómo identificar el servidor privado de `--standalone` y si sobrevive a su cliente. Filtrar campos; no volcar configuración/transcripciones.
- [ ] Documentar operaciones, argumentos y respuestas reales de sesión existente, actividad, entrada pendiente, eventos e interrupción. Contrastar Context7 con versión instalada; no reutilizar endpoints v1.
- [ ] Verificar sin inferencia soporte de cambio de modelo en la misma sesión y política efectiva para la excepción `quota_resume`. Un `deny` vigente no se ignora ni se retira globalmente. Si no existe mecanismo suficientemente acotado, registrar la limitación y devolver esa decisión al coordinador antes de habilitar OpenAI.
- [ ] Puerta de diseño: si no se puede identificar/controlar `--standalone`, registrar `control_unavailable`. Implementar observación local y limitaciones; presentar al coordinador la necesidad de otro contrato antes de crear un servidor dedicado. No cambiar silenciosamente de transporte ni usar el servidor habitual como sustituto.
- [ ] Escribir pruebas con respuestas sanitizadas: servidor equivocado/reiniciado, sesión inexistente, directorio distinto, permisos pendientes, reintento, evento terminal antiguo seguido de actividad, cursor duplicado, timeout y respuesta malformada. Todos deben impedir conclusiones falsas o mutaciones inciertas.
- [ ] Ejecutar `uv run pytest tests/test_session_backend.py -q` y comprobar fallo previo.
- [ ] Implementar el adaptador solo con operaciones verificadas y conectar el callback de tarea 2 a `interrupt_session`. Identidad externa desconocida implica observación limitada; no admitir URLs arbitrarias procedentes de registros manipulados. Mantener loopback y autenticación normal, sin exponerla en JSON.
- [ ] Pasar pruebas; revisión independiente y commit `feat: observar el servidor propietario de una sesion`.

## Tarea 4: recuperación, continuación y detención

**Archivos:** crear `session_service.py`, `tests/test_session_service.py`; modificar `delegate.py`, `restrictions.py`, `tests/test_selection.py` y pruebas de restricciones afectadas para la excepción acotada.

**Interfaces:** `start_task(cwd: Path, task: str, model: str, reason: str, *, role: str, execution_timeout: float) -> TaskReply`; `task_status(cwd: Path, task_id: str) -> TaskReply`; `task_result(cwd: Path, task_id: str) -> TaskReply`; `resume_task(cwd: Path, task_id: str, task: str, model: str, reason: str) -> TaskReply`; `interrupt_task(cwd: Path, task_id: str) -> TaskReply`; `stop_task(cwd: Path, task_id: str, *, force: bool) -> TaskReply`.

- [ ] Escribir pruebas tabuladas: entrega terminada devuelve resultado sin nueva ejecución; activa observa; incompleta inactiva comprobada conserva sesión y crea intento; sesión desconocida/no existente, rol o cwd incorrectos rechazan continuación antes de enviar. No pasar `--continue` ni crear sesión porque el ID no existe.
- [ ] Añadir pruebas de dos clientes simultáneos y un cliente externo: reconciliar bajo bloqueo y no emitir segundo prompt ante admisión de resultado incierto. Conservar identidad de envío para consultar si fue aceptado; usar idempotencia API solo si fue verificada, no asumir que la CLI la tiene.
- [ ] Añadir pruebas de interrupción confirmada/no confirmada; force sin flag, PID reutilizado, propietario incierto, supervisor ajeno o servidor compartido nunca llama a kill. Con propiedad válida, terminar solo cliente/supervisor propios; comprobar después la ejecución por separado.
- [ ] Ejecutar `uv run pytest tests/test_session_service.py -q`; verificar fallo previo.
- [ ] Implementar reconciliación: comprobación de existencia/directorio/rol y estado del propietario, entradas pendientes y cambios parciales declarados por el coordinador. Si falta evidencia, devolver `pending` con limitación sin nuevo prompt. Una continuación requiere trabajo adicional explícito; el revisor no continúa sesión de autor.
- [ ] Revalidar catálogo, motivo y restricciones antes de cada envío usando el núcleo existente. Cambiar modelo exige selección explícita; no cambiarlo automáticamente para continuar.
- [ ] Escribir y comprobar en rojo pruebas de `quota_resume`: `openai` rechazado para inicio nuevo, tarea/rol/cwd distinto, error no relacionado con cuota, sesión activa/desconocida y política efectiva denegada. Solo permitir misma sesión inactiva con cuota acreditada, selección OpenAI adecuada explícita y permisos efectivos válidos. No confiar únicamente en un booleano aportado por el cliente.
- [ ] Implementar la excepción del contrato, conservando bloqueo por defecto y verificando capacidad/contexto del nuevo modelo. Permitir consultar metadatos OpenAI para esta selección acotada sin presentarlos como autorizados para tareas nuevas. Probar recuperación sin ejecutar modelos reales de pago por defecto.
- [ ] Pasar pruebas, revisión independiente y commit `feat: recuperar y continuar tareas sin duplicar envios`.

## Tarea 5: superficie CLI/MCP y distribución coherente

**Archivos:** modificar `delegate.py`, `mcp_server.py`, `scripts/build_plugin.py`, `pyproject.toml`, `uv.lock`, `plugin.json`, `README.md`, `AGENTS.md`, la skill y sus referencias pertinentes. El catálogo `.agents/plugins/marketplace.json` es salida generada por el exportador, no archivo fuente. Añadir `tests/test_session_cli_mcp.py`; ampliar `tests/test_plugin_export.py` y pruebas MCP existentes.

**Interfaces:** CLI añade `start`, `status`, `result`, `resume`, `interrupt`, `stop`; `stop --force` es explícito. MCP añade `opencode_task_start`, `opencode_task_status`, `opencode_task_result`, `opencode_task_resume`, `opencode_task_interrupt`, `opencode_task_stop`, con los mismos argumentos y resultados de tarea 4.

- [ ] Escribir pruebas de paridad CLI/MCP, validación previa, campos desconocidos, errores sin secretos y exportación de todos los módulos nuevos desde un directorio limpio.
- [ ] Añadir prueba de cancelación MCP: el cliente deja de esperar, supervisor sigue identificado, `result` recupera sin otra inferencia. `pending` no se trata como error que autoriza reintento.
- [ ] Ejecutar `uv run pytest tests/test_session_cli_mcp.py tests/test_plugin_export.py tests/test_mcp_async.py tests/test_mcp_stdio.py -q`; comprobar fallos nuevos.
- [ ] Implementar las entradas. `start` devuelve IDs antes de esperar trabajo largo; `status`/`result` son consultas breves. `run` y `opencode_delegate` conservan argumentos actuales como envoltorios de inicio/espera; éxito conserva campos existentes y añade seguimiento. Al agotarse solo espera, devuelven `status: pending`, no éxito ni cancelación.
- [ ] Separar `--wait-timeout` del existente `--timeout` (límite de ejecución). En CLI, espera predeterminada igual al límite existente; MCP limita espera a 45 s para devolver seguimiento antes del límite habitual del cliente. No prometer deadlines si desaparece el supervisor.
- [ ] Documentar el cambio de semántica y actualizar versión a `0.2.0` en los metadatos existentes, con lock coherente. Incluir módulos/documentación en lista permitida; no exportar `.aikit` ni instalar.
- [ ] Pasar pruebas; revisión independiente y commit `feat: exponer seguimiento de sesiones en CLI y MCP`.

## Tarea 6: validación integrada y revisión final

**Archivos:** ampliar `docs/sesiones-opencode.md`; evidencias privadas en `.aikit/validation-sessions/`. Sin cambios al perfil del usuario.

- [ ] Ejecutar en OpenCode: `uv sync --locked`, `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`. Registrar comandos, cwd y códigos reales; ningún test normal llama a modelos.
- [ ] Ejecutar caso local con falso backend en proceso separado: desconexión de cliente, recuperación, interrupción y continuación; comprobar IDs, contadores de envío y efecto único.
- [ ] Solo si tarea 3 acredita capacidades: seleccionar catálogo actual y anunciar modelo/esfuerzo/tarifa para una prueba real mínima. Pedir que guarde un marcador antes de un paso observable; interrumpir esa sesión y continuarla cuando conste inactiva. Comprobar mismo ID/contexto y que no repite el marcador; no usar sesiones históricas del usuario ni forzar procesos compartidos.
- [ ] Si capacidad no disponible o respuesta incierta, conservar evidencia/IDs y declarar la limitación; no repetir inferencia ni afirmar recuperación real probada. Volver a diseño solo para esa capacidad pendiente.
- [ ] Revisor nuevo independiente examina snapshot final, ejecuta comprobaciones necesarias y emite `review.json`. Codex valida metadata con `scripts/review_evidence.py`; no repite revisión técnica. Corregir en la sesión del implementador cuando ya sea seguro usar continuación.
- [ ] Documentar resultados observados y límites, incluido reinicio del supervisor, compactación del contexto y efectos externos ambiguos. Commit `docs: registrar validacion de sesiones OpenCode`.

## Autorrevisión del plan

El registro y exclusión cubren identidad/persistencia (tarea 1); supervisor cubre
captura temprana, parciales y plazos (2); backend cubre propiedad y capacidades
reales (3); servicio cubre las cinco operaciones y roles (4); CLI/MCP y paquete
comparten contrato (5); revisión y prueba mínima cubren aceptación (6).
No se ha afirmado que la API privada sea controlable. La puerta de tarea 3 evita
convertir una limitación conocida en una implementación basada en supuestos.

## Entrega para ejecución

Método conservado del proyecto: implementador OpenCode por etapas dependientes,
continuación segura cuando exista, revisores nuevos e independientes. Codex
selecciona modelos y resuelve decisiones. Este plan no autoriza publicación,
instalación, push ni detener procesos actuales del usuario. Requiere revisión
del usuario antes de comenzar implementación.
