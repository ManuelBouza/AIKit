# Diseño: evidencia de reconciliación terminal

**Diseño aprobado por el usuario el 2026-11-03 (Europe/Madrid), commit `27daa45`.** Diseño documental para la deuda REC-001, REV-003/004; no implementado ni probado. No añade selector ni autoriza implementación por sí solo.

## Problema y dirección de alcance acordada

`TerminalReconciliation` ya devuelve `accepted`, `outcome`, `reason`, `limitations`, `assistant_message_id`, `finish` y `completed_at` (`session_backend.py`). `session_worker.supervise` solo conserva parte de las limitaciones cuando `accepted=True`; descarta el diagnóstico de respuestas negativas. Además, el registro TaskRecord solo guarda `delivery` y `execution` (`session_store.py`), por lo que la correlación queda en memoria.

La dirección acordada es guardar evidencia mínima, saneada y acotada de cada reconciliación intentada, incluidas las negativas, reutilizando el registro local existente y su persistencia atómica. La observación no es la entrega final, no demuestra cuota y nunca autoriza por sí sola `completed`.

El ciclo de vida y la secuencia descritos abajo pertenecen al diseño aprobado; su corrección aún debe verificarse mediante implementación y pruebas, no se presentan como garantía existente.

## Alternativas

1. **Elegida:** campo opcional en `TaskRecord`, con validación y `save_task`/`lock_task` existentes. Centraliza evidencia por tarea y reutiliza atomicidad y recuperación actuales.
2. **Descartada:** sidecar/journal separado, servicio o base de datos. Duplicaría almacenamiento, identidad, recuperación y sincronización sin necesidad demostrada.
3. **Descartada:** dejar el diagnóstico solo en logs o reducirlo a `delivery.source`. No permite recuperar con el registro local `outcome`, razón ni correlación, y no satisface la dirección aprobada.

## Representación propuesta

Añadir a `TaskRecord` un `reconciliation: ReconciliationObservation | None` opcional, serializado como propiedad opcional `reconciliation` en `record.json`. El `task_id` y `server_identity` corresponden al registro contenedor; la observación repite `attempt_id` y `session_id` para validar que pertenece a la tentativa actual.

Propuesta de tipo interno:

| Campo | Tipo/valores propuestos | Regla |
|---|---|---|
| `attempt_id`, `session_id`, `assistant_message_id` | UUID actual; sesión/ID opcionales según lo observado | La presencia acredita dato observado, no identidad válida. |
| `observed_at` | timestamp ISO-8601 con zona | Fecha de la observación local, no del mensaje remoto. |
| `generation` | entero positivo por intento | Identifica la única observación vigente; se incrementa solo al iniciar una reevaluación autorizada del mismo intento. |
| `phase` | `not_attempted`, `local_failure`, `response_observed` | Distingue precheck/presupuesto, excepción local y respuesta HTTP obtenida. Propuesta: `TerminalReconciliation` expone `response_observed: bool`, falso antes de una respuesta y verdadero tras recibirla; no se guarda el cuerpo. |
| `identity` | `unverified`, `verified`, `invalidated` | `verified` solo si pasan las comprobaciones existentes de propietario, registro, intento, sesión e ID; mismatch/unknown nunca verifica. |
| `lifecycle` | `provisional`, `committed`, `invalidated` | `committed` significa observación diagnóstica consistente en `record.json`, nunca éxito. Es independiente de `identity` y `outcome`. |
| `source` | `local`, `durable_message` | Solo `response_observed` identifica respuesta durable; fallos previos no inventan una lectura. |
| `accepted`, `outcome` | `bool | None`; `completed`, `partial`, `failed`, `uncertain`, `pending` o `None` | Solo se rellenan desde el resultado real del helper; son diagnóstico, no autoridad de entrega. |
| `reason`, `finish`, `completed_at`, `limitations` | códigos enumerados; finish permitido o `None`; número finito o `None`; tupla de códigos | Validación estricta, sin texto de excepción, contenido, transcripción ni campos arbitrarios. |
| `result_sha256` | SHA-256 o `None` | Hash de bytes exactos del `result.json` preparado para esta generación; vincula el artefacto sin cambiar su JSON público. |

`reason` y `limitations` usarían códigos existentes del helper o un allowlist pequeño acordado al implementar. No se guarda cuerpo HTTP ni `message.error`. `server_identity` se contrasta con el registro contenedor; no se copia contraseña, credencial, configuración ni texto de autenticación. Si el diseño de tipos/validadores actual no admite este campo sin alterar materialmente el contrato de `TaskRecord`, devolver esa decisión al coordinador antes de implementar.

El registro contiene como máximo una observación para el intento actual, no un historial ilimitado. Un cambio de `attempt_id` limpia la anterior. Antes de escribir, bajo el `lock_task` existente, comprobar que tarea, intento, propietario y sesión siguen siendo los mismos; no reemplazar evidencia vigente con una observación de un intento ajeno o stale.

El campo se incorpora solo al camino de reconciliación elegible. Un turno con
evento terminal CLI válido que no necesita reconciliar conserva sus gates
actuales: no se le crea una observación vacía que impida completar por carecer
de `accepted` o de mensaje durable. La matriz de pruebas debe cubrir también
esta compatibilidad.

| Lifecycle | Significado y uso |
|---|---|
| `provisional` | Barrera conservadora persistida durante evaluación/publicación. Nunca permite recuperar `completed`. |
| `committed` | Diagnóstico y vínculo al artefacto escritos en `record.json` de forma consistente. Outcomes negativos también pueden estar committed; esto no implica identidad verificada ni éxito. |
| `invalidated` | Observación obsoleta, identidad perdida o reevaluación; no se reutiliza para acreditar entrega. |

## Flujo e invariantes

1. **Reutilizar antes de reevaluar.** Si el intento actual ya tiene entrega `completed` válida según los gates existentes, recuperar esa evidencia; no volver a reconciliar. Si se decide reevaluar o invalidar, bajo `lock_task` guardar primero una nueva generación `provisional` y un estado de entrega conservador. Retirar la observación terminal del host solo mediante mecanismo existente y comprobar que la barrera quedó persistida. Debe verificarse en implementación si el mecanismo existente realmente puede retirar `terminal_observed`; no inventar API. Si no se puede establecer la barrera, no iniciar reconciliación ni publicar otro `completed`. Si ya había un `completed` y falla la escritura de invalidación, no hay garantía de revocación durable: conservar el error por el canal existente y declarar este límite, no afirmar rollback.
2. **Observar una vez.** Verificar identidad y presupuesto existentes; realizar como máximo el `GET` ya definido. No invocar helper si precheck/identidad/deadline impiden el intento. Guardar `not_attempted`/`local_failure` como diagnóstico local, o `response_observed` solo si hubo respuesta HTTP real. Una excepción sin respuesta no inventa outcome remoto.
3. **Guardar diagnóstico provisional.** Persistir bajo `lock_task` la generación actual, outcome/reason/limitations normalizados e identidad por separado. Mientras se prepara publicación, `record.json` mantiene delivery conservador y lifecycle provisional.
4. **Preparar artefacto actual.** Construir el `result.json` con su forma pública vigente, sin nueva clave JSON, y escribirlo atómicamente. Calcular SHA-256 de los bytes exactos, incluida codificación y terminador que use el escritor. Para outcomes negativos, `delivery` final sigue las reglas actuales; el outcome del helper se añade solo al diagnóstico local.
5. **Completar gates de éxito.** Solo si el helper aceptó, repetir los checks actuales de propietario/registro. Observar estado terminal del host con la vía existente únicamente después de los checks; realizar los últimos checks de identidad antes del commit local. Los resultados negativos no generan una observación terminal de host. No se afirma atomicidad entre `result.json`, host registry y `record.json`.
6. **Commit local final.** Para una observación negativa, tras escribir el artefacto y validar la identidad actual, hacer `save_task` atómico con lifecycle `committed` y la entrega final conservada según reglas existentes; no requiere host terminal. Para un candidato exitoso, solo tras artefacto escrito y host terminal observado satisfactoriamente hacer el último `save_task` atómico con lifecycle `committed`, identity verificada, digest, `delivery` final y source. `record.json` es el punto local único de confirmación: éxito requiere `accepted=true`, `outcome=completed`, IDs/owner/sesión vigentes, digest coincidente y todos los gates de entrega actuales. Un diagnóstico negativo puede quedar `committed` sin implicar éxito.
7. **Fallo/crash antes del commit.** Si pending-save, result-write, host observation, última verificación o commit-save falla, no declarar éxito en el registro: conservar durablemente `pending`/`provisional` si el guardado previo tuvo éxito. Aunque un `result.json` candidato diga completed o el host marque terminal, `_recover` lo rechaza mientras el record no esté committed o no coincida el digest. El save atómico evita que un fallo antes del commit haga aparecer un commit nuevo. Si falla también el guardado de la barrera inicial, no prometer invalidación del completed previo.

El helper conserva una sola lectura `GET` como máximo y el timeout por proceso aprobado en REV-002: precheck/helper usan el tiempo restante actual del worker, sin reiniciar deadline ni sumar preflight. No se añaden consultas, reintentos, cancelación ni llamadas de modelo. `record.json` es el punto de commit local único, no una transacción atómica entre el registro, `result.json` y host registry.

## Comprobación factual de mecanismos existentes

- `host_registry.record_host_observation(..., terminal=False)` cambia el intento actual a fase `uncertain` y source `client_observation`, bajo `_lock_host`; `_write_host` ya publica con temporal, `fsync` y `_atomic_replace`. Es el mecanismo existente para retirar el marcador terminal de ese intento, sujeto a una prueba de regresión al implementar.
- `session_worker` actualmente crea `result.json` con `open_artifact` (`xb`), que evita reutilizar archivos, pero no es reemplazo atómico. Sí existe `session_store._atomic_replace(source, destination)`: exige temporal y destino en el mismo directorio, usa `os.replace` en POSIX y reemplazo POSIX-semántico en Win32. `host_registry._write_host` demuestra el patrón temporal + flush/`fsync` + helper. El plan propone reutilizarlo para preparar/reemplazar `result.json` en el directorio del intento, sin servicio ni API nueva; su uso entre módulos y la preservación de ACL/lectores requieren pruebas antes de aceptación.

La correspondencia que deberá quedar explícita en la documentación actualizada es:

| Outcome del helper | Diagnóstico conservado | `delivery` final |
|---|---|---|
| `completed` aceptado | Mensaje correlacionado con `finish=stop` y metadatos válidos | Puede pasar a `completed` solo tras los gates actuales de propietario, persistencia y terminal del host. |
| `partial` | Por ejemplo, `finish=length` | No sustituye automáticamente el estado derivado de CLI; puede seguir `partial`/`pending`. |
| `failed` | Error/finish negativo del mensaje | No sobrescribe por sí solo el estado final establecido por las reglas actuales. |
| `uncertain` / `pending` | Mismatch, dato ausente, timeout o backend no disponible | Conserva entrega no satisfactoria; nunca promueve éxito. |

## Compatibilidad, seguridad y recuperación

Los lectores nuevos aceptan ausencia de `reconciliation` como registro legacy; ausencia no invalida por sí sola una entrega histórica ni crea éxito nuevo. Si está presente, validan estructura, enums, timestamp, intento/sesión y límites; dato malformado es evidencia inutilizable y no puede promover `completed`. Sin migración masiva. El validador actual de `TaskRecord` (`_RECORD_KEYS`, `_record_from_json`/`_record_to_json`, `_validate_record`) exige claves exactas: propuesta es permitir explícitamente el conjunto legacy y el conjunto con la clave opcional. `save_task` ya serializa con reemplazo atómico; `lock_task` proporciona el lock no bloqueante por tarea. `session_worker.supervise` ya centraliza `persist()` bajo ese lock; añadir la observación allí sin locks nuevos. `bound_execution._recover` carga el registro vigente y valida procedencia, y `_map_result` rechaza resultados `completed` discrepantes. No se garantiza que escritores antiguos preserven campos desconocidos; coordinar versiones del escritor antes del despliegue.

Cuando existe una observación nueva, `_recover` solo puede aceptar el resultado actual si coinciden intento, sesión, propietario/procedencia y generación; lifecycle es `committed`, identity es `verified`, `accepted=true`, `outcome=completed`, IDs corresponden y SHA-256 coincide con los bytes actuales de `result.json`, además de los gates actuales de entrega/host. Cualquier estado provisional, invalidado, stale o digest discordante queda pending. Sin observación legacy se mantiene el gate legacy existente; la ausencia no fabrica completitud ni dispara migración. No hay reintento ni inferencia tras crash.

Un cambio de propietario después del commit exige los checks actuales al recuperar. No se promete conocimiento instantáneo si el cambio no se observa; IDs persistidos no prueban que el propietario siga vivo.

## Matriz de aceptación futura

| Caso | Resultado requerido |
|---|---|
| Respuesta aceptada y checks actuales válidos | Guarda observación; solo los gates de entrega existentes pueden terminar en `completed`. |
| Respuesta negativa (`length`, error, `unknown`) | Conserva outcome/reason/limitations; no los confunde con `delivery` ni los descarta. |
| Precheck bloquea, no hay presupuesto o helper no se invoca | `not_attempted`/fallo local diferenciado; sin respuesta durable inventada ni GET adicional. |
| Mismatch de owner, sesión, intento o mensaje | Diagnóstico no verificado; nunca acredita ni reemplaza evidencia actual de otra identidad. |
| Check final falla tras aceptar helper | `delivery` no queda completed; evidencia invalidada/provisional no se reutiliza en `_recover`. |
| Escritura atómica falla | El registro anterior permanece; resultado conservador y limitación, sin afirmar persistencia del nuevo diagnóstico. |
| Falla el save de barrera antes de reevaluar un completed anterior | No inicia nueva reconciliación; si no se pudo persistir invalidación, no se promete revocación durable del estado anterior. |
| Falla el pending-save inicial | No se inicia GET ni reconciliación; no se afirma que el estado anterior se haya invalidado. |
| Falla escritura atómica de `result.json` | Record sigue provisional/pending; no se observa host terminal ni se confirma completed. |
| Falla observación terminal del host | Se conserva provisional/pending; no se hace commit exitoso aunque haya resultado candidato. |
| Falla el último check de owner / verificación de identidad | No se confirma completed; marcar invalidado si se guarda, en otro caso mantener provisional fail-closed. |
| Crash después de pending-save, antes de response | Registro provisional; recuperación no acredita completed ni reintenta automáticamente. |
| Crash después de result-write o host-terminal, antes de commit-save | Artefacto/host no bastan; record provisional o digest no coincidente bloquea recuperación como completed. |
| Falla commit-save | Atomicidad conserva record provisional previo; `result.json` completed no basta para recuperar éxito. |
| Registro legacy sin campo | Sigue legible; comportamiento previo, sin migración ni promoción por ausencia. |
| Campo opcional malformado | No se usa para completar; carga/recuperación falla de forma conservadora y saneada. |
| Observación de intento anterior en registro actual | No reemplaza estado actual; no se acredita en recuperación. |
| Recuperación repetida | Reutiliza solo evidencia local vigente, sin GET ni inferencia adicional. |

Archivos de implementación/pruebas a decidir en un plan posterior: `session_store.py`, `session_backend.py`, `session_worker.py`, `bound_execution.py` y pruebas existentes de store, reconciliación de worker y recuperación local. Este borrador no es ese plan.

## Comprobación de diseño

El builder independiente señaló que faltaba resolver el lifecycle provisional y el orden de `record.json`/`result.json`/host para impedir recuperar un `completed` stale si fallaba la invalidación. Referencia acotada: `.aikit/rev003004-builder-report.json` (sesión `ses_e5fdce7b7ffeYxwV4NcoCnfvGG`). La respuesta del coordinador usa `record.json` como commit local único, con estados provisional/committed/invalidated, digest del artefacto y recuperación fail-closed. El usuario aprobó el diseño `27daa45`; esto no afirma que el builder haya revisado o aceptado una revisión posterior ni que la implementación esté verificada.

## Pendientes y límites

Plan de implementación: [2026-11-03-evidencia-reconciliacion.md](../plans/2026-11-03-evidencia-reconciliacion.md). Su ejecución requiere autorización separada. Siguen pendientes la implementación y verificación de validadores/allowlist, escritura atómica de `result.json`, invalidación host y gates de recuperación. Si las pruebas muestran que el mecanismo actual no cubre esos requisitos sin ampliación material, detenerse y devolver la decisión al coordinador. El protocolo local no está verificado y no promete transacción multiartefacto. La aceptación de REV-001 es limitada; Task 6 global sigue sin cerrar. No corrige DEF-001, no cambia el timeout decidido ni resuelve instalación/prueba real; no está implementado.
