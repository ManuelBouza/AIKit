# Validación del complemento AIKit

29 de octubre de 2026. Coordinador: Codex. Windows, cliente Codex 0.153.4,
Python de desarrollo 3.14.9; uv eligió Python 3.13.14 para el runtime instalado,
SDK MCP 1.30.0 y dependencias resueltas con el lock incluido.

**Corrección 0.1.1:** la validación de la versión 0.1.0 descrita abajo no
demostró publicación de herramientas en el chat. La prueba posterior falló:
el formato legacy transmitía `${PLUGIN_ROOT}` literalmente y Windows devolvía
error 267 al usarlo como `cwd`. La sonda nativa también confirmó que no expandía
`${CLAUDE_PLUGIN_ROOT}`. El SDK usado inicialmente expandía las rutas por su
cuenta, lo que ocultó la diferencia del cargador.

Se corrigió a manifiestos portables estrictos y sin variante legacy generada.
En una sesión diagnóstica efímera del cliente nativo, sin inferencia, se observó
`pluginId: aikit@aikit-local` y ambas herramientas `opencode_catalog` y
`opencode_delegate`. Los campos de timeout específicos se eliminan porque ese
lector los rechaza: se aplican los límites predeterminados del cliente. Para
tareas largas se conserva CLI; no se promete un timeout de 15000 s en el paquete.
Las regresiones nuevas verifican metadatos portables y rechazo de campos no
admitidos antes de crear la salida. Las secciones siguientes conservan el
registro histórico; no deben interpretarse como validación de chat de 0.1.0.

## Comprobación real de 0.1.1

Chat de prueba: `01a1892f-26d3-7bc3-9a99-8d5088fec8ce`. Se revisaron sus
llamadas MCP nativas, además del informe local ignorado por Git.

- Las herramientas aparecieron tras una espera de seis segundos y una segunda
  consulta al inventario; la primera búsqueda aún coincidía con el arranque.
- `opencode_catalog` devolvió 74 modelos, sin el proveedor directo `openai`.
- `opencode_delegate` rechazó `openai/gpt-6-luna` con `provider_not_allowed`.
- Una llamada real a `opencode/beam-free#low`, con timeout 10 por proceso,
  devolvió exactamente `AIKIT_CHAT_OK` en unos 9,6 s. Se anunció selección y
  tarifa gratuita publicada antes de ejecutar; coste devuelto `null`, sin
  importe acreditado por llamada. No hizo falta Go ni reintentar.
- El chat comparó estado y diff completos antes y después; los cambios
  preexistentes del coordinador se conservaron. No usó CLI/SDK como sustitutos.

La implementación de este bugfix se intentó con Beam gratuito `medium`; alcanzó
60 s con cambios parciales y el adaptador terminó su árbol. Codex revisó y
completó los cambios mediante el fallback autorizado. Se observó RED para la
extensión OpenAI incorrecta y para tres campos MCP no portables; GREEN posterior.
Resultado final: **215 pruebas**, Ruff y mypy correctos. La revisión independiente
no encontró bloqueantes; se corrigió la codificación de metadatos y se documentó
la preparación previa del runtime. Instalación personal 0.1.1 con respaldo,
hashes coincidentes y configuración ajena conservada.

## Registro histórico de 0.1.0

## Cobertura y decisiones

Se reutilizaron el núcleo CLI, MCP, política y skill existentes. Superpowers
cubre el proceso de desarrollo y revisión, `skill-installer` skills individuales
y `plugin-management` conexiones. Solo se añadió la exportación del paquete.
No se crearon hooks ni otra skill ni se modificó Superpowers.

Dos intentos de implementación por OpenCode no dieron resultado: MiniMax Go
`high` (de pago) fue detenido tras más de doce minutos sin cambios; GLM gratuito
`high` alcanzó 240 s y el adaptador terminó su árbol. No se demostró falta de
cuota ni se registró coste. Se continuó con Codex conforme al fallback del usuario.

## Esperado y observado

| Comprobación | Esperado | Observado |
| --- | --- | --- |
| Exportación | Solo lista permitida, salida nueva, sin enlaces | Pruebas de exclusión de `.env`, Git, `.aikit`, `.venv`, archivo privado en skill y enlaces de archivo/directorio correctas |
| Esquema MCP | Cliente reconoce servidor y límites | El formato portable rechazó timeouts; salida compatible sin manifiestos portables sí reconoce `aikit-opencode` |
| Perfil limpio | Instalar y arrancar sin `.venv` del checkout | Codex CLI instaló; uv creó entorno en caché; SDK inicializó, listó dos herramientas y bloqueó OpenAI directo sin inferencia |
| Con Superpowers | Ambos instalados, sin cambios a Superpowers | CLI listó ambos habilitados; retirada de AIKit dejó Superpowers instalado |
| Actualización | Renovar fuente e instalar copia nueva | Codex exigió retirar el registro anterior antes de añadir una ruta diferente; actualizado y reinstalado correctamente |
| Retirada | Eliminar solo AIKit y su caché temporal | `plugin remove` quitó la caché comprobada; Superpowers permaneció |
| Migración personal | Respaldo, reemplazo válido y ajustes ajenos intactos | SHA256 de paquete/caché coincidentes; MCP desde caché validado antes de retirar manuales; comparación estructural de configuración correcta |

Antes de implementar se observaron cuatro errores por ausencia del exportador;
tras implementarlo pasaron. La regresión de resolución de manifiesto falló con
`KeyError: mcpServers` y pasó con la salida compatible. Resultado final:
**212 pruebas**, Ruff lint/formato y mypy correctos. Revisión independiente
de lectura sin hallazgos bloqueantes; observaciones documentales y de cobertura
incorporadas.

La CLI de Codex omitió argumentos predeterminados de `node_repl` al escribir
configuración; se detectó y restauró esa pérdida antes de completar la migración.
La copia manual se apartó a `<CODEX_HOME>/backups/aikit/plugin-migration-*/manual-skill`.
El mismo respaldo conserva `config.toml` anterior y el estado previo a retirar
el MCP manual. Las cuentas y permisos de OpenCode no cambiaron.

## Límites de la evidencia

El backend nativo reconoce `aikit@aikit-local`, la skill
`aikit:delegating-to-opencode` y el MCP con `pluginId: aikit@aikit-local`.
No declara aplicaciones registradas ni hooks. El arranque y las dos herramientas
se probaron con el cliente del SDK usando la configuración del paquete instalado.
El inventario nativo aún mostró `tools: {}` para el MCP del plugin: no se afirma
que el chat activo lo haya cargado ni que ya aparezca en una pestaña concreta.
Se debe recargar el cliente y comprobar su catálogo.

La convivencia demostrada es de instalación y descubrimiento; no equivale a una
evaluación completa de todas las combinaciones de workflows de Superpowers.
No se repitió inferencia en el MCP al empaquetar: el núcleo ya tenía una prueba
real previa con Go. Cancelación activa y publicación pública siguen fuera del alcance.

## Validación de preparación 0.2.0

Versión preparada, no instalada: `0.2.0`. El cliente debe recargarse tras la
instalación para renovar el catálogo de herramientas.

- Fuente exportada con `scripts/build_plugin.py` a
  `.aikit/plugin-update-020/distribution-v020-final` (42 archivos de la lista
  permitida + 1 catálogo = 43 en la distribución).
- Checks congelados: `uv sync --locked`, `uv run pytest` (778 passed),
  `uv run ruff check .`, `uv run ruff format --check .`,
  `uv run mypy` (60 archivos, sin problemas).
- Validación aislada del paquete exportado: imports de CLI y MCP correctos;
  `doctor` devuelve `host_context_unavailable` sin inferencia; flags ocultos
  verificados en el módulo exportado real (`CREATE_NO_WINDOW` y, donde aplica,
  `CREATE_NEW_PROCESS_GROUP`/`DETACHED_PROCESS`).
- La causa de la captura de consola del usuario no está correlacionada; no se
  puede afirmar que el flash global esté resuelto. La versión instalada sigue
  siendo `0.1.5` con flags antiguos conocidos.
- No hay notificación universal en chats inactivos; tiempos vacíos de caché son
  aceptables. La automatización diaria 001 sigue pendiente.
- La tarea 4 de enlace no se declara E2E real sin ejecución del runtime
  empaquetado; si requiere inferencia en vivo, queda diferida al coordinador.
- No se realizaron sondas de modelo/proveedor ni mutaciones de perfil/config.
