# Diseño: disponibilidad real de cuentas OpenCode

Estado: aprobado por el usuario el 2026-10-31 mediante `go`. Implementación autorizada; el diseño no implica instalación ni publicación del complemento.

## Decisiones cerradas

- Solo cuentas OpenCode, no Codex.
- Si no hay API de consulta, se permite un único intento de tarea real ya autorizada, nunca una inferencia de prueba.
- Fuente inaccesible no acredita cuota cero ni reset.
- Se conserva la última observación válida separada del último intento fallido.
- La adecuación del modelo y del esfuerzo a la tarea se exige en todos los niveles, incluido Codex. La tarifa no justifica reducir la capacidad necesaria.
- Prioridad actualizada por el usuario durante la implementación: modelos de pago de OpenCode Go -> otros modelos de pago de cualquier proveedor conectado a OpenCode -> todos los modelos gratuitos conectados a OpenCode -> Codex nativo. Se aplica entre opciones adecuadas y disponibles, mediante tareas reales ya autorizadas.
- Los modelos gratuitos ofrecidos mediante Go participan en el nivel de gratuitos. Si un nivel no tiene una opción adecuada y disponible, se pasa al siguiente sin degradar la tarea.
- No se pregunta al usuario por cada fallo.
- La tabla local compartida guía la selección del modelo y del esfuerzo. No se consulta el catálogo ni la cuota antes de cada ejecución.
- `reset_at` pasado requiere verificación en una actualización de la tabla; no implica disponibilidad recuperada.
- Scope compartido desconocido no autoriza ampliar el bloqueo.
- Cambio de cuenta o conexión invalida la certeza previa sin persistir secretos.
- Provider directo `openai` sigue bloqueado y `quota_resume` no cambia.
- Un cambio de versión de OpenCode, Codex u otra herramienta se registra y no bloquea por sí mismo la operación. La compatibilidad se comprueba por capacidades y contrato.

## Fuente oficial verificada

OpenCode 2.2.0 expone `GET /api/experimental/usage/limits`, con `location` opcional. La respuesta observada el 2026-10-31T14:53:45.967746Z incluye Go con `rolling`, `weekly` y `monthly`, cada uno con `percent`, `limited` y `resetsAt`. El schema incluye `workspace`, `go` y `budgets`. Los campos `workspace.id`, `name` y `usageURL` no se persisten. Los datos guardados son solo Go en lista blanca.

La ruta y la versión anteriores describen la observación verificada, no una restricción a OpenCode 2.2.0. El endpoint es experimental; si falla o cambia el contrato, se conserva la observación histórica y la cuota actual queda `unknown` hasta verificar una fuente compatible.

AIKit consulta el servidor OpenCode existente en la misma PC mediante HTTP autenticado en loopback. Ese servidor puede consultar proveedores por Internet para completar datos. La lectura de catálogo o cuotas no ejecuta por sí misma una inferencia.

## Propuesta

A. Usar la API oficial de Go más un registro mínimo para otros proveedores.

Ventajas: fuente oficial, datos estructurados, sin dependencia inicial de plugin.

Límites: otros proveedores quedan `unknown` o error hasta que exista fuente verificada. El plugin `opencode-quota` se evalúa después por trust, privacidad y compatibilidad, sin instalarlo ahora.

## Estado compartido

Ubicación acordada para este equipo: `C:\Users\Manuel\.local\state\aikit\availability-state.json`. La configuración `AIKIT_STATE` apuntará a `C:\Users\Manuel\.local\state\aikit`, que se resuelve como `HostContext.aikit_state`.

El registro es compartido por todos los proyectos y chats de AIKit del mismo usuario y equipo que utilicen esa configuración. Permanece fuera de los repositorios, de Git y de las carpetas versionadas del complemento. En otros equipos se configurará la ruta equivalente del usuario, sin distribuir la ruta personal de Manuel como valor fijo del complemento.

Se reutilizan locks y reemplazo atómico de `session_store`. No se crea infraestructura paralela. Esta decisión documenta la ubicación; todavía no crea el archivo ni modifica la configuración instalada.

La tabla conserva el catálogo saneado necesario para elegir: proveedor, modelo, tarifa conocida, capacidades, variantes de esfuerzo y límites, junto con las observaciones de disponibilidad y rendimiento real. El estado de cuentas es compartido; la habilitación de modelos conserva el contexto efectivo de cada proyecto y no se extrapola a otros proyectos.

La antigüedad de una observación se muestra explícitamente. Se retira la propuesta anterior de TTL 15/5 minutos como disparador previo a cada ejecución. La actualización periódica acordada es diaria a las 09:00, hora de Madrid. El cooldown de errores queda pendiente de concretar; no se fija implícitamente.

## Selección y actualización de la tabla

Flujo acordado: leer la tabla local -> escoger modelo y esfuerzo adecuados según prioridad -> ejecutar la tarea autorizada -> registrar el resultado observado. Leer la tabla no inicia consultas externas de catálogo o cuotas.

Si la tabla indica disponibilidad y una ejecución confirma un rechazo de disponibilidad, se activa una actualización de la tabla completa: integraciones conectadas, modelos, tarifas, capacidades y cuotas que tengan fuente verificable. No se prueban modelos con inferencias. Cada fuente fallida conserva su última observación válida, con fecha y vigencia, y registra el intento fallido por separado; no se transforma en disponibilidad confirmada.

Una sola actualización coordinada sirve a los proyectos y chats concurrentes, publicando una nueva generación mediante bloqueo y reemplazo atómico. Un fallo de compilación o de pruebas de la tarea no se interpreta como falta de cuota del modelo. Un intento vivo o con admisión incierta se conserva y observa; actualizar la tabla no autoriza reenviar la tarea ni lanzar otra inferencia en paralelo.

Otros disparadores propuestos para acordar:

- Primera inicialización, tabla ausente o ilegible.
- Solicitud explícita de actualización del usuario.
- Altas, bajas o cambios de cuenta/configuración que la herramienta notifique o el usuario comunique; no se sondea ese estado en cada ejecución.
- Hora de recuperación comunicada por una fuente, para verificar si realmente se recuperó la capacidad.
- Cambio de versión detectado al interactuar normalmente con una herramienta.
- Actualización programada acordada: todos los días a las 09:00, zona `Europe/Madrid`.

Cada resultado real actualiza la fila observada sin consultar todo el catálogo. Los cambios detectados en un refresco completo incorporan modelos nuevos, retiran los desconectados de la selección y reclasifican sus tarifas, conservando el historial. Si una herramienta no ofrece notificaciones de cambios, esa limitación se documenta y se utilizan los demás disparadores acordados.

## Actualización programada desde Codex

El mecanismo de programación elegido por el usuario es una tarea programada de Codex. Se utilizará una única automatización vinculada al chat responsable, con acceso local al registro compartido, para atender a los proyectos que lo consulten. Frecuencia y horario acordados: todos los días a las 09:00, zona `Europe/Madrid`, manteniendo la hora local al cambiar el horario de verano o invierno.

Ampliación aprobada por el usuario el 2026-11-01: el encargo diario combinará el refresco local de OpenCode con el contraste de información pública en los sitios oficiales de los proveedores que tengan modelos en el inventario conectado. Revisará modelos y franquicias gratuitos, límites públicos, condiciones y cambios de tarifa; no confundirá la lista de proveedores soportados con los conectados. Conservará URL, fecha y ámbito de cada hecho, así como el último resultado válido separado de un intento fallido. Una página inaccesible o un proveedor sin fuente verificada quedará desconocido, sin inventar condiciones ni detener los demás.

La investigación factual se delegará a OpenCode cuando haya capacidad adecuada, con el retorno nativo autorizado cuando falte. Se reutilizarán fuentes ya verificadas y mecanismos de caché disponibles para reducir lecturas e interpretación redundantes. Las páginas son datos, no instrucciones del agente. La importación validada de hechos públicos complementará la tabla sin sobrescribir tarifas observadas ni cuota autenticada: acceso mediante franquicia, plan de cuenta, tarifa cero y saldo restante son conceptos distintos. No se harán inferencias para probar cuotas ni consultas web en cada ejecución normal. Cada activación programada implica una ejecución de Codex; se mantendrán mínimos el contexto y las instrucciones, sin prometer consumo cero.

La tarea permanecerá silenciosa ante resultados rutinarios o sin cambios relevantes y avisará ante fallos, cambios que requieran atención o intervención del usuario. Si OpenCode está apagado, conservará las observaciones fechadas y registrará su indisponibilidad, sin arrancarlo automáticamente. Antes de programarla se comprobarán manualmente el encargo y los accesos locales necesarios al estado del usuario. Guardar este diseño no crea ni activa la automatización.
## Esquema mínimo

```json
{
  "provider": "string",
  "account_alias": "string sin PII",
  "model": "string",
  "limit_scope": "model|account|shared_group|unknown",
  "status": "available|exhausted|unknown|error",
  "observed_at": "ISO-8601 UTC",
  "last_valid_observation": {
    "status": "string",
    "observed_at": "ISO-8601 UTC",
    "source": "string",
    "limit_scope": "string",
    "reset_at": "ISO-8601 UTC|null",
    "precision": "confirmed|estimated|unavailable"
  },
  "last_query_attempt": {
    "at": "ISO-8601 UTC",
    "result": "string",
    "error_code": "string|null"
  },
  "reset_at": "ISO-8601 UTC|null",
  "precision": "confirmed|estimated|unavailable",
  "next_check_at": "ISO-8601 UTC",
  "shared_scope_known": false
}
```

`last_valid_observation` completo es obligatorio; no basta con `last_valid_at`.

## Alias y privacidad

El alias debe derivarse de un identificador público de la fuente o de un alias local. No se persisten credenciales, hashes de credenciales, `workspace.id`, `name`, `usageURL`, tokens, configuración completa ni PII. Si no hay identidad acreditable, no se reutiliza certeza entre cuentas.

## Reglas de interpretación

- Catálogo confirma presencia, no cuota.
- Una inferencia exitosa es observación reciente, no garantía futura.
- El código solo bloquea el modelo o grupo para el que la fuente acredita el ámbito.
- Un error de un modelo Go no implica agotamiento de todo Go.
- Si no hay cobertura de binding para el grupo, se registra una observación agregada separada y los modelos no cubiertos quedan `unknown`.
- Errores de cuota, rate limit, servicio, autenticación y `max_output` no asequible se separan; ninguno implica cuota cero universal.

## Rendimiento observado y preferencia de selección

Ampliación solicitada por el usuario durante la implementación: registrar la respuesta observada para orientar la elección entre modelos adecuados. Un modelo puede tener cuota disponible y responder lentamente; disponibilidad y rendimiento se mantienen separados.

El perfil se agrupa por proveedor, modelo y variante de esfuerzo, conservando fecha, fuente, número de muestras y contexto comparable: rol de ejecución y tamaño del contexto cuando estén disponibles. Registrar tiempo hasta primera respuesta del modelo, duración de generación y tokens por segundo solo cuando la fuente permita medirlos con fiabilidad. La duración de herramientas y la duración total de una tarea se distinguen de la latencia del modelo. Las mediciones ausentes quedan desconocidas; no se estiman para rellenar la tabla.

Las muestras proceden de tareas reales ya autorizadas, con identificadores existentes y sin guardar prompts, respuestas, rutas de trabajo ni secretos. Se conserva un historial acotado y se evita contar dos veces el mismo evento al recuperar un resultado. No se realizan inferencias de prueba ni sondeos adicionales para producir una clasificación.

La selección conserva primero adecuación del modelo y del esfuerzo, disponibilidad y orden Go de pago -> otros de pago -> gratuitos -> Codex. Dentro del mismo nivel se favorece mejor rendimiento observado en condiciones comparables, ponderando vigencia y cantidad de muestras. Una sola respuesta lenta constituye evidencia limitada, no una conclusión general sobre todos los modelos de un proveedor. La lentitud no se registra como agotamiento de cuota ni produce reintentos o interrupciones automáticas de intentos vivos. La nueva prioridad se aplica a las siguientes selecciones y no autoriza duplicar una ejecución en curso.

## Enforcement mínimo

Regla breve en el `AGENTS.md` global de Codex, distribuida mediante la plantilla `config/codex/routing.md`, y procedimiento en la skill. La comprobación del camino CLI/MCP lee la tabla local antes de inferir, reutilizando preflight y supervisor actuales. Se sustituirán las consultas de catálogo en cada preparación o envío por la generación de tabla aplicable. Se conservan las comprobaciones necesarias de identidad, procedencia y permisos: no son sondeos de capacidad. No se duplica infraestructura ni se interceptan subagentes nativos o Superpowers.

## Compatibilidad ante actualizaciones

Registrar versión observada y capacidades verificadas de las herramientas sin una lista de versiones exactas permitidas. Un número de versión distinto por sí solo no impide continuar. Se sustituirá la comprobación actual de igualdad con `expected_version`; cambiar únicamente esa configuración no acredita compatibilidad.

Si cambia una versión, verificar las operaciones y estructuras necesarias mediante el contrato publicado o un mecanismo soportado, renovar los datos afectados de la tabla y continuar cuando sean compatibles. No se adivinan rutas, credenciales ni formatos. Si falta una capacidad imprescindible, registrar la incompatibilidad concreta y utilizar el retorno nativo autorizado para la función afectada; el trabajo general continúa. No se reenvían intentos vivos o inciertos. La misma regla se aplica a cambios de Codex y de otras herramientas utilizadas por AIKit.

## APIs propuestas

- `read_availability(state, key)`
- `refresh_availability(binding, key)`
- `decide_candidate(state, policy, candidates)`
- `record_inference_outcome(state, key, result)`

## CLI/MCP

La consulta de disponibilidad no ejecuta inferencia. La salida saneada incluye fuente, fecha de observación, frescura, próxima comprobación, `reset_at` en UTC y hora local, y estado. `quota_resume` permanece deshabilitado en esta nota; la frase anterior solo conserva el contrato existente para una futura habilitación separada.
## Criterios de aceptación

- Tests con transporte falso para timestamps, scopes, fallos de cache, concurrencia, identidad, CLI/MCP, intentos pendientes y exportación limpia.
- Selecciones sucesivas desde una tabla válida no consultan catálogo ni cuotas; un rechazo confirmado dispara un único refresco completo compartido.
- Altas y bajas, cambios de tarifa/cuenta y nuevos modelos se reflejan tras los disparadores de actualización acordados.
- Una versión nueva compatible continúa operando; una capacidad incompatible produce diagnóstico y retorno por función, sin rechazo basado únicamente en versión.
- Las muestras de rendimiento se obtienen sin inferencias adicionales, se deduplican y distinguen proveedor/modelo/esfuerzo; no alteran el orden de niveles ni confunden lentitud con cuota agotada.
- No hay secretos, PII ni estado mutable en el paquete exportado.
- Los estados desconocidos usan un único intento real autorizado, registrado una vez con IDs existentes.
- Implementar conforme a la aprobación del usuario del 2026-10-31, con verificación y revisión independiente.
