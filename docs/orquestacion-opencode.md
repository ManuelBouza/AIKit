# Orquestación Codex/OpenCode

Codex conserva conversación, diseño, arquitectura, contratos, plan y selección
de modelo. OpenCode ejecuta exploración factual, diagnóstico, implementación,
pruebas, correcciones, documentación, revisión independiente y verificación.

Roles y flujo: implementador en OpenCode; revisor en sesión nueva, sin
redelegar ni modificar la entrega; Codex comprueba evidencias. Capacidad primero:
Free adecuado -> Go -> otras alternativas adecuadas -> Codex nativo si no hay
opción adecuada/disponible. No degradar para evitar Codex ni agotar Free
inadecuados. Si falta modelo adecuado o disponibilidad adecuada, retornar
automáticamente por función, anunciando y registrando motivo, sin nueva
aprobación; mantener revisión independiente. Solo bloquea proveedor directo
`openai`; GPT de otros proveedores sigue permitido.

Contrato futuro `review.json`: `role: reviewer`, `session`, `snapshot`,
`verdict: accepted|needs_corrections`, `checks[]` (`id`, `command`, `cwd`,
`exit_code`, `summary`), `findings[]` (`severity: blocker|warning|info`,
`description`), `limitations[]`. La metadata no prueba autoría ni calidad;
`session` esperada proviene del backend real y `snapshot` lo fija el
coordinador. La utilidad de validación aún no existe hasta tarea 2.

MCP preferido si está publicado y cabe en 60 s; CLI para tareas largas; no
reintentar si hay intento vivo. No interceptar nativos ni Superpowers ni crear
nueva skill. Evidencias históricas permanecen históricas.