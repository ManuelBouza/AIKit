# Binding seguro al servicio existente de OpenCode

Estado: opción 1 elegida por el usuario; revisión técnica completada por Beam
Free de Kilo (high). Pendiente de aprobación del documento. No implementado
ni instalado.

## Propósito y cobertura

Conectar las tareas de AIKit a un servicio OpenCode ya encendido para observar,
interrumpir y continuar la sesión correcta. Codex conserva diseño y coordinación;
OpenCode ejecuta trabajo y revisión según capacidad, con Free adecuados primero.
No cambia roles, subagentes ni archivos de Superpowers.

Se reutilizan `session_store`, `session_worker` y `session_backend` de las etapas
1–3. Superpowers aporta diseño, planes y revisión; la carencia es una fábrica
real de `TrustedBinding` y un transporte que no arranque servidores al consultar.
No hace falta otra skill ni otro MCP.

## Enfoques y decisión

1. **Servicio existente, sin autoarranque: elegido por el usuario.** Reutiliza su
   autenticación normal y sesiones durables; comparte proceso con otros clientes,
   por lo que AIKit controla únicamente sus propias sesiones.
2. Servidor exclusivo: descartado para esta entrega. Añade custodia y ciclo de
   vida propios, y su arranque puede participar en recuperación de claims.

La elección no autoriza iniciar, reiniciar, actualizar, detener o reconfigurar el
servicio compartido. Si falta, AIKit devuelve `service_unavailable`. Sin intento
vivo o incierto que duplicar, la tarea puede seguir por el fallback nativo acordado.

## Descubrimiento sin efectos de arranque

OpenCode 2.2.0 distingue `Service.discover()` de `Service.ensure()`. El primero
lee el registro y comprueba salud/versión; no crea procesos. La nueva fábrica
Python reproduce ese contrato con biblioteca estándar, sin añadir un runtime
JavaScript. El cliente oficial es la referencia semántica.

El registro procede de la ubicación del usuario/canal acreditada por OpenCode,
no de `TaskRecord`, `opencode.json`, prompts o archivos del proyecto. Cualquier
configuración de ubicación debe pertenecer al host confiable, fuera de los datos
de tarea. No se usa `ensure`, `api` con descubrimiento implícito ni `--standalone`
como alternativa ante un fallo.

Una ausencia, esquema desconocido, enlace/reparse no confiable o identidad no
comprobable produce un error estable sin conexión ni arranque. No se modifica el
registro. Se limita tamaño y complejidad de JSON; errores no imprimen su cuerpo.

## Identidad y autenticación

Antes de vincular se comprueban registro estable, ID de instancia, URL, PID,
nacimiento real del proceso y versión. La respuesta autenticada `/api/info`
debe concordar con PID/versión; no aporta por sí sola el nacimiento. Windows usa
la identidad de creación del SO; otras plataformas requieren prueba equivalente,
o devuelven capacidad no disponible. La hora actual no sustituye esa prueba.

El token opaco de AIKit deriva de la identidad de instancia/proceso verificada;
no contiene dirección ni credenciales. `TaskRecord.server_identity` conserva
solo ese token. Leer un token del registro de una tarea no crea autoridad.

Solo se admiten direcciones locales literales de loopback, puerto válido y ruta
base prevista. No DNS, usuario en URL, query, fragmentos, redirects ni proxies.
La credencial del registro se usa con la autenticación normal de OpenCode y se
mantiene en memoria; no se copia a `.aikit`, Git, logs, prompts o argv.
Si falta autenticación requerida o no puede acreditarse el origen del registro,
el binding queda indisponible; no se cambia la configuración para habilitarlo.

La identidad se comprueba antes de cada petición y tras la respuesta antes de
publicar una conclusión. Reinicio, PID reutilizado, cambio de registro/credencial
o discrepancia invalidan el binding; no se adopta otro servidor ni se reintenta
una mutación. No se promete fencing ni ejecución exactamente una vez.

## Transporte de inferencia y preflight

El supervisor conserva una referencia al binding verificado y lanza el cliente
con `--server <URL verificada>`, sin `--standalone`. La credencial llega por el
mecanismo normal de entorno de ese hijo (`OPENCODE_PASSWORD` en 2.2.0), sin
alterar el entorno global. El hijo no recibe autoridad para administrar el
servicio. Una conexión fallida no cae al descubrimiento implícito ni a otro host.

El catálogo y la configuración efectiva se consultan por el mismo binding y en
la ubicación de proyecto exacta: `GET /api/model` y `config.get`,
`GET /api/config`, con `location[directory]` explícito. La comprobación de
viabilidad en el servicio 2.2.0 existente devolvió una lista de cuatro fuentes
de configuración y pasó el validador actual sin copiarlas al proyecto.
Se reutilizan las reglas del certificado actual:
`provider.use openai deny` y `tool.use subagent:* deny`; un archivo local aislado
no acredita por sí solo la configuración efectiva. Si la API no permite obtener
el equivalente necesario, el preflight falla cerrado; no usa `debug config
--standalone` como sustituto. El plan incorporará esa consulta antes de migrar
las rutas legadas de `doctor`, `_catalog` y `_check_restrictions`.

Selección de modelo/esfuerzo, motivo y tarifa siguen siendo explícitos. Cada
inferencia se anuncia. El diseño no habilita todavía `quota_resume`: cambiar
modelo y modificar política son capacidades distintas; su excepción exige
otro contrato acotado, manteniendo la autorización del usuario ya registrada.

## Sesiones y procedencia

Un intento nuevo se reserva bajo los bloqueos existentes. El coordinador registra
el binding antes del envío y el supervisor captura el ID real de sesión desde
el cliente ligado. Se conservan directorio, rol, modelo y procedencia del intento.
Los datos de evento se validan, incluidas identidades contradictorias.

Solo se permite control cuando concuerdan tarea/intento autorizado, sesión,
directorio, rol y propietario actual. Una sesión que simplemente aparece en la
base de datos compartida no queda adoptada por AIKit. Tampoco un título o un
`server_identity` editado en JSON constituyen prueba independiente de origen.
La procedencia se conserva además en un registro del host, separado del proyecto:
`<CODEX_HOME>/state/aikit/tasks/`, con ubicación decidida por la instalación
confiable. No contiene credenciales. El supervisor escribe allí, bajo bloqueo y
de forma atómica, tarea/intento, raíz canónica, rol, binding y sesión observada.
Cada operación coteja ambos registros; una discrepancia o falta del registro del
host devuelve `provenance_unavailable`, sin reconstruirlo desde el proyecto.
CLI y MCP usan el mismo registro. Se valida propietario/permisos/rutas del host;
esta separación protege la frontera con datos del proyecto y no constituye un
sandbox frente a programas con los mismos permisos del usuario.

Recuperar la procedencia tras reinicio requiere un registro del host existente y
coherente, registro OpenCode estable y nueva comprobación del nacimiento del
proceso. Un cambio de instancia no se adopta automáticamente. No se eliminan
entradas inciertas por antigüedad. La implementación de escritura fuera del
checkout se hará por los permisos de instalación autorizados, sin escalación
global ni creación de este estado durante la presente fase de diseño.

Sesiones legadas `--standalone` permanecen sin binding. La adopción o migración
queda fuera de esta entrega: se exigen pruebas de finalización/reconciliación y
un procedimiento explícito antes de continuar su contexto en otro propietario.
No se arranca un servidor para comprobar si otro trabajo sigue activo.

## Control y pérdida de conexión

El backend conserva sus presupuestos totales de 10 s y sus comprobaciones de
sesión/directorio. Interrumpir requiere actividad observada del propietario;
ACK no equivale a cierre. La confirmación es puntual y local al proceso, con
comprobación de asentamiento/sucesor. Si se pierde una respuesta, no se repite el
POST ni se reenvía el prompt sin reconciliar.

La muerte del cliente no prueba que el modelo haya parado. Forzar cierre, cuando
corresponda a la etapa 4, alcanza solo procesos cliente/supervisor propios con
identidad comprobada; jamás el servidor compartido ni procesos de otras tareas.
Un trabajo incierto impide lanzar otro intento que lo duplique. Las consultas
fallidas conservan artefactos, sesión y estado desconocido.

Cuando termina una tarea se cierran conexiones y se descartan las credenciales
en memoria; el servicio continúa bajo OpenCode. No se promete borrado seguro de
memoria ni aislamiento frente a código con los mismos permisos del usuario.

## Componentes y aceptación

### Decisiones concretas del coordinador tras la revisión técnica

Estas precisiones son propuestas de Codex para este contrato, no preferencias
nuevas atribuidas al usuario:

1. **Nacimiento y token.** En Windows se usa `OpenProcess` con consulta limitada
   y `GetProcessTimes`; se conserva el FILETIME de creación de 64 bits para
   identidad y su conversión UTC para `started_at`. No se solicita depuración ni
   se termina el proceso. La primera fábrica acredita Windows; otro SO devuelve
   `process_identity_unavailable` hasta disponer de implementación equivalente
   verificada. El token es `aikit-owner-v1-` seguido de SHA-256 hexadecimal de un
   array JSON UTF-8 compacto `[1, registration_id, canonical_url, pid,
   birth_filetime_decimal, version]`. No contiene ni deriva de la contraseña.
   Releer registro e identidad debe producir el mismo token. Una credencial
   distinta se detecta por comparación solo en memoria e invalida el binding,
   aunque el token de proceso no cambie; no se intenta autenticar con ella hasta
   una nueva adquisición explícita y comprobada.

2. **Directorio.** Se aplica la misma validación del almacén actual a raíz y
   rutas gestionadas: ruta absoluta, resolución canónica, rechazo de enlaces y
   reparse points en los componentes controlados. En Windows la comparación usa
   la clave de `normcase` de esa ruta resuelta; no se aceptan rutas relativas,
   `C:relativa`, raíz sin unidad o URI. La misma clave se guarda en el registro
   del host y se compara con `location.directory` absoluto del API. Para el token
   de URL se normalizan esquema/host de IP literal y puerto explícito, con ruta
   raíz única y sin los componentes prohibidos; no se resuelve DNS.

3. **Registro del host.** Esquema `version: 1`, con `task_id`, `project_root`,
   `role`, `current_attempt_id` y `attempts`. Cada intento conserva `attempt_id`,
   `launch_nonce`, `binding_token`, `session_id` nullable, selección de modelo,
   identificadores/arranque de cliente y supervisor si acreditados, fuente/fecha
   y fase `reserved|client_started|session_observed|terminal_observed|uncertain`.
   UUID canónicos, campos conocidos y tipos se validan; esquema futuro o corrupto
   no se sobrescribe. Bloqueo de SO por tarea y reemplazo atómico en el mismo
   directorio, reutilizando las garantías del almacén, con permisos del usuario.
   Solo el supervisor confiable publica la procedencia del lanzamiento.

4. **Orden de escrituras.** Reserva del host antes del registro de proyecto y
   antes del envío; al capturar sesión, primero host y después proyecto. No se
   afirma atomicidad entre ambos directorios. Cualquier caída/discrepancia deja
   `provenance_unavailable/uncertain`, sin inferir otra vez ni reconstruir el host
   desde el proyecto. La reconciliación usa el registro del host y artefactos del
   supervisor; si no bastan, conserva el bloqueo de duplicación. La existencia
   de sesión por sí sola no acredita admisión del prompt.

5. **Preflight y petición.** Orden fijo: adquirir/verificar binding; leer
   `config.get` (`GET /api/config`, es la misma operación, no otra consulta);
   validar certificado; leer `GET /api/model`; validar modelo/variante/motivo;
   reservar intento; volver a comprobar binding; enviar por canal explícito.
   Cada error termina ese intento de preflight sin iniciar servicio, retirar
   bloqueos ni enviar al modelo. Un fallo de autenticación no cambia a otro host
   o credencial automáticamente. `doctor` solo hace la parte de consulta; la
   comprobación de permisos protege cualquier envío real, independientemente de
   que el catálogo ya hubiera sido consultado para elegir modelo.

6. **Cierre.** Se reutiliza `session_backend` ya aceptado: `session.get` con
   coincidencia de ID/directorio, `session.active` del propietario (`data` con
   entradas `{type: "running"}`), POST `session.interrupt` con `resume=false` y
   dos muestras consecutivas de ausencia, con propietario fresco y presupuesto
   total 10 s. Un sucesor observado, cambio de binding o respuesta perdida
   conserva `confirmed=null`. No se rediseña este algoritmo en la fábrica.

7. **Respuesta perdida.** El intento pasa a `uncertain` con sesión/artefactos y
   posición de envío conocida. Si solo falló el GET de preflight, no hubo envío.
   Si pudo enviarse el prompt, se conserva el mismo intento: consultar únicamente
   al propietario acreditado, esperar si hay actividad, y recuperar el resultado
   del supervisor si hay terminal correlacionado con ese intento. Un servidor
   idle no prueba por sí solo entrega o rechazo del prompt. Sin evidencia de
   admisión/rechazo y resultado ligada al intento, permanece desconocido: no
   reenviar ni ejecutar en paralelo por fallback. La etapa 4 definirá su lector
   de admisiones/inbox; esta fábrica no promete resolverlas a partir de un título,
   un cursor histórico ni una sesión que exista. Reintentar una lectura segura
   requiere una nueva consulta; nunca implica repetir POST o prompt.

La fábrica/conexión vive separada del parser de respuestas de `session_backend`;
un transporte autenticado ya ligado implementa su protocolo. El supervisor es
dueño de la procedencia del intento. CLI y MCP compartirán ese núcleo, sin copiar
políticas ni distribuir registros del usuario en el complemento.

La revisión técnica debe acreditar la consulta equivalente de configuración
efectiva en el servicio y revisar el registro del host entre procesos. Si falta
soporte, el diseño vuelve con esa limitación; no se rellena con supuestos.

Las pruebas usarán registro y servidor local falsos: servicio apagado sin spawn,
PID reutilizado, registro/credencial rotados, endpoint malicioso, autenticación
fallida, JSON extremo, sesión ajena, pérdida de respuesta y reinicio. Comprobarán
que no se ejecuta `ensure`, `serve`, `--standalone` ni una mutación repetida.
Después habrá una prueba mínima autorizada en servicio existente, con modelo
Free adecuado, evidencias sanitizadas y revisión independiente. No usar sesiones
históricas del usuario como pruebas ni afirmar control real por tests falsos.

## Fuentes y relación con el plan

- [Descubrimiento sin arranque, v2.2.0](https://github.com/anomalyco/opencode/blob/v2.2.0/packages/client/src/effect/service.ts).
- [Registro y autenticación, v2.2.0](https://github.com/anomalyco/opencode/blob/v2.2.0/packages/client/src/service-probe.ts).
- [Canales y configuración del servicio, v2.2.0](https://github.com/anomalyco/opencode/blob/v2.2.0/packages/cli/src/services/service-config.ts).
- [Resolución explícita de conexión, v2.2.0](https://github.com/anomalyco/opencode/blob/v2.2.0/packages/cli/src/services/server-connection.ts).
- [Contrato de sesiones](2026-10-30-sesiones-opencode-design.md) y [límites de etapa 3](../../sesiones-opencode.md).

Este diseño resuelve la puerta de binding de la etapa 3. Tras aprobación se
preparará un plan propio antes de integrar la etapa 4 existente. No autoriza
implementación, instalación, inicio de servicios ni push.
