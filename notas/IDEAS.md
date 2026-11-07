# Notas e ideas pendientes

Espacio para guardar ideas según surgen y retomarlas más adelante, de una en una,
para debatirlas y, cuando se decida, implementarlas.

Todas las ideas se recogerán por este canal de conversación y se guardarán aquí,
en la carpeta `notas/` del repositorio.

Guardar una nota no aprueba su diseño ni autoriza su implementación. Las dudas
pueden quedarse abiertas hasta que se elija trabajar en esa nota.

## Índice

| Nota | Estado | Idea |
| --- | --- | --- |
| [001 — Disponibilidad de cuentas](001-disponibilidad-cuentas.md) | En implementación | Revisar cuentas y modelos antes de inferir y mantener actualizadas sus fechas de recuperación. |
| [002 — OpenCode como subagente acotado](002-opencode-como-subagente-acotado.md) | Pendiente de debatir | Investigar cómo Codex lanza, supervisa y recibe la finalización de sus subagentes para reproducir ese ciclo con OpenCode y tareas acotadas. |
| [003 — Coste de delegación](003-heuristica-coste-delegacion.md) | Pendiente de debatir | Decidir con una heurística rápida cuándo ejecutar directamente en Codex y cuándo lanzar un subagente. |
| [004 — Privacidad al delegar](004-guardarrailes-privacidad-opencode.md) | Pendiente de debatir | Evitar filtraciones de datos privados, empresariales y sensibles mediante guardarraíles fuertes. |
| [005 — Prompts concisos para OpenCode](005-prompts-concisos-opencode.md) | Pendiente de debatir | Investigar cómo preparar encargos eficaces, similares a los de subagentes de Codex y sin información redundante. |
| [006 — Herramientas y skills en OpenCode](006-herramientas-skills-opencode.md) | Pendiente de debatir | Investigar cómo habilitar Superpowers, Context7 y AIKit en OpenCode y verificar su acceso durante las tareas. |
| [007 — Separar delegación de AIKit](007-separar-delegacion-de-aikit.md) | Pendiente de debatir | Hacer independiente delegating-to-opencode y que AIKit lo utilice como otra herramienta disponible. |
| [008 — Espera pasiva de OpenCode](008-espera-pasiva-opencode.md) | Implementada en fuentes; instalación pendiente | Reducir la vigilancia de Codex mediante esperas pasivas y avisos relevantes, conservando la multitarea. |
| [009 — Método del Director de Ideas](009-metodo-director-de-ideas.md) | Pendiente de debatir | Organizar cada solicitud en visión, estructura y requisitos, asegurando la comprensión del usuario y un contexto rico. |
| [010 — Criterios de modelo y esfuerzo](010-criterios-modelo-y-esfuerzo.md) | Pendiente de debatir | Investigar cómo estimar cada tarea y escoger el modelo y esfuerzo que mejor encajen con sus necesidades y las capacidades disponibles, sin asignaciones fijas. |
| [011 — Control de contexto en OpenCode](011-control-contexto-opencode.md) | Pendiente de debatir | Determinar cuándo conviene compactar el contexto antes de lanzar una nueva tarea. |
| [012 — Referencia a BMAD en AGENTS.md](012-referencia-bmad-en-agents.md) | Implementada | Referencia breve de uso aprobada con go e incorporada a AGENTS.md, complementaria al descubrimiento de skills. |

## Uso

1. Añadir una nota con un número consecutivo y un nombre breve: `002-tema.md`.
   Basta con la fecha, la idea y las dudas que interese conservar.
2. Añadirla al índice con el estado «Pendiente de debatir».
3. Cuando se elija una nota, debatirla y actualizar su estado a «En debate».
4. Al acordar su diseño y autorizar su implementación, pasarla a «En implementación».
5. Al terminar, marcarla como «Implementada» y enlazar la entrega. Conservar la
   nota como referencia; si se descarta, marcarla como «Descartada».

Las notas pueden tener distinta extensión. No necesitan ser especificaciones ni
planes de trabajo para quedar guardadas aquí.
