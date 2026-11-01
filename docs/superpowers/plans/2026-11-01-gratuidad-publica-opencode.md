# Plan: gratuidad condicionada y contraste público de proveedores

## Tareas

1. Crear `availability_public_terms.py` con `PublicTerm` y validación.
2. Integrar campos aditivos en `AvailabilitySnapshot`.
3. Conservar hechos públicos en `availability_refresh`.
4. Añadir importación validada en CLI.
5. Añadir `opencode_availability` en MCP.
6. Mostrar recuentos separados en `doctor`.
7. Incorporar Cloudflare 3 como hecho público en estado temporal.
8. Actualizar diseño/plan y referencia de tarea diaria.
9. Ejecutar TDD, pytest, ruff y mypy.

## Verificación

- `uv run pytest`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy`
- `python skills/delegating-to-opencode/scripts/delegate.py doctor --cwd .` con contexto configurado.