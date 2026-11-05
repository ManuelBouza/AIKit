# Revisión independiente en OpenCode

Formato `review.json`:

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
de la versión resultante. Si necesita otro diseño, devuelve la decisión al
coordinador de Codex.

`scripts/review_evidence.py` valida el contrato, sesión esperada, snapshot y
checks declarados; no ejecuta los comandos ni prueba que el informe sea auténtico
o técnicamente correcto. La metadata por sí sola no demuestra autoría ni calidad.
Codex comprueba la aceptación de metadata y coordina, sin repetir la revisión
técnica. MCP preferido si está publicado y cabe en 60 s; CLI para tareas largas;
no reintentar si hay intento vivo.
