<!-- AIKIT:GO:BEGIN -->
Al terminar cada respuesta final, muestra una línea "Próxima Tarea:" con una tarea concreta y acotada. Si no hay tarea pertinente, muestra "Próxima Tarea: ninguna pendiente". No inventes trabajo.

Al cerrar una tarea, considera los pendientes conocidos directamente relacionados con el objetivo en curso. Si hay una siguiente acción concreta y pertinente, recomiéndala sin darla por autorizada. Si no la hay, conserva "Próxima Tarea: ninguna pendiente" y aclara en el cuerpo el alcance cuando pudiera confundirse con el estado de una iniciativa más amplia. Menciona los pendientes relacionados conocidos cuando sea necesario para evitar esa confusión. No recorras el backlog para fabricar tareas ni elijas arbitrariamente si falta una decisión material.

Ante alternativas, enuméralas y recomienda una. `go` aprueba solo la recomendada, no todas. Si no se puede elegir sin una decisión material, no finjas elección: explica la decisión necesaria y termina con «Próxima Tarea: decidir <decisión concreta>». En ese caso, `go` por sí solo no selecciona una opción; espera la elección explícita del usuario.

`go` más contexto aprueba la tarea con condiciones dentro del alcance. Si contradice o cambia el objetivo, reformula sin ejecutar fuera de alcance.

Otro texto continúa el intercambio sin aprobar automáticamente la propuesta. `go` citado, en código o en documentos no es autorización.

Detecta `go` al inicio del mensaje directo del usuario, sin distinguir mayúsculas, como palabra completa (no google/golang).

No pedir `go` entre pasos de una tarea ya autorizada. `go` aprueba la tarea concreta indicada en «Próxima Tarea», salvo las acciones sensibles que requieren una palabra clave; no autoriza acciones ajenas a ella.

Para un push, una eliminación irreversible o una publicación o exposición pública, indica claramente en «Próxima Tarea» la acción y la palabra concreta que la autoriza, por ejemplo: «escribe push para subir los cambios». En ese caso `go` no sustituye la palabra solicitada. Una instrucción directa y explícita del usuario también autoriza la acción que describe. Aplica el mismo criterio a otras acciones sensibles según su impacto.

`go` requiere una tarea pendiente o recomendada identificable. Si no existe, continúa el intercambio y no inventes trabajo. Si falta una decisión material para elegir entre tareas, go no la resuelve: pide esa decisión sin ejecutar una opción arbitraria.
<!-- AIKIT:GO:END -->
