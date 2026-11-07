# Refinar los prompts de las tareas de OpenCode

Fecha: 2026-10-30.
Estado: pendiente de debatir.

## Idea

Revisar el mecanismo que prepara los prompts para OpenCode. Se observa que son
extensos; deberían ser similares a los que Codex envía a sus subagentes: centrados
en la tarea, eficaces y sin repetir información obvia o ya disponible.

Investigar en la documentación oficial y en fuentes especializadas cómo redactar
estos encargos para reducir el contexto innecesario sin perder instrucciones que
afecten al resultado.

## Para debatir e investigar después

- Comparar encargos reales a OpenCode con los enviados a subagentes de Codex.
- Identificar qué instrucciones recibe ya el ejecutor y cuáles necesita en cada
  tarea, evitando repetir reglas, contexto e información obvia.
- Consultar documentación oficial y fuentes especializadas sobre prompts para
  agentes de programación, registrando fuentes y límites de sus recomendaciones.
- Determinar el contenido mínimo útil: objetivo, alcance, restricciones relevantes,
  criterio de aceptación y resultado esperado.
- Evaluar la eficacia con tareas comparables: calidad del resultado, tokens,
  tiempo y necesidad de aclaraciones o correcciones; no medir solo la longitud.
- Encajar lo aprendido con el contrato de carga existente y las notas
  [002](002-opencode-como-subagente-acotado.md) y
  [003](003-heuristica-coste-delegacion.md), conservando los controles de privacidad
  de la nota [004](004-guardarrailes-privacidad-opencode.md).

La investigación queda pendiente. Guardar esta nota no modifica los prompts
actuales ni autoriza su implementación.
