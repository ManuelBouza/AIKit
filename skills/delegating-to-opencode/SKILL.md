---
name: delegating-to-opencode
description: Use when delegating a bounded task or subtask to OpenCode, especially to use free models alongside Codex or Superpowers workflows.
---

# Delegar a OpenCode

OpenCode es un ejecutor externo complementario. El coordinador o un subagente
nativo de Codex con autorización y acceso a shell puede usar el adaptador para
una tarea acotada. El resultado vuelve al rol que lo invocó para su verificación.
Los workers de OpenCode no cargan esta skill ni vuelven a delegar.

## Activación e integración

Se puede invocar con `$delegating-to-opencode` o seleccionar cuando la tarea
coincida con su descripción. Estar disponible no obliga a utilizarla. Una
consulta sin trabajo externalizable no necesita ejecutar OpenCode.

Conserva los roles, subagentes, revisiones y pruebas previstos por Codex y
Superpowers. El coordinador elige entre ejecución nativa y externa según la
tarea; prioriza modelos gratuitos para subtareas adecuadas. Un implementador
nativo puede encargar una subtarea al adaptador y conservar su responsabilidad.
La salida de OpenCode no sustituye una revisión independiente requerida.

Esta skill no intercepta `spawn_agent`, cambia modelos o esfuerzos nativos ni
instala hooks, MCP o servicios. Solo `run` inicia trabajo de inferencia externo;
`doctor` consulta versión y catálogo. No crea subagentes nativos automáticamente.

## Ruta del adaptador

El adaptador es `scripts/delegate.py` dentro de la misma carpeta que este
`SKILL.md`. No uses rutas relativas al repositorio de origen: descubre la carpeta
real de la skill instalada en el catálogo de Codex y define `$skillDir` con esa
ruta absoluta.

```powershell
# Sustituye el marcador por la ruta absoluta real descubierta en el catálogo.
$skillDir = 'C:\ruta\absoluta\descubierta\delegating-to-opencode'
$delegate = Join-Path $skillDir 'scripts\delegate.py'
python $delegate doctor --cwd .
```

## Flujo

1. Prepara la tarea en un archivo dentro de `.aikit/`, que está ignorado por Git.
   Incluye objetivos, rutas permitidas, comandos de prueba y límites.
2. Comprueba el entorno desde la raíz del proyecto:

   ```powershell
   python $delegate doctor --cwd .
   ```

3. Ejecuta un único intento con un modelo explícito y timeout acotado:

   ```powershell
   python $delegate run --cwd . --task-file .aikit/tarea.md --model opencode/deepseek-v4.1-flash-free --agent build --timeout 600
   ```

   El timeout por proceso debe ser finito, mayor que 0 y como máximo 3600 segundos. La variante
   opcional se pliega en el modelo como `provider/model#variant` o se indica con
   `--variant`. Si el catálogo real no documenta una variante para el modelo,
   omite la variante: no inventes `high`, `low` ni equivalentes. Nunca se pasan
   `--variant`, `--effort` ni `--auto` a OpenCode.
4. Revisa el JSON de salida: `status`, `summary`, `session`, `cost` y errores.
   El coste es `null` si OpenCode no lo informa; no se interpreta como cero.
5. Verifica los cambios y ejecuta las pruebas localmente antes de aceptarlos.

## Política requerida en el proyecto

El directorio destino debe tener un `opencode.json` con esta política. El orden
importa: `deny` de `provider.use '*'` debe ir antes del `allow` de `opencode`.
No agregues `allow` para otros proveedores, comodines ni `tool.use`.
La regla `subagent:*` limita únicamente la subdelegación interna de OpenCode;
no limita los subagentes de Codex ni los roles de Superpowers.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/mimo-v2.6-flash-free",
  "policies": [
    { "action": "provider.use", "resource": "*", "effect": "deny" },
    { "action": "provider.use", "resource": "opencode", "effect": "allow" },
    { "action": "tool.use", "resource": "subagent:*", "effect": "deny" }
  ]
}
```

La lista cerrada de modelos vive en `policy.json`, junto a este `SKILL.md`.
Después de leer el catálogo, el adaptador exige que todos los proveedores
disponibles sean `opencode`; si aparece otro, falla con `unsafe_catalog`. Si
falta `opencode.json` o la política no cumple, el adaptador falla cerrado.

## Reglas

- Solo se permiten `opencode/mimo-v2.6-flash-free`,
  `opencode/deepseek-v4.1-flash-free` y `opencode/glm-5.3-flash-free`.
  No hay pago, proveedor `openai/*`, reintentos ni alternativa automática.
- Si el modelo gratuito falla, vuelve al coordinador con el error. No cambies a
  un modelo de pago por iniciativa propia.
- El adaptador no reintenta; OpenCode puede reintentar internamente dentro del
  tiempo máximo del proceso. Revisa cambios parciales antes de un nuevo intento.
- Las restricciones de proveedor y modelo se aplican a este adaptador; no
  cambian la selección de modelos de los subagentes nativos.
- Una carpeta o worktree no es un sandbox del sistema operativo. Revisa permisos
  y no ejecutes tareas destructivas sin supervisión.
- No escribas credenciales, transcripciones ni registros desde el adaptador.
  OpenCode conserva sus propios registros. Los errores de proceso, versión o
  catálogo solo muestran el código de salida; consulta esos registros locales.

## Instalación

Copia la carpeta completa que contiene este `SKILL.md` (con `scripts/` y
`policy.json`) a `<CODEX_HOME>/skills/delegating-to-opencode`; si `CODEX_HOME` no
está definido, usa `$HOME/.codex`. No sobrescribas una instalación existente:
valida la ruta, aparta la copia actual a un respaldo con fecha y decide
manualmente. Después vuelve a descubrir `$skillDir` desde el catálogo.
