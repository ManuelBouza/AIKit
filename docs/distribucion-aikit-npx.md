# Distribución de AIKit mediante npx

Fecha: 2026-11-07. Estado: decisión de distribución; implementación pendiente.

AIKit se distribuirá para instalación y actualización mediante `npx`. El
objetivo es que una persona pueda aplicar la misma versión de sus preferencias
en distintos equipos con un comando. El nombre del paquete, su publicación y
el comando definitivo aún no están definidos ni disponibles.

El instalador deberá aplicar las preferencias aprobadas de AIKit al `AGENTS.md`
global de Codex, conservar contenido ajeno, crear respaldos y permitir repetir
la operación sin duplicar bloques. Debe identificar la versión aplicada,
mostrar los cambios previstos y tratar los conflictos de marcadores y de
`AGENTS.override.md` sin sobrescribirlos silenciosamente. La actualización del
paquete y la aplicación de sus preferencias deben quedar claramente explicadas.

El diseño y las pruebas deben cubrir Windows y otros sistemas que se decida
soportar, perfiles ficticios, instalación inicial, actualización, repetición,
errores y recuperación. Las pruebas iniciales no modifican perfiles reales.
Context7 es una preferencia; su conexión o instalación requiere tratamiento
separado. Delegating to OpenCode conserva su distribución independiente.

## Decisión de implementación

Se elige implementar el instalador de preferencias en Node.js, con un paquete
npm y un ejecutable declarado en `bin`. Requiere Node.js y npm, pero no Python
ni uv en el equipo destinatario. Un lanzador Node que invoque los scripts
Python reutilizaría más código hoy, a cambio de exigir y detectar ambos entornos
o añadir mecanismos para obtener Python. Esa complejidad contradice el objetivo
de instalación sencilla en otros equipos.

La reimplementación tiene un coste y no hereda la fiabilidad de Python por
automático. `scripts/global_instructions.py` y sus pruebas son referencia de
comportamiento: conservar bytes ajenos y BOM, validar marcadores y override,
detectar enlaces y junctions, respaldar y evitar cambios concurrentes. Las
garantías equivalentes en Node, especialmente junctions y sustitución en
Windows, deben verificarse; no se asumen por la elección del lenguaje. El
instalador debe planificar ambos bloques antes de escribir, para evitar una
actualización parcial por procesarlos de forma independiente.

El paquete debe declarar una versión mínima de Node que se decidirá y probará,
identificar la versión aplicada y admitir una versión fijada para reproducirla.
La ruta para solicitar la última versión debe considerar la caché de npm y
documentarse tras su verificación. El nombre, registro y publicación del paquete
permanecen pendientes. No se instalarán dependencias durante la aplicación de
preferencias sin explicarlo al usuario.

Las pruebas y especificaciones anteriores del complemento permanecen como
evidencia histórica; el complemento de configuración es opcional en esta vía.

Referencias: [npm exec](https://docs.npmjs.com/cli/v11/commands/npm-exec/),
[instrucciones AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
