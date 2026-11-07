# Referencia a BMAD en AGENTS.md

Fecha: 2026-11-07.
Estado inicial: Pendiente de debatir.
Estado actual: Implementada; bloque aprobado con go y añadido el 2026-11-07.

## Pregunta del usuario

Probar `bmad-help` para conocer sus funciones e investigar si conviene añadir
referencias a las funciones habituales de BMAD en el AGENTS.md del proyecto,
además del descubrimiento automático existente.

## Evidencia y resultado

- En este chat están publicadas las 29 skills BMAD del proyecto. No hay datos
  suficientes para afirmar cuáles son las más usadas: las candidatas siguientes
  son una propuesta, no estadísticas de uso.
- Se siguieron las instrucciones de `bmad-help`, su catálogo y el resolvedor
  `.venv/Scripts/python.exe -B _bmad/scripts/resolve_config.py --project-root
  C:/Manuel/Projects/AIKit --key core --key modules.bmm` (código 0).
  Comunicación y documentos en Spanish, usuario Manuel, conocimiento en docs,
  salidas bajo `_bmad-output/`. Se reutilizó el intérprete existente porque el
  intento anterior con uv falló por acceso denegado a su caché.
- No hay archivos en `_bmad-output/` que acrediten flujos terminados. Se leyó
  AGENTS.md y la referencia local de buenas prácticas de bmad-project-context
  como fuente; no se activó su flujo de adopción o auditoría.
- OpenAI documenta el descubrimiento en `.agents/skills`, la carga inicial de
  nombre y descripción, y la invocación explícita o por coincidencia de tarea.
  AGENTS.md se carga como instrucciones persistentes del proyecto. Se deduce
  que una referencia a BMAD no es requisito técnico de descubrimiento.
- BMAD 6.12.4 identifica los directorios instalados como catálogo canónico y
  propone bmad-help para orientar. Sus reglas de contexto admiten políticas y
  puntos de entrada útiles, y desaconsejan copias de información que envejecen.
- La web actual de BMAD ya describe `bmad` y otros cambios; se consultaron también
  los documentos fijados a v6.12.4 para evitar atribuirlos a la instalación local.

## Alternativas

1. Mantener solo el descubrimiento: suficiente para encontrar las skills.
2. Añadir una referencia breve de uso: recomendada si se desea fijar orientación
   compartida; no copiar el catálogo ni imponer un proceso completo a cada tarea.

## Texto aprobado y aplicado

```markdown
## Uso de BMAD

Para preguntas sobre BMAD o sobre qué flujo elegir, usa `bmad-help` y consulta
el catálogo instalado en `_bmad/_config/bmad-help.csv`.
Selecciona las demás skills según la petición y sus descripciones publicadas;
lee su SKILL.md al utilizarlas. No impongas el flujo completo a cambios pequeños.
Las recomendaciones de BMAD no autorizan tareas ni reanudan trabajos pausados:
se mantienen el mecanismo global go y las restricciones de este proyecto.
```

Se añadió únicamente este bloque a [AGENTS.md](../AGENTS.md), conservando las
instrucciones y cambios anteriores. No se modificó ninguna skill ni se inició
implementación de producto, automatización u OpenCode; tampoco commit o push.
La prueba de adaptación a un cambio real y los trabajos pausados conservan su
estado. Validación documental en el checkout principal: se comprobó que el bloque
coincide literalmente con la propuesta aprobada, que aparece una sola vez y que
el catálogo referenciado existe. `git diff --check` terminó con código 0.

## Fuentes primarias consultadas

- [OpenAI: skills y descubrimiento](https://learn.chatgpt.com/docs/build-skills).
- [OpenAI: instrucciones AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
- [BMAD 6.12.4: skills, agentes y ayuda](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/docs/reference/skills-and-agents.md).
- [BMAD 6.12.4: contexto del proyecto](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/docs/existing-codebases/set-and-maintain-project-context.md).
- Documentación web actual contrastada: https://docs.bmad-method.org/.

La recomendación es una conclusión para este proyecto, no una exigencia del
instalador ni una garantía de activación automática en todas las peticiones.
