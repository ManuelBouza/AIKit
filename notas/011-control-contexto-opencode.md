# Control del contexto y compactación en OpenCode

Fecha: 2026-11-04.
Estado: pendiente de debatir.

## Idea

Investigar cómo controlar el contexto de OpenCode y determinar cuándo es óptimo
compactarlo antes de lanzar una nueva tarea.

## Para investigar y debatir después

- Qué información permite conocer el contexto utilizado y el margen disponible
  para la siguiente tarea.
- Cómo estimar las necesidades de contexto de la nueva tarea y decidir si conviene
  continuar, compactar o iniciar una sesión nueva.
- Qué mecanismos de compactación ofrece OpenCode y cuándo se activan.
- Cómo conservar tras la compactación las decisiones, restricciones, resultados
  relevantes y trabajo pendiente necesarios para continuar correctamente.
- Cómo evaluar el equilibrio entre tokens, tiempo y calidad, considerando también
  el coste de compactar y el riesgo de perder información útil.

Relacionada con la nota [002](002-opencode-como-subagente-acotado.md), sobre el
ciclo de las sesiones delegadas, y la [005](005-prompts-concisos-opencode.md),
sobre el contexto necesario para cada encargo.

La investigación queda pendiente. Guardar esta nota no activa compactaciones ni
modifica la gestión actual de las sesiones.
