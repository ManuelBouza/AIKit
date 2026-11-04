# Revisión independiente de reconciliación terminal

## Alcance y resultado

Revisión global de la implementación `612fe08..ed00065`, sobre el snapshot de
125 archivos versionados de `9a00248`. Sesión independiente
`ses_e62ddcb19ffeB5tHibJULBsavW`, Kimi K3.1 Pro mediante OpenCode Go,
variante publicada `high`, de pago. La selección se apoyó en las capacidades de
programación con herramientas declaradas en la
[documentación oficial](https://www.kimi.com/code/docs/en/kimi-code/models.html);
no constituye una evaluación universal de calidad del modelo.

**Dictamen del revisor: `needs_corrections`. Cierre no aceptado.**
El coordinador contrastó identidad, snapshot intacto y logs, sin repetir el
análisis técnico. `review_evidence.py` rechazó la aceptación con
`verdict_not_accepted`, conforme al dictamen. Es un rechazo del contrato de
aceptación, no de permisos ni aprobación automática del entorno.

## Hallazgos del revisor

| ID | Severidad informada | Resultado |
|---|---|---|
| REV-001 | Bloqueante | En `session_worker.py`, la verificación de propietario previa a reconciliar puede lanzar fuera del manejo de excepciones. La reproducción produjo `ServiceError(owner_mismatch)`, registro `partial` y ausencia de `result.json`. |
| REV-002 | Advertencia | El deadline se fija después de la preparación y arranque, por lo que el presupuesto no descuenta todo el preflight como exige el contrato revisado. |
| REV-003 | Advertencia | Una reconciliación no aceptada pierde `outcome`, `reason` y limitaciones, con diferencias respecto a los estados documentados. |
| REV-004 | Advertencia | Se persiste `source=durable_message`, pero no los IDs y detalles de correlación previstos por el diseño. |

En la fecha del dictamen, los hallazgos quedaron pendientes de evaluación y
corrección; la revisión no autoriza nuevos diseños ni certifica una entrega
modificada. REV-001 no demuestra la causa del fallo histórico de arranque
DEF-001.

## Triage del coordinador — 2026-11-02

Este triage contrasta los hallazgos con el snapshot revisado, el código actual y
los contratos. No modifica ni sustituye el dictamen original. La revisión global
sigue `needs_corrections`; la corrección REV-001 de `1d816fe` fue aceptada
independientemente en el seguimiento descrito a continuación.

**Estado actual:** REV-001 aceptado de forma independiente; REV-002 con disposición
aprobada documentalmente y sin cambio de código; REV-003 y REV-004 abiertos. Esto
no cambia el dictamen global `needs_corrections` ni cierra Task 6.

| ID | Evaluación | Evidencia y decisión siguiente |
|---|---|---|
| REV-001 | **Confirmado; corrección `1d816fe` aceptada independientemente.** El precheck `verify_owner` de la fase de reconciliación se evaluaba fuera del `try`; la reproducción observó excepción propagada y ausencia de `result.json`. También se protegió el check final de propietario, otra salida abrupta posible. Un resultado `None` ahora permanece conservador. | Código: `skills/delegating-to-opencode/scripts/session_worker.py:537-585,615-629`; regresión: `tests/test_worker_owner_precheck.py`. No se llama al reconciliador sin propietario verificado; se persiste salida `pending` con limitación saneada y sin procedencia `durable_message`. Aceptación limitada al snapshot del seguimiento. No explica DEF-001. |
| REV-002 | **Disposición resuelta por aclaración aprobada; sin cambio de código.** El deadline de ejecución arranca después de preparar y lanzar la CLI (`session_worker.py:481`), observación válida del revisor. La exigencia adicional de sumar preflight y ejecución apareció en el brief de revisión del coordinador (`.aikit/mcp-reconciliation-task6-review.md`), no explícitamente en el diseño original ni en Task 3. El usuario aprobó conservar el contrato de timeout por proceso, no crear un presupuesto total nuevo. | `docs/mcp-opencode.md` §Tiempos y cancelación y §Supervisor de CLI y reconciliación; `docs/balance-carga.md` §Disparador y límites. Se aclaran los ámbitos sin cambiar valores, deadline o cancelación. No es aceptación del hallazgo por el revisor ni corrección funcional. |
| REV-003 | **Confirmado como pérdida de diagnóstico; sin cambio.** El resultado del helper no aceptado no se refleja en `delivery`, `outcome`, `reason` ni `limitations`; el estado del CLI se conserva y no se promueve a `completed`. | `session_worker.py:586-596` copia `limitations` solo al aceptar; tabla de `docs/balance-carga.md:54-60`. El [diseño aprobado](superpowers/specs/2026-11-03-evidencia-reconciliacion-design.md) y el [plan](superpowers/plans/2026-11-03-evidencia-reconciliacion.md) preparan su tratamiento; REV-003 sigue abierto hasta implementación/revisión. |
| REV-004 | **Confirmado como divergencia con el diseño; disposición pendiente de implementación.** El diseño §4 pide evidencia mínima durable con procedencia, IDs, outcome y reason; la documentación de implementación dice que esos detalles quedan en memoria y solo persisten estado/fuente (`docs/balance-carga.md:70-89`). Documentar el comportamiento no demuestra que se aprobara cambiar el requisito. | El [diseño aprobado](superpowers/specs/2026-11-03-evidencia-reconciliacion-design.md) y el [plan](superpowers/plans/2026-11-03-evidencia-reconciliacion.md) concretan el campo opcional; REV-004 sigue abierto hasta implementación/revisión. |

Informe de corrección y checks de REV-001: `.aikit/mcp-reconciliation-fix1/report.json`.
REV-003/004 siguen abiertos; Unidades 1 y 2 están aceptadas independientemente; las unidades 3–4 no iniciadas. Esto no
acepta el cierre global. La prueba real mínima y la instalación conservan
autorizaciones separadas.
La corrección del bypass por `source=cli_event` está pendiente de rerevisión;
RED/GREEN y checks se registran en `.aikit/rev003004-unit2-fix1/report.json`.

## Evidencia y límites

- El revisor ejecutó siete módulos focalizados: **155 pruebas pasaron en
  29,15 segundos**. `git diff --check` pasó.
- La primera ejecución del arnés temporal falló al importar `delegate`, antes de
  ejecutar producto. Se conservó el log; corregido únicamente el arnés ignorado,
  la reproducción confirmó REV-001. No hubo cambios versionados durante la
  revisión original; la corrección posterior está descrita en el triage actual.
- Informe original: `.aikit/mcp-reconciliation-task6/review.json`, SHA-256
  `4579889a7483956f7caa6a5c10ede04d357334b002f0abbf947371e0d4ad5d0f`.
  La copia `review-bound.json` añade solo la sesión observada por el coordinador;
  `coordinator.json` conserva la comprobación. Estos artefactos son locales e
  ignorados por Git; este resumen permite recuperar los pendientes sin ellos.
- No se repitió la suite histórica de 849 pruebas. Las pruebas con transporte
  falso no certifican eventos de un servidor real.
- No hubo prueba real mínima, exportación nueva, instalación, recarga ni
  comprobación de paridad actual del candidato anterior. El cliente venció,
  pero se conservó la misma sesión hasta observarla inactiva; no se duplicó
  inferencia. El resultado `pending` del cliente no es el dictamen final.

## Continuación

Continuar con Unidad 3, con autorización propia; se conserva la aceptación de
Unidades 1 y 2. REV-002 tiene una decisión aprobada
documentalmente, sin cambio funcional.
No reabrir ni presentar como pendiente la revisión ya aceptada de REV-001 sin
cambios nuevos. La aceptación de REV-001 no acepta Task 6 global ni acredita
otros cambios posteriores a su snapshot.
La prueba real y la instalación conservan sus autorizaciones separadas.
Seguimiento en [REC-001](pendientes.md#rec-001--task-6-cierre-global-de-reconciliación).

## Seguimiento independiente de REV-001

Dictamen **`accepted`, solo para REV-001**, sobre cuatro archivos modificados
del commit `1d816fe`. Se reutilizó la sesión de revisor
`ses_e62ddcb19ffeB5tHibJULBsavW`, distinta de la del implementador, con
Kimi K3.1 Pro mediante OpenCode Go, variante `high`, de pago. No hubo hallazgos
nuevos ni modificaciones de la entrega.

- Pruebas propias: **72 aprobadas en 15,33 s** y `git diff --check` correcto.
- Reproducción temporal adicional del check final, tras reconciliación aceptada:
  excepción y `None` conservan reporte/registro `pending`, restauran la fuente
  anterior y no filtran detalles. Esta cobertura temporal no sustituye una
  regresión versionada del check final; el test versionado cubre el precheck.
- El coordinador verificó sesión, snapshot intacto y logs. La copia vinculada
  pasó `review_evidence.py` antes de actualizar estos documentos de seguimiento.
  No se repitió la revisión técnica en Codex ni la suite global de 851 pruebas.
- Original local: `.aikit/review-rev001/review.json`, SHA-256
  `d2eb470c17cf6dcb15313a832c9cbd524b31b285b8980a90b5683b3ee73b714c`.
  Copia vinculada y comprobación en `review-bound.json` y `coordinator.json`
  del mismo directorio ignorado por Git.
- REV-003/004 permanecen abiertos; el diseño está aprobado y el plan preparado,
  con Unidades 1 y 2 aceptadas y unidades 3–4 pendientes. REV-002 se resolvió documentalmente según el
  triage, sin que el revisor volviera a aceptarlo. No acepta Task 6 global, no explica DEF-001,
  no incluye prueba real mínima, instalación, nueva exportación ni paridad del
  paquete anterior con la fuente actual.

## Unidad 1 de evidencia — aceptación independiente, 2026-11-03

Implementada la extensión opcional `TaskRecord.reconciliation`, su validación y
serialización compatible, y `TerminalReconciliation.response_observed`.
Supervisor y recuperación no se modificaron; las unidades 2–4 siguen pendientes.
REV-003/004 y Task 6 global permanecen abiertos.

- Implementador: sesión `ses_e646f8e11ffe32fS2z1SqClTdW`, GPT-6 Luna mediante
  OpenCode Go, `high`, de pago. Evidencia RED/GREEN de almacenamiento y del
  marcador HTTP; suite final **866 aprobadas**, Ruff lint y mypy correctos.
- Revisor independiente: `ses_e5d09204fffeiFXrNO99xPXVmW`, Kimi K3.1 Pro mediante
  OpenCode Go, `high`, de pago. Dictamen **`accepted`**, sin hallazgos. Ejecutó
  **175 pruebas focalizadas** y una reproducción temporal con 49 mutaciones,
  16 campos ausentes y ocho incoherencias rechazadas conservadoramente.
- Se verificaron identidad y los siete hashes del snapshot antes de actualizar
  este seguimiento; `review_evidence.py` aceptó el contrato. El coordinador no
  repitió la revisión técnica. Los casos temporales no son pruebas versionadas
  ni una demostración exhaustiva de toda entrada posible.
- Informe original: `.aikit/rev003004-unit1-review/review.json`, SHA-256
  `992770b4d50d8ed1d8480c0711e375771587eae984c04e089d40ee16e0a60510`.
  Comprobación local: `.aikit/rev003004-unit1/coordinator-acceptance.json`.
- El formato global detectó inicialmente un ejemplo del plan anterior. El
  coordinador corrigió solo ese formato: Ruff informó 122 archivos formateados.
  `uv` nativo falló por permisos de caché del sandbox; se utilizó el Ruff ya
  instalado en `.venv`. No se repitió inferencia ni suite por ese cambio documental.
- Sin exportación, instalación, prueba real, nueva política ni cierre global.

## Unidad 2 — recuperación local aceptada, 2026-11-03

Se incorporó una captura única de bytes y JSON del resultado, y un gate para
validar evidencia presente antes de recuperar `completed`. Se conservan los
gates legacy cuando no existe observación; no se consulta backend. El escritor
del supervisor sigue pendiente de Unidad 3.

- Implementador: misma sesión `ses_e646f8e11ffe32fS2z1SqClTdW`, GPT-6 Luna por
  OpenCode Go, `high` para Unidad 2 y `medium` para la corrección puntual, de pago.
  Suite final **875 pruebas aprobadas**, Ruff, formato y mypy correctos.
- La primera revisión de `ses_e5ce9e5adffegZQ71MHqEMJUZt`, Kimi K3.1 Pro por
  OpenCode Go, `high`, de pago, encontró RECOVERY-SOURCE-GATE: una observación
  negativa podía eludir la validación cuando la fuente era `cli_event`.
  Se conservó el dictamen `needs_corrections` en
  `.aikit/rev003004-unit2-review/review.json`.
- Tras reproducir el bloqueo en RED, se retiró la dependencia de la fuente y
  se verificó GREEN, incluido CLI legacy sin observación. El mismo revisor
  aceptó el nuevo snapshot, sin hallazgos: **186 pruebas focalizadas** y tres
  reproducciones aprobadas. Los intentos paralelos iniciales colisionaron en
  el directorio temporal; quedaron registrados y se repitieron secuencialmente
  con directorio propio. No se atribuyó esa colisión al producto.
- Informe de seguimiento:
  `.aikit/rev003004-unit2-rereview/review.json`, SHA-256
  `d2d18d02a12b799fd359af28bed7dbe8af2650b45815aed13cce090d5842f585`.
  El coordinador vinculó la sesión en una copia separada y verificó cuatro
  hashes, logs y el contrato de aceptación antes del seguimiento documental.
  Evidencia: `.aikit/rev003004-unit2/coordinator-acceptance.json`.
- Desviación TDD registrada: un primer parche se aplicó antes de la regresión;
  se retiró íntegramente y el RED confirmado se ejecutó sobre el código base
  antes de reimplementar. El primer pase verde no se presentó como RED.
- No existe referencia externa de `generation`: se valida positiva en el
  registro actual y se enlaza por intento/sesión/digest. No se acredita
  autoría criptográfica ni propietario online por esos metadatos.
- Aceptación exclusiva de Unidad 2. Unidades 3–4, REV-003/004 completos y
  Task 6 global siguen pendientes. Sin exportación, instalación o prueba real.

## Unidad 3 — publicación y diagnóstico aceptados, 2026-11-04

Se incorporan barrera provisional, diagnóstico persistido, resultado atómico con
digest y commit final condicionado a identidad y propietario vigentes.

- OpenCode agotó alternativas adecuadas o encontró límites de presupuesto;
  Beam no alcanzó progreso suficiente de producción y el coordinador interrumpió
  su intento. Se conservó la sesión y el trabajo parcial. El fallback nativo
  autorizado fue GPT-6.1 Terra, high; revisión independiente GPT-6 Astra, high,
  por los riesgos concretos de publicación, concurrencia y recuperación.
- Autor nativo `/root/unit3_native_implementation`: suite global 892 aprobadas
  antes de la última corrección; después, 55 focales, Ruff, formato y mypy.
  El RED inicial incluía fallos de harness, no solo defectos funcionales.
- Revisor `/root/unit3_native_review`: 121 focales iniciales. Rechazó el
  diagnóstico local_failure cuando el precheck agotaba el presupuesto sin
  invocar el helper. Corregido con regresión RED/GREEN; revalidación propia de
  35 pruebas y una reproducción adicional, dictamen accepted.
- Informe inicial conservado en `.aikit/rev003004-unit3-native-review/review.json`;
  seguimiento `review-corrected.json`, SHA-256
  `b4e8a009aa9f6b95ba8a73b250ceaa7a6d008283d493c3add35080ea8ebc8673`.
  Coordinador comprobó metadata, tres hashes y existencia de logs, sin repetir
  revisión técnica; `.aikit/rev003004-unit3-native/coordinator-acceptance.json`.
- La prueba Windows conservó DACL. Un lector sin SHARE_DELETE puede impedir
  reemplazar el resultado: se comprobó conservación de bytes y limpieza del
  temporal propio. No se promete una transacción entre host y archivos.
- Permanece un comentario informativo desactualizado en
  `test_supervisor_reconcile_write_failure_keeps_conservative`, asignado a
  Unidad 4; no hay bloqueantes de Unidad 3 pendientes.
- Beam continuó después en la misma sesión, con medium para la investigación
  de esfuerzo y low para correcciones documentales; no es revisión independiente
  ni comparación controlada de rendimiento.
- Unidad 4, REV-003/004 globales y Task 6 siguen pendientes. Sin exportación,
  instalación, prueba real mínima ni push.

## Unidad 4 — aceptación global de código, 2026-11-04

Contrato documentado en `docs/balance-carga.md`; corregido el comentario
informativo de Unidad 3. No se añadieron cambios funcionales en esta unidad.

- Autor: Beam por Kilo, medium, gratuito; sesión reutilizada
  `ses_e646f8e11ffe32fS2z1SqClTdW`. 39 focales y suite global **893 aprobadas**
  (134,98 s), Ruff, formato, mypy y diff correctos. No se atribuyen a este
  resultado las pruebas anteriores de Unidad 3.
- Candidato 0.2.0: `.aikit/rev003004-unit4/dist/aikit`, **42 archivos**,
  nueva exportación sin instalación ni activación.
- Revisor independiente: Nemotron 3 Ultra 550B A55B por Kilo, high, gratuito,
  nueva sesión `ses_e5815168dffeN8Y8WfTf4AjPOe`. El high se eligió por riesgos
  de publicación prematura, identidad y fallos entre artefactos. Ejecutó
  **124 focales**, Ruff, formato y mypy; revisó las cinco áreas del plan y
  comprobó paridad de los 42 archivos por SHA-256. Dictamen **accepted**, sin
  hallazgos accionables. Los puntos info describen comportamiento comprobado.
- Informe original `.aikit/rev003004-unit4-review/review.json`, SHA-256
  `2320734f32d6f65e67de17843e400b0bbb86043e44f56a2fa7f490356239e28b`.
  Omitía sesión y enlaces a logs: se preservó y vinculó la sesión real en
  `review-bound.json`. El coordinador recuperó metadata y resultados compactos
  de cinco checks ya ejecutados desde el backend verificado, sin repetirlos ni
  inferir de nuevo. `review_evidence.py` aceptó contrato/sesión/snapshot de diez
  archivos; los hashes del candidato coinciden con el manifiesto del revisor.
  Evidencia: `.aikit/rev003004-unit4/coordinator-acceptance.json`.
- Disposiciones del coordinador: aceptar inspección acotada por lista permitida
  y revisión manual de posibles secretos, sin certificación exhaustiva; aceptar
  fixtures ACL en Windows sin afirmar validación en otros sistemas; aceptar
  suite global del autor más focales independientes, sin duplicar la suite.
  Límites: podrían quedar datos sensibles fuera de la inspección, comportamiento
  de otros sistemas no probado o regresiones fuera de la cobertura focal.
- La espera del cliente venció mientras el revisor seguía activo; se conservó
  la sesión y se esperó su finalización determinísticamente, sin duplicar
  inferencia. El mismo mecanismo recuperó la entrega del autor tras un reinicio
  del entorno de herramientas del chat.
- REV-003/004 quedan aceptados a nivel de código. Task 6 original conserva su
  prueba real mínima pendiente de autorización; instalación/paridad con el host
  instalado siguen separadas. No hay push, instalación ni nueva política de
  selección de modelos en esta entrega.
