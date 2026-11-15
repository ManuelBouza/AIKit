# Contraste del reparto entre coordinador y chats de tarea

Fecha de consulta: 2026-11-15.
Alcance: contraste documental de la propuesta de la nota 025. No es una prueba
de rendimiento de AIKit ni una activación de reglas nuevas.

Aclaración posterior del usuario, 2026-11-15: el coordinador de AIKit se dedica
a coordinar; no ejecuta implementaciones ni code review. Puede usar subagentes
para apoyos acotados de una sola ejecución. Las recomendaciones de ejecución
directa que figuran abajo son historial del contraste y quedan sustituidas para
AIKit por el [contrato actualizado](contrato-responsabilidades-propuesto.md).
La recomendación general de empezar con un agente no prescribe que ese agente
deba ser el coordinador del proyecto.

## Fuentes y evidencia

Se consultaron fuentes primarias de ingeniería y documentación de producto.
Context7 se utilizó para localizar los patrones actuales de LangChain; se
contrastó su documentación oficial. No se selecciona un framework ni se fija una
versión de implementación: el análisis trata de arquitectura y responsabilidades.

1. OpenAI, [A practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/), página fechada 2026-01-15.
   Recomienda aprovechar primero un solo agente y dividir cuando la complejidad
   de instrucciones o la elección de herramientas lo requieran. Explica tanto
   coordinación centralizada como transferencias entre agentes.
2. Anthropic, [Building effective agents](https://www.anthropic.com/research/building-effective-agents), 2024-12-19.
   Propone patrones componibles, herramientas con resultados comprobables y
   condiciones de parada. La propia página advierte que su descripción de
   herramientas ha evolucionado; aquí se usan sus principios arquitectónicos.
3. Anthropic, [How we built our multi-agent research system](https://www.anthropic.com/research/multi-agent-research-system), 2025-06-13.
   Describe objetivos, formato de entrega y fronteras explícitas al delegar;
   identifica duplicación y costes de comunicación. Advierte sobre trabajos con
   mucho contexto compartido y dependencias. Su experiencia es de investigación,
   no una demostración para todos los proyectos de desarrollo.
4. Google Research, [Towards a science of scaling agent systems](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/), 2026-01-28.
   Compara arquitecturas bajo condiciones controladas: los beneficios dependen
   de la posibilidad de descomponer el problema; los flujos secuenciales pueden
   empeorar. La centralización contiene errores en sus evaluaciones. Sus cifras
   no predicen directamente los resultados de nuestros chats persistentes.
5. Anthropic, [Orchestrate teams of Claude Code sessions](https://code.claude.com/docs/en/agent-teams), documentación vigente sin fecha editorial visible.
   Distingue sesiones independientes y subagentes; destaca independencia de
   tareas, contexto suficiente y propiedad de archivos. Es una función
   experimental específica de Claude Code, no evidencia de capacidades de Codex.
6. LangChain, [Multi-agent](https://docs.langchain.com/oss/python/langchain/multi-agent), documentación vigente sin fecha editorial visible.
   Diferencia subagentes, handoffs, skills y routing. Presenta la selección del
   contexto como decisión central y admite resolver trabajo complejo con un solo
   agente y herramientas adecuadas.

## Evaluación de nuestra propuesta

Conclusión de diseño: mantener coordinación central y responsabilidad por entrega
es razonable para los requisitos de AIKit. Las fuentes también describen otras
arquitecturas; no acreditan un modelo universal ni nuestras garantías operativas.

| Elemento | Evaluación y ajuste recomendado para AIKit |
| --- | --- |
| Coordinador con ejecución directa | Conservar. No limitarlo a tareas pequeñas: puede ejecutar una tarea coherente si separarla no aporta beneficio. |
| Entrega independiente como motivo de otro chat | Es necesario delimitar la entrega, pero no es suficiente. Exigir un beneficio identificable de continuidad propia, aislamiento de contexto, especialización, revisión independiente o paralelismo útil. |
| Subagente frente a chat persistente | Usar apoyo acotado cuando basta un resultado de vuelta. Reservar el chat para responsabilidad y continuidad propias; la conversación directa con el usuario puede justificarlo. Respetar las capacidades y autorizaciones del cliente. |
| Dependencias y aislamiento | Valorar cuánto contexto debe compartirse y cuánto trabajo espera a otro. Mantener junto lo estrechamente acoplado. Worktrees aíslan archivos de trabajo, no contratos ni recursos externos. Sin Git se conserva la secuenciación acordada. |
| Integración del coordinador | Conservar su autoridad y aceptación final. Usar evidencia, controles automáticos y revisión independiente cuando corresponda; evitar repetir toda la ejecución y convertirlo en cuello de botella. |
| Autonomía de la tarea | Decidir detalles técnicos dentro del encargo; comunicar cambios de supuestos o dependencias. No elevar cada decisión rutinaria ni ampliar el alcance. |
| Comunicación | Avisar ante hitos, bloqueos, dependencias, cambios materiales y solicitudes de integración; evitar retransmitir cada paso. Entregar resúmenes verificables y referencias, no copiar toda la conversación. |
| Supervisión y parada | Acordar aceptación y puntos de control proporcionales. Si aparecen fallos repetidos, incertidumbre de permisos, cambio de alcance o falta de progreso, reevaluar y detener la parte afectada. No fijar aquí presupuestos numéricos universales. |

## Validación propuesta

Comparar casos representativos: ejecución directa, apoyo acotado y chat con
continuidad propia. Registrar resultado aceptado, trabajo duplicado, correcciones,
mensajes de coordinación, intervenciones necesarias del usuario y coste/tiempo
cuando las herramientas los proporcionen. No inferir ahorro por número de chats.

Comenzar con un encargo de límites claros, sin dos escritores sobre el mismo
recurso. Probar después integración y cierre, y repetir en otro proyecto elegido
por el usuario. Una prueba satisfactoria no acreditará todos los mecanismos de
recuperación, concurrencia o archivado.

Este documento propone ajustes. No cambia las skills instaladas, no crea chats,
no activa automatizaciones y no autoriza trabajo del backlog.
