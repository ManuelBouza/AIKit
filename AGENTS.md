# Guía del repositorio

## Propósito

Desarrollar AIKit y Delegating to OpenCode en este repositorio, como componentes
independientes. AIKit reúne preferencias y capacidades generales; la integración
gestiona la delegación a OpenCode y puede utilizarse sin AIKit. La separación y
el cambio de empaquetado aún no están implementados: consulta
`docs/limites-delegacion-aikit.md` antes de mover o retirar componentes.

## Restricción temporal del usuario

Hasta nuevo aviso, no ejecutar ni invocar Delegating to OpenCode para el trabajo
de desarrollo. Usar las herramientas nativas de Codex. Las instrucciones de
delegación posteriores describen el comportamiento histórico y no prevalecen
sobre esta restricción.

## Uso de BMAD

Para preguntas sobre BMAD o sobre qué flujo elegir, usa `bmad-help` y consulta
el catálogo instalado en `_bmad/_config/bmad-help.csv`.
Selecciona las demás skills según la petición y sus descripciones publicadas;
lee su SKILL.md al utilizarlas. No impongas el flujo completo a cambios pequeños.
Las recomendaciones de BMAD no autorizan tareas ni reanudan trabajos pausados:
se mantienen el mecanismo global go y las restricciones de este proyecto.

## Documentación técnica actualizada

Cuando una tarea requiera consultar documentación actualizada de bibliotecas,
frameworks u otras tecnologías cubiertas, prioriza Context7 si está disponible.
Comprueba la versión pertinente y, si Context7 no está disponible o no cubre la
consulta, recurre a la documentación oficial u otras fuentes primarias adecuadas.
Respeta las fuentes y restricciones que indique el usuario para cada tarea.

## Antes de crear o modificar una skill

Explora primero las skills y herramientas instaladas y lee sus instrucciones
pertinentes. Registra cobertura, carencias y justificación. Reutiliza lo existente;
implementa solo lo no cubierto. No dupliques Superpowers ni alteres sus archivos,
activación o roles. Conserva los principios de reutilización descritos en
`docs/principios-aikit.md`, cuyo alcance de producto es histórico.

## Estructura

- `skills/delegating-to-opencode/`: instrucciones, política y scripts tipados
  (`delegate.py` para la CLI y `mcp_server.py` para el servidor MCP local).
- `tests/`: pytest con transporte falso, sin inferencia.
- `scripts/build_plugin.py`: exporta el complemento histórico AIKit; pendiente
  de separar el empaquetado de la integración.
- `docs/`: investigación, validación y diseño.
- `notas/`: ideas pendientes de debatir e implementar; índice en `notas/IDEAS.md`.
- `opencode.json`: bloqueos de proveedor y subdelegación.
- `.aikit/`: tareas y evidencias ignoradas por Git.

## Notas e ideas pendientes

Registra cada idea o duda nueva del usuario en una nota numerada bajo `notas/`,
con fecha y estado inicial «Pendiente de debatir», y añádela al backlog canónico
[notas/IDEAS.md](notas/IDEAS.md). Conserva el contexto, las decisiones y enlaces
a evidencias; actualiza el backlog cuando cambie el estado de la nota.

Antes de planificar una tarea, consulta el backlog para identificar ideas y
dependencias relacionadas. Propón retomarlas cuando sea oportuno, sin asumir
prioridades ni iniciar trabajo adicional. Registrar una idea no aprueba su diseño
ni autoriza implementarla: respeta el mecanismo go y las decisiones del usuario.
Si se convierte en especificación o historias BMAD, enlaza los artefactos y
conserva el estado y la trazabilidad en el backlog; no dupliques tareas activas.
Conserva en Git los artefactos de proyecto de `_bmad-output/`, incluidas las
fuentes `.memlog.md` de las especificaciones, tras revisar su contenido. No
incluyas credenciales, datos privados ni salidas temporales en los commits.

## Regla de coordinación

Conserva roles, subagentes y revisiones de Codex y Superpowers. El coordinador o
subagente nativo delega la implementación y verifica diff y pruebas. Los workers
no redelegan; sus resultados no sustituyen revisiones independientes.

Activa `$delegating-to-opencode` explícitamente o por descripción.
No intercepta `spawn_agent` ni MCP. `run` exige modelo y motivo explícitos.
`run` comprueba en el destino, global o proyecto, `provider.use openai deny` y
`tool.use subagent:* deny`. Sin certificado rechaza la inferencia; `doctor` no
lo exige. Consulta `docs/correcciones-revision-funcional.md` para sus límites.
Escoge modelo y esfuerzo según la tarea. Capacidad primero: Go de pago ->
otros de pago conectados -> todos los gratuitos conectados (incluido GoFree) ->
Codex nativo si no hay opción adecuada/disponible. Lee primero la tabla local
(`availability status --cwd <proyecto> --json`); no consultes catálogo/cuota por
rutina. Bloquea solo el proveedor directo `openai`; GPT de otros proveedores
siguen permitidos. Usa variantes publicadas o el predeterminado.
Antes de cada tarea o reintento en OpenCode, anuncia su objetivo, modelo,
esfuerzo y condición gratuita o de pago; indica cuando la tarifa sea desconocida.

El servidor MCP local `aikit-opencode` expone el mismo núcleo con
`opencode_catalog` y `opencode_delegate`; prefiere esas herramientas si el
cliente las publica y conserva la CLI como alternativa. No elige modelo ni
reintenta. El timeout del núcleo es por proceso. El paquete portable usa los
límites del cliente (normalmente 60 s por herramienta); usa CLI si la tarea
no cabe en ese límite. El MCP independiente puede configurarse a 15000 s para
cubrir cuatro procesos al máximo. Consulta `docs/mcp-opencode.md`.

Con `free_limit_reached` y `fallback: reselect`, evalúa Go y alternativas sin
nueva confirmación. Sin opciones adecuadas disponibles, informa y continúa con
Codex nativo. Revisa cambios parciales antes de reintentar. No eludas permisos,
autenticación o privacidad.

OpenCode es ejecutor habitual del trabajo externalizable autorizado; Codex
conserva comprensión, roles y comprobación de aceptación de metadata, sin repetir
la revisión técnica. Contrato de carga en
`skills/delegating-to-opencode/references/carga-opencode.md`; evidencia en
`docs/balance-carga.md`.

Espera por finalización (coordinación): preferir espera acotada por proceso/tarea
propia con límite máximo y retorno anticipado; notificación asíncrona solo si está
publicada y en turno activo. La salida del cliente es solo señal; `pending`/
`uncertain` nunca autoriza reintento ni duplicar inferencia. Si el cliente vence
pero el backend sigue vivo, conservar IDs/contexto y usar reconciliador/estado
determinista propio que despierte solo ante cambio o guardia razonable (puede
consultar la API sin LLM). Sin SSE global, hooks ni servidores aquí, ni sleep
fijo de 300 s ni monitorización. Duraciones por intento real en caché, no vida de
sesión reutilizada; grupos comparables y límites honestos. Capacidades portables
variables; instalación pendiente.

## Orquestación Codex/OpenCode

Codex conserva conversación, coordinación, decisiones del usuario, selección de
modelo y validación de metadata de aceptación. Cuando hay capacidad adecuada,
OpenCode ejecuta diseño, arquitectura, contratos, planes, exploración factual,
diagnóstico, implementación, pruebas, correcciones, documentación, revisión
independiente y verificación. Revisor en sesión nueva, sin redelegar ni modificar
la entrega; devuelve decisiones de diseño al coordinador. Codex no repite la
revisión técnica independiente.

Capacidad primero: Go de pago -> otros de pago adecuados -> todos los gratuitos
conectados (incluido GoFree) -> continuar en Codex nativo si no hay opción
adecuada/disponible. No degradar para evitar Codex ni agotar Free inadecuados.
Si falta modelo adecuado o disponibilidad adecuada, retornar automáticamente por
función, anunciando y registrando motivo, sin nueva aprobación; mantener revisión
independiente. Solo bloquea proveedor directo `openai`; GPT de otros proveedores
sigue permitido. Primero tabla local; no sondeo global por cada elección.

Formato `review.json`: `role: reviewer`, `session`, `snapshot`,
`verdict: accepted|needs_corrections`, `checks[]` (`id`, `command`, `cwd`,
`exit_code`, `summary`), `findings[]` (`severity: blocker|warning|info`,
`description`), `limitations[]`. La metadata no prueba autoría ni calidad;
`session` esperada proviene del backend real y `snapshot` lo fija el
coordinador. `scripts/review_evidence.py` valida el contrato, snapshot, sesión y
checks declarados; no ejecuta los comandos ni certifica su autoría. MCP preferido
si está publicado y cabe en 60 s; CLI para tareas largas; no reintentar si hay
intento vivo. No interceptar nativos ni Superpowers ni crear nueva skill.
Evidencia histórica permanece histórica.

Si un subagente nativo usa la CLI, devuelve el JSON de stdout directamente al
coordinador; solo este persiste en una ruta permitida. Si falla el guardado,
recupera la salida y registra el problema: no repitas una inferencia terminada.
Reutiliza permisos conocidos solo para el mismo entorno y alcance; si se sabe que
el sandbox bloquea la CLI, solicita `exec_command` con `require_escalated` desde
el primer intento y justificación acotada. Si el entorno cambió o se desconoce,
haz primero un preflight sin inferencia. No escales globalmente ni para eludir
controles; ante denegación informa código y motivo, sin reintento a ciegas. No
pruebes permisos con modelos ni elijas otra vía CLI por un caso antiguo si MCP
está disponible.

## Comandos

Desde la raíz:

```powershell
uv sync --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
python skills/delegating-to-opencode/scripts/delegate.py doctor --cwd .
```

Consulta `README.md` para uso, instalación y restauración. Conserva configuración
ajena y respaldos fuera de rutas descubribles.
El empaquetado actual sigue siendo el histórico descrito en
`docs/plugin-aikit.md`; aún no existe un paquete independiente verificado. No
instales desde la raíz del checkout: Codex también copia archivos ignorados por Git.

## Estilo

Python tipado; Ruff para formato/lint, mypy para tipos. Pytest con fixtures y
parametrización por comportamiento. Documenta en español.

## Validación

Registra entorno, configuración, resultado esperado y observado de cada cambio.
No declares preferencias verificadas sin evidencia.

## Seguridad

No incluyas credenciales ni datos privados. Usa ejemplos ficticios. Políticas y
certificado no son un sandbox; bloquear `subagent` no bloquea `shell`.
