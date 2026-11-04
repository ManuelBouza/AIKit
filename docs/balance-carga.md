# Balance de carga AIKit/OpenCode

Evidencia sanitizada del cambio autorizado "OpenCode como ejecutor habitual".

## Cobertura

Superpowers ya cubre planificación, pruebas y revisiones; skill-creator cubre
edición de skills. La brecha es la activación de exploración técnica y el
reparto de trabajo externalizable: no se crea una nueva skill.

Superpowers using-superpowers, brainstorming, writing-plans, writing-skills y
test-driven-development; skill-creator; skill actual y docs/principios-aikit.md.

## Baseline

Evaluador independiente leyendo solo la SKILL anterior eligió, en escenario de
bug desconocido, exploración inicial con Codex hasta identificar objetivo y
alcance acotados, porque la skill solo hablaba de implementación/transformación.
En otros escenarios ya eligió OpenCode para corregir fallos, CLI para tareas
largas y Go tras cuota free. Es una decisión en seco, no ejecución real ni
ahorro de tokens.

## Reconciliación terminal en la fuente actual (Task5)

Este apartado documenta la implementación fuente de Tasks1–4 y su exportación
candidata; no amplía ni reinterpreta las evidencias históricas de abajo. No se
instaló el candidato ni se realizó una inferencia E2E real.

### Disparador y límites

`session_worker` espera a que la CLI termine y finaliza el parser. Solo intenta
reconciliar si no hay un `step_finish`/`step-finish` con `reason=stop` ni error,
la entrega observada sigue en `partial` o `pending`, no hay discrepancias de
sesión o de ID, se capturó un ID de mensaje asistente y siguen válidos el registro,
la sesión, el propietario y el contexto del intento. Un código de salida distinto
de cero, vencimiento del deadline, fallo de lectura/persistencia o procedencia
inválida impide la reconciliación.

El ID de mensaje proviene de `messageID` observado por `EventStream` en el evento
o su `part`; IDs contradictorios invalidan esa evidencia. El supervisor usa el
`attempt_id`, la sesión y la identidad de propietario/servidor ya vinculados al
registro, además de comprobar que el propietario no cambió. No pasa un
`prompt_message_id`: por tanto, no se afirma que esta integración valide el
parentesco con el mensaje del usuario. Si no hay ID actual fiable, se conserva
`uncertain`; nunca se elige el último mensaje por cercanía temporal.

Se hace como máximo un `GET /api/session/{session_id}/message/{message_id}`
read-only. El presupuesto del helper es `min(tiempo_restante_del_worker, 10 s)`;
la comprobación previa del propietario usa como máximo `min(tiempo_restante, 1
s)`, y el helper vuelve a verificar propietario y registro alrededor de la
lectura. No hay polling ni una inferencia adicional. El timeout MCP del cliente no
cambia el deadline del worker ni autoriza a cancelar o repetir un intento vivo.

Estos tiempos tienen ámbitos distintos. La preparación/preflight usa los límites
propios de sus operaciones y queda fuera del contador de ejecución; no se afirma
que carezca de límites ni se fija aquí un máximo global. El deadline actual del
worker/CLI comienza una vez iniciado el proceso. La reconciliación consume su
tiempo restante, sin reiniciarlo ni extenderlo. La espera MCP de 45 s configurada
para la llamada referida es otra espera: su vencimiento no prueba que el backend
terminó, no lo cancela ni autoriza un reenvío. No se promete un tope exacto de
tiempo de pared que incluya limpieza o respuesta HTTP final.

| Evidencia del mensaje | Resultado conservador |
| --- | --- |
| ID/sesión coherentes, mensaje asistente, sin error, `finish=stop` y `completed_at` numérico finito | Puede acreditar `completed` |
| `finish=length` | `partial`, no éxito |
| Error del mensaje o `finish=error`, `content-filter`, `interrupted` o `cancel` | `failed` |
| `tool-calls`, `unknown`, finish ausente/desconocido o timestamp inválido | `uncertain`, nunca `completed` |
| ID ausente/contradictorio, sesión ajena, respuesta inválida, backend no disponible, timeout, propietario/registro cambiado o presupuesto agotado | Se conserva estado no satisfactorio (`pending`/`uncertain`) |
| Error del evento CLI o proceso con código distinto de cero | No se consulta el mensaje para promover el intento |

Un `parent_id` ausente o nulo no permite buscar otro mensaje ni establecer por sí
solo un enlace al prompt. Si se proporciona un prompt esperado, un padre distinto
se rechaza; la integración actual no proporciona ese ID. Solo la identidad de
mensaje capturada para el intento actual puede participar en la decisión.
`idle`, texto en stdout, código CLI cero y `source=durable_message` por separado
no demuestran éxito.

### Evidencia persistida y recuperación

`TerminalReconciliation` devuelve metadatos en memoria (`finish`,
`completed_at`, `assistant_message_id`, `reason` y `limitations`); el supervisor
no persiste ese objeto ni añade esos campos al contrato JSON. Al aceptar, el
registro de entrega conserva su estado y `DeliveryObservation.source` pasa a
`durable_message`. También se guarda la observación de host existente: fase
`terminal_observed` (su campo de fuente actual sigue siendo `cli_terminal`). El
`result.json` local y el resultado público conservan JSON plano con `delivery`
como cadena; no existe un objeto anidado `delivery` nuevo. La observación de
ejecución puede continuar como `unknown`: reconciliar entrega no acredita por sí
misma el estado del proceso/servidor, y `server_state_unknown` no se borra si esa
ejecución sigue sin acreditar.

`bound_execution` recupera localmente, validando la identidad de tarea, intento,
sesión y procedencia del host. No llama al backend ni inicia otra inferencia. Una
respuesta antigua `completed` se rechaza si el registro actual fue demovido o ya
no tiene entrega completada (`result_mismatch`). Las entregas `completed`
heredadas que sí tienen identidad y observación terminal válidas siguen siendo
compatibles; `TaskRecord` no requiere campos nuevos.

### Evidencia persistida de reconciliación

`TaskRecord` puede contener una `ReconciliationObservation` opcional. Su ausencia
es registro legacy y no invalida una entrega histórica válida. Si está presente,
valida identidad, intento, sesión, observación, outcome, reason, finish, timestamp,
limitaciones y digest.

- `lifecycle=provisional` es una barrera conservadora; nunca permite recuperar
  `completed`.
- `lifecycle=committed` significa que la observación diagnóstica y el vínculo con
  el artefacto quedaron escritos en `record.json`; no implica éxito.
- `identity=verified` solo se acredita si pasan los checks de propietario,
  registro, intento, sesión e ID del mensaje observado.
- El digest SHA-256 vincula la generación actual con los bytes exactos del
  `result.json` preparado; no modifica el JSON público ni su forma.
- `_recover` exige, además de los gates actuales de entrega y host terminal, que la
  observación sea `committed`, `verified`, `accepted=true`, `outcome=completed`,
  con identidad vigente y digest coincidente. Cualquier estado provisional,
  invalidado, stale o digest discordante produce `pending`.
- CLI-terminal válido sin observación conserva el comportamiento legacy; no se
  crea una observación vacía que bloquee su éxito.
- Las observaciones negativas quedan committed como diagnóstico y no bloquean
  indefinidamente la entrega conservadora.
- La generación es un entero positivo dentro del registro actual; no existe otra
  copia para compararla independientemente.
- La publicación usa `_atomic_replace` sobre un temporal hermano, con
  `fsync`. En Windows, un lector abierto sin `FILE_SHARE_DELETE` puede provocar
  fallo conservador; se preservan los bytes previos y se limpia el temporal.
- El timeout sigue siendo por proceso: reconciliación consume el tiempo restante
  del worker, sin reiniciar ni sumar preflight.
- No se afirma atomicidad entre `record.json`, `result.json` y host registry.

La modificación documental no cambia requisitos de instalación ni versiones.
El exportador produce un candidato fuente; no acredita que el host haya
recargado o instalado ese candidato.

## Diseño

OpenCode ejecuta por defecto trabajo externalizable autorizado: exploración
técnica/diagnóstico, propuesta técnica dentro del alcance acordado,
implementación + pruebas/lint/tipos + correcciones/documentación. Codex conserva
comprensión de la petición, exploración mínima para seguridad/skills/alcance,
decisiones del usuario y selección, roles nativos/Superpowers, revisión
independiente del diff y verificación final con comandos.

## Plan breve

1. Actualizar activación y contrato de ejecución.
2. Probar escenarios de selección.
3. Revisión y comandos de verificación.

## Límites

La instalación no garantiza activación global ni ejecución real. No se prometen
jobs, cancelación ni hooks.

## Verificación del 29 de octubre de 2026

Entorno: Windows, Python 3.14.9, OpenCode 2.2.0 y complemento 0.1.2.
Esperado: delegar también el diagnóstico inicial y las correcciones pequeñas,
conservar revisión independiente y no confundir timeout o cuota de un modelo
con indisponibilidad de todos los proveedores.

Observado: un evaluador independiente tomó las cinco decisiones esperadas
con la skill modificada: diagnóstico en Free, correcciones en OpenCode,
CLI para cinco minutos, Go tras cuota Free y Codex sin opciones adecuadas.
Una revisión posterior mantuvo la delegación bajo presión de tiempo y tres
rondas previas. Son simulaciones limitadas; no garantizan activación global
ni permiten calcular ahorro de tokens.

Implementación real: dos llamadas CLI a `opencode/beam-free#medium`, ambas
con resultado `ok` y coste informado 0.0. La primera entrega necesitó
correcciones, que también hizo OpenCode. Codex coordinó, revisó y verificó;
no hubo retorno nativo para implementar. Se cuenta una tarea con dos intentos.

Verificación final independiente: `scripts/verificar.ps1` pasó sincronización
con lock, 215 pruebas, Ruff, formato y mypy; el validador de la skill y
`git diff --check` también pasaron. Las pruebas de exportación comprueban que
el contrato de carga se distribuye dentro del complemento.

En el registro de coordinación se distingue result/backend_status (ok/error) de
review (accepted/needs_corrections); el éxito de ejecución no equivale a calidad.

## Prueba real desde un subagente nativo

El 29 de octubre de 2026 se comprobó el recorrido coordinador Codex →
subagente nativo `opencode_e2e_worker` → OpenCode → revisión del subagente →
verificación independiente del coordinador. Se usó la skill instalada de AIKit
0.1.2, Windows y OpenCode 2.2.0, en un directorio ignorado y con datos ficticios.

El subagente consultó el catálogo y eligió
`opencode/deepseek-v4.1-flash-free#low`, gratuito según tarifas publicadas,
para agregar un CSV a JSON. No encontró MCP tras una espera de seis segundos
y ejecutó él mismo la CLI instalada, con un intento y timeout de 120 s por
proceso. El coordinador anunció la selección antes de autorizar la inferencia.

Esperado: que OpenCode creara el archivo, sin implementación nativa, y que
ambos niveles de revisión comprobaran sus valores y la integridad de entradas.
Observado: backend `ok`, código 0, coste informado 0.0 y sesión
`ses_e7691deb2ffegL2bBT2q3ub72T`. El JSON inexistente al inicio quedó creado
con seis filas agregadas, nueve unidades y 1130 céntimos. Subagente y
coordinador recalcularon y verificaron el resultado; los hashes de entradas y
configuración permanecieron intactos, sin cambios inesperados en Git ni en
el inventario local comprobado. No se necesitó reintentar ni corregir el JSON.

Las evidencias locales están en
`.aikit/subagent-e2e-8ae6895ee2f3416d922a15f98b027307/`:
`delegate-result.json`, `summary.json` y `verification.json`. La comprobación
del coordinador está en `.aikit/subagent-e2e-coordinator-verification.json`.
Son archivos ignorados; este apartado conserva la evidencia sanitizada.

Esta prueba acredita una delegación real por CLI desde un subagente con la
skill indicada explícitamente. No acredita descubrimiento implícito en todos
los subagentes, MCP desde subagentes, funcionamiento de todos los roles de
Superpowers ni aislamiento del sistema operativo.
