# Instrucciones del chat de tarea: avisos y confirmación

Aplicar el [flujo compartido](flujo-avisos.md). Mantener la responsabilidad del
encargo, estado declarado, título, entrega, verificaciones y limpieza. La tarea
comunica sus datos; solo el coordinador escribe el registro canónico.

## Preparar y enviar

Al arrancar, confirmar encargo y alcance con el usuario, proyecto, tarea, ciclo,
chat asignado, coordinador vigente y cauces de envío/consulta. No empezar un
alcance nuevo por una entrada informativa. En un worktree conservar la entrega
y los avisos en el entorno propio; no crear una segunda raíz `coordinacion/`.

Ante un cambio significativo o hito pertinente, preparar el aviso completo con
ID estable y revisión creciente. Conservar su contenido recuperable antes de
enviarlo y registrar su ubicación. Si no puede persistirse, informar y no afirmar
que hay envío recuperable. Incluir referencias accesibles al coordinador, sin
suponer que puede abrir una ruta del worktree o un recurso privado.

Enviar por la herramienta disponible solo con autorización humana aplicable;
el encargo del coordinador no la concede por sí solo. Si falta capacidad o
autorización, dar al usuario el aviso exacto y el destino para traslado manual.
Conservar evidencia del envío y lo que realmente confirma el transporte.
No escribir TAREA, acuses o índices canónicos aunque el sandbox lo permita.

## Reconciliar

Distinguir aviso preparado, enviado, recibido e incorporado; son hitos de
comunicación, no estados nuevos de la tarea. Consultar el acuse al retomar, en
hitos relevantes o por el cauce acordado; no abrir bucles de mensajes o vigilancia.

Comparar el aviso íntegro con el recibo y comprobar su procedencia según el
flujo compartido. Solo decisión aplicado del mismo aviso acredita incorporación;
un duplicado puede remitir a ese recibo. Antiguo confirma recepción sin aplicación;
pendiente, conflicto e incierto conservan una intervención pendiente. No deducir
registro desde el envío exitoso, el silencio, el título o los índices derivados.

Ante un envío incierto, conservar ID/contenido y consultar primero registro e
historial accesibles. Sin acceso, solicitar al usuario o al coordinador por el
cauce autorizado el acuse identificado; informar de la limitación. No reenviar
ciegamente por timeout. Un reenvío justificado y autorizado usa el mismo aviso;
una novedad real o corrección usa ID y revisión nuevos, manteniendo el original.

## Título, integración y cierre

Ante cambio de estado, mantener el nombre acordado para la tarea; formato
propuesto: `[Estado] T-001 · Nombre breve`, conservando marca PRUEBA si procede.
Verificar el renombrado cuando sea posible. Si el estado declarado aún no está
incorporado, o el título falla o difiere del canónico, comunicar la discrepancia;
no presentar el título como confirmación del registro. Sin herramienta, facilitar
el nombre exacto para cambio manual. Respetar cambios intencionales del usuario.

Cuando integrar forme parte del encargo, preparar la solicitud antes del cierre:
tarea/ciclo, alcance, destino, versión exacta si hay Git, verificaciones y
pendientes. Referenciarla en el aviso. Esperar el resultado de integración del
coordinador y verificarlo antes de limpiar recursos que aún necesite. La tarea
gestiona su rama; el coordinador, las ramas principales. Sin Git, una tarea de
escritura a la vez; el usuario decide si necesita habilitar Git/worktrees para
paralelismo. No instalar Git ni crear worktrees automáticamente.

Al terminar satisfactoriamente, o cancelar con autorización del usuario, persistir
el trabajo y evidencias que deban conservarse y limpiar los recursos propios con
las herramientas y permisos del proyecto. Identificar cada pendiente, causa y
acción necesaria. No borrar ramas/worktrees con trabajo no integrado o no
persistido, ni recursos ajenos; acciones sensibles mantienen autorización específica.
El acuse no demuestra integración ni limpieza.

Si el acuse sigue sin reconciliar, conservar el aviso original y la evidencia de
envío en un lugar recuperable que sobreviva a la limpieza. Antes de retirar un
worktree u otro recurso que los contenga, persistirlos en una ubicación autorizada,
verificar la copia y dejar su referencia; si no es posible, mantener ese recurso
como limpieza pendiente. No borrar esas copias por el mero cierre de la tarea.

Aplicar los criterios de cierre del encargo: si un pendiente impide cumplirlos,
esperar intervención o declarar bloqueo según corresponda; si no, mostrarlo por
separado sin ocultarlo tras Finalizada. Un acuse pendiente no bloquea por sí solo
el cierre, ni desaparece al cerrar. El coordinador gestiona el archivado conforme
al procedimiento del proyecto; este flujo no archiva chats ni crea otros chats.
