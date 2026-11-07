# Investigar criterios para escoger modelo y esfuerzo por tarea

Fecha: 2026-11-01.
Estado: pendiente de debatir.

## Idea

Realizar una investigación profunda en documentación oficial y medios
especializados sobre los criterios para elegir el modelo y el nivel de esfuerzo
adecuados para cada tarea.

El objetivo es estimar las necesidades y el esfuerzo de cada tarea y escoger el
modelo que mejor encaje según sus capacidades, junto con el nivel de esfuerzo
apropiado. No se busca crear una tabla fija de asignaciones entre tareas y modelos.
La elección debe ajustarse al encargo concreto y a las capacidades disponibles.

La motivación es equilibrar la calidad necesaria con el consumo de tokens, el
coste y el tiempo hasta obtener un resultado útil. Como hipótesis para comprobar,
usar `high` o `max` puede consumir más tokens y demorar la respuesta sin aportar
una mejora necesaria; `low` puede resultar insuficiente para algunas tareas,
pero ofrecer el mejor coste para tareas mecánicas. Incluir también `medium` en
la evaluación, además de los demás niveles que publique cada modelo.

## Para investigar y debatir después

- Qué características de la tarea determinan la capacidad necesaria: complejidad,
  ambigüedad, contexto, herramientas, alcance y consecuencias de un error.
- Cómo producir una estimación breve de las necesidades y el esfuerzo de la tarea
  y contrastarla con las capacidades de los modelos candidatos para decidir cuál
  encaja mejor, sin reducir la selección a una tabla fija.
- Cómo elegir por separado el modelo y el esfuerzo, y qué relación existe entre
  ambos según el proveedor y las variantes realmente disponibles.
- Cuándo aumentar el esfuerzo mejora el resultado y cuándo solo añade consumo o
  demora; evitar asumir equivalencias entre niveles de distintos modelos.
- Qué evidencia ofrecen las fuentes oficiales, los análisis especializados y las
  evaluaciones reproducibles; distinguir recomendaciones de resultados medidos.
- Cómo comparar tareas mecánicas, exploración, diagnóstico, implementación,
  arquitectura, pruebas y revisión independiente.
- Cómo medir el coste total hasta un resultado aceptable, incluyendo fallos,
  reintentos, correcciones y revisión, además de los tokens de la primera salida.
- Qué reglas prácticas permiten escoger rápidamente y cuándo conviene escalar a
  otro esfuerzo o modelo, sin realizar una deliberación costosa en cada encargo.

## Resultado que se quiere obtener

Un método de estimación y selección por tarea basado en evidencia, con criterios,
ejemplos orientativos, límites y fuentes fechadas. Debe relacionar las necesidades
del encargo con las capacidades del modelo y el esfuerzo estimado, incluyendo
`low`, `medium`, `high` y `max` cuando estén disponibles. Los ejemplos no serán
asignaciones fijas. Las recomendaciones deben poder actualizarse
cuando cambien los modelos, sus variantes o las condiciones del proveedor.

Relacionada con la nota [003](003-heuristica-coste-delegacion.md), sobre el coste
de delegar, y la [005](005-prompts-concisos-opencode.md), sobre la eficacia de los
encargos. Complementa la disponibilidad de la nota
[001](001-disponibilidad-cuentas.md): tener cuota no demuestra que un modelo o
esfuerzo sea adecuado para una tarea.

La investigación queda pendiente. Guardar esta nota no cambia la política actual
de selección ni autoriza investigaciones o pruebas con inferencias.
