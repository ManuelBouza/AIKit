# Backlog de ideas y notas

Registro canónico de ideas, dudas y trabajo derivado de ellas. Las notas enlazadas
conservan el contexto y las decisiones. Cada entrada mantiene su número histórico;
el orden dentro de cada grupo no representa prioridad ni autorización.

Registrar una idea no aprueba su diseño ni autoriza su implementación. El usuario
elige cuándo retomarla conforme al mecanismo go. No se han supuesto prioridades ni
se ha trasladado automáticamente ninguna idea a ejecución.

## Flujo

1. Registrar cada idea nueva en una nota numerada con fecha y estado inicial
   «Pendiente de debatir»; añadirla a este backlog.
2. Al debatir o implementar, actualizar el estado aquí y en la nota, conservando
   decisiones, restricciones y enlaces a evidencias. No borrar el historial.
3. Cuando proceda, usar BMAD para elaborar una especificación e historias;
   enlazar esos artefactos desde la nota y mantener aquí el estado resumido.
   No crear historias activas duplicadas ni asumir que un documento es aprobación.
4. Al completar o descartar, registrar la decisión y la evidencia; conservar la
   entrada como referencia. Revisar el backlog al planificar trabajo relacionado.

Los artefactos de proyecto en `_bmad-output/`, incluidas las fuentes canónicas
`.memlog.md` de `bmad-spec`, se conservan en Git tras revisar su contenido.
La instalación, cachés, datos personales y salidas temporales siguen excluidos.
Los estados históricos se trasladaron tal como estaban; deben contrastarse con la
nota y la evidencia antes de usarlos para decidir el siguiente trabajo.

## En implementación

| Nota | Estado | Idea |
| --- | --- | --- |
| [001 — Disponibilidad de cuentas](001-disponibilidad-cuentas.md) | En implementación | Revisar cuentas y modelos antes de inferir y mantener actualizadas sus fechas de recuperación. |

## Implementada en fuentes; instalación pendiente

| Nota | Estado | Idea |
| --- | --- | --- |
| [008 — Espera pasiva de OpenCode](008-espera-pasiva-opencode.md) | Implementada en fuentes; instalación pendiente | Reducir la vigilancia de Codex mediante esperas pasivas y avisos relevantes, conservando la multitarea. |

## En debate

| Nota | Estado | Idea |
| --- | --- | --- |
| [013 — Uso de BMAD en el proyecto existente](013-uso-bmad-proyecto-existente.md) | En debate | Determinar cómo adaptar el flujo de desarrollo de BMAD al repositorio y conservar el trabajo existente. |

## Pendiente de debatir

| Nota | Estado | Idea |
| --- | --- | --- |
| [002 — OpenCode como subagente acotado](002-opencode-como-subagente-acotado.md) | Pendiente de debatir | Investigar cómo Codex lanza, supervisa y recibe la finalización de sus subagentes para reproducir ese ciclo con OpenCode y tareas acotadas. |
| [003 — Coste de delegación](003-heuristica-coste-delegacion.md) | Pendiente de debatir | Decidir con una heurística rápida cuándo ejecutar directamente en Codex y cuándo lanzar un subagente. |
| [004 — Privacidad al delegar](004-guardarrailes-privacidad-opencode.md) | Pendiente de debatir | Evitar filtraciones de datos privados, empresariales y sensibles mediante guardarraíles fuertes. |
| [005 — Prompts concisos para OpenCode](005-prompts-concisos-opencode.md) | Pendiente de debatir | Investigar cómo preparar encargos eficaces, similares a los de subagentes de Codex y sin información redundante. |
| [006 — Herramientas y skills en OpenCode](006-herramientas-skills-opencode.md) | Pendiente de debatir | Investigar cómo habilitar Superpowers, Context7 y AIKit en OpenCode y verificar su acceso durante las tareas. |
| [007 — Separar delegación de AIKit](007-separar-delegacion-de-aikit.md) | Pendiente de debatir | Hacer independiente delegating-to-opencode y que AIKit lo utilice como otra herramienta disponible. |
| [009 — Método del Director de Ideas](009-metodo-director-de-ideas.md) | Pendiente de debatir | Organizar cada solicitud en visión, estructura y requisitos, asegurando la comprensión del usuario y un contexto rico. |
| [010 — Criterios de modelo y esfuerzo](010-criterios-modelo-y-esfuerzo.md) | Pendiente de debatir | Investigar cómo estimar cada tarea y escoger el modelo y esfuerzo que mejor encajen con sus necesidades y las capacidades disponibles, sin asignaciones fijas. |
| [011 — Control de contexto en OpenCode](011-control-contexto-opencode.md) | Pendiente de debatir | Determinar cuándo conviene compactar el contexto antes de lanzar una nueva tarea. |
| [014 — Preferencia de Context7 en AIKit](014-preferencia-context7.md) | Pendiente de debatir | Incorporar de forma portable la preferencia de consultar documentación técnica actualizada con Context7. |

## Implementada

| Nota | Estado | Idea |
| --- | --- | --- |
| [012 — Referencia a BMAD en AGENTS.md](012-referencia-bmad-en-agents.md) | Implementada | Referencia breve de uso aprobada con go e incorporada a AGENTS.md, complementaria al descubrimiento de skills. |
| [015 — Backlog de ideas compatible con BMAD](015-backlog-ideas-bmad.md) | Implementada | Organizar las notas y registrar ideas nuevas en un backlog trazable. |
