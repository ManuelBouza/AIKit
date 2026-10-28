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

## Selección

Antes de ejecutar:

1. Clasifica la tarea: mecánica, integración o compleja.
2. Consulta capacidades, herramientas, modalidades, límites, tarifas por nivel y
   variantes con `doctor`.
3. Entre opciones suficientes para la tarea y su esfuerzo, prioriza gratuitos de
   OpenCode (también los servidos por Go), después OpenCode Go. Otros proveedores
   conectados siguen permitidos si aportan una alternativa adecuada. No se
   confirma cada uso de Go o pago dentro del alcance autorizado.
4. Elige una variante acorde con la complejidad solo si su ID aparece en
   metadatos; sin variante, registra el ajuste predeterminado.
5. Registra en `--reason` por qué modelo y variante bastan.

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
`$HOME/.codex`. No sobrescribas una instalación existente: valida la ruta, aparta
un respaldo con fecha y decide.

## Límites

Una carpeta o worktree no es un sandbox del sistema operativo. Revisa permisos y
evita tareas destructivas sin supervisión. No escribas credenciales,
transcripciones ni registros. Los errores solo muestran códigos y mensajes
breves; consulta los registros locales de OpenCode.
