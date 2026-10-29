# Instalar AIKit como complemento privado

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
codex plugin add aikit@aikit-local
codex plugin list --marketplace aikit-local --json
```

La salida contiene `aikit/` y su catálogo `.agents/plugins/marketplace.json`.
Conserva esa carpeta de distribución como fuente de actualizaciones; puedes
trasladarla antes de registrar el catálogo. El MCP instalado usa su propia
copia en caché y el lock incluido, sin depender de la `.venv` del checkout.
El primer arranque prepara dependencias y puede necesitar red. El directorio
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

Las fuentes canónicas del build son `plugin.json`, `mcp.json` y `skills/`.
El exportador genera únicamente `.codex-plugin/plugin.json` y `.mcp.json` como
manifiestos de ejecución. No coloca `plugin.json` ni `mcp.json` en la salida:
Codex 0.153.4 los prioriza y su esquema portable rechaza los campos de timeout
específicos de Codex. El formato compatible sí reconoce esas opciones y el MCP.
Así se mantienen los límites de tareas largas sin una segunda copia manual.

El complemento se presenta como AIKit; no se promete una entrada en la pestaña
«Aplicaciones». El MCP sigue llamándose `aikit-opencode`, con dos herramientas.
Se conservan los límites de cancelación y permisos de [MCP](mcp-opencode.md).
La distribución privada no equivale a publicación en el directorio público.

Fuentes: [paquetes](https://developers.openai.com/plugins/build/plugins) y
[MCP locales](https://developers.openai.com/plugins/deploy/desktop-only).

Evidencia de pruebas, instalación y migración: [validación](validacion-plugin.md).
