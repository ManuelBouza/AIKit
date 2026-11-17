# Encargo de implementación: seguimiento local de ideas y tareas

Fecha: 2026-11-17.
Estado operativo: consultar [IMP-0001](tareas/IMP-0001/TAREA.md).
Este documento conserva el encargo y arranque históricos; no es otra fuente
editable de estado tras la migración.
Responsable: Coordinador `01a1da03-23f1-7eb0-b0a0-5cb5184e6941`.
Origen: nota 043 y SPEC-seguimiento-ideas-tareas.
Autorización: Manuel aprueba con «go» implementar registro, vistas conectadas,
setup y migración inicial, coordinando previamente el reparto con 028.

## Alcance y aceptación

Cumplir las seis capacidades y los compañeros de la especificación en
`_bmad-output/specs/spec-seguimiento-ideas-tareas/`. Registro local Markdown,
validación y generación seguras, vistas Ideas/Tareas, instrucciones distribuidas
y entrada en setup, migración inicial de encargos y dependencia BMAD.
Implementación y revisión técnica delegadas; el Coordinador mantiene canónico,
responsabilidades, evidencias e integración.

## Arranque y límites

Este registro manual y la nota 043 visible en el tablero conservan trazabilidad
durante el arranque: el nuevo sistema aún no puede mostrar su propio ticket.
Tras disponer de generación validada, registrar este mismo encargo una sola vez
en el nuevo sistema y enlazar este origen; no afirmar visibilidad de tickets
antes de que exista. No es una excepción para encargos posteriores.

La preparación BMAD de los worktrees se registra pero no se ejecuta. No modificar
ramas/worktrees de 028/040, instalar en el perfil, hacer push ni publicar.
Preservar decisiones humanas vigentes; 028 espera decisión visual, 040 sigue
bloqueada por entorno. Aviso de reparto a 028 conservado en
`.aikit/043-reparto-028-03.txt`; esperar confirmación de ausencia de escrituras
antes de modificar el tablero. La implementación visual de 028 no se autoriza.

El árbol contiene cambios documentales de los encargos previos autorizados;
se conserva su procedencia y no se descartan ni se mezclan con cambios ajenos.

## Entrega — 2026-11-17

Registro, vistas y ampliación distribuible de setup implementados. Migración
inicial aplicada con cuatro tickets y procedimiento reproducible conservado.
988 pruebas aprobadas, calidad Python correcta y revisión independiente
aceptada tras corregir los hallazgos. Resultado y límites en
docs/validacion-seguimiento-043.md. La instalación en perfil y push no forman
parte de esta entrega; no se ha preparado BMAD ni modificado recursos de tareas.
