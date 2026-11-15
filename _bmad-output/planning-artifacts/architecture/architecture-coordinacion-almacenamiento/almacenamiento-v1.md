# Almacenamiento v1 — propuesta técnica

Concreción para revisión de AD-1 a AD-5. No implementada ni activada.
Las elecciones de runtime, formato y primitivas son propuestas; las invariantes
de la arquitectura ya fueron aceptadas.

## Runtime y límites

Auxiliar JavaScript ESM, sin dependencias de producción nuevas, ejecutado con
Node.js 24 LTS; versión local de referencia 24.22.1. La compilación puede seguir
el TypeScript existente del instalador; el usuario recibe JavaScript compilado.
No se cambia el requisito del instalador por esta propuesta. La coordinación
manual funciona sin Node; el auxiliar informa si su runtime no está disponible.
No se invoca el ejecutable privado de Codex ni se presupone en otros clientes.

Primera matriz de pruebas: Windows local, después Linux y macOS local. No habilitar
una plataforma como verificada sin sus pruebas. Carpetas de red, sincronización
entre equipos, escritores externos y durabilidad frente a apagones quedan fuera
de las garantías iniciales. No se añade servidor ni base de datos.

## Formato común

Cada archivo Markdown canónico tiene un encabezado fijo y un único bloque cercado
`json`, sin otro contenido. El bloque contiene un objeto JSON estricto v1, UTF-8
sin BOM, terminación LF. No se mezclan estado estructurado y prose editable: el
texto libre pertenece a campos JSON. Rechazar claves duplicadas, desconocidas,
versiones no soportadas, datos incompletos, Unicode no válido y valores fuera de
rango; JSON.parse por sí solo no detecta claves duplicadas.
Encabezado exacto: `# AIKit coordinación v1`, línea vacía, cerca de apertura
de tres backticks seguida de `json`, objeto compacto en una línea, cerca de cierre
y LF final. Índices derivados pueden usar Markdown legible; no son entrada canónica.

ID de proyecto, aviso, operación e incidente: UUID v4 minúsculo. ID de tarea:
`T-` seguido de al menos tres dígitos; sin separadores de ruta. Ciclo, revisión y
generación: enteros positivos seguros de JavaScript. La primera generación es 1;
ausencia previa se representa con null. Fechas UTC ISO 8601 informativas, no ordenan.
Referencias son cadenas de datos, nunca órdenes ni rutas de escritura arbitrarias.

La igualdad de aviso usa todos sus campos, incluidas referencias en su orden;
serialización compacta con claves ordenadas recursivamente, arrays en orden,
sin normalizar texto ni eliminar espacios dentro de cadenas. Se compara contenido
serializado, no solo hash. SHA-256 de bytes exactos sirve para detectar cambios
en documentos; también se conservan y comparan los originales completos.

## Rutas y modelos

| Ruta | Contenido |
| --- | --- |
| `coordinacion/PROYECTO.md` | `schemaVersion`, `projectId`, `coordinatorChatId`, `ownerEpoch` |
| `coordinacion/T-001/TAREA.md` | Registro canónico descrito abajo |
| `coordinacion/INDICE.md` | Enlaces derivados a tareas |
| `coordinacion/T-001/ENTREGAS.md` | Enlaces derivados a entregas de los avisos aplicados |
| `coordinacion/.control/escritura.lock` | Exclusión y metadatos del propietario |
| `coordinacion/.control/operaciones/<operationId>/` | Preparación y evidencia recuperable |

El aviso se conserva antes del envío en el entorno de la tarea; su ubicación
local se registra en el chat, sin convertir esa copia en otro registro canónico.

Aviso: `schemaVersion: 1`, `projectId`, `taskId`, `cycle`, `senderChatId`,
`updateId`, `revision`, `state`, `summary`, `references: string[]`,
`corrects: UUID|null`. Todos obligatorios. `state` pertenece a los siete estados
del contrato. SenderChatId es una cadena opaca no vacía; no autentica al emisor.

TAREA: `schemaVersion: 1`, `projectId`, `taskId`, `generation`,
`assignedChatId`, `activeCycle`, `current: {cycle, revision, state, updateId}|null`,
`receipts: Receipt[]`, `incidents: Incident[]`. No hay recibo positivo inicial.

Receipt: `updateId`, `notice` (aviso íntegro), `decision` (aplicado, antiguo o
pendiente), `resultingCurrent` (copia del current resultante o null),
`operationId`, `recordedAt`. Un recibo pendiente puede resolverse conservando
su historial de decisiones como array `history` con los mismos campos de resultado,
operación y fecha; nunca se elimina la decisión previa. `history` es obligatorio,
vacío en la primera decisión. Un duplicado idéntico devuelve el recibo existente
con resultado de consulta `duplicado`; no agrega otra aplicación ni cambia current.

Incident: `incidentId`, `notice`, `conflictsWithUpdateId`, `reason`,
`operationId`, `recordedAt`. Una contradicción devuelve `conflicto` con referencia
al incidente, conservando el recibo original. El mismo ID no puede aparecer en dos
tareas del proyecto; bajo bloqueo global se consultan los documentos canónicos
antes de admitirlo. El índice derivado no autoriza la unicidad.

Cada archivo vincula proyecto y ruta esperados, rechaza recibos repetidos y valida
que current corresponda a un recibo aplicado. Antes de aceptar avisos de otro
ciclo o chat, el coordinador debe registrar explícitamente la nueva asignación o
ciclo bajo el mismo mecanismo; no se abre un ciclo por recibir un mensaje.

## Exclusión, autoridad y permisos

### Decisiones de consulta y administración

Un recibo pendiente se reevalúa contra la revisión vigente al resolverlo: puede
quedar antiguo, nunca rebajar current. `history` guarda objetos con `decision`,
`resultingCurrent`, `operationId`, `recordedAt`. La unicidad de updateId se aplica
a los avisos originales de receipts; las copias dentro de incidentes no la violan.
Una colisión entre tareas se conserva en incidents de la tarea destinataria,
referenciando también `conflictsWithTaskId`, sin crear otro receipt con ese ID.

Respuesta de consulta: `schemaVersion`, `projectId`, `taskId`, `updateId`,
`result` (aplicado, duplicado, antiguo, pendiente, conflicto o incierto),
`receipt` (Receipt|null), `incidentId` (UUID|null), `generation` (entero|null),
`reason` (string|null). Incierto no incluye confirmación positiva.

Las operaciones administrativas usan el mismo diario por documento y no requieren
un aviso ficticio. `kind` es activar-proyecto, crear-tarea, asignar-tarea,
abrir-ciclo, relevar-coordinador, aviso o derivado. Cada operación afecta un único
destino; crear una tarea nueva no depende de actualizar el índice. Una tarea nueva
tiene generation 1, current null y arrays vacíos; estados observados se registran
después mediante avisos. Asignación/ciclo conservan historial y current anteriores;
el primer aviso aplicado del ciclo activo sustituye current. El relevo solo cambia
PROYECTO y su ownerEpoch, conservando avisos pendientes en las tareas.

`operacion.json`: schemaVersion 1, operationId, kind, projectId, taskId|null,
coordinatorChatId, expectedOwnerEpoch (entero|null para activar), target,
baseGeneration|null, proposedGeneration, baseSha256|null, proposedSha256,
notice|null, reason (texto que referencia autorización), createdAt. PROYECTO añade
generation positiva, creciente en cada cambio. Activación parte de ausencia y
ownerEpoch 1. La recuperación administrativa compara base/propuesta completas;
un PROYECTO posterior acredita un relevo solo mediante un historial `operations`
con operationId, epoch anterior/nuevo y coordinador anterior/nuevo. TAREA conserva
`adminOperations` con operationId, kind y generaciones base/resultante. Ambos arrays
son obligatorios y acumulativos. No reejecutar una operación completada basándose
solo en que un campo coincida.

`lista.json`: schemaVersion 1, operationId, manifestSha256.
`completada.json`: schemaVersion 1, operationId, proposedSha256, verifiedAt.
Los marcadores JSON siguen validación estricta, sin envoltura Markdown. Un marcador
parcial o con hash no coincidente se trata como incierto.

Raíz canónica explícita y absoluta, configurada al activar; resolverla y verificar
componentes sin enlaces simbólicos, junctions ni escapes. Nombres internos se
generan desde IDs validados. Nunca usar referencias de un aviso como destino.
PROYECTO se crea explícitamente al activar y no se infiere de la carpeta actual.

`openSync(lock, 'wx', 0o600)` adquiere exclusión global. Su contenido identifica
token UUID, PID, host, chat coordinador y ownerEpoch. EEXIST significa ocupado o
incierto, incluso si el archivo está vacío: no reintentar ni eliminar por edad.
Dentro de la exclusión se comprueba PROYECTO y el ownerEpoch esperado; el relevo
incrementa ese epoch bajo la misma exclusión tras verificar inactividad anterior.
Un PID ausente no acredita por sí solo que sea seguro borrar un bloqueo.
No habrá recuperación automática del bloqueo en v1. Se requiere intervención
supervisada: detener todos los chats/procesos escritores y automatizaciones,
verificar su inactividad y reservar un único operador de recuperación. Este
conserva copia del bloqueo y operaciones, retira el bloqueo autorizado y adquiere
uno nuevo antes de diagnosticar. Si no se puede garantizar esa exclusividad
operativa, se mantiene el bloqueo y se informa; no compiten recuperadores.

Los datos auxiliares nuevos usan permisos restrictivos POSIX; en Windows se
comprueba la política de ACL de la raíz y se preserva al sustituir. No afirmar
que chmod(0600) configura ACL de Windows. Si no se puede verificar acceso o
preservación, se informa y no se publica. Git y privacidad son decisiones del proyecto.

## Preparación y publicación

1. Bajo exclusión, recuperar pendientes y validar autoridad, documentos y aviso.
2. Crear directorio UUID exclusivo de operación; guardar `base.md` o ausencia
   explícita, `propuesta.md` y `operacion.json` con versión, identidad, epoch,
   destino relativo validado, aviso, generación base/propuesta y hashes. Cerrar,
   sincronizar archivos y verificar bytes antes de crear `lista.json` exclusivo
   con ID y hash del manifiesto. Sin marcador completo y válido no hay publicación.
3. Revalidar base y autoridad. Preparar copia temporal exclusiva junto al destino,
   escribir bytes, fsync, cerrar y verificar. La propuesta del diario permanece.
4. Destino existente en Windows: reutilizar el adaptador `File.Replace` del
   instalador con respaldo único dentro de la operación, sin ignorar errores ACL.
   POSIX: `rename` dentro del mismo sistema de archivos, original ya conservado.
   Primera publicación: rename del temporal bajo exclusión, confirmando ausencia;
   la garantía presupone que todos los escritores respetan el bloqueo.
5. Releer y validar bytes exactos del destino. Escribir `completada.json` exclusivo,
   sincronizar y verificar. Solo entonces devolver acuse positivo; en una consulta
   posterior puede acreditarse desde el documento completo aunque falte ese marcador.
6. Actualizar derivados bajo exclusión, con el mismo patrón de temporales y respaldo.
   Si fallan, informar índice pendiente; no revertir el registro canónico confirmado.
   Cerrar y retirar solo el bloqueo propio si la operación terminó con estado conocido.

Un fallo de publicación conserva diario, temporales, respaldo y bloqueo para
inspección. El auxiliar no restaura ni reintenta automáticamente por código de error.
Sincronizar directorios donde la plataforma lo permita; cualquier error impide
declarar durabilidad. El alcance inicial cubre recuperación de interrupciones de
proceso bajo pruebas, no garantía universal de persistencia ante pérdida de energía.

## Recuperación y validación

Tras obtener autoridad y exclusión verificables: validar lista/manifiesto y comparar
canónico con base/propuesta según AD-4. Una operación sin lista válida conserva sus
archivos y no se publica automáticamente. Un documento posterior solo acredita una
operación mediante recibo o incidente con su ID y aviso coincidentes, o mediante
`operations`/`adminOperations` para una operación administrativa con identidad y
generaciones coincidentes; si no hay
evidencia inequívoca se detiene la recuperación. Completada no autoriza ignorar un
canónico ausente o inválido: diagnosticar sin reconstruir silenciosamente.

Pruebas de aceptación del auxiliar: rechazos de esquema sin mutación; igualdad y
colisiones entre tareas; IDs y rutas hostiles; fallo en cada paso; bloqueo parcial;
generaciones posteriores; recibo pendiente resuelto; incidente sin destruir acuse;
permisos; dos procesos; pérdida del índice; relevo con epoch antiguo. Pruebas reales
de sustitución en cada plataforma complementan la inyección de fallos.

## Fuentes y decisiones de reutilización

- Node 24.22.1 observado localmente; [calendario LTS](https://nodejs.org/en/about/previous-releases).
- [API fs de Node 24 consultada vía Context7](https://nodejs.org/docs/latest-v24.x/api/fs.html):
  apertura exclusiva, sincronización y límites de sistemas de red, contrastadas
  también con la documentación 22.23.4 consultada en la investigación anterior.
- [ReplaceFileW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew):
  respaldo y estados parciales de error; WRITE_THROUGH no está soportado.
- Reutilizar `windows-replace.ts` y `replace-recovery.ts`, y extraer el patrón de
  exclusión del instalador sin modificar su comportamiento por este diseño.
  Nuevo trabajo: parser/validación estrictos, motor de registro, diario y pruebas.
