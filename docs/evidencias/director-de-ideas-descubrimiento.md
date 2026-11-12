# Prueba del Director de Ideas

Fecha: 2026-11-09. Se ejecutó `codex exec` en Windows con sesiones efímeras,
`--ignore-user-config` y carpetas temporales fuera del repositorio. Las sesiones
usaron la autenticación y las instrucciones globales existentes; no representan
un perfil de Codex completamente limpio ni prueban Codex Desktop.

## Descubrimiento

Se copió la skill a `.agents/skills/director-de-ideas` en dos carpetas. En la
segunda se añadió únicamente el `SKILL.md` de `bmad-forge-idea` como candidato
de descubrimiento; no era una instalación funcional completa de BMAD.

Ante la misma petición de explorar una aplicación sin construirla, en ambas
sesiones Codex anunció que usaría Director de Ideas y trató de leer su archivo.
En ambos casos la política del entorno de ejecución bloqueó el comando de
lectura; cada sesión informó que no había podido aplicar la skill. La primera
usó `--sandbox read-only`, la segunda `--sandbox workspace-write`. La selección
observada no demuestra carga ni convivencia funcional con BMAD.

## Comportamiento con instrucciones suministradas

En una tercera sesión se incluyó el contenido completo de la skill en la
solicitud, sin depender de la lectura bloqueada. Ante la idea abierta, Codex
pidió un ejemplo para aclarar el problema y afirmó que no construiría la
aplicación. Esta prueba muestra una respuesta coherente para ese caso; no prueba
la carga automática, todos los escenarios ni el comportamiento de la skill
instalada en el complemento. Una evaluación conceptual independiente de otros
escenarios está anotada en la especificación y no equivale a ejecución real.

Quedan pendientes una ejecución que pueda leer la skill descubierta y la
verificación con una instalación funcional de BMAD y sin ella. No se modificó
la instalación real del complemento ni el AGENTS.md global.

## Diagnóstico de la política

Codex CLI 0.153.4 informó `blocked by policy` al intentar abrir la skill desde
ambos perfiles de sandbox. Según la [documentación oficial de reglas](https://developers.openai.com/codex/rules),
`codex execpolicy check` permite comprobar coincidencias en archivos `.rules`.
La comprobación del comando de lectura frente a `~/.codex/rules/default.rules`
devolvió `matchedRules: []`. Eso descarta una coincidencia en ese archivo para
esa forma del comando, pero no identifica la política efectiva ni descarta otras
capas; el origen concreto del bloqueo sigue sin demostrarse.

Se intentó solicitar una prueba con `--approve-for-me`. La revisión automática
rechazó iniciar la acción porque permitiría aprobar otras acciones de la sesión,
excediendo el alcance de leer la skill. No se intentó eludir el rechazo. La
prueba de lectura efectiva y comportamiento sigue pendiente de un entorno que
permita la operación sin ampliar indebidamente sus permisos.
