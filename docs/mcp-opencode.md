# MCP local de AIKit sobre el adaptador de OpenCode

Actualizado: 29 de octubre de 2026. Diseño aprobado:
`docs/superpowers/specs/2026-10-28-mcp-local-design.md`. Plan:
`docs/superpowers/plans/2026-10-28-mcp-local.md`. Evaluación previa:
`docs/evaluacion-mcp-opencode.md`.

El servidor MCP expone el núcleo ya existente de la skill
`delegating-to-opencode` como dos herramientas locales. No crea otro
planificador, instalador ni sistema de subagentes: el núcleo de `delegate.py`
sigue siendo el único que aplica políticas, catálogo, bloqueos y errores.

## Transporte

Solo STDIO local. El servidor se lanza como proceso y habla JSON-RPC por la
entrada y salida estándar:

```powershell
$root = 'C:\ruta\absoluta\AIKit'
$python = Join-Path $root '.venv\Scripts\python.exe'
$server = Join-Path $root 'skills\delegating-to-opencode\scripts\mcp_server.py'
& $python $server
```

El cliente MCP lo arranca con ese Python absoluto. Alternativa dentro del
repositorio: `uv run --extra mcp python skills/delegating-to-opencode/scripts/mcp_server.py`.

Requisitos:

- Python 3.10+ y el SDK oficial `mcp>=1.26,<2` instalado en ese intérprete
  (`uv sync --locked` incluye el SDK en el grupo de desarrollo; el extra `mcp`
  lo declara para entornos de ejecución).
- OpenCode v2 en `PATH` del proceso servidor, como en la CLI.
- La CLI sigue siendo solo biblioteca estándar: importar o ejecutar
  `delegate.py` no carga el SDK de MCP.

`stdout` queda reservado al protocolo MCP. El servidor no escribe diagnóstico
en `stdout`; los logs del SDK van a `stderr`. Importar el módulo o listar
herramientas no ejecuta el backend: los procesos de OpenCode solo arrancan al
invocar una herramienta.

## Herramientas

| Herramienta | Parámetros | Anotaciones | Efecto |
| --- | --- | --- | --- |
| `opencode_catalog` | `cwd` (absoluta, obligatoria), `model` (opcional), `timeout` (300 por defecto) | `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=false` | Solo consulta versión y catálogo |
| `opencode_delegate` | `cwd` (absoluta, obligatoria), `task`, `model`, `reason` (obligatorios), `variant` (opcional), `agent` (`build`/`plan`, `build` por defecto), `timeout` (300 por defecto) | `readOnlyHint=false`, `destructiveHint=true`, `idempotentHint=false`, `openWorldHint=true` | Ejecuta una tarea y puede modificar el proyecto |

`openWorldHint` distingue el catálogo de la delegación: el catálogo solo
consulta el backend local, mientras que la delegación deja que OpenCode use
shell y red arbitraria, con lo que interactúa con sistemas externos.

Reglas del contrato:

- `cwd` debe ser una ruta absoluta. Las rutas relativas se rechazan con
  `invalid_cwd` antes de cualquier proceso.
- `model` es obligatorio en la delegación y no hay modelo por defecto. Se
  rechaza `openai/*` con `provider_not_allowed` antes de iniciar procesos.
- `reason` es obligatorio y no vacío. Un motivo vacío o solo con espacios
  llega al núcleo y devuelve `reason_required` con su JSON. Si el campo
  `reason` **falta** en los argumentos, el SDK lo rechaza antes de invocar
  el handler y la respuesta no lleva `reason_required` del núcleo (ver
  «Respuesta»).
- `task` es texto en memoria; no se crea ningún archivo de tarea. El texto con
  comillas, Unicode o aspecto de opción se pasa literal a OpenCode.
- `timeout` es finito, mayor que cero y máximo 3600 s. Fuera de rango:
  `invalid_timeout`, sin procesos.
- No existe `autoApprove`, ni reintento automático, ni selección de modelo por
  parte del servidor.
- Las delegaciones del mismo servidor se serializan con un `asyncio.Lock`; el
  bucle de eventos no se bloquea porque el núcleo se ejecuta con
  `anyio.to_thread.run_sync`.

## Respuesta

Cada llamada devuelve un `CallToolResult`. Cuando el handler llega a
ejecutarse:

- `content`: una línea JSON compacta con el mismo payload del núcleo.
- `structuredContent`: copia de ese payload.
- `isError`: `true` cuando el núcleo devuelve `status: "error"`.

Hay dos clases de error y no deben confundirse:

1. **Errores del núcleo.** Cuando el handler llega a ejecutarse, la respuesta
   es siempre JSON: `content` con una línea JSON compacta y
   `structuredContent` con la copia del payload. Así llegan los errores
   controlados (`provider_not_allowed`, `invalid_cwd`, `empty_task`,
   `invalid_variant`, `invalid_timeout`, `reason_required` con motivo vacío,
   `free_limit_reached` con `fallback: reselect`, `unsafe_configuration`,
   `opencode_missing`, `opencode_failed`, `timeout`…) y también los éxitos. Un
   fallo inesperado devuelve un mensaje fijo (`internal_error`) sin detalles ni
   secretos.
2. **Errores de validación del SDK.** El servidor usa el SDK oficial de MCP y
   **no** implementa un protocolo de validación propio. Cuando los argumentos
   no satisfacen el esquema declarado, el SDK rechaza la llamada antes de
   invocar el handler y devuelve `isError: true` con **texto** y **sin**
   `structuredContent`. Es el caso de un campo obligatorio ausente —por
   ejemplo `reason`— y de argumentos con tipo incorrecto, como
   `timeout: "mucho"` o `agent: "zzz"`. El texto es un mensaje de validación
   del SDK, no un payload del núcleo, y no incluye `code` de AIKit.

Consecuencia para los consumidores: respeta siempre `isError`. Un resultado
con `isError: true` puede no traer `structuredContent`, así que no deserialices
`structuredContent` sin comprobar antes que existe. Intenta leer el JSON de
`content` solo cuando el propio `content` sea JSON; si es un mensaje de
validación del SDK, trátalo como texto plano y no lo interpretes como payload.

La tabla de argumentos que el SDK publica es la única validación de tipos y de
campos obligatorios: es intencional que el SDK la aplique, sin duplicar
validaciones de protocolo propias en el servidor.

## Tiempos y cancelación

El timeout es **por proceso**. Una ejecución completa lanza hasta cuatro
procesos de OpenCode —versión, catálogo, comprobación de configuración y
`run`— cada uno con su propio límite. Con el máximo de 3600 s por proceso, el
peor caso es `4 × 3600 = 14400` s más la limpieza del árbol de procesos.

Por eso el **timeout del cliente MCP** debe cubrir ese rango: usa
`tool_timeout_sec = 15000` (o el equivalente de tu cliente) y no un valor de
600 s. Un cliente con 60 s por herramienta, el valor por defecto documentado
para Codex, cortará la llamada antes de tiempo.

Límites explícitos de esta versión:

- No hay progreso, ni cancelación activa de la inferencia, ni trabajos
  persistentes, ni API HTTP.
- **Cancelar o cerrar una llamada MCP no detiene el backend.** El SDK puede
  responder a la cancelación de inmediato mientras el worker protegido sigue
  ejecutándose en segundo plano: la respuesta MCP puede llegar **antes** de
  que el backend termine, y la ejecución abandonada no se detiene. Por eso no
  se puede afirmar que la respuesta MCP llega cuando el backend termina; no
  se sabe en qué momento termina.
- El **timeout del proceso** lo aplica el núcleo dentro del hilo worker del
  servidor MCP, así que solo protege mientras ese servidor siga vivo. Si el
  servidor MCP termina de forma forzada, no hay garantía de que se maten los
  procesos hijos de OpenCode ni de que exista un plazo de huérfanos: pueden
  sobrevivir más allá de su timeout o quedar pegados al proceso que los
  lanzó.
- Esta versión no implementa cancelación activa del backend. No se debe
  reintentar a ciegas: un reintento puede solaparse con la ejecución anterior
  todavía viva y dejar cambios parciales contradictorios.
- No hay reintentos ciegos. Un intento fallido puede dejar cambios parciales
  en el destino; revisa el diff y el estado de los procesos antes de reintentar.
- Cerrar el cliente puede dejar procesos de OpenCode huérfanos hasta que
  vence su timeout, o más allá si el servidor MCP muere antes.

## Esperado y observado

Esta sección separa lo que fija el diseño de lo que se comprobó en esta
ejecución. La verificación con OpenCode conectado la realizó el coordinador;
las pruebas automatizadas no usan inferencia.

### Esperado (diseño aprobado y pruebas de contrato)

- Dos herramientas exactas con los nombres, parámetros y anotaciones de la
  tabla anterior.
- `cwd` absoluto obligatorio; `model` y `reason` obligatorios en la
  delegación; `timeout` finito en `(0, 3600]`.
- `openai/*` rechazado antes de cualquier proceso.
- Respuesta con JSON compacto en `content`, copia en `structuredContent` e
  `isError` coherente con `status` en los resultados del núcleo.
- Errores de validación del SDK con `isError: true`, texto y sin
  `structuredContent` (campo obligatorio ausente o tipo incorrecto).
- Fallos inesperados con mensaje fijo.
- `stdout` solo con mensajes JSON-RPC.

### Observado en esta ejecución

Autor: el coordinador, con STDIO real, y el worker de correcciones, con
pruebas del contrato. Entorno Windows, Python 3.14.9 y SDK MCP 1.30.0;
configuración del proyecto con OpenAI directo y subdelegación bloqueados.

Del coordinador, con STDIO real y el cliente del SDK:

- `initialize` responde `serverInfo.name = "aikit-opencode"`; `tools/list`
  devuelve exactamente `opencode_catalog` y `opencode_delegate` con las
  anotaciones esperadas.
- Sin OpenCode en `PATH`: `opencode_catalog` devuelve `opencode_missing` y
  `opencode_delegate` con `openai/gpt-5` devuelve `provider_not_allowed`, sin
  iniciar procesos.
- Todas las líneas de `stdout` son mensajes JSON-RPC válidos.
- Catálogo real de OpenCode Go obtenido sin inferencia.
- Inferencia real MCP → núcleo → CLI → OpenCode Go: respuesta esperada y
  observada `AIKIT_MCP_OK`, con `opencode-go/minimax-m3.1-flash`, variante
  publicada `low`, sin herramientas ni cambios de archivos. Go es de pago;
  OpenCode no informó coste de esa llamada (`null`).
- Verificación final del coordinador: **205 pruebas**, Ruff (lint y formato) y
  mypy correctos. La primera ejecución restringida se interrumpió al quedar
  bloqueada; la ejecución con creación de procesos STDIO permitida pasó.
- Copia personal: handshake, dos herramientas, catálogo real y bloqueo de
  OpenAI directo comprobados sin repetir inferencia.

De esta corrección de revisión, en la suite en memoria del contrato MCP:

- El campo `reason` ausente lo rechaza el SDK antes del handler: `isError:
  true`, texto de validación y `structuredContent` ausente; no devuelve el
  `reason_required` del núcleo.
- Un `reason` vacío o solo con espacios sí alcanza el núcleo y conserva
  `reason_required` en el JSON y en `structuredContent`.
- Un argumento con tipo incorrecto (`timeout: "mucho"`) también lo rechaza el
  SDK: `isError: true`, texto y sin `structuredContent`.
- `opencode_delegate` publica `openWorldHint: true` y `opencode_catalog`
  mantiene `openWorldHint: false`, con regresión propia.
- Resto de la suite del repositorio en verde, Ruff y mypy sin hallazgos.

La revisión independiente detectó la anotación de mundo abierto y promesas
excesivas sobre cancelación y validación; se corrigieron y cubrieron con
regresiones. No se ha demostrado cancelación activa ni ausencia de huérfanos.
La última revisión independiente adicional no se pudo ejecutar por límite de
cuota; las comprobaciones finales anteriores las ejecutó el coordinador.

## Relación con la skill y la CLI

- La skill `delegating-to-opencode` prefiere las herramientas MCP cuando el
  cliente las expone; la CLI queda como alternativa y como herramienta de
  diagnóstico.
- El servidor MCP no intercepta `spawn_agent` ni los subagentes nativos: el
  coordinador conserva orquestación, roles y revisiones.
- La política (`policy.json`), el bloqueo del proveedor directo `openai`, la
  comprobación del certificado de configuración y el `fallback: reselect` son
  los mismos del núcleo; no hay una segunda copia de esas reglas.

## Instalación personal

Instalada la skill personal con respaldo fuera de rutas descubribles y SHA256
coincidentes en sus cinco archivos. Registrado `aikit-opencode` en Codex con
el Python absoluto de `.venv`, servidor de la skill personal, arranque de 30 s,
timeout de herramienta de 15000 s y solo las dos herramientas documentadas.

`codex mcp add` omitió los argumentos del servidor previo `node_repl`. Se
detectó por comparación estructural, se restauraron desde el respaldo y se
comprobó que todos los ajustes ajenos coincidían con los originales.

El catálogo de herramientas de este chat todavía no publica el nuevo servidor.
Abre una nueva sesión o recarga el cliente para cargarlo. El entorno `.venv`
debe seguir disponible en su ruta actual; aún no es un complemento empaquetado.

Actualización del 29 de octubre de 2026: esa instalación manual se sustituyó por
`aikit@aikit-local`. El paquete resuelve el runtime con uv y su lock desde caché;
ya no depende de la `.venv` del checkout. La skill manual y su configuración
quedaron respaldadas. Consulta [instalación](plugin-aikit.md) y
[validación del complemento](validacion-plugin.md); el apartado anterior conserva
la evidencia de la primera instalación del MCP independiente.

## Tabla local de disponibilidad

`delegate.py availability status --cwd <proyecto> --json` solo lee el estado del
host configurado. Si falta `HostContext`, devuelve un diagnóstico; no busca una
tabla alternativa dentro del proyecto. `availability refresh` consulta únicamente
el servicio registrado y publica metadatos, sin ejecutar modelos ni arrancarlo.

La distribución usa `prefer_free: false`: Go de pago, otros de pago y gratuitos,
siempre entre modelos adecuados. Un archivo de usuario con `prefer_free: true`
sigue mostrando los gratuitos primero; el runtime no lo reescribe. Para adoptar
voluntariamente la prioridad nueva, el usuario puede cambiar ese valor a `false`.

La firma de contexto cubre selección y permisos publicados por lista blanca,
no credenciales ni identidades de cuenta. Un cambio privado de cuenta requiere
la notificación o actualización explícita acordada; no se detecta almacenando
hashes de secretos. Las muestras de rendimiento conservan IDs y medidas tipadas,
sin prompts/respuestas. Un intento pendiente no se reenvía al leer la tabla.
