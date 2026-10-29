---
name: delegating-to-opencode
description: Use when delegating a bounded implementation or transformation task to OpenCode with a connected model other than the direct openai provider, preferring free models and recording the selection reason.
---

# Delegar a OpenCode

OpenCode ejecuta trabajo acotado. El coordinador o subagente nativo de Codex
autorizado usa esta skill antes de implementar o transformar archivos. Conserva
roles, ciclo de vida y revisiones de Codex y Superpowers: ejecuta en OpenCode y
devuelve el resultado a quien lo invocó, que verifica diff y pruebas. Los workers
de OpenCode no cargan esta skill ni redelegan.

## Activación

Se invoca con `$delegating-to-opencode` o por descripción. No intercepta
`spawn_agent`, MCP ni modelos nativos. Sin ejecución externalizable no se llama
al backend. `run` inicia inferencia; `doctor` solo consulta versión y catálogo.

## Ruta y requisitos

El adaptador es `scripts/delegate.py` en la carpeta de este `SKILL.md`. Descubre
su ruta absoluta instalada, no relativa al repositorio de origen. Requiere Python
3.10+ y OpenCode v2 en `PATH`; en Windows se resuelve el shim de npm al
`opencode.exe` nativo. No requiere `opencode.json` en destino ni modificar
cuentas, proveedores o credenciales.

## MCP local

El mismo núcleo se expone como servidor MCP local por STDIO
(`scripts/mcp_server.py`), con dos herramientas: `opencode_catalog` y
`opencode_delegate`. Si el cliente publica ese servidor, prefiere las
herramientas MCP; la CLI sigue como alternativa y diagnóstico. Ninguna de las
dos rutas intercepta `spawn_agent` ni los subagentes nativos.

```powershell
$skillDir = 'C:\ruta\absoluta\descubierta\delegating-to-opencode'
$python = 'C:\ruta\absoluta\AIKit\.venv\Scripts\python.exe'
& $python (Join-Path $skillDir 'scripts\mcp_server.py')
```

El servidor necesita el SDK oficial `mcp>=1.26,<2` en ese intérprete; la CLI
sigue siendo solo biblioteca estándar. `stdout` queda reservado al protocolo
MCP. Las mismas políticas, bloqueos, certificado de configuración y errores se
aplican en ambos caminos: no hay una segunda copia de esas reglas.

El timeout del cliente MCP debe ser suficiente: una ejecución lanza hasta cuatro
procesos de OpenCode, así que usa `tool_timeout_sec` 15000 (o el equivalente de
tu cliente), no 600 s ni el valor por defecto de 60 s. Cancelar o cerrar la
llamada no detiene el backend: el SDK puede responder de inmediato mientras el
worker sigue, y el timeout del proceso solo protege mientras el servidor MCP
esté vivo. Detalle y límites en `docs/mcp-opencode.md`.

Las respuestas del núcleo son JSON en `content` y en `structuredContent`. Los
errores de validación del SDK —campo obligatorio ausente o tipo incorrecto—
llegan como texto con `isError: true` y sin `structuredContent`: respeta
`isError` y no deserialices `structuredContent` sin comprobar que existe.

## Selección

La prioridad la decide el coordinador siguiendo estas instrucciones. El
adaptador no evalúa si un modelo basta para la tarea, no ordena la elección ni
la toma: solo presenta el catálogo y ejecuta el modelo indicado con su motivo.
La preferencia de `policy.json` es solo `prefer_free` booleano y únicamente
ordena la presentación del catálogo; el motivo es obligatorio en `run` en todos
los casos.

Antes de ejecutar:

1. Clasifica la tarea: mecánica, integración o compleja.
2. Consulta capacidades, herramientas, modalidades, límites, tarifas por nivel y
   variantes con `doctor`.
3. Entre opciones suficientes para la tarea y su esfuerzo, prioriza gratuitos de
   OpenCode (también los servidos por Go), después OpenCode Go, después otras
   alternativas adecuadas de proveedores conectados y, si ninguna sirve,
   continúa con Codex nativo. Otros proveedores
   conectados siguen permitidos si aportan una alternativa adecuada. No se
   confirma cada uso de Go o pago dentro del alcance autorizado.
4. Elige una variante acorde con la complejidad solo si su ID aparece en
   metadatos; sin variante, registra el ajuste predeterminado.
5. Registra en `--reason` por qué modelo y variante bastan.

Antes de cada tarea o reintento con inferencia, avisa al usuario qué se delega,
el modelo/proveedor elegido, el esfuerzo (variante publicada o predeterminado)
y si es gratuito o de pago. Si la tarifa no está acreditada, indícala como
desconocida; no equipares coste no informado con gratuito.

No elige automáticamente el mejor modelo ni usa siempre el mismo. El proveedor
directo `openai` está bloqueado porque comparte la cuenta Codex: se rechaza
`openai/*`, incluidas variantes, y `doctor` lo excluye. Los modelos GPT/OpenAI de
otros proveedores conectados (`opencode`, `opencode-go`, etc.) siguen permitidos,
gratuitos o de pago. El bloqueo depende del `providerID`, no del fabricante,
nombre o metadatos `canonical`. El catálogo prueba disponibilidad actual, no
calidad.

## Ejecución

```powershell
$skillDir = 'C:\ruta\absoluta\descubierta\delegating-to-opencode'
$delegate = Join-Path $skillDir 'scripts\delegate.py'
python $delegate doctor --cwd .
python $delegate run --cwd . --task-file .aikit/tarea.md --model opencode/deepseek-v4.1-flash-free#high --reason "Integracion acotada; variante alta disponible" --agent build --timeout 600
```

Guarda la tarea en `.aikit/`, ignorado por Git, con objetivos, rutas, pruebas y
límites. `--model` y `--reason` son obligatorios. La variante va en `#variante` o
`--variant`, nunca en ambos. Usa solo IDs de `doctor`; no inventes equivalencias
con esfuerzos de Codex. Timeout finito, mayor que cero y máximo 3600 s. No se
pasan `--variant`, `--effort` ni `--auto` a OpenCode.

La salida es una línea JSON. En éxito incluye modelo base, variante, esfuerzo,
motivo, sesión, resumen <=4000 caracteres y coste informado o `null`. Errores y
eventos fallidos vuelven al invocador. El adaptador no reintenta automáticamente;
revisa cambios parciales antes de otro intento seleccionado por el coordinador.

## Protección del destino

`run` comprueba antes de inferir que la configuración efectiva del destino
acredita los bloqueos `provider.use openai deny` y `tool.use subagent:* deny`.
Los bloqueos pueden estar en la configuración global o en la del proyecto; no
hace falta un archivo local. `doctor` no exige esos bloqueos: solo consulta.

Si la comprobación falla o el certificado no se consigue, `run` devuelve
`unsafe_configuration` o `config_check_failed` sin iniciar la inferencia. El
mensaje es fijo y no expone salida, rutas ni contenido de la configuración. El
certificado es conservador: cualquier `allow` que pueda contradecir un bloqueo
impide la ejecución, aunque la configuración sea segura en la práctica. Detalles
y límites en `docs/correcciones-revision-funcional.md`.

## Orquestación y verificación

Codex conserva orquestación y verificación, incluidas comprobaciones de shell.
Si OpenCode agota el uso gratuito, `free_limit_reached` con `fallback: reselect`
devuelve la elección al coordinador. Evalúa Go y otras alternativas conectadas
adecuadas, con modelo y variante razonados, sin nueva confirmación. Si no queda
una opción adecuada disponible en OpenCode, informa y continúa normalmente con
Codex y sus subagentes nativos. El catálogo no garantiza cuota ni disponibilidad
de inferencia; un fallo aislado tampoco demuestra que todo OpenCode esté agotado.
No uses `openai/*` ni eludas controles de permisos, autenticación o privacidad.
El helper no cambia cuentas, reintenta ni lanza Codex. Informa los bloqueos reales
sin presentar trabajo no ejecutado como completado.

## Instalación

Copia la carpeta completa (`scripts/` y `policy.json`) a
`<CODEX_HOME>/skills/delegating-to-opencode`; si `CODEX_HOME` no existe, usa
`$HOME/.codex`. No sobrescribas una instalación existente: valida la ruta y aparta
un respaldo con fecha en `<CODEX_HOME>/backups/aikit`, fuera de los directorios
`skills/` y `plugins/` que Codex descubre, para que el respaldo no se active
como skill duplicada.

## Límites

Una carpeta o worktree no es un sandbox del sistema operativo. El aislamiento es
responsabilidad del entorno; esta skill no aporta contenedor ni aislamiento.
El bloqueo `tool.use subagent:*` es una política de la herramienta `subagent` de
OpenCode: no impide por sí solo el uso de `shell` ni de otros comandos
arbitrarios que las reglas del agente permitan. Revisa permisos y evita tareas
destructivas sin supervisión. El timeout se
aplica por proceso: OpenCode puede reintentar internamente hasta que venza. Un
intento puede dejar cambios parciales; el adaptador no los revierte ni ofrece
rollback, así que revisa el diff antes de reintentar. No escribas credenciales,
transcripciones ni registros. Los errores solo muestran códigos y mensajes
breves; consulta los registros locales de OpenCode. El empaquetado del
complemento está disponible mediante el exportador del repositorio; instalación
y migración en `docs/plugin-aikit.md`. La propagación global automática de la
preferencia sigue pendiente.
