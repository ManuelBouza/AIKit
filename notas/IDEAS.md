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

## En planificación

| Nota | Estado | Idea |
| --- | --- | --- |
| [021 — Chats, subagentes y relevo](021-coordinacion-chats-subagentes-relevo.md) | Implementación futura; criterios investigados | Elegir el medio de trabajo, distinguir pruebas y conservar el estado al relevar al coordinador. |
| [007 — Separar delegación de AIKit](007-separar-delegacion-de-aikit.md) | En planificación | AIKit instalado con setup explícito; la migración, convivencia y validación de la integración independiente siguen pendientes. |

## Implementada en fuentes; instalación pendiente

| Nota | Estado | Idea |
| --- | --- | --- |
| [008 — Espera pasiva de OpenCode](008-espera-pasiva-opencode.md) | Implementada en fuentes; instalación pendiente | Reducir la vigilancia de Codex mediante esperas pasivas y avisos relevantes, conservando la multitarea. |
| [018 — Herramientas recomendadas en setup](018-herramientas-recomendadas-setup.md) | Implementada e instalada; prueba de comportamiento pendiente | Comprobar y proponer herramientas, e instalarlas con aprobación si el cliente lo permite. |
| [009 — Método del Director de Ideas](009-metodo-director-de-ideas.md) | Instalada en perfil de prueba; activación y convivencia simulada observadas | Madurar ideas y aclarar decisiones antes de materializarlas; límites de validación registrados en la nota. |
| [020 — Próxima Tarea y pendientes del contexto](020-proxima-tarea-pendientes-contexto.md) | Regla global y complemento actualizados; vista previa sin cambios | Evitar confundir el cierre de una tarea acotada con la ausencia de pendientes de la iniciativa relacionada. |

## Pendiente de debatir

| Nota | Estado | Idea |
| --- | --- | --- |
| [002 — OpenCode como subagente acotado](002-opencode-como-subagente-acotado.md) | Pendiente de debatir | Investigar cómo Codex lanza, supervisa y recibe la finalización de sus subagentes para reproducir ese ciclo con OpenCode y tareas acotadas. |
| [003 — Coste de delegación](003-heuristica-coste-delegacion.md) | Pendiente de debatir | Decidir con una heurística rápida cuándo ejecutar directamente en Codex y cuándo lanzar un subagente. |
| [004 — Privacidad al delegar](004-guardarrailes-privacidad-opencode.md) | Pendiente de debatir | Evitar filtraciones de datos privados, empresariales y sensibles mediante guardarraíles fuertes. |
| [005 — Prompts concisos para OpenCode](005-prompts-concisos-opencode.md) | Pendiente de debatir | Investigar cómo preparar encargos eficaces, similares a los de subagentes de Codex y sin información redundante. |
| [006 — Herramientas y skills en OpenCode](006-herramientas-skills-opencode.md) | Pendiente de debatir | Investigar cómo habilitar Superpowers, Context7 y AIKit en OpenCode y verificar su acceso durante las tareas. |
| [010 — Criterios de modelo y esfuerzo](010-criterios-modelo-y-esfuerzo.md) | Pendiente de debatir | Investigar cómo estimar cada tarea y escoger el modelo y esfuerzo que mejor encajen con sus necesidades y las capacidades disponibles, sin asignaciones fijas. |
| [011 — Control de contexto en OpenCode](011-control-contexto-opencode.md) | Pendiente de debatir | Determinar cuándo conviene compactar el contexto antes de lanzar una nueva tarea. |

## Implementada

| Nota | Estado | Idea |
| --- | --- | --- |
| [012 — Referencia a BMAD en AGENTS.md](012-referencia-bmad-en-agents.md) | Implementada | Referencia breve de uso aprobada con go e incorporada a AGENTS.md, complementaria al descubrimiento de skills. |
| [015 — Backlog de ideas compatible con BMAD](015-backlog-ideas-bmad.md) | Implementada | Organizar las notas y registrar ideas nuevas en un backlog trazable. |
| [013 — Uso de BMAD en el proyecto existente](013-uso-bmad-proyecto-existente.md) | Adoptado en el proyecto | Aplicar las skills pertinentes; su distribución con AIKit no está decidida. |
| [014 — Preferencia de Context7 en AIKit](014-preferencia-context7.md) | Implementada y configurada mediante setup explícito | Preferencia aplicada en global y proyecto; validada la configuración. |
| [017 — Identidad visual de AIKit](017-identidad-visual-aikit.md) | Implementada e instalada; visible en la lista de complementos | Icono azul y naranja inspirado en la armonía evocada por aiki. |
| [016 — Investigar antes de experimentar](016-investigacion-antes-de-experimentar.md) | Implementada e instalada en global y proyecto | Priorizar documentación y fuentes especializadas sin omitir pruebas de verificación. |
| [019 — Go y acciones sensibles](019-go-autoriza-proxima-tarea.md) | Implementada e instalada | Go autoriza tareas ordinarias; para acciones sensibles se indica una palabra de autorización. |
