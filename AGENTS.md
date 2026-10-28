# Guía del repositorio

## Propósito

Evolucionar AIKit hacia un complemento instalable de configuraciones y skills
reproducibles. Complementa Superpowers y otras skills instaladas.
OpenCode ejecuta; Codex y Superpowers coordinan y verifican.

## Antes de crear o modificar una skill

Primero explora las skills y herramientas instaladas y lee sus instrucciones
pertinentes. Registra cobertura, carencias y justificación del cambio.
Reutiliza lo existente; implementa solo la necesidad no cubierta.
No dupliques flujos de Superpowers ni alteres sus archivos, activación o roles.
Aplica esta comprobación también a modificaciones de AIKit. Consulta
`docs/principios-aikit.md` para los criterios de compatibilidad y distribución.

## Estructura

- `skills/delegating-to-opencode/`: skill, política y adaptador Python.
- `tests/`: pruebas pytest tipadas, fixtures y transporte falso, sin inferencia.
- `docs/`: investigación, validación y diseño.
- `opencode.json`: bloquea `openai` directo y subdelegación interna de OpenCode.
- `.aikit/`: tareas locales ignoradas por Git.

## Regla de coordinación

Conserva roles, subagentes, revisiones y pruebas de Codex y Superpowers.
El coordinador o subagente nativo delega la implementación a OpenCode y verifica
el resultado; no sustituye revisiones independientes. Los workers no redelegan.

Activa `$delegating-to-opencode` explícitamente o por descripción.
No intercepta `spawn_agent` ni MCP. `run` exige modelo y motivo explícitos.
Permite modelos conectados gratuitos o de pago, salvo el proveedor directo
`openai`. GPT de `opencode`, `opencode-go` u otros proveedores siguen permitidos;
prioriza gratuitos suficientes.
Escoge modelo y esfuerzo según la tarea. La variante debe existir en los
metadatos; sin variante se registra el ajuste predeterminado.

Si OpenCode agota el uso gratuito (`free_limit_reached`), informa y continúa con Codex y sus subagentes
nativos sin nueva confirmación; no uses OpenAI directo en OpenCode ni cambies
automáticamente a pago. Para otros fallos, informa el bloqueo sin eludir permisos.

## Comandos

Desde la raíz:

```powershell
uv sync --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
python skills/delegating-to-opencode/scripts/delegate.py doctor --cwd .
```

`doctor` consulta el catálogo. Consulta `README.md` para ejecutar tareas,
instalar y restaurar la skill. OpenCode respeta la configuración existente.

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
