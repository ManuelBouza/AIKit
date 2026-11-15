# Validación recuperada con el cliente actual — 2026-11-15

La lectura completa e invocación explícita de la skill se han verificado.
La corrección fue usar la CLI de la aplicación activa y MXC en la prueba,
manteniendo permisos de solo lectura. No se reparó la ACL del sandbox legado.

## Diferencia que faltaba comprobar

El diagnóstico anterior tomó `codex` del PATH como representante del cliente
actual. La inspección de ejecutables y procesos fuera del sandbox mostró:

| Componente | Versión observada |
| --- | --- |
| CLI resuelta por PATH, instalación local Programs/OpenAI/Codex | 0.153.4 |
| Aplicación activa, paquete OpenAI.Codex | 26.1111.2228.0 |
| CLI incluida en app/resources del paquete activo | 0.169.0-alpha.11.1 |
| Otra copia en caché local OpenAI/Codex/bin | 0.167.0-alpha.4.1 |

Los tres ejecutables CLI tienen firma Authenticode válida. Los procesos activos
apuntan al paquete indicado; su servicio de sandbox se ejecuta como LocalSystem.
No se sustituyeron binarios ni se cambió PATH.

La configuración guardada selecciona elevated, pero el log del día registra
`MXC availability: true` y `Windows sandbox selection: mxc` para ejecuciones del
cliente actual. La lectura que falló anteriormente registra explícitamente un
helper de `packages/standalone/releases/0.153.4-x86_64-pc-windows-msvc`.
Por tanto, leer solo config.toml y ejecutar el primer codex del PATH no identificó
correctamente el backend efectivo de la aplicación.

## Fuentes y diagnóstico

- La [guía oficial Windows](https://learn.chatgpt.com/docs/windows/windows-sandbox)
  documenta la preferencia automática de MXC en equipos compatibles y una prueba
  puntual mediante `-c windows.sandbox=mxc`, sin guardar configuración.
- Los [perfiles de permisos](https://learn.chatgpt.com/docs/permissions) incluyen
  `:read-only`. Se utilizó `--include-managed-config` en las sondas deterministas.
- La [corrección oficial #59745](https://github.com/openai/codex/pull/59745),
  integrada el 5 de noviembre, trata la falta de WRITE_DAC para SYSTEM y su
  recuperación en ACL legadas. Confirma que esta clase de bloqueo existe; no
  demuestra qué código contiene cada ejecutable local ni que repare nuestro caso.
- Los reportes [#61328](https://github.com/openai/codex/issues/61328) y
  [#61296](https://github.com/openai/codex/issues/61296) aportan casos recientes
  de discrepancias entre componentes y setup exitoso sin recuperación. Se
  consideran observaciones de usuarios, no instrucciones oficiales de reparación.

El bloqueo de la prueba anterior corresponde a CLI antigua + backend legado
forzado, mientras el cliente actual dispone de un backend nativo operativo.
La falta de WRITE_DAC sigue respaldando el fallo legado. No se aisló qué cambio
de versión lo corregiría dentro de elevated: cambiaron ejecutable y backend.
No se afirma que MXC haya reparado el helper ni que la CLI antigua funcione.

## Comprobaciones realizadas

Se consultó primero la ayuda del ejecutable actual. Con su ruta absoluta:

```powershell
& $taskCli -c windows.sandbox=mxc sandbox --include-managed-config --permission-profile :read-only -- $taskShell -NoLogo -NoProfile -NonInteractive -Command 'Get-FileHash -LiteralPath C:/Manuel/Projects/AIKit/packaging/skills/coordinacion-chats/SKILL.md,C:/Manuel/Projects/AIKit/packaging/skills/coordinacion-chats/references/avisos.md | Select-Object Hash,Path | ConvertTo-Json -Compress'
```

`taskCli` se obtuvo del paquete activo, no del PATH; `taskShell` es el PowerShell
actual de Codex. Dos procesos consecutivos terminaron con código 0 y hashes
idénticos a los originales para ambos archivos. El SDDL de .sandbox-bin permaneció
idéntico antes y después de ambas sondas.

Se conservan también dos sondas previas fallidas, sin contarlas como éxitos:
cmd/type devolvió un error de sintaxis y Windows PowerShell 5.1 rechazó la carga
de un archivo .ps1 con AuthorizationManager. Ninguna acredita fallo del helper.
Se consultó la documentación de
[PowerShell](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_powershell_exe)
y [políticas de ejecución](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies/)
antes de utilizar un comando de lectura con el PowerShell actual. No se cambió
ExecutionPolicy ni se utilizó Bypass; esas dos causas no se investigaron por separado.

Después se ejecutó una sola invocación efímera de la skill en un proyecto
temporal externo, conservando el caso ficticio original y los flags read-only,
ignore-user-config, skip-git-repo-check y json. Se cambió la CLI por su ruta
absoluta actual y elevated por mxc. El script nuevo recibe `--codex` obligatorio;
el script histórico y sus resultados se conservaron.

Resultado comprobado por parser JSON, no inferido del texto final del modelo:

- Proceso CLI con exitCode 0 y evento turn.completed.
- Un comando completado con exit_code 0: Get-Content de SKILL.md y avisos.md.
- Su salida contiene íntegros ambos archivos, contrastados con las fuentes.
- La respuesta conserva el worktree mientras el recibo esté pendiente y no se
  haya confirmado la integración; distingue transporte, registro e integración.

Evidencias privadas ignoradas por Git: `.aikit/025-investigacion-final/` y
`.aikit/aikit-025-invocacion-3pui1n8y/`. Script corregido de prueba:
`.aikit/025-invocar-skill-actual.py`. No publicar logs o rutas de identidad sin redactar.

## Alcance y continuación

La validación bloqueada ya puede continuar con el cliente actual. No procede
enviar el borrador anterior como si siguiera sin poder leerse la skill. Si se
reporta el fallo legado, hay que indicar expresamente la versión y el backend,
así como esta recuperación por MXC.

No se repitió setup ni se modificaron manualmente ACL, propietarios, cuentas,
firewall, configuración global o PATH. El error previo del runtime de navegador
(`failed to write kernel assets`, os error 3) no se ha vuelto a probar ni se da
por resuelto mediante este resultado. La skill sigue en fuentes: esta prueba no
la instala ni activa coordinación, mensajería, archivado o automatizaciones.
