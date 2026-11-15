# Auxiliar local de registro y recuperación

Prototipo de la nota 025, implementado en TypeScript y compilado a JavaScript ESM
en el paquete existente. Requiere Node 24; no añade dependencias de producción ni
un comando al instalador. No activa coordinación, automatizaciones ni chats reales.
Las identidades suministradas son datos de prueba, no autenticación de Codex.

El 2026-11-15 se conectó este auxiliar con dos chats reales de prueba mediante
mensajes y un runner local; véanse [resultados y límites de esa prueba guiada](prueba-integracion-mensajes-coordinacion.md).
El demo sigue siendo independiente y esto no activa el protocolo de producción.

Para aplicar el flujo en cada rol, consultar las instrucciones del
[coordinador](coordinacion/coordinador.md), del
[chat de tarea](coordinacion/tarea.md) y el
[contrato operativo compartido](coordinacion/flujo-avisos.md).
Son documentos de uso, no una skill instalada ni un adaptador de transporte.

Desde `packages/aikit-installer`, ejecutar `npm run build`. Crear explícitamente
una carpeta ficticia vacía y pasar su ruta absoluta:

```powershell
node dist/coordination-demo.js C:\ruta\privada\proyecto-ficticio
```

El demo rechaza carpetas no vacías y rutas relativas. Activa un proyecto ficticio,
crea T-001 con asignación fija y primer ciclo, aplica un aviso, reconstruye índices
y consulta el acuse desde otra instancia del store. La salida JSON debe indicar
`result: aplicado` y contener el aviso íntegro y la generación confirmada.
La carpeta queda disponible para inspección; no se limpia automáticamente.

La raíz debe existir y no contener enlaces simbólicos ni junctions en sus
componentes. En POSIX debe tener permisos 0700. En Windows se consulta GetAccessControl:
solo el usuario actual, SYSTEM y Administradores pueden tener permisos de escritura.
Una política no interpretable o un grupo adicional con escritura detiene el demo.
No se modifican ACL para adaptarlas silenciosamente. `chmod(0600)` no se presenta
como protección de Windows. La sustitución de un archivo existente utiliza el
adaptador File.Replace del instalador, verifica el respaldo y compara su SDDL
antes/después; los temporales y destinos también pasan la política de permisos.
Esta comprobación local no acredita una política organizativa de privacidad.

La API interna se importa de `dist/coordination/store.js`:

```javascript
const store = new CoordinationStore({
  root: 'C:\\ruta\\privada\\proyecto-ficticio',
  projectId: '00000000-0000-4000-8000-000000000001',
  coordinatorChatId: 'coordinador-ficticio',
  ownerEpoch: 1,
});
store.activate('Autorización de la prueba ficticia');
store.createTask('T-001', 'tarea-ficticia', 'Asignación fija autorizada');
// store.apply(avisoCompleto, 'Motivo autorizado');
// store.query('T-001', avisoCompleto.updateId);
```

`apply` valida documentos y aviso, adquiere exclusión global con `wx`, recupera
operaciones preparadas y vuelve a validar autoridad y generaciones. Estado y
acuse se publican juntos en TAREA.md. Un duplicado idéntico devuelve el recibo
existente; los antiguos conservan current. Las contradicciones se registran como
incidentes sin destruir el original, incluidas colisiones de ID entre tareas.
Avisos de otro chat o ciclo quedan pendientes. No hay API para relevar, reasignar,
abrir otro ciclo o resolver pendientes: se mantienen para una entrega posterior.
`query` devuelve `incierto`, sin recibo positivo, si el canónico falta o es inválido;
un canónico completo permite consultar el acuse aunque falte completada.json.

Los documentos usan el encabezado y bloque JSON v1 acordados. Se rechazan claves
duplicadas y desconocidas, UTF-8/Unicode inválido, BOM, números no seguros y estados
no admitidos. La validación vincula proyecto/ruta, generación, current y recibos.
Los siete estados conservan la escritura del contrato: Preparada, Esperando al
usuario, En curso, Bloqueada, Pausada, Finalizada y Cancelada.

Cada operación conserva base o ausencia explícita, propuesta, manifiesto con
hashes SHA-256 y lista de preparación sincronizados. La publicación relee los
bytes exactos antes de confirmar el marcador completada. Un fallo conserva diario,
temporales, respaldos y bloqueo; no restaura ni reintenta por el código de error.
La operación siguiente no se ejecuta si una anterior sigue siendo ambigua.

INDICE.md y ENTREGAS.md son derivados y nunca acreditan unicidad ni acuses.
El acuse confirma exclusivamente TAREA.md; no acredita que los derivados estén
actualizados. En este prototipo el llamante sigue expresamente la secuencia
`apply(aviso, motivo)` y después `rebuildIndex()`, como hace el demo. Una
interrupción entre ambas llamadas conserva el acuse canónico; tras recuperar
la exclusión, reconstruir los índices no vuelve a aplicar el aviso.
`rebuildIndex()` los reconstruye expresamente bajo exclusión, con preparación,
temporal, respaldo y marcador propios. Un fallo de índices no revierte avisos ya
confirmados. Los diarios de derivados completados son históricos y su archivo
puede faltar; la reconstrucción explícita lo regenera. Referencias arbitrarias
se muestran como texto JSON, nunca se ejecutan ni se utilizan como destinos.

## Recuperación supervisada

Un bloqueo existente, incluso vacío, impide otro escritor. No se borra por edad,
PID ausente o reinicio. El auxiliar no incluye ninguna función de retirada del
bloqueo. Antes de intervenir, detener todos los escritores y automatizaciones,
comprobar su inactividad y reservar un solo operador. Conservar copia íntegra del
bloqueo, operaciones y temporales antes de retirar o mover el bloqueo con una
acción manual autorizada. Si no puede garantizarse esa exclusividad, detenerse.

Después, crear el store con la misma raíz, proyecto, coordinador y epoch y llamar
`recover()`. Adquiere un bloqueo nuevo. Si el canónico coincide con la base y la
preparación está completa, publica la propuesta guardada sin repetir decisiones.
Si coincide con la propuesta, completa el marcador. Una versión posterior debe
contener la evidencia inequívoca del operationId y aviso, o su registro
administrativo. Nunca se restaura una base antigua encima de una versión posterior.
Una preparación incompleta, temporal previo, marcador parcial, hash incorrecto,
canónico inválido o evidencia ambigua conserva el bloqueo para inspección humana.
No se ofrece una reparación destructiva automática de estos casos.

Las pruebas de `test/coordination-*.test.cjs` cubren parser, decisiones, colisiones,
fallos de las fases de publicación, bloqueo vacío, procesos y adaptadores de
sustitución/permisos. Las pruebas controladas no acreditan ACL reales. Las pruebas
nativas acreditan únicamente la plataforma y entorno donde se ejecutaron.
En el sandbox de Windows, un principal de escritura adicional puede provocar
el rechazo esperado antes de crear datos: la prueba comprueba la raíz vacía y
marca explícitamente como omitida la ruta positiva. Para exigir esa ruta sin
permitir dicha omisión, definir `AIKIT_REQUIRE_NATIVE_ACL=yes` y ejecutar la prueba
`demo nativo` en un entorno cuya ACL permita exclusivamente los principales
admitidos. Se verificó la ruta positiva fuera del sandbox en Windows el
2026-11-14: una prueba correcta, cero omisiones; también se acreditó el rechazo
de una segunda ejecución sobre la carpeta ya poblada. La ejecución completa
del paquete pasó tipos, lint y formato, con 75 pruebas correctas y tres omitidas
en el sandbox (esta ruta positiva y dos pruebas históricas de junctions).
Evidencias locales: `.aikit/025-verify-final.log` y `.aikit/025-native-acl.log`.
El alcance cubre interrupción de proceso en almacenamiento local; no promete
durabilidad ante apagones, carpetas de red, sincronización entre equipos o
escritores externos que ignoren el bloqueo. Los directorios se sincronizan donde
la plataforma lo permite; en Windows no se afirma fsync de directorios.

## Validación posterior a revisión — 2026-11-15

Se corrigieron pérdidas de precisión en literales numéricos, reutilización de IDs
que solo constaban como incidentes y contradicciones entre avisos pendientes.
Las referencias se representan en bloques JSON literales, sin activar Markdown.
La política Windows comprueba también propietario, directorios intermedios y lock;
la consulta ACL está limitada a 15 segundos. En POSIX se rechaza antes de publicar
un modo que no pueda conservarse. Rechazos explícitos sin operación incierta
liberan solo el bloqueo propio; una interrupción o un diario ambiguo lo conserva.

El coordinador ejecutó npm run verify con código 0: 83 pruebas correctas y seis
omisiones documentadas. Se verificaron fuera del sandbox tres casos nativos
Windows sin omisiones: ambas redirecciones reales y el demo con ACL/File.Replace.
POSIX real sigue sin verificarse en Windows; su regresión controlada pasó.
Logs finales: .aikit/025-verificacion-coordinador.log y
.aikit/025-review-fixes-native.log. Las cifras anteriores conservan la trazabilidad
de la primera pasada, no sustituyen estos resultados posteriores a las correcciones.
