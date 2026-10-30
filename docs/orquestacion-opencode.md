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
coordinador. La utilidad de validación está disponible en scripts/review_evidence.py (tarea 2).

MCP preferido si está publicado y cabe en 60 s; CLI para tareas largas; no
reintentar si hay intento vivo. No interceptar nativos ni Superpowers ni crear
nueva skill. Evidencias históricas permanecen históricas.


## CLI de evidencia de revision

`scripts/review_evidence.py` expone dos subcomandos (stdlib, sin dependencias nuevas):

- `snapshot --root R --files F.json`: lee una lista JSON de rutas relativas y
  emite en stdout una linea JSON compacta con la huella SHA256 por ruta
  (`null` si el archivo no existe). Salida 0 si se captura la huella.
- `validate --root R --report P.json --expectation E.json`: valida un informe
  `review.json` contra el contrato y la expectativa. JSON compacto en stdout;
  salida 0 solo si el veredicto es `accepted`, 1 en caso contrario.

No ejecuta comandos contenidos en los informes ni recorre el repositorio.

## Instalación de preferencias globales

`scripts/install_go.py` y `scripts/install_routing.py` instalan bloques globales en
`AGENTS.md` mediante el motor común `scripts/global_instructions.py`. Cada uno
acepta `--codex-home` y `--template`; la plantilla por defecto se resuelve desde
`__file__`, no desde el directorio actual. La instalación crea respaldo con UUID
fuera de descubrimiento y preserva bytes ajenos, incluidos BOM y CRLF. No se
ejecuta al cargar el plugin ni por hooks.
