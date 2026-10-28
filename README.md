# AIKit: preferencias de Codex

Objetivo: reproducir y validar preferencias de configuración de Codex. La
delegación de subtareas adecuadas a OpenCode reduce trabajo de ejecución en
Codex y complementa sus subagentes y los flujos de Superpowers.

## Activación e integración

La skill personal `delegating-to-opencode` ya aparece en el catálogo de esta
conversación. Puede invocarse explícitamente:

```text
$delegating-to-opencode ejecuta esta subtarea y conserva los revisores de Superpowers
```

Codex también puede seleccionarla por coincidencia entre tarea y descripción;
esa selección no está garantizada en todas las tareas. No hay hooks ni un MCP
que intercepten `spawn_agent`. Leer la skill no ejecuta inferencia: el comando
`run` inicia el trabajo externo y `doctor` solo consulta versión y catálogo.

El coordinador conserva la elección de ejecutor y los roles de Superpowers.
Un implementador nativo de Codex, autorizado y con acceso a shell, puede llamar
al adaptador para una subtarea, recibir el resultado y continuar su trabajo.
Los revisores independientes conservan su función. El adaptador no cambia los
modelos, esfuerzos ni el ciclo de vida de los subagentes nativos.

La regla `tool.use subagent:*` de `opencode.json` bloquea únicamente nuevas
delegaciones dentro de OpenCode; no bloquea subagentes de Codex o Superpowers.
El ejecutor externo no se registra como un subagente nativo y su resultado no
equivale por sí solo a la revisión independiente requerida por un flujo.

## Requisitos

- Windows (probado) o Unix con Python 3.10+.
- OpenCode v2 instalado y disponible como `opencode` en `PATH`. En Windows, el
  adaptador resuelve el shim de npm al ejecutable `node_modules/@opencode/cli/bin/opencode.exe`.
- Política `opencode.json` en el directorio de destino. La del repo deniega todos
  los proveedores, permite solo `opencode` y deniega `tool.use subagent:*`.
- Modelos gratuitos permitidos: `opencode/mimo-v2.6-flash-free` (predeterminado),
  `opencode/deepseek-v4.1-flash-free` y `opencode/glm-5.3-flash-free`.

El adaptador no admite modelos de pago ni fallback automático. Esta restricción
no modifica la selección de modelos de Codex ni de sus subagentes nativos.

## Pruebas

Desde la raíz del repositorio:

```powershell
python -m unittest discover -s tests -v
```

Si el sandbox exige temporales dentro del proyecto:

```powershell
$env:TEMP = (Join-Path (Get-Location) '.aikit\tmp')
$env:TMP = $env:TEMP
New-Item -ItemType Directory -Force $env:TEMP | Out-Null
python -m unittest discover -s tests -v
```

Las pruebas usan un transporte falso: no invocan OpenCode ni consumen cuota.

## Uso

Comprobar versión, catálogo y disponibilidad de los modelos permitidos:

```powershell
python skills/delegating-to-opencode/scripts/delegate.py doctor --cwd .
```

Guardar la tarea en `.aikit/` (ignorado por Git) y ejecutar un único intento:

```powershell
New-Item -ItemType Directory -Force .aikit | Out-Null
Set-Content -Path .aikit/tarea.md -Encoding utf8 -Value 'Describe la tarea, rutas permitidas y pruebas.'
python skills/delegating-to-opencode/scripts/delegate.py run --cwd . --task-file .aikit/tarea.md --model opencode/deepseek-v4.1-flash-free --agent build --timeout 600
```

Opciones de `run`: `--model provider/model`, `--variant NAME`, `--agent build|plan`
y `--timeout SECONDS`. El timeout debe ser finito, mayor que cero y como máximo
3600 segundos; `NaN`, infinito y valores superiores se rechazan. La variante se
pliega en `--model provider/model#variant`; el adaptador nunca pasa `--variant`,
`--effort` ni `--auto` a OpenCode. Si no conoces una variante real del catálogo,
omítela.

La salida es una sola línea JSON compacta. En éxito incluye `status`, `session`,
`model`, `agent`, `summary` (máximo 4000 caracteres) y `cost`; el coste es `null`
si OpenCode no lo informa. Un evento `error` produce `status: "error"` y salida
no cero aunque el proceso termine con código 0. Los rechazos de modelo, política,
directorio o tarea ocurren antes de invocar un modelo.

Antes de ejecutar, el adaptador exige que todos los proveedores del catálogo sean
`opencode`; si la configuración externa expone otro, falla con `unsafe_catalog`.
Los errores de proceso, versión o catálogo solo muestran el código y un mensaje
breve: consulta los registros locales de OpenCode para el detalle.

## Política para otro repositorio

Copia esta plantilla sin sobrescribir una configuración previa. Si ya existe
`opencode.json`, el script crea un respaldo y se detiene para que compares y
combines los cambios manualmente.

```powershell
$repo = 'C:\ruta\otro-repositorio'
$config = Join-Path $repo 'opencode.json'
if (-not (Test-Path $repo)) { throw "No existe el repositorio: $repo" }
if (Test-Path $config) {
    $backup = "$config.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Copy-Item -LiteralPath $config -Destination $backup
    throw "Ya existe $config. Compara la plantilla con el archivo, combina los cambios y conserva el respaldo: $backup"
}
@'
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/mimo-v2.6-flash-free",
  "policies": [
    { "action": "provider.use", "resource": "*", "effect": "deny" },
    { "action": "provider.use", "resource": "opencode", "effect": "allow" },
    { "action": "tool.use", "resource": "subagent:*", "effect": "deny" }
  ]
}
'@ | Set-Content -LiteralPath $config -Encoding utf8
```

El orden importa: `deny` de `provider.use '*'` debe preceder al `allow` de
`opencode`. No agregues `allow` de otros proveedores, comodines ni `tool.use`.

## Instalación personal

La instalación respeta `CODEX_HOME` si está definido y no sobrescribe una copia
existente. Valida las rutas antes de mover nada.

```powershell
$source = Join-Path (Get-Location) 'skills\delegating-to-opencode'
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$dest = Join-Path $codexHome 'skills\delegating-to-opencode'
if (-not (Test-Path $source)) { throw "No existe el origen: $source" }
if (Test-Path $dest) { throw "Ya existe $dest. Valida la ruta y aparta un respaldo antes de continuar." }
New-Item -ItemType Directory -Force (Split-Path $dest) | Out-Null
Copy-Item -Recurse -Path $source -Destination $dest
```

Para actualizar, aparta primero la instalación actual a una carpeta de respaldo
específica después de validar las rutas:

```powershell
$source = Join-Path (Get-Location) 'skills\delegating-to-opencode'
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$dest = Join-Path $codexHome 'skills\delegating-to-opencode'
if (-not (Test-Path $source)) { throw "No existe el origen: $source" }
if (-not (Test-Path $dest)) { throw "No existe la instalación actual: $dest" }
$backup = Join-Path (Split-Path $dest) ("delegating-to-opencode.backup-" + (Get-Date -Format 'yyyyMMdd-HHmmss'))
Move-Item -LiteralPath $dest -Destination $backup
Copy-Item -Recurse -Path $source -Destination $dest
```

Restauración sin borrados recursivos: solo mueve carpetas verificadas y no
sobrescribe una instalación existente.

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$dest = Join-Path $codexHome 'skills\delegating-to-opencode'
$backup = Join-Path (Split-Path $dest) 'delegating-to-opencode.backup-20261028-120000'
if (-not (Test-Path $backup)) { throw "No existe el respaldo: $backup" }
if (Test-Path $dest) { throw "Ya existe $dest. Aparta esa carpeta a otro respaldo antes de restaurar." }
Move-Item -LiteralPath $backup -Destination $dest
```

Ajusta la fecha del ejemplo al respaldo real. Desinstalar es apartar manualmente
solo la carpeta `delegating-to-opencode`.

## Límites

- La lista de modelos y la política del proyecto no son un sandbox del sistema
  operativo ni garantizan precios o cuotas futuras. Revisa permisos antes de
  delegar tareas destructivas.
- La política es del proyecto. En otro repositorio debes comprobar `doctor` y la
  política antes de ejecutar; si falta `opencode.json`, el adaptador falla cerrado.
- No se modifican credenciales ni la configuración personal de OpenCode. El
  adaptador no escribe transcripciones ni registros.
- Los workers no cargan esta skill para no delegarse a sí mismos. Un fallo de
  modelo vuelve al coordinador, que decide sin fallback de pago.
- El timeout se aplica por proceso. El adaptador no repite llamadas; OpenCode
  puede reintentar internamente hasta que venza ese límite.
- La validación real se realizó en Windows; Unix no se ha probado con OpenCode.
