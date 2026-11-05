# Observación y control de sesiones OpenCode

Etapa 3 del contrato de sesiones, contrastada con OpenCode **2.2.0**. El backend
productivo actual conserva observaciones locales y devuelve
`control_unavailable`: todavía no existe una fábrica de conexiones que acredite
el propietario del servidor privado de `run --standalone`.

## Comportamiento disponible

`session_backend.inspect_session(record)` no ejecuta CLI, red, descubrimiento de
servicios ni inferencia. Devuelve ejecución actual `unknown` y copia por separado
las observaciones locales con sus fuentes y fechas originales. La entrega local
completada sigue siendo histórica; no prueba inactividad actual. El cursor local
también se conserva como histórico, sin avanzar ni consumir logs.

`interrupt_session(record)` devuelve `requested=false`, `acknowledged=null` y
`confirmed=null` cuando falta el binding. No intenta interrumpir el servicio
habitual. `worker_interrupt` es el callback predeterminado del supervisor y, en
esa situación, devuelve `None`; el worker conserva su estado desconocido y sigue
drenando la salida, sin afirmar cancelación ni terminar procesos.

`BackendCapabilities` separa operaciones documentadas de acceso disponible.
`observation`, `control`, `model_change`, `quota_resume` y `logs` son falsas por
defecto. Que exista una operación en OpenAPI no acredita un canal que pueda
usarla. Tampoco una prueba con transporte falso acredita acceso productivo.

## Frontera del binding

El keyword opcional `binding` admite únicamente un objeto `TrustedBinding`
aportado desde código. El protocolo no es un certificado por su nombre: una
futura implementación debe proporcionar un transporte ya ligado y autenticado,
sin arrancar servicios, y comprobar de nuevo el propietario antes de cada
petición. Esta etapa solo define la interfaz y utiliza un cliente falso en tests;
no construye bindings desde JSON, variables de entorno o argumentos CLI.

La identidad esperada incluye un token opaco, PID, nacimiento comprobable del
proceso y versión. Debe coincidir con el token de `TaskRecord.server_identity`.
El nacimiento procede de la comprobación del sistema operativo del binding,
nunca de la hora de observación ni del PID por sí solo. `server.info` permite
contrastar PID y versión, pero no publica un instante de nacimiento.

Una identidad ausente, discrepante, reiniciada o no comprobable impide las
peticiones o invalida el control. El registro no aporta autoridad ni un endpoint:
el backend nunca interpreta `server_identity` como URL, ni añade credenciales,
proxies, redirects o descubrimiento del servicio habitual. La futura fábrica
necesita otro contrato de custodia de credenciales, endpoint y vida del servidor,
incluidas sus defensas frente a SSRF. No forma parte de esta entrega.

Cada inspección o interrupción comparte un presupuesto total de **10 segundos**
medido con reloj monotónico. El backend pasa únicamente el tiempo restante a
cada comprobación y petición; el transporte confiable debe respetar ese timeout.
No hay una implementación HTTP cuyo cumplimiento real se haya verificado aquí.
Los errores públicos son códigos fijos; no devuelven cuerpos ni excepciones del
transporte que pudieran contener credenciales o conversaciones.

## Operaciones acreditadas por OpenAPI instalado

| Operación | HTTP | Datos y límites |
| --- | --- | --- |
| `server.info` | `GET /api/info` | Respuesta directa con `version`, `pid`, `urls`, `paths`; no ofrece credencial ni nacimiento. Las URLs recibidas no se usan para conectar. |
| `session.get` | `GET /api/session/{sessionID}` | Envelope `data` con sesión y `location.directory`. Se comprueban ID y directorio antes del control. Un 404 tipado distingue sesión ausente. |
| `session.active` | `GET /api/session/active` | `data` es un mapa de sesiones con `{type: "running"}`. Solo informa de ejecuciones que posee ese proceso. |
| `session.inbox.list` | `GET /api/session/{sessionID}/inbox` | `data` es una lista. El backend acredita lista vacía; con elementos conserva `pending_count=null` y una limitación, sin inspeccionar payload ni deducir entrega. |
| `session.permission.list` | `GET /api/session/{sessionID}/permission` | `data` es una lista de solicitudes. Solo se cuenta la colección de objetos; no se interpreta su contenido ni se concede permiso. |
| `session.log` | `GET /api/experimental/session/{sessionID}/log` | SSE; parámetros `after` (secuencia codificada como string) y `follow` (`true`/`false`). Documentado, sin consumidor en esta etapa. |
| `session.interrupt` | `POST /api/session/{sessionID}/interrupt` | Respuesta directa `{interrupted: boolean}`. La llamada condicional del backend especifica `resume=false`. |
| `session.switchModel` | `POST /api/session/{sessionID}/model` | Body `{model: {id, providerID, variant?}}`; respuesta 204. Documentado, sin mutador habilitado. |

Los envelopes anteriores proceden del esquema HTTP capturado: no se extrapola
el formato de salida de otros comandos CLI. Los tipos que se consumen se
validan, incluidos booleanos frente a enteros, números finitos y el único estado
`running` acreditado. Campos como títulos, payloads, credenciales o texto de
errores no se publican. Una lista de permisos no demuestra `waiting`; tampoco
`active` permite inventar `retrying` o una espera de entrada.

No se consulta `session.log`: `SessionLogItemEncoded` figura como string JSON y
no se acreditó un consumidor de su contenido. `logs=false` y `log_evidence=()`
expresan esa limitación. Repetir el mismo cursor no produce evidencia nueva ni
autoriza reenvíos. Un terminal histórico no vence una muestra actual `running`.

## Interrupción condicional

Solo un binding verificado puede habilitar el camino de control. Primero se
comprueban el servidor, la existencia de la sesión, su directorio y una ejecución
activa del propietario. La ausencia de actividad local no acredita interrupción
exitosa y no produce POST preventivo.

`requested` indica que se intentó el envío por el canal comprobado; incluso una
respuesta perdida conserva esa incertidumbre sin repetir el POST.
`acknowledged=true` exige el booleano `interrupted=true` de la API y significa
aceptación. No significa que los finalizadores hayan terminado.

Después del ACK se comprueba el mismo propietario y se buscan dos muestras
consecutivas de `active` sin esa sesión, dentro del presupuesto común. Una
actividad sucesora entre las muestras devuelve `successor_activity` con
`confirmed=null`. Un timeout o cambio de identidad tampoco confirma cierre.
`confirmed=true` es una observación puntual del asentamiento en ese proceso: no
es fencing, autoría criptográfica, inactividad global ni garantía de que otro
cliente no envíe trabajo después. La observación histórica de entrega no se usa
para confirmar el cierre.

## Modelo y excepción por cuota

La API instalada acredita cambiar el modelo seleccionado en una sesión. Eso no
acredita que el proveedor sea utilizable: las políticas `provider.use` pertenecen
a configuración/administración y filtran el catálogo. Los permisos de sesión son
otra capa y no restituyen un proveedor retirado por una política efectiva.

`quota_resume` permanece deshabilitado. No se ha acreditado un mecanismo que
permita una excepción de proveedor para la recuperación autorizada sin retirar
el bloqueo general ni contradecir un `deny` vigente. Esta limitación corresponde
al contrato disponible, no afirma imposibilidad para cualquier diseño futuro.
El backend no cambia modelo, permisos, política ni cuentas.

## Evidencia factual y límites

Los probes propios del preflight consultaron `server.info`, OpenAPI y metadatos
de una sesión histórica de AIKit. La sesión era visible desde otro servidor
privado con `active` vacío: existencia en almacenamiento no demuestra propiedad
de ejecución. Una sesión ficticia ausente produjo código CLI 1 y
`SessionNotFoundError`. Tras terminar un probe propio, su PID ya no existía
(`OpenProcess` error 87) y el puerto privado estaba cerrado. No se probó una
interrupción o continuación real ni se enviaron prompts.

La fuente etiquetada 2.2.0 muestra que `standalone` genera una credencial privada
y un hijo `serve --stdio --port 0` cuya vida depende del pipe del cliente.
El endpoint y la credencial permanecen dentro de esa conexión; no se acreditó
un mecanismo seguro para recuperarlos desde el `run` actual.

Además, el cierre del servidor puede conservar claims para recuperación en un
arranque posterior. Aunque los probes solicitaron **cero llamadas inferenciales**,
no se midió la recuperación automática: no se afirma cero inferencias observadas
universalmente. No se hicieron más probes standalone después de identificarlo.

Esta limitación también afecta a rutas previas del adaptador: `_catalog` ejecuta
`api --standalone GET /api/model`, `doctor` llama a ese catálogo y
`_check_restrictions` ejecuta `debug config --standalone`. Son consultas sin
prompt solicitado que pueden iniciar privados; no deben presentarse como
preflight universalmente libre de efectos de arranque. Esas rutas de
`delegate.py` se conservan fuera del alcance de la etapa 3. El backend nuevo
no las usa para inspeccionar ni controlar.

Las pruebas nuevas emplean respuestas sanitizadas y un binding falso, sin red
ni modelos. Cubren identidad/reinicio, ausencia de binding, sesión/directorio,
datos malformados, historia frente a actividad, envío incierto, ACK, sucesor y
presupuesto compartido. No certifican una integración real con el servidor
privado. La revisión independiente y los resultados finales se registran como
evidencia local por separado.

## Fuentes primarias

- [Servidor privado, etiqueta v2.2.0](https://github.com/anomalyco/opencode/blob/v2.2.0/packages/cli/src/services/standalone.ts).
- [Resolución de conexiones, v2.2.0](https://github.com/anomalyco/opencode/blob/v2.2.0/packages/cli/src/services/server-connection.ts).
- [Ejecución y ACK de interrupción, v2.2.0](https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/session/execution.ts).
- [Asentamiento y ejecución sucesora, v2.2.0](https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/session/run-coordinator.ts).
- [Selección de modelo y permisos de sesión, v2.2.0](https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/session/session.ts).
- [Filtrado de proveedores por política, v2.2.0](https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/config/plugin/policy.ts).
- [Políticas, documentación actual](https://dev.opencode.ai/v2/docs/policies), contrastada con la etiqueta y OpenAPI instalado.

Context7 ayudó a localizar fuentes de la rama `dev`; no se equiparó esa rama con
el binario instalado. El presupuesto de tres consultas de la etapa está agotado.
