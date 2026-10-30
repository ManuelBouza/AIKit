# Seguimiento y recuperación de sesiones OpenCode

Estado: contrato aprobado por el usuario el 30 de octubre de 2026. No implementado.

## Objetivo y cobertura existente

Conservar el contexto y los resultados de una tarea al perder la conexión,
agotarse un plazo o fallar el guardado. Evitar inferencias y efectos duplicados.
Codex conserva diseño, selección de modelo y coordinación; OpenCode ejecuta.

Se consultaron `delegating-to-opencode`, `superpowers:systematic-debugging` y
`superpowers:brainstorming`. Superpowers cubre diagnóstico, diseño y roles; la
skill existente cubre transporte y política. Ninguna aporta hoy seguimiento
recuperable de las ejecuciones del adaptador. Se amplía ese núcleo compartido,
sin crear otra skill, interceptar subagentes ni modificar Superpowers.

## Evidencia y alternativas

OpenCode 2.2.0 publica `run --session ID`. El adaptador no lo expone, analiza la
sesión después de terminar y descarta la salida recuperada tras un timeout.
Además usa `--standalone`: una consulta al servicio habitual no acredita el
estado de su servidor privado. No hay evidencia suficiente de un defecto de
OpenCode ni de recuperación de extremo a extremo ya verificada.

Alternativas consideradas:

- Añadir solo `--session`: barato, pero deja sin resolver actividad, resultados
  parciales y duplicados tras una desconexión.
- Sustituir todo por API: permite control, pero amplía la migración y exige
  resolver tiempos del cliente y compatibilidad antes de retirar la CLI.
- Ampliación incremental del núcleo existente: CLI para tareas largas y API
  para observación/control cuando se pueda identificar su servidor. Es la
  propuesta recomendada; una capacidad no comprobada se declara no disponible.

## Identidad y registro

Cada tarea tiene un `task_id` estable; cada intento, un `attempt_id` distinto.
Se registra: versión del contrato, rol, directorio canónico, modelo, variante,
motivo, tarifa acreditada o desconocida, sesión, transporte, identidad del
servidor, PID cliente con instante de creación, plazos y último evento observado.

La sesión puede ser desconocida durante el arranque; se persiste al primer
evento que la identifique, antes de esperar el resultado completo. El registro
local usa escritura atómica en `.aikit/`, sin credenciales ni transcripciones.
Los eventos guardan cursor y metadatos mínimos. La salida parcial necesaria se
conserva por separado, con límites de tamaño y bajo las mismas restricciones.
Un fallo al guardar no oculta el resultado de stdout ni provoca otra inferencia.

## Estado y exclusión

Se separan tres observaciones: proceso cliente, ejecución en servidor y entrega.
La ejecución puede estar activa, esperando permiso o entrada, en reintento,
inactiva o desconocida. La entrega puede estar pendiente, parcial, completada,
fallida o interrumpida. Un cliente terminado no implica entrega completada.

Cada observación indica fuente y fecha. Un evento terminal es evidencia
histórica, no prueba de que no exista una ejecución posterior. La ausencia en
`session.active` solo informa sobre el proceso servidor consultado. El silencio
es una señal para inspeccionar, nunca prueba suficiente de bloqueo.

Solo se admite una mutación coordinada por sesión: bloqueo local entre procesos
de AIKit y comprobación del servidor antes de enviar. El bloqueo no controla
clientes externos; ante una carrera o estado incierto se reconcilia, sin repetir
automáticamente el envío. Un registro huérfano no se elimina por antigüedad.

## Operaciones propuestas

- **Estado:** consulta sin inferencia; devuelve identidad, actividad, entrega,
  evidencia, parciales y acciones disponibles, sin exponer secretos.
- **Recuperar resultado:** reúne salida y evidencias existentes sin enviar un
  prompt. No convierte un timeout en éxito por encontrar archivos.
- **Continuar:** valida sesión existente, directorio y rol; reconcilia eventos,
  entrada pendiente y cambios parciales. Si ya está activa, observa. Si terminó,
  recupera. Si requiere trabajo adicional, envía una continuación acotada a la
  sesión exacta y registra un nuevo intento. Nunca usa la última sesión implícita.
- **Interrumpir:** solicita interrupción al servidor propietario y verifica el
  resultado. No equivale a borrar la sesión ni descarta su contexto.
- **Forzar detención:** acción explícita y separada; exige identidad vigente,
  propiedad del proceso y alcance autorizado. Nunca termina un servicio
  compartido ni todos los procesos OpenCode. Si no puede acreditar propiedad,
  devuelve una limitación y no mata el proceso.

No se inventan parámetros API. La implementación verificará operaciones y
semántica en la versión instalada. En particular, `interrupt` con `resume=true`
no se trata como continuación general. Un envío de resultado incierto se
reconcilia mediante identidad/eventos; no se promete ejecución exactamente una vez.

## Plazos, permisos y roles

El plazo de espera del cliente es distinto del límite de ejecución. Agotar el
primero devuelve seguimiento pendiente, no autorización para reiniciar o matar.
El límite de ejecución sigue siendo finito y se aplica donde vive el supervisor:
solicita interrupción, espera un periodo de gracia acotado y registra el estado
observado. Si el supervisor desaparece, no se promete cancelación automática.
La pérdida de conectividad devuelve estado desconocido y contexto recuperable.

Antes de cada inferencia, incluida continuación, se anuncia objetivo, modelo,
esfuerzo y tarifa. Continúan el bloqueo de `openai` directo, la prohibición de
subdelegación y las reglas de permisos. No se añaden aprobaciones automáticas.
El implementador reutiliza sesión; un revisor independiente comienza otra.
Sin OpenCode adecuado/disponible se aplica el retorno nativo existente, tras
resolver intentos vivos o inciertos para no duplicar trabajo.

## Aceptación y entrega incremental

Primero se valida sin inferencia: captura temprana, timeout con parciales,
fallo de persistencia, concurrencia, PID reutilizado, servidor equivocado,
sesión inexistente, trabajo completado y envío de resultado incierto. CLI y MCP
comparten contrato; las llamadas de control son breves y no esperan una tarea
larga dentro de una llamada MCP.

Después se comprueba con una tarea mínima que interrupción y continuación
conservan el mismo ID y contexto, y que no se repiten efectos ya realizados.
Se registra qué capacidades permite realmente el servidor privado. Si no ofrece
control identificable, se presenta la limitación; cambiar a un servidor dedicado
gestionado por AIKit requiere concretarlo antes de implementar esa parte.
No se publica ni instala hasta disponer de evidencia independiente.

## Fuentes

- [CLI oficial v2](https://dev.opencode.ai/v2/docs/cli/commands/).
- [API oficial v2](https://dev.opencode.ai/v2/docs/api).
- [Contrato de sesiones](https://github.com/anomalyco/opencode/blob/dev/specs/v2/session.md),
  localizado con Context7; contrastar sus detalles con la versión instalada.
