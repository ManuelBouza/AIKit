# Encargo documental: diseño del seguimiento de ideas y tareas

Fecha: 2026-11-17.
Estado: Finalizada la entrega documental; opción local adoptada para especificar.
Responsable de coordinación: chat `01a1da03-23f1-7eb0-b0a0-5cb5184e6941`.
Apoyo acotado: subagente nativo `/root/diseno043`, diseño técnico documental.

## Origen y autorización

Solicitud humana de separar ideas y tareas, exigir registro previo a implementar
y trasladar la regla a AIKit. El usuario confirma que una idea puede generar
varias tareas y un encargo directo puede no tener idea previa, y aprueba con
«go» la próxima tarea de definir el registro y sus conexiones.
Origen: [nota 043](../notas/043-separar-ideas-y-tareas-implementacion.md).

## Alcance y aceptación

Entregar un borrador técnico con fuente canónica, identificadores, estados,
autorización, responsables, enlaces con ideas y artefactos existentes, vistas,
migración gradual y criterios verificables. Contrastar fuentes oficiales.
Explicar alternativas de almacenamiento y recomendar una para este proyecto.
La entrega no implementa el segundo sistema ni instala preferencias.

## Límites y dependencias

No modificar código, skills ni configuración global, no crear un nuevo Chat
de Tarea, no migrar encargos ni levantar pausas. No ejecutar la preparación
BMAD pendiente de 040. El registro actual sigue siendo manual; esta entrada
no es un ticket del sistema todavía por desarrollar ni figura como tal en
el tablero de notas. La implementación futura necesita registro y autorización.

## Entrega documental

[Diseño](../docs/diseno-ideas-tareas-043.md), entregado como borrador con fuentes
oficiales, recomendación local y criterios de aceptación para una implementación
futura. Se conserva el alcance documental; no se han creado los tickets ni las
vistas propuestas. Próximo paso recomendado: acordar el modelo y formalizar su
contrato con bmad-spec antes de encargar implementación. El entorno de 040
sigue pendiente. La pausa de 028 reflejaba el estado conocido al cerrar el
borrador; la conciliación posterior del 2026-11-17 acredita Esperando al usuario
para aprobar su propuesta visual (véase paralelo-028-040/ACUSES.md).

## Adopción posterior — 2026-11-17

Manuel indica «go, la opcion 1»: adopta la modalidad Markdown local y autoriza
formalizar el contrato mediante bmad-spec. El seguimiento de esa formalización
está en [su encargo](especificacion-seguimiento-043.md); no aprueba implementar.
