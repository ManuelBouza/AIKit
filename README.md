# AIKit: selección de modelos para delegar

Objetivo: documentar y validar preferencias de Codex para delegar ejecución
acotada a OpenCode. Codex conserva la orquestación, los roles de Superpowers,
las revisiones y la verificación; OpenCode ejecuta la tarea elegida y devuelve un
resultado breve a quien la encargó. El adaptador no sustituye una revisión
independiente.

## Activación e integración

La skill personal `delegating-to-opencode` se invoca explícitamente:

```text
$delegating-to-opencode ejecuta esta subtarea y conserva los revisores de Superpowers
```

Codex también puede seleccionarla por coincidencia entre tarea y descripción. No
hay hooks ni un MCP que intercepten `spawn_agent`. Leer la skill no ejecuta
inferencia: `run` inicia el trabajo externo y `doctor` solo consulta versión y
catálogo.

El coordinador decide si ejecuta de forma nativa o delega. Un subagente nativo de
Codex autorizado y con shell puede usar el adaptador, recibir el resultado y
continuar su trabajo. Los revisores independientes conservan su función. El
`opencode.json` del repositorio bloquea nuevas delegaciones dentro de OpenCode con
`tool.use subagent:*` y el proveedor directo `openai` con `provider.use`; no
limita otros proveedores ni subagentes nativos.

## Requisitos

- Windows (probado) o Unix con Python 3.10+.
- OpenCode v2 instalado y disponible como `opencode` en `PATH`. En Windows, el
  adaptador resuelve el shim de npm al ejecutable
  `node_modules/@opencode/cli/bin/opencode.exe`.
- Las cuentas y proveedores que uses deben estar conectados previamente en
  OpenCode. No se crean cuentas ni se modifican credenciales.
- No se exige `opencode.json` en el directorio de destino. Se respeta la
  configuración y las cuentas ya conectadas.

Los modelos conectados y habilitados en el catálogo efectivo pueden usarse, sean
gratuitos o de pago, salvo el proveedor directo `openai`: comparte la cuenta de
Codex y se rechaza. Los modelos GPT/OpenAI servidos por otros proveedores
conectados (`opencode`, `opencode-go`, `openrouter`, etc.) siguen permitidos. El
adaptador no mantiene una lista cerrada ni un modelo predeterminado.

## Uso

Consultar la versión y el catálogo compacto:

```powershell
python skills/delegating-to-opencode/scripts/delegate.py doctor --cwd .
python skills/delegating-to-opencode/scripts/delegate.py doctor --cwd . --model opencode/deepseek-v4.1-flash-free
```

`doctor` muestra `version`, `catalog_count` y `catalog`. Cada entrada incluye
modelo, nombre, `pricing`, `pricing_tiers`, variantes, herramientas, modalidades
de entrada/salida, límites, `free_candidate` y `may_use_openai_quota`. El
catálogo se ordena con los candidatos gratuitos primero y excluye las entradas
cuyo `providerID` sea `openai`. `--model` filtra por el ID base; un filtro
`openai/...` devuelve `provider_not_allowed` antes de consultar el catálogo.

`pricing` es la primera tarifa, conservada como precio base. `pricing_tiers`
contiene todos los niveles saneados, incluido el `tier` de contexto cuando
existe. Solo expone `input`, `output`, `cache` y `tier`; los importes siguen el
esquema `Model.Cost` en USD por millón de tokens. No se infiere un coste por
llamada.

`free_candidate` solo es `true` si las tarifas conocidas de entrada, salida y
caché son cero. No se deduce por el sufijo `-free`, por el nombre ni por metadatos
de fabricante. Es `null` si el coste es desconocido. Los GPT/OpenAI de otros
proveedores se clasifican por sus tarifas; el proveedor directo `openai` no
aparece en el catálogo.

Guardar la tarea en `.aikit/` (ignorado por Git) y ejecutar un único intento:

```powershell
New-Item -ItemType Directory -Force .aikit | Out-Null
Set-Content -Path .aikit/tarea.md -Encoding utf8 -Value 'Describe la tarea, rutas permitidas y pruebas.'
python skills/delegating-to-opencode/scripts/delegate.py run --cwd . --task-file .aikit/tarea.md --model opencode/deepseek-v4.1-flash-free#high --reason "Integracion acotada; variante alta disponible" --agent build --timeout 600
```

`run` exige `--model` y `--reason` no vacíos. La ausencia de cualquiera de los dos
produce un error JSON antes de iniciar OpenCode; no hay modelo por defecto. La
variante puede indicarse como `provider/model#variante` o con `--variant`, pero
no en ambos formatos. Solo se aceptan IDs de variante presentes en los metadatos
del modelo. Sin variante, la salida informa `variant: null` y
`effort: "provider_default"`. Un `--model openai/...` se rechaza con
`provider_not_allowed` antes de iniciar cualquier proceso, aunque uses variante.

Opciones de `run`: `--model`, `--variant`, `--reason`, `--agent build|plan` y
`--timeout SECONDS`. El timeout debe ser finito, mayor que cero y como máximo
3600 segundos. No se pasan `--variant`, `--effort` ni `--auto` a OpenCode. No hay
`--allow-paid` ni confirmación adicional por uso de pago.

La salida es una sola línea JSON compacta. En éxito incluye `status`, `session`,
`model` base, `variant`, `effort`, `reason`, `agent`, `summary` (máximo 4000
caracteres) y `cost`. El coste de ejecución es `null` si OpenCode no lo informa.
Un evento `error` produce `status: "error"` y salida no cero aunque el proceso
termine con código 0. Los rechazos de modelo, variante, tarea, directorio o
timeout ocurren antes de ejecutar la inferencia.

## Selección por tarea

Antes de ejecutar, clasifica la tarea como mecánica, integración o compleja y
consulta capacidades, herramientas, modalidades, límites, tarifas y variantes.
Elige primero un modelo gratuito suficiente. Un modelo de pago está permitido si
aporta capacidad o fiabilidad necesaria; el usuario ya autorizó considerar pagos
dentro de este alcance. El proveedor directo `openai` está bloqueado; los GPT de
otros proveedores siguen disponibles según su conexión y tarifas.

La variante debe existir en los metadatos. Si no hay variantes o conviene el
ajuste predeterminado, regístralo en `--reason`; no inventes equivalencias con
esfuerzos de Codex. El adaptador no elige automáticamente el mejor modelo ni
debe usarse siempre el mismo. El catálogo prueba disponibilidad actual, no
calidad garantizada.

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

- El catálogo y la política de preferencias no son un sandbox del sistema
  operativo ni garantizan precios, cuotas o calidad futuras. Revisa permisos
  antes de delegar tareas destructivas.
- No se modifican credenciales ni la configuración personal de OpenCode. El
  adaptador no escribe transcripciones ni registros.
- Los workers de OpenCode no cargan esta skill para no delegarse a sí mismos.
  Un fallo vuelve al coordinador, que decide si revisa cambios parciales y prueba
  otro modelo o presupuesto.
- El timeout se aplica por proceso. El adaptador no repite llamadas; OpenCode
  puede reintentar internamente hasta que venza ese límite.
- La validación real se realizó en Windows; Unix no se ha probado con OpenCode.
