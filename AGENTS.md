# Guía del repositorio

## Propósito

Evolucionar AIKit hacia un complemento instalable de configuraciones y skills
reproducibles, complementando Superpowers y otras skills.

## Antes de crear o modificar una skill

Explora primero las skills y herramientas instaladas y lee sus instrucciones
pertinentes. Registra cobertura, carencias y justificación. Reutiliza lo existente;
implementa solo lo no cubierto. No dupliques Superpowers ni alteres sus archivos,
activación o roles. Aplica también a cambios de AIKit. Consulta
`docs/principios-aikit.md`.

## Estructura

- `skills/delegating-to-opencode/`: instrucciones, política y scripts tipados
  (`delegate.py` para la CLI y `mcp_server.py` para el servidor MCP local).
- `tests/`: pytest con transporte falso, sin inferencia.
- `scripts/build_plugin.py`: exporta el complemento y catálogo por lista permitida.
- `docs/`: investigación, validación y diseño.
- `opencode.json`: bloqueos de proveedor y subdelegación.
- `.aikit/`: tareas y evidencias ignoradas por Git.

## Regla de coordinación

Conserva roles, subagentes y revisiones de Codex y Superpowers. El coordinador o
subagente nativo delega la implementación y verifica diff y pruebas. Los workers
no redelegan; sus resultados no sustituyen revisiones independientes.

Activa `$delegating-to-opencode` explícitamente o por descripción.
No intercepta `spawn_agent` ni MCP. `run` exige modelo y motivo explícitos.
`run` comprueba en el destino, global o proyecto, `provider.use openai deny` y
`tool.use subagent:* deny`. Sin certificado rechaza la inferencia; `doctor` no
lo exige. Consulta `docs/correcciones-revision-funcional.md` para sus límites.
Escoge modelo y esfuerzo según la tarea: gratuitos suficientes, después Go y
otras alternativas conectadas. Bloquea solo el proveedor directo `openai`; GPT de
otros proveedores siguen permitidos. Usa variantes publicadas o el predeterminado.
Antes de cada tarea o reintento en OpenCode, anuncia su objetivo, modelo,
esfuerzo y condición gratuita o de pago; indica cuando la tarifa sea desconocida.

El servidor MCP local `aikit-opencode` expone el mismo núcleo con
`opencode_catalog` y `opencode_delegate`; prefiere esas herramientas si el
cliente las publica y conserva la CLI como alternativa. No elige modelo ni
reintenta. Su timeout es por proceso: el cliente MCP necesita 15000 s para
cubrir los cuatro procesos de una ejecución. Consulta `docs/mcp-opencode.md`.

Con `free_limit_reached` y `fallback: reselect`, evalúa Go y alternativas sin
nueva confirmación. Sin opciones adecuadas disponibles, informa y continúa con
Codex nativo. Revisa cambios parciales antes de reintentar. No eludas permisos,
autenticación o privacidad.

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

Consulta `README.md` para uso, instalación y restauración. Conserva configuración
ajena y respaldos fuera de rutas descubribles.
Para empaquetar, consulta `docs/plugin-aikit.md`; no instales desde la raíz del
checkout, ya que Codex también copia archivos ignorados por Git.

## Estilo

Python tipado; Ruff para formato/lint, mypy para tipos. Pytest con fixtures y
parametrización por comportamiento. Documenta en español.

## Validación

Registra entorno, configuración, resultado esperado y observado de cada cambio.
No declares preferencias verificadas sin evidencia.

## Seguridad

No incluyas credenciales ni datos privados. Usa ejemplos ficticios. Políticas y
certificado no son un sandbox; bloquear `subagent` no bloquea `shell`.
