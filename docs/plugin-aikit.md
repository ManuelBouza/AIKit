# Instalar AIKit como complemento privado

> Documento del empaquetado histórico: este repositorio desarrollará AIKit y
> Delegating to OpenCode como componentes independientes. El exportador aún genera AIKit y no se
> ha verificado un paquete independiente. La instalación descrita aquí no
> representa la nueva distribución; consulta [límites y migración](limites-delegacion-aikit.md).

AIKit agrupa la skill existente y el MCP local. Mantiene las funciones de
orquestación y revisión de Codex y Superpowers. No instala hooks ni conecta
cuentas por su cuenta. Requiere Codex con soporte de plugins locales, uv,
Python 3.10+ y OpenCode v2 con los proveedores conectados y bloqueos necesarios.

## Construir e instalar

Desde el repositorio, elige una salida que aún no exista:

```powershell
python scripts/build_plugin.py --output .aikit/distribucion-v1
$distribucion = (Resolve-Path .aikit/distribucion-v1).Path
codex plugin marketplace add $distribucion
$instalacion = codex plugin add aikit@aikit-local --json | ConvertFrom-Json
uv sync --project $instalacion.installedPath --locked --no-dev --extra mcp
codex plugin list --marketplace aikit-local --json
```

La salida contiene `aikit/` y su catálogo `.agents/plugins/marketplace.json`.
Conserva esa carpeta de distribución como fuente de actualizaciones; puedes
trasladarla antes de registrar el catálogo. El MCP instalado usa su propia
copia en caché y el lock incluido, sin depender de la `.venv` del checkout.
La preparación explícita evita que una primera descarga consuma el timeout de
arranque del cliente. Puede necesitar red. El directorio
de caché debe permitir crear `.venv`; se requieren uv y OpenCode en su `PATH`.

No instales directamente desde la raíz del repositorio: Codex puede copiar
archivos ignorados. El exportador solo incluye archivos de su lista permitida,
rechaza enlaces simbólicos y destinos existentes. Si falla una escritura puede
dejar una salida parcial; inspecciónala y usa otro destino nuevo.

## Actualizar y retirar

Exporta otra salida nueva. Si cambia la ruta de la fuente, retira primero el
registro con `codex plugin marketplace remove aikit-local` y registra la nueva
ruta absoluta con `codex plugin marketplace add`. Después reinstala con
`codex plugin add aikit@aikit-local`. Comprueba el listado y recarga
el cliente. Para retirar el complemento:

```powershell
codex plugin remove aikit@aikit-local
codex plugin marketplace remove aikit-local
```

Estos comandos no desconectan las cuentas de OpenCode. Guarda respaldo de
`config.toml` antes de una migración y conserva las preferencias ajenas.

## Migrar la instalación manual

Comprueba primero el paquete en un `CODEX_HOME` temporal. Después instala el
complemento, valida el MCP desde su caché, aparta la skill personal manual a
`<CODEX_HOME>/backups/aikit/` y retira solo la entrada MCP manual equivalente.
No mantengas activas ambas copias. Compara la configuración anterior y posterior;
restaura el respaldo si falla la migración. Reinicia o recarga Codex para renovar
su catálogo de herramientas; registrar un plugin no demuestra su carga en el chat.

## Formatos y límites

Las fuentes canónicas `plugin.json`, `mcp.json` y `skills/` se exportan sin una
variante legacy que compita con ellas. El formato portable es necesario para que
Codex expanda `${PLUGIN_ROOT}`: en el formato compatible anterior los argumentos
y `cwd` llegaron literales y Windows devolvió el error 267. La prueba con el SDK
no detectó ese fallo porque expandía las variables por su cuenta.

El esquema portable admite los campos STDIO `type`, `command`, `args`, `env` y
`cwd`; el exportador rechaza extras como `tool_timeout_sec`. Los límites del
cliente se aplican sin aumentarlos desde el paquete: normalmente 10 s de arranque
y 60 s por herramienta. Si una tarea no cabe en ese tiempo, usa la CLI instalada
con modelo y esfuerzo explícitos. No reintentes mientras continúe una ejecución
anterior. Los 15000 s documentados corresponden al servidor MCP independiente
configurado expresamente, no al complemento portable por defecto.

El complemento se presenta como AIKit; no se promete una entrada en la pestaña
«Aplicaciones». El MCP sigue llamándose `aikit-opencode`, con dos herramientas.
Se conservan los límites de cancelación y permisos de [MCP](mcp-opencode.md).
La distribución privada no equivale a publicación en el directorio público.

Fuentes: [paquetes](https://developers.openai.com/plugins/build/plugins) y
[MCP locales](https://developers.openai.com/plugins/deploy/desktop-only).

Evidencia de pruebas, instalación y migración: [validación](validacion-plugin.md).

En la prueba real de 0.1.1 el primer inventario del chat aún no tenía las
herramientas; tras seis segundos aparecieron y la delegación mínima funcionó.
Si acabas de iniciar el chat, espera brevemente y vuelve a consultar el inventario
una vez antes de diagnosticar un fallo. La skill visible por sí sola no acredita
que la conexión MCP esté lista.
