# Ideas y tareas de implementación conectadas

Fecha: 2026-11-17.
Estado inicial: Pendiente de debatir.
Estado actual: Implementada y verificada localmente; incorporación al perfil instalado pendiente.

## Entrega local — 2026-11-17

Registro Markdown, vistas Ideas/Tareas, validación y ampliación de las skills de
coordinación/setup implementados en fuentes. Migración inicial: cuatro tickets
canónicos, sin ejecutar BMAD ni alterar encargos. Verificación conjunta de
988 pruebas aprobadas, Ruff/mypy correctos y revisión independiente aceptada.
[Evidencia](../docs/validacion-seguimiento-043.md) y
[procedimiento de migración](../coordinacion/MIGRACION-043.md).
El complemento del perfil habitual sigue en la versión previamente instalada;
no se ha instalado esta ampliación ni publicado. El generador es una herramienta
local del desarrollo y no un requisito universal para otros proyectos.

## Implementación — 2026-11-17

Manuel aprueba implementar con «go», turno del Coordinador
`01a1e85d-1934-7672-9cc3-6a4d7b0314e1`, mensaje humano
`01a1e85d-1aaa-7183-a8df-7baafeaeefe8`. Encargo canónico de ejecución:
[IMP-0001](../coordinacion/tareas/IMP-0001/TAREA.md).
Migración inicial simulada y preestado conservado: altas de 028, 040 y su
dependencia BMAD, sin ejecutar la preparación ni cambiar decisiones humanas.
La nueva vista se ha generado; pruebas y revisión final siguen pendientes.

## Especificación — 2026-11-17

Manuel elige «go, la opcion 1»: se adopta el registro local Markdown.
El contrato está en [SPEC.md](../_bmad-output/specs/spec-seguimiento-ideas-tareas/SPEC.md),
con sus compañeros de datos/flujo y migración/aceptación y memoria canónica.
La formalización no ejecuta la implementación ni la migración.

La conciliación de estados actualiza el snapshot: 028 está Esperando al usuario
para aprobar su propuesta visual tras su reanudación directa; 040 sigue Bloqueada
por el entorno. La migración debe contrastar el estado vigente al ejecutarse,
sin aplicar pausas históricas como instrucciones nuevas.

## Diseño propuesto — 2026-11-17

El usuario confirma explícitamente la relación de una idea con varias tareas y
la posibilidad de encargos directos sin idea previa. Aprueba con «go» definir
el registro y su conexión con el tablero, sin implementar todavía el sistema.

[Borrador técnico](../docs/diseno-ideas-tareas-043.md), contrastado con GitHub
Docs y la Kanban Guide. Recomienda para AIKit tickets Markdown bajo el registro
canónico existente, identidades independientes de las notas, vistas derivadas
Ideas/Tareas y separación entre fase de ejecución, espera y estado del chat.
Los estados, rutas e identificadores se concretan en la especificación posterior.
En otros proyectos se reutiliza su tracker canónico disponible sin duplicarlo.

[Encargo documental y resultado](../coordinacion/diseno-seguimiento-043.md).
La migración, el nuevo generador y la distribución mediante setup no se han
implementado. La regla local ya registrada no equivale a esas capacidades.

## Solicitud del usuario

Cada encargo de implementación debe estar registrado y visible para seguimiento
antes de implementarlo. Si el agente detecta un encargo sin registro, debe
agregarlo antes de comenzar. Incorporar este comportamiento como regla de AIKit,
además de aplicarlo en su desarrollo.

Separar dos sistemas conectados:

- Notas e ideas: ocurrencias, dudas, contexto y maduración con el usuario,
  consultables en el tablero de ideas.
- Tareas de implementación: tickets del backlog para seguir trabajo pendiente
  de implementar, en implementación y completado, incluyendo esperas y bloqueos.

## Criterios y propuesta inicial

- Una idea puede dar lugar a varias tareas; un encargo directo puede crear una
  tarea sin obligar a inventar una idea previa. Conservar enlaces de origen.
- Separar estado de maduración de una idea y estado de ejecución de sus tareas.
  No declarar una idea implementada por completar solo una parte de su alcance.
- Registrar antes de implementar, comprobar duplicados y reutilizar la tarea
  existente al recibir instrucciones adicionales del mismo encargo.
- Registrar no equivale a autorizar ejecución: conservar go, pausas, decisiones
  materiales y permisos sensibles.
- Conservar alcance, responsable, estado, dependencias, chat cuando exista,
  criterios de aceptación y evidencia de entrega con profundidad proporcional.
- El Coordinador mantiene el registro canónico; las tareas comunican cambios
  por el cauce autorizado sin escribir el registro compartido desde su worktree.
- Reutilizar herramientas existentes cuando cubran el seguimiento; el mecanismo
  general de AIKit no debe exigir BMAD, Git, GitHub ni un cliente concreto.
- Integrar la activación y configuración en aikit-setup, con ámbito y herramienta
  de seguimiento identificados. No instalar ni activar preferencias por leerlas.

## Situación y decisiones pendientes

El tablero actual se genera desde notas/IDEAS.md y mezcla ideas con resúmenes
de implementación. Los encargos 028/040 tienen seguimiento manual en coordinacion/,
pero no existe todavía el segundo sistema general solicitado.

La regla local en AGENTS.md exige registrar antes de implementar y permite usar
el registro existente mientras se diseña el sistema. Esto no acredita que los
tickets sean ya visibles en el tablero actual ni que la regla esté distribuida
en el complemento instalado.

Definir almacenamiento canónico de tickets, identificadores, estados y vistas,
reutilización de artefactos BMAD, migración de encargos existentes y comprobación
del registro previo. Contrastar documentación oficial y fuentes especializadas
antes de recomendar la implementación. No migrar ni ampliar el encargo 028
automáticamente; coordinar cualquier cambio que afecte al tablero.

La preparación aislada de BMAD para 040 sigue pendiente. Debe figurar como tarea
de implementación identificable antes de ejecutarse; esta nota no la resuelve
ni autoriza instalaciones.

## Relaciones

- [015 — Backlog de ideas](015-backlog-ideas-bmad.md).
- [023 — Tablero de notas](023-visualizacion-backlog.md).
- [025 — Coordinación de chats](025-coordinador-global-chats-autonomos.md).
- [028 — Modernizar el tablero](028-modernizacion-tablero-notas.md).
- [039 — Setup como centro de activación](039-setup-centro-activacion-capacidades.md).
