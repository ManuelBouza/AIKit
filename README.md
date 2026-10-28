# AIKit: configuraciones y skills para Codex

AIKit evoluciona hacia un complemento instalable que reúna preferencias de
configuración y distintas skills reutilizables. Debe complementar Superpowers y
las demás capacidades instaladas. Antes de crear o modificar una skill, se
comprueba si una existente cubre la necesidad y se documenta la diferencia que
justifica el cambio.

Actualmente el repositorio distribuye una skill individual con instalación
manual; todavía no contiene el empaquetado de un complemento. La portabilidad
del complemento entre entornos sigue pendiente: las rutas, las cuentas y las
credenciales son locales y no forman parte de la preferencia distribuible. Los
criterios de evolución, reutilización y compatibilidad están en
[Principios de AIKit](docs/principios-aikit.md).

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
- Para usar `run` sí hace falta que la configuración efectiva del destino
  acredite dos bloqueos: el proveedor directo `openai` (`provider.use`) y la
  subdelegación interna (`tool.use` con `subagent:*`). Basta con que estén en
  la configuración global o en la del proyecto; no hace falta un archivo local.
  `doctor` no exige esos bloqueos.

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
catálogo se ordena con los candidatos gratuitos primero, después OpenCode Go y
finalmente otros proveedores (coste desconocido antes de pago). Ese orden es de
lectura, no una selección: el adaptador no elige modelo. Excluye entradas
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

Antes de inferir, `run` comprueba la configuración efectiva del destino con
`opencode debug config --standalone` y exige un certificado: los bloqueos exactos
`provider.use openai deny` y `tool.use subagent:* deny`, presentes en la
configuración global o en la del proyecto, y ningún `allow` que pueda
contradecirlos. Si la comprobación falla o el certificado no se consigue, `run`
devuelve `unsafe_configuration` o `config_check_failed` y no inicia la
inferencia. El mensaje es fijo y no incluye salida, rutas ni contenido de la
configuración. El certificado es conservador: un `allow` anterior o demasiado
amplio puede impedir la ejecución aunque la configuración sea segura en la
práctica. Los detalles y los límites están en
[Correcciones de la revisión funcional](docs/correcciones-revision-funcional.md).

## Selección por tarea

La prioridad es una decisión del coordinador: las preferencias se aplican por
instrucciones al coordinador, no dentro del adaptador. El adaptador no evalúa
si un modelo basta para la tarea, no ordena la elección y no la toma; solo
presenta el catálogo y ejecuta el modelo que el coordinador indica junto a su
motivo.

Antes de ejecutar, clasifica la tarea como mecánica, integración o compleja y
consulta capacidades, herramientas, modalidades, límites, tarifas y variantes.
Determina primero las capacidades y el esfuerzo necesarios. Entre opciones
suficientes, el coordinador prioriza gratuitos de OpenCode (incluidos los de
Go), después OpenCode Go, después otras alternativas adecuadas de proveedores
conectados y, si ninguna sirve, continúa con Codex nativo. Otros proveedores
conectados siguen permitidos si ofrecen una alternativa adecuada; no se
confirma cada uso dentro del alcance autorizado. El proveedor directo `openai`
está bloqueado; los GPT de otros proveedores siguen disponibles según su
conexión y tarifas.

La variante debe existir en los metadatos. Si no hay variantes o conviene el
ajuste predeterminado, regístralo en `--reason`; no inventes equivalencias con
esfuerzos de Codex. El adaptador no elige automáticamente el mejor modelo ni
debe usarse siempre el mismo. El catálogo prueba disponibilidad actual, no
calidad garantizada.

La preferencia distribuida en `policy.json` solo admite `prefer_free`
booleano y únicamente ordena la presentación del catálogo. No contiene
opciones de modelo, de pago ni de motivo: el motivo es obligatorio en `run` en
todos los casos y el modelo lo elige el coordinador. Cualquier clave
desconocida hace fallar la carga de la política con `policy_invalid`.

## Desarrollo y pruebas

Instala [uv](https://docs.astral.sh/uv/) y, desde la raíz, sincroniza el entorno
reproducible. `uv sync` crea o actualiza `.venv` usando `uv.lock`; no necesitas
activar el entorno manualmente. Solo las herramientas de desarrollo requieren
dependencias: el adaptador distribuido sigue usando la biblioteca estándar.

```powershell
uv sync --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

Para aplicar el formato:

```powershell
uv run ruff format .
```

Las pruebas usan fixtures, parametrización y un transporte falso: no invocan
OpenCode ni consumen cuota. Los temporales de pytest viven en `.aikit/pytest-tmp`.
Si el sandbox restringe la caché de uv, usa
`$env:UV_CACHE_DIR = Join-Path (Get-Location) '.aikit\uv-cache'`.

La configuración de pytest, Ruff y mypy está en `pyproject.toml`. Las anotaciones
son obligatorias; el uso de `Any` se reserva para los datos JSON externos. Los
módulos de pruebas se organizan por comportamiento y comparten solo fixtures
y constructores de datos.

## Disponibilidad y paso a Codex

Si OpenCode informa `provider.free-limit`, el adaptador devuelve
`code: free_limit_reached` y `fallback: reselect`. El coordinador evalúa OpenCode
Go y otras alternativas conectadas adecuadas, elige modelo y variante y revisa
los cambios parciales antes de otro intento. Go está autorizado sin nueva
confirmación. Si no queda una opción adecuada disponible en OpenCode, informa
y continúa con Codex nativo, conservando el flujo de Superpowers.

El catálogo no garantiza cuota ni inferencia disponible. Un fallo aislado no
demuestra agotamiento de todos los modelos. El helper ejecuta un único intento:
no reintenta ni lanza Codex automáticamente. No habilita `openai` directo ni
elude restricciones de permisos, autenticación o privacidad. Consulta el
[escenario de Go](docs/prioridad-opencode-go.md) para los resultados observados.

## Instalación personal

La instalación respeta `CODEX_HOME` si está definido y no sobrescribe una copia
existente. Valida las rutas antes de mover nada.

```powershell
$source = Join-Path (Get-Location) 'skills\delegating-to-opencode'
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$dest = Join-Path $codexHome 'skills\delegating-to-opencode'
if (-not (Test-Path $source)) { throw "No existe el origen: $source" }
if (Test-Path $dest) { throw "Ya existe $dest. Valida la ruta y aparta un respaldo antes de continuar." }
New-Item -ItemType Directory -Force -ErrorAction Stop (Split-Path $dest) | Out-Null
Copy-Item -Recurse -Path $source -Destination $dest -ErrorAction Stop
```

Los respaldos viven en `<CODEX_HOME>/backups/aikit`, fuera de los directorios
`skills/` y `plugins/` que Codex descubre. Un respaldo guardado dentro de
`<CODEX_HOME>/skills/` aparecería en el catálogo como una skill duplicada y
podría activarse por descripción. Fuera de esas rutas habituales no se puede
garantizar que un archivo sea indescubrible: comprueba que ningún enlace ni
referencia de la configuración o de tus scripts apunte al respaldo.

Para actualizar, aparta primero la instalación actual a una carpeta de respaldo
específica después de validar las rutas. La marca de tiempo puede colisionar, así
que el respaldo no debe existir antes de mover nada:

```powershell
$source = Join-Path (Get-Location) 'skills\delegating-to-opencode'
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$dest = Join-Path $codexHome 'skills\delegating-to-opencode'
$backupRoot = Join-Path $codexHome 'backups\aikit'
if (-not (Test-Path $source)) { throw "No existe el origen: $source" }
if (-not (Test-Path $dest)) { throw "No existe la instalación actual: $dest" }
New-Item -ItemType Directory -Force -ErrorAction Stop $backupRoot | Out-Null
$backup = Join-Path $backupRoot ("delegating-to-opencode-" + (Get-Date -Format 'yyyyMMdd-HHmmss'))
if (Test-Path $backup) { throw "Ya existe el respaldo $backup. Aparta ese respaldo o usa otra marca de tiempo." }
Move-Item -LiteralPath $dest -Destination $backup -ErrorAction Stop
Copy-Item -Recurse -Path $source -Destination $dest -ErrorAction Stop
```

Restauración sin borrados recursivos: solo mueve carpetas verificadas y no
sobrescribe una instalación existente.

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$dest = Join-Path $codexHome 'skills\delegating-to-opencode'
$backup = Join-Path $codexHome 'backups\aikit\delegating-to-opencode-20261028-120000'
if (-not (Test-Path $backup)) { throw "No existe el respaldo: $backup" }
if (Test-Path $dest) { throw "Ya existe $dest. Aparta esa carpeta a otro respaldo antes de restaurar." }
Move-Item -LiteralPath $backup -Destination $dest -ErrorAction Stop
```

Ajusta la fecha del ejemplo al respaldo real. Desinstalar es apartar manualmente
solo la carpeta `delegating-to-opencode`.

## Límites

- El catálogo y la política de preferencias no son un sandbox del sistema
  operativo ni garantizan precios, cuotas o calidad futuras. El aislamiento es
  responsabilidad del entorno; esta skill no aporta contenedor ni aislamiento.
  Revisa permisos antes de delegar tareas destructivas.
- El bloqueo `tool.use subagent:*` es una política de la herramienta `subagent`
  de OpenCode, no un sandbox: no impide por sí solo que el agente use `shell`
  ni otros comandos arbitrarios que sus reglas permitan.
- No se modifican credenciales ni la configuración personal de OpenCode. El
  adaptador no escribe transcripciones ni registros.
- Los workers de OpenCode no cargan esta skill para no delegarse a sí mismos.
  Un fallo vuelve al coordinador, que decide si revisa cambios parciales y prueba
  otro modelo o presupuesto.
- El timeout se aplica por proceso. El adaptador no repite llamadas; OpenCode
  puede reintentar internamente hasta que venza ese límite.
- Un intento puede dejar cambios parciales en el destino. El adaptador no los
  revierte ni ofrece rollback: revisa el diff antes de reintentar.
- El empaquetado del complemento y la propagación global de la preferencia
  siguen pendientes; hoy la instalación es manual y por entorno.
- La validación real se realizó en Windows; Unix no se ha probado con OpenCode.
