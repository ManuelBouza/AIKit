# Guía del repositorio

## Propósito

Documentar preferencias de configuración de Codex. OpenCode ejecuta
tareas acotadas con modelos conectados, preferentemente gratuitos; Codex y
Superpowers conservan coordinación, subagentes, revisiones y verificación.

## Estructura

- `skills/delegating-to-opencode/`: skill autocontenida, `policy.json` con
  preferencias y `scripts/delegate.py`.
- `tests/`: pruebas `unittest` con transporte falso, sin inferencia real.
- `docs/`: investigación, validación, diseño y planes.
- `opencode.json`: bloquea `openai` directo y subdelegación interna de OpenCode.
- `.aikit/`: tareas locales ignoradas por Git.
- `README.md`: requisitos, uso, instalación y restauración.

## Regla de coordinación

Conserva roles, subagentes, revisiones y pruebas de Codex y Superpowers.
Antes de implementar o transformar archivos, el coordinador o un subagente
nativo autorizado delega la ejecución a OpenCode y conserva la verificación. El
resultado no sustituye una revisión independiente. Los workers de OpenCode no
delegan.

La skill se invoca con `$delegating-to-opencode` o se selecciona por descripción;
no intercepta `spawn_agent` ni MCP. `run` exige modelo y motivo explícitos.
Permite modelos conectados gratuitos o de pago, salvo el proveedor directo
`openai`. GPT de `opencode`, `opencode-go` u otros proveedores siguen permitidos;
el bloqueo no depende del fabricante. Prioriza gratuitos suficientes.
La variante debe existir en los metadatos; sin variante se registra el
ajuste predeterminado. No hay lista cerrada, modelo por defecto ni elección
automática del mejor modelo.

Preparar briefs y ejecutar verificaciones, incluidas comprobaciones de shell,
siguen siendo coordinación de Codex. Si falla el backend, informa el bloqueo
real; no implementes en local en silencio. Sin ejecución externalizable no se
llama a OpenCode.

## Comandos

Desde la raíz del repositorio:

```powershell
python -m unittest discover -s tests -v
python skills/delegating-to-opencode/scripts/delegate.py doctor --cwd .
python skills/delegating-to-opencode/scripts/delegate.py run --cwd . --task-file .aikit/tarea.md --model opencode/deepseek-v4.1-flash-free#high --reason "Integracion acotada; variante alta disponible" --agent build --timeout 600
```

`doctor` consulta la API local y muestra el catálogo compacto; `--model` filtra.
`run` no exige un archivo de configuración local; OpenCode respeta la
configuración existente. Consulta `README.md` para instalar la skill sin
sobrescribir y restaurar una copia anterior.

## Estilo

Documentación en español, instrucciones breves y ejemplos reproducibles. Conserva
nombres originales de opciones y archivos. Distingue preferencias verificadas de
experimentos pendientes.

## Validación

Cada cambio requiere un escenario concreto con entorno, configuración, resultado
esperado y observado. No presentes una preferencia como verificada sin evidencia.

## Seguridad

No incluyas credenciales, tokens, conversaciones privadas ni datos de cuenta. Usa
ejemplos ficticios. La política de preferencias y el catálogo no sustituyen un
sandbox del sistema operativo.
