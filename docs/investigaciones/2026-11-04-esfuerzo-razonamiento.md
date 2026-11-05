# Investigación: cuándo usar low, medium, high, xhigh y max

**Fecha:** 2026-11-04. **Estado:** borrador de investigación. No implementa política ni cambia routing.

## Criterio de elección

El esfuerzo debe derivarse del encargo: complejidad, ambigüedad, contexto real, herramientas, alcance e impacto de un error. No hay tabla fija tarea-modelo. Un nivel más alto no garantiza mejor resultado; solo amplía el razonamiento disponible.

## Fuentes oficiales y evidencia

OpenAI documenta que el esfuerzo controla cuánto razona el modelo y que los niveles soportados y el valor por defecto dependen del modelo. En su guía general, recomienda `medium` como punto equilibrado para la mayoría de tareas, `low` para tareas acotadas o uso de herramientas, y `high` para razonamiento difícil, depuración compleja o flujos de varios pasos donde la calidad es prioritaria; `xhigh` solo si una evaluación demuestra que el beneficio justifica coste y latencia. (Fuente: [OpenAI reasoning guide](https://developers.openai.com/api/docs/guides/reasoning), consultada 2026-11-04.)

La guía de prompting de GPT-5.3-Codex recomienda `medium` para codificación interactiva y `high`/`xhigh` para trabajo más difícil, pero es una guía específica de ese modelo y harness, no una recomendación atemporal para todos los modelos. (Fuente: [Codex prompting guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide), consultada 2026-11-04.)

Anthropic afirma que el comportamiento y el valor por defecto cambian por modelo y generación. Para Opus 5.5 y Haiku 5.5, el default es `medium`; Sonnet 4.6 recomienda `medium` para la mayoría de la codificación agéntica; otros como Opus 4.7 recomiendan `xhigh` para codificación sensible. El esfuerzo afecta tokens, incluidos tool calls y thinking; la verbosidad visible no es lo mismo, y cambiar esfuerzo en Opus 5 no acorta de forma fiable la respuesta visible. (Fuente: [Claude effort guide](https://platform.claude.com/docs/en/build-with-claude/effort), consultada 2026-11-04.)

Reflection Beam publica que un esfuerzo menor favorece respuestas más cortas y uno mayor permite razonamiento más largo en tareas complejas, optimizando el trade-off entre tarea y cómputo. No garantiza que `medium` baste para cada resultado. (Fuente: [Introducing Beam](https://reflection.ai/blog/introducing-beam), consultada 2026-11-04.)

GPT-5.6 separa `text.verbosity` de `reasoning.effort`: no conviene confundir salida visible con razonamiento interno. (Fuente: [Latest model guide](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6), consultada 2026-11-04.)

## Datos de benchmark

En Artificial Analysis, con GPT-6.1 Terra bajo el harness de Codex, la comparación muestra:

| Esfuerzo | Índice | Coste/tarea | Tiempo | Tokens totales |
|---|---:|---:|---:|---:|
| medium | 42 | $0,39 | 10,2 min | 4,1 M |
| high | 46 | $0,54 | 12,7 min | 5,6 M |
| xhigh | 48 | $0,69 | 16,4 min | 6,9 M |
| max | 48 | $1,24 | 26,1 min | 12,3 M |

El índice no es un porcentaje de éxito. Los tokens incluyen input en caché, no solo razonamiento. Los datos son de benchmark y entorno; no son una estimación directa para este repositorio ni una prueba causal de que un nivel baje el coste. (Fuente: [Codex vs Mirror](https://artificialanalysis.ai/agents/coding-agents/comparisons/codex-vs-mirror), consultada 2026-11-04.)

La metodología mide éxito, coste, tiempo y tokens end-to-end. El entorno y el harness importan; no se debe extrapolar las condiciones de una cuenta Go a una API pay-as-you-go directa. (Fuente: [Benchmark methodology](https://artificialanalysis.ai/methodology/coding-agents-benchmarking), consultada 2026-11-04.)

TALE (Token-Budget-Aware LLM Reasoning, v6 revisada 2026-10-16) sugiere que un presupuesto adaptado a la complejidad puede reducir tokens con una pérdida leve en evaluaciones propias. No prueba que `medium` baste para implementación en este repositorio ni para pasos medidos de OpenCode. (Fuente: [TALE](https://arxiv.org/abs/2412.18547), consultada 2026-11-04.)

## Recomendación propuesta

Esta sección es una síntesis del coordinador, no un hecho experimental:

- Usar `low` para transformaciones mecánicas o tareas de herramienta con instrucciones verificables; ejecutar comandos deterministas puede hacerse con código, sin necesidad de alto razonamiento.
- Usar `medium` como punto inicial para implementación acotada, cambios definidos, debugging común y revisión pequeña.
- Usar `high` cuando la ambigüedad, el impacto entre módulos, la concurrencia, la seguridad o la recuperación requieren razonamiento profundo, o cuando `medium` falla por razonamiento real, no por permisos, cuota o error de herramienta.
- Reservar `xhigh`/`max` para ganancia observada y medible; no por tamaño o duración sin más.
- Respetar variantes publicadas; no asumir equivalencias entre proveedores. Go/Kimi 3.1 Pro publica `low`, `high` y `max`, pero no `medium`; Beam publica `medium`. Elegir combinaciones adecuadas, no inventar una variante ni llamar `default` a `medium` cuando no exista.

Escalar por fallo de razonamiento real, no repitiendo la misma instrucción. Medir por intento aceptado y comparable (tarea, modelo, proveedor, esfuerzo, contexto): tiempo, tokens de input/caché/razonamiento/output cuando existan, reintentos, correcciones y coste conocido. Usar trabajos reales autorizados, no una batería de inferencias de benchmark. No afirmar ahorro no medido, no atribuir latencia total a `high`, ni comparar `high` de Beam con `medium` de Kimi como equivalentes. Mantener contexto útil, pero no cargar historial innecesario por costumbre; no compactar ni borrar la sesión en esta tarea.
