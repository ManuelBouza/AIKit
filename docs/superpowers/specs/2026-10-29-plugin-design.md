# AIKit como complemento privado de Codex

El usuario aprobó empaquetar la skill y el MCP existentes con «go». Se elige
complemento nativo privado frente a instalador propio: la evaluación previa está
en `docs/evaluacion-distribucion-plugin.md`. No se publicará en el directorio ni
se hará push como parte de esta ejecución.

## Diseño

La raíz actual será el paquete: `plugin.json`, `mcp.json`, `skills/`,
`pyproject.toml` y `uv.lock`. Un catálogo de repositorio apuntará a `./` con
identidad `aikit@aikit-local`. No copiar fuentes a otra carpeta mantenida a mano.

El MCP usará `uv run --project ${PLUGIN_ROOT} --locked --no-dev --extra mcp`
para ejecutar su script dentro del paquete instalado. Python, uv y OpenCode son
requisitos del equipo; el SDK y sus dependencias se resuelven con `uv.lock`.
El entorno se crea en la copia local del paquete y necesita escritura, no se
distribuye una `.venv` ni se usa la del checkout original. La primera preparación
puede necesitar red; se documentará el tiempo de arranque adecuado.

El manifiesto portable es preferido. Si el cliente instalado necesita el formato
compatible, se añadirá una adaptación mínima comprobada, conservando una fuente
canónica. No inventar `.app.json` ni identificadores de aplicación registrada.
El complemento no tiene hooks, no modifica Superpowers ni orquesta subagentes.

## Verificación y migración

Primero instalar con Codex CLI real en un `CODEX_HOME` temporal dentro de `.aikit/`.
Comprobar descubrimiento, copia instalada, rutas MCP, handshake y herramientas
desde otro directorio. Sin inferencia en pruebas; conservar 205 pruebas previas.
Comprobar actualización y retirada con el cliente real y registrar límites.

Solo después, instalar personalmente con respaldo de configuración y skill
manual fuera de rutas descubribles. Evitar que coexistan skill manual y empaquetada
o dos MCP equivalentes. Conservar el resto de configuraciones exactamente y
restaurar si la migración falla. No prometer que aparezca en «Aplicaciones»:
se verificará como complemento instalado, con herramientas MCP.

## Cobertura y fuentes

Reutiliza `skill-installer` para skills individuales, `plugin-management` para
integraciones y Superpowers para el proceso; ninguna crea este paquete de AIKit.
`plugin-creator` no está instalado en el catálogo consultado.

- https://developers.openai.com/plugins/build/plugins
- https://developers.openai.com/plugins/deploy/desktop-only

La compatibilidad se demuestra con ejecución local, no solo leyendo estas fuentes.

## Ajustes por evidencia durante la ejecución

La prueba del coordinador con Codex 0.153.4 mostró que `plugin add` copia incluso
un directorio ignorado por `.gitignore`. Por tanto el catálogo distribuible se
generará en una salida limpia, con copia por lista permitida, nunca apuntando
directamente al checkout. Los manifiestos y fuentes raíz siguen siendo canónicos;
el exportador genera el catálogo y el paquete sin duplicación mantenida a mano.

Una segunda prueba con `plugin/read` reconoció la skill portable pero no el MCP
en `mcp.json`. Con `.codex-plugin/plugin.json` y referencia `mcpServers` a
`./.mcp.json`, el mismo cliente reconoció el MCP. La exportación generará esa
adaptación desde los manifiestos canónicos, y se verificará el arranque real.
Estos ajustes sustituyen la instalación directa `source.path: ./` de la raíz
del repositorio propuesta inicialmente.

El diagnóstico posterior del registro precisó la causa: el lector de `mcp.json`
portable rechaza `startup_timeout_sec`, `tool_timeout_sec` y `enabled_tools`.
Ponerlos bajo `extensions` tampoco funciona en este cliente. Por ello se exporta
solo el formato compatible (`.codex-plugin/plugin.json` y `.mcp.json`), generado
desde las fuentes raíz, omitiendo los manifiestos portables en la salida.
Codex reconoce entonces skill y MCP. El problema no era la extensión inline
por sí sola; el diseño inicial se ajusta por esta evidencia.
