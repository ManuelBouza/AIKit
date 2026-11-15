# Revisión adversaria del contrato v1

Veredicto: los tres hallazgos del primer borrador están atendidos. Quedan dos
contratos imprescindibles antes de implementar; no se observa pérdida inevitable
si la implementación se detiene conservadoramente, pero sí divergencia y bloqueos
permanentes entre implementaciones aparentemente conformes.

## Alta — Operaciones administrativas no encajan en el motor descrito

El documento exige el mismo mecanismo para PROYECTO, nueva asignación y nuevo
ciclo, y manda recuperar antes de toda mutación. Sin embargo `operacion.json`
requiere aviso y generaciones base/propuesta y el reconocimiento posterior se
basa en recibo o incidente con operationId. PROYECTO no tiene generación ni
recibos; la modificación de assignedChatId/activeCycle no tiene aviso definido.
Implementación A inventa operaciones administrativas sin recibo; B exige un aviso
ficticio. Tras publicar un relevo y perder completada.json, la primera no tiene
el testimonio exigido para reconocerlo al observar un PROYECTO posterior.

Fijar tipos de operación (aviso, asignación/ciclo, relevo, bootstrap y derivados),
los campos y evidencia aplicables y el algoritmo recuperable por tipo. Alternativa
acotada: excluir explícitamente esas mutaciones del auxiliar v1 y definir el
procedimiento manual verificable, sin afirmar que usa el mismo motor.

## Alta — Exclusión recuperable y adquisición de autoridad se remiten entre sí

Un proceso que falla conserva escritura.lock. Recuperación comienza «tras obtener
autoridad y exclusión verificables», mientras la adquisición con EEXIST prohíbe
reintentar y no define cómo resolver el bloqueo. El texto previene eliminar por
edad o por PID ausente, pero no fija qué prueba sí permite sustituirlo, quién lo
hace y cómo se impide que dos recuperadores lo hagan a la vez. Una implementación
solo permite intervención humana; otra retira tras comprobar PID y chat inactivo.
Ambas pueden defender su interpretación. La segunda puede competir con otro
recuperador y retirar un bloqueo nuevo adquirido en la ventana intermedia.

Fijar recuperación v1 exclusivamente manual y con todos los escritores detenidos,
o definir un protocolo de recuperación del bloqueo con identidad/token y exclusión
entre recuperadores. La evidencia y el bloqueo original deben conservarse; cambiar
ownerEpoch no reemplaza la exclusión del sistema de archivos.

## Media — Historial de recibo pendiente no fija la transición del estado vigente

Se permite resolver un recibo pendiente conservando history, pero falta indicar que
la resolución debe recalcular su decisión contra el current que existe en ese
momento. Caso: aviso revisión 2 pendiente, revisión 3 aplicada y resolución tardía
de revisión 2. Aplicar el recibo sin reevaluar rebaja el estado; reclasificarlo como
antiguo lo conserva. Añadir la regla explícita y un test de esa secuencia.

## Media — Colisión de ID entre tareas y unicidad de recibos/incidentes

La unicidad de updateId por proyecto y el rechazo de recibos repetidos no aclaran
si los incidentes con el mismo updateId se excluyen de la unicidad (deben poder
conservar el contenido contradictorio). Fijar que la unicidad vincula el aviso
original/recibo, y que incidentes posteriores lo referencian sin reservar otra vez
ese ID; indicar en qué tarea se conserva un incidente de colisión entre tareas.

## Addendum — cierre de hallazgos altos

Revisada la sección «Decisiones de consulta y administración» y las reglas de
recuperación supervisada añadidas posteriormente.

- Operaciones administrativas: cerrado al nivel de este contrato propuesto. Se
  distinguen kind, notice nullable, generaciones, adminOperations y operations de
  PROYECTO; el relevo y el bootstrap dejan de requerir avisos ficticios. La evidencia
  acumulativa permite reconocer una operación administrativa tras publicaciones
  posteriores.
- Bloqueo tras fallo: cerrado. V1 exige detener todos los escritores y reservar
  un operador único, conservar el bloqueo y adquirir exclusión nueva antes del
  diagnóstico. Si no se garantiza exclusividad no se retira el bloqueo. No hay
  recuperación automática por PID/edad ni competencia entre recuperadores.

No quedan hallazgos altos de esta revisión. Conviene armonizar la frase general
«Un documento posterior solo acredita una operación mediante recibo o incidente»
con la excepción administrativa ya definida, para evitar que una lectura aislada
oculte el uso de operations/adminOperations. Es una corrección editorial de
consistencia, no una nueva carencia del protocolo administrativo.
