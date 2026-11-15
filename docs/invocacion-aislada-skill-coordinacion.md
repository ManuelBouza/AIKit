# Invocación explícita aislada — 2026-11-15

Se usó Codex CLI 0.153.4 en Windows con una copia de la skill en un proyecto
temporal externo. Invocación `$coordinacion-chats` mediante `codex exec`, con
`--ephemeral --ignore-user-config --sandbox read-only --skip-git-repo-check --json`.
Se siguió el [modo no interactivo oficial](https://learn.chatgpt.com/docs/non-interactive-mode).
Se mantuvieron autenticación e instrucciones globales existentes: esta prueba
no equivale al perfil limpio del ensayo previo de descubrimiento.

El caso ficticio preguntaba si retirar un worktree que contenía el único aviso
y evidencia de envío, con respuesta duplicado cuyo recibo seguía pendiente,
sin acceso al canónico y con integración no confirmada. Se prohibieron mensajes,
mutaciones e instalación en el prompt; la sesión hija conservó sandbox read-only.

El primer intento falló antes de inicializar el cliente por acceso denegado a
recursos del perfil bajo el sandbox exterior. El segundo se ejecutó con permiso
acotado para iniciar el cliente, sin cambiar el sandbox de la sesión hija ni
habilitar aprobaciones automáticas. Terminó con código 0.

Resultado observado: el agente anunció la selección de la skill y afirmó haber
leído el SKILL.md incluido en su contexto. Respondió que debía conservar el
worktree y las evidencias, sin confundir duplicado pendiente con incorporación
o integración. Informó expresamente que la política impedía la lectura local de
SKILL.md y references/avisos.md. Los eventos JSONL conservados no muestran una
ejecución de lectura que permita verificar el motivo exacto de ese bloqueo.
No se presenta esa declaración del agente como diagnóstico demostrado de la
política ni el código 0 como prueba de lectura completa de las referencias.

Evidencias locales ignoradas por Git:

- `.aikit/aikit-025-invocacion-m7opy12x/`: primer intento, código 1.
- `.aikit/aikit-025-invocacion-1bmyt_82/`: prompt, comando, eventos y stderr del
  intento concluido; sesión efímera 01a1defa-95ef-7da3-b50f-abeff9d47776.
- `.aikit/025-invocar-skill.py`: lanzador de prueba con límite de 180 segundos.

La selección explícita y respuesta para ese caso se observaron; la lectura local
de la referencia sigue sin acreditarse. No se activó coordinación del proyecto
ni se modificaron chats existentes. Antes de repetir la prueba, diagnosticar las
capacidades y política efectiva de lectura de la sesión; no omitir reglas ni
ampliar permisos de ejecución para forzar un resultado positivo.
