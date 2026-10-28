# Revisión de integración con subagentes

Fecha: 2026-10-28. Entorno: Codex Desktop en Windows; OpenCode v2.2.0.

## Hallazgo y corrección

La versión anterior interfería en la elección de ejecutor: `SKILL.md` reservaba el adaptador al coordinador y prohibía el spawn nativo para tareas rutinarias. `AGENTS.md` repetía la prohibición. No era un bloqueo técnico de la API de Codex, pero podía desviar los flujos de Superpowers.

Ahora el coordinador conserva la elección de ejecutor. Los subagentes nativos autorizados pueden encargar subtareas al adaptador; mantienen sus responsabilidades, las pruebas y los revisores independientes. Se corrigieron la skill, la guía del repositorio y el README. No se modificaron el código del adaptador, las políticas ni los archivos del plugin Superpowers o la configuración de Codex.

La regla `tool.use subagent:*` pertenece a OpenCode y bloquea solo subdelegaciones dentro de ese ejecutor. No afecta a los subagentes nativos de Codex.

## Activación observada

La skill instalada aparece en el catálogo suministrado a esta conversación: su descubrimiento está comprobado. Puede invocarse mediante `$delegating-to-opencode` o seleccionarse por coincidencia de la tarea con su descripción. La selección implícita depende del modelo; no se garantiza para cualquier tarea.

No hay interceptación de `spawn_agent`, MCP ni hooks en el adaptador. Cargar instrucciones no inicia inferencia. `run` inicia la tarea externa; `doctor` consulta versión y catálogo. No se cambian modelos ni esfuerzos de subagentes nativos.

Fuente oficial consultada: [Skills: How skills activate](https://developers.openai.com/plugins/concepts/skills).

## Validación y límites

- Antes: un evaluador nativo independiente leyó la skill anterior y concluyó que la composición implementador nativo → subtarea OpenCode → revisor nativo no estaba permitida.
- Después: otro evaluador nativo, con contexto independiente y el mismo caso, concluyó que los dos roles nativos se conservan y que la subtarea externa está permitida. Ambos evaluadores fueron lanzados mediante el sistema nativo de subagentes de Codex.
- Suite existente: **53 pruebas superadas**. Validador de skill: **Skill is valid!**. No se añadieron pruebas que comparasen texto fuente.
- La evaluación externa no llegó a inferencia: el adaptador devolvió `catalog_unavailable`. Al consultar directamente `opencode models --standalone`, OpenCode informó `ServiceUnavailableError: Location plugins did not finish activating`.

La composición está validada a nivel de instrucciones y el sistema nativo se utilizó en esta revisión. No se afirma una nueva ejecución extremo a extremo con OpenCode mientras persista el error de plugins; las ejecuciones exitosas anteriores permanecen documentadas en `validacion-opencode.md`.
