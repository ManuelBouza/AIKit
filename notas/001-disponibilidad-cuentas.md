# Notas: consultar disponibilidad de cuentas antes de una inferencia

Fecha: 2026-10-30.
Estado: En implementación. Diseño aprobado por el usuario el 2026-10-31 mediante `go`.
La implementación y la validación están en curso; todavía no cambia el comportamiento instalado.

## Idea que se quiere conservar

Antes de lanzar una inferencia, revisar el estado de las cuentas y los modelos.
Mantener una tabla con fechas y horas precisas de cuándo volverán a estar
disponibles. Si falta información de disponibilidad, consultar la fuente
correspondiente. Cada consulta debe actualizar la tabla para futuras revisiones.

Alcance confirmado el 2026-10-31: disponibilidad de modelos y cuentas conectadas
a OpenCode. Las cuotas de Codex quedan fuera de este registro. Esta nota no
autoriza el proveedor directo `openai`, actualmente bloqueado por la política.

## Cobertura registrada al redactar la nota (2026-10-30)

Se consultaron el catálogo de skills y herramientas de esta sesión,
`delegating-to-opencode`, Superpowers (`using-superpowers` y `brainstorming`) y
[`docs/principios-aikit.md`](../docs/principios-aikit.md).

- La skill de delegación ya contempla selección de modelos, consulta del catálogo,
  agotamiento gratuito y elección de alternativas. Sus instrucciones advierten que
  el catálogo no garantiza cuota ni disponibilidad para inferir.
- En esta sesión no están publicadas las herramientas MCP de OpenCode; la skill
  documenta una alternativa CLI. No se consultaron cuentas ni se lanzó inferencia
  para redactar estas notas de diseño.
- La cobertura consultada es parcial: no acredita una tabla persistente de cuotas
  con horas de recuperación. Verificar las capacidades reales del transporte y
  de cada proveedor antes de diseñar una integración.
- Reutilizar selección, políticas y flujos de Superpowers. Añadir únicamente el
  procedimiento y el estado que falten.

## Procedimiento propuesto para discutir

1. Antes de cada inferencia, leer el registro local de la cuenta, proveedor y
   modelo candidatos, incluidos los límites compartidos que les afecten.
2. Si consta un bloqueo vigente con una recuperación conocida y futura, tenerlo
   en cuenta al seleccionar otra opción conforme a la política de AIKit.
3. Si el registro falta, está desactualizado, es incierto o ya llegó la hora de
   recuperación, consultar una fuente autorizada. Alcanzar esa hora requiere
   volver a verificar; no demuestra por sí solo que exista cuota.
4. Actualizar el registro tras cada consulta, también cuando falle: conservar la
   última observación válida y distinguirla del intento fallido más reciente.
5. Actualizarlo también cuando una inferencia revele agotamiento o una nueva
   fecha de recuperación. Evitar reintentos mientras siga vivo un intento anterior.
6. Si no se puede verificar, registrar «desconocido» y aplicar la política que se
   acuerde. No inventar una hora ni presentar el catálogo como prueba de cuota.

Consultar se refiere inicialmente a una lectura del estado del servicio, no a
preguntar al usuario ni a gastar una inferencia de prueba. Debatir qué hacer si
el proveedor no ofrece una consulta de cuota.

## Datos mínimos propuestos

| Campo | Propósito |
| --- | --- |
| Proveedor y alias local de cuenta | Identificar el origen sin credenciales ni datos personales. |
| Modelo y ámbito del límite | Distinguir límites por modelo, cuenta o grupo compartido. |
| Estado | Disponible, agotado, desconocido o error de consulta. |
| Última comprobación válida | Fecha y hora de la observación y su fuente. |
| Último intento de consulta | Fecha, hora y resultado, incluso si falló. |
| Recuperación comunicada | Fecha y hora exactas si la fuente las proporciona; desconocida si no. |
| Precisión y origen | Distinguir dato confirmado, estimación y dato no disponible. |
| Vigencia y próxima comprobación | Evitar usar observaciones antiguas indefinidamente. |

Guardar instantes en ISO 8601 con zona u offset explícito, preferiblemente UTC;
mostrar también la hora local si ayuda. No confundir la hora de recuperación con
la de la próxima consulta. Una hora estimada debe seguir marcada como estimada.
No hay datos reales de cuentas ni fechas de recuperación verificadas en esta nota.

## Dónde ubicarlo: alternativas

1. **Regla breve en AGENTS.md, procedimiento en la skill y estado local separado
   (recomendada).** AGENTS.md indica cuándo activar la revisión; la skill de
   delegación explica cómo consultar, actualizar y decidir. El estado mutable se
   guarda en un archivo local ignorado por Git, cuya ubicación queda por decidir.
   Evita duplicar el procedimiento y mezclar instrucciones con cuotas cambiantes.
2. **Todo el procedimiento en AGENTS.md, estado local separado.** Hace visible la
   regla, pero amplía las instrucciones generales y dificulta mantenerla junto al
   transporte que consulta las cuentas.
3. **Solo en la skill, estado local separado.** Encaja con un procedimiento de
   delegación, pero habría que comprobar que se activa antes de todos los
   lanzamientos incluidos en el alcance.

La recomendación es provisional. Si se necesitan garantías para todas las vías de
ejecución, debatir además una comprobación en el adaptador: documentar una regla
no asegura por sí solo su ejecución.

## Decisiones pendientes para el debate

- Concretar la identificación local de cuentas y los ámbitos de cuota que
  acrediten las fuentes de OpenCode.
- Identificar fuentes autorizadas y qué precisión de recuperación ofrecen.
- Definir cuánto dura una observación de disponibilidad y cuándo volver a consultar.
- Acordar qué hacer ante cuota desconocida o fuente inaccesible: consultar al
  usuario, elegir alternativa o intentar una inferencia bajo condiciones explícitas.
- Decidir si el registro pertenece al proyecto o es compartido entre proyectos;
  contemplar actualizaciones concurrentes si se comparte.
- Elegir la ubicación definitiva del procedimiento y si exige control en código.

## Decisiones confirmadas el 2026-10-31

- El usuario solicita implementar esta nota y pausar el avance de la tarea 4 del
  plan de binding mientras se trabaja en ella.
- Si un proveedor no ofrece consulta de cuota y la disponibilidad es desconocida,
  se permite un único intento de una tarea real ya autorizada y se registra el
  resultado. No se lanzan inferencias de prueba para averiguar la cuota.
- Se distinguirá disponibilidad para inferir de presencia en el catálogo y de
  actividad de una sesión; el diseño y sus fuentes siguen pendientes de revisión.

## Comprobaciones para la futura implementación

Registrar entorno, configuración, resultado esperado y observado. Comprobar con
transporte falso, sin consumir inferencias, los casos de registro ausente o
caducado, bloqueo futuro, recuperación alcanzada, cuota compartida, consulta
fallida, zona horaria y actualización tras agotamiento. Verificar que cada consulta
deja actualizado su resultado y que no se almacenan credenciales.

Siguiente paso: verificar las fuentes y revisar un diseño concreto antes de
implementar el mecanismo.
