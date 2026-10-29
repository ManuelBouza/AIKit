# Revisión independiente en OpenCode

Contrato futuro `review.json`:

- `role`: `reviewer`
- `session`: sesión real del revisor
- `snapshot`: huella fijada por el coordinador
- `verdict`: `accepted` o `needs_corrections`
- `checks`: lista de `{ id, command, cwd, exit_code, summary }`
- `findings`: lista de `{ severity: blocker|warning|info, description }`
- `limitations`: lista de cadenas

El revisor recibe diseño, criterios de aceptación y archivos. Usa sesión nueva
y ejecuta sus comprobaciones. No modifica la entrega mientras la revisa. Los
defectos vuelven al implementador; cualquier cambio posterior requiere revisión
de la versión resultante. Si necesita otro diseño, devuelve la decisión a Codex.

La metadata no prueba autoría ni calidad. La utilidad de validación aún no
existe hasta tarea 2; no ejecutar un comando inexistente como si estuviera
validado. MCP preferido si está publicado y cabe en 60 s; CLI para tareas
largas; no reintentar si hay intento vivo.