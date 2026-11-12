# 021 — Coordinación de chats, subagentes y relevo

- Fecha: 2026-11-12
- Estado inicial: Pendiente de debatir
- Estado actual: Implementación futura; criterios investigados, pendiente de concretar e implementar

## Objetivo y decisión

Incorporar a AIKit criterios para escoger entre herramientas directas, subagentes,
chats independientes y relevo del coordinador, evitando confundir pruebas con
trabajo real. Manuel solicita conservar esta propuesta y aplicarla en el momento
apropiado; ahora se prioriza terminar el trabajo en curso.

## Criterios propuestos

| Medio | Cuándo utilizarlo |
| --- | --- |
| Herramientas directas | Comprobaciones deterministas y tareas sencillas que no justifican otro agente. |
| Subagente | Encargo acotado, revisión independiente o exploración separable dentro de la tarea actual. |
| Chat independiente | Iniciativa con conversación propia del usuario; creación solo por petición explícita. |
| Chat de prueba | Cuando se necesita verificar arranque, descubrimiento de skills o interacción real entre turnos; una simulación con subagente no acredita esas capacidades. |
| Mismo coordinador | Mientras el objetivo siga siendo coherente y el estado pueda recuperarse correctamente. Compactar no exige cambiar de coordinador. |
| Relevo del coordinador | Confusión recurrente, decisiones obsoletas, entorno incorrecto o cambio material de alcance; no por un número arbitrario de turnos. |

Los subagentes no garantizan ahorro de tokens. Limitar contexto y encargo,
evitar duplicación de análisis y escrituras concurrentes sobre los mismos archivos.
No abrir chats visibles para subtareas que pueden resolverse dentro del encargo.

## Identidad y relevo

- Distinguir títulos: `AIKit · Chat principal de coordinación` y
  `PRUEBA · AIKit · <objetivo>`. Identificar también alcance y criterio de cierre
  en el encargo; el título por sí solo no limita las acciones.
- Antes del relevo, persistir objetivo, decisiones, restricciones, trabajo
  terminado y pendiente, evidencias, rama, checkout y cambios sin commit.
- Identificar el chat de destino y su responsabilidad; no dejar dos
  coordinadores modificando la misma entrega sin reparto explícito.
- El receptor contrasta el resumen con el repositorio antes de continuar.
  Compactar conserva un resumen operativo, no sustituye el registro persistente.
- Conservar el chat anterior; no archivarlo, cerrarlo o eliminarlo automáticamente.

## Cobertura y validación pendientes

Las herramientas nativas ya permiten subagentes y gestión de chats; AIKit debe
aportar criterios e instrucciones, no otro sistema de ejecución. Antes de
implementar, revisar las skills y herramientas entonces instaladas y decidir
qué regla breve corresponde a las preferencias y qué procedimiento necesita
documentación adicional, sin duplicar BMAD ni otras capacidades.

Validar tarea acotada, revisión independiente, prueba que requiere chat nuevo,
continuidad tras compactación y relevo entre checkouts. Distinguir simulación,
descubrimiento real e interacción observada. No hay garantía de memoria perfecta.

## Evidencia y relaciones

La confusión observada fue entre un chat de prueba y el coordinador; no demuestra
un fallo de compactación. Se renombraron el coordinador y once chats identificados
como pruebas. Eso no instala una política general en AIKit.

Relacionada con [003 — Coste de delegación](003-heuristica-coste-delegacion.md),
[011 — Contexto de OpenCode](011-control-contexto-opencode.md) y
[020 — Próxima Tarea](020-proxima-tarea-pendientes-contexto.md), sin sustituirlas.

Fuentes consultadas en la investigación previa:

- [Buenas prácticas de Codex](https://learn.chatgpt.com/guides/best-practices).
- [Comandos de desarrollo](https://learn.chatgpt.com/docs/developer-commands).
- [Guía multiagente de la API](https://developers.openai.com/api/docs/guides/responses-multi-agent): principios de diseño, no prueba de costes del cliente Desktop.

Esta nota no modifica skills, instrucciones globales ni configuración y no
autoriza abrir chats, desplegar la política o reactivar OpenCode.
