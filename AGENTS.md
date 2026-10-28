# Guía del repositorio

## Propósito

Documentar preferencias de Codex: OpenCode ejecuta; Codex y Superpowers coordinan
y verifican.

## Estructura

- `skills/delegating-to-opencode/`: skill autocontenida, `policy.json` con
  preferencias y `scripts/delegate.py`.
- `tests/`: pruebas pytest tipadas, fixtures y transporte falso, sin inferencia.
- `docs/`: investigación, validación, diseño y planes.
- `opencode.json`: bloquea `openai` directo y subdelegación interna de OpenCode.
- `.aikit/`: tareas locales ignoradas por Git.
- `README.md`: requisitos, uso, instalación y restauración.

## Regla de coordinación

Conserva roles, subagentes, revisiones y pruebas de Codex y Superpowers.
El coordinador o subagente nativo delega la implementación a OpenCode y verifica
el resultado; no sustituye revisiones independientes. Los workers no redelegan.

La skill se invoca con `$delegating-to-opencode` o se selecciona por descripción;
no intercepta `spawn_agent` ni MCP. `run` exige modelo y motivo explícitos.
Permite modelos conectados gratuitos o de pago, salvo el proveedor directo
`openai`. GPT de `opencode`, `opencode-go` u otros proveedores siguen permitidos;
el bloqueo no depende del fabricante. Prioriza gratuitos suficientes.
La variante debe existir en los metadatos; sin variante se registra el
ajuste predeterminado. No hay lista cerrada, modelo por defecto ni elección
automática del mejor modelo.

Preparar briefs y verificar sigue siendo coordinación. Si OpenCode agota el uso
gratuito (`free_limit_reached`), informa y continúa con Codex y sus subagentes
nativos sin nueva confirmación; no uses OpenAI directo en OpenCode ni cambies
automáticamente a pago. Para otros fallos, informa el bloqueo sin eludir permisos.

## Comandos

Desde la raíz del repositorio:

```powershell
uv sync --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
python skills/delegating-to-opencode/scripts/delegate.py doctor --cwd .
python skills/delegating-to-opencode/scripts/delegate.py run --cwd . --task-file .aikit/tarea.md --model opencode/deepseek-v4.1-flash-free#high --reason "Integracion acotada; variante alta disponible" --agent build --timeout 600
```

`doctor` consulta la API local y muestra el catálogo compacto; `--model` filtra.
`run` no exige un archivo de configuración local; OpenCode respeta la
configuración existente. Consulta `README.md` para instalar la skill sin
sobrescribir y restaurar una copia anterior.

## Estilo

Python tipado; Ruff comprueba formato y lint, mypy verifica tipos. Usa fixtures
y parametrización pytest, con módulos por comportamiento. Documenta en español.

## Validación

Cada cambio requiere un escenario concreto con entorno, configuración, resultado
esperado y observado. No presentes una preferencia como verificada sin evidencia.

## Seguridad

No incluyas credenciales, tokens, conversaciones privadas ni datos de cuenta. Usa
ejemplos ficticios. La política de preferencias y el catálogo no sustituyen un
sandbox del sistema operativo.
