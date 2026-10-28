# Guía del repositorio

## Propósito

Reproducir y documentar preferencias de configuración de Codex. La ejecución de
tareas rutinarias se delega a modelos gratuitos de OpenCode; Codex coordina y
verifica el resultado.

## Estructura

- `skills/delegating-to-opencode/`: skill autocontenida, `policy.json` y
  `scripts/delegate.py`.
- `tests/`: pruebas `unittest` con transporte falso, sin inferencia real.
- `docs/`: investigación, validación, diseño y planes.
- `opencode.json`: política del proyecto que limita proveedores y subagentes.
- `.aikit/`: tareas locales ignoradas por Git.
- `README.md`: requisitos, uso, instalación y restauración.

## Regla de coordinación

Codex usa `delegating-to-opencode` para el trabajo de ejecución rutinario y
verifica al final el diff, las pruebas y el resultado. No usa el spawn nativo de
subagentes para esas tareas. Los workers no cargan la skill. Si un modelo
gratuito falla, el error vuelve al coordinador; no hay fallback de pago.

## Comandos

Desde la raíz del repositorio:

```powershell
python -m unittest discover -s tests -v
python skills/delegating-to-opencode/scripts/delegate.py doctor --cwd .
python skills/delegating-to-opencode/scripts/delegate.py run --cwd . --task-file .aikit/tarea.md --model opencode/deepseek-v4.1-flash-free --agent build --timeout 600
```

Solo se permiten los tres modelos `-free` de `opencode` listados en
`skills/delegating-to-opencode/policy.json`. Consulta `README.md` para instalar
la skill sin sobrescribir y restaurar una copia anterior.

## Estilo

Documentación en español, instrucciones breves y ejemplos reproducibles. Conserva
nombres originales de opciones y archivos. Distingue preferencias verificadas de
experimentos pendientes.

## Validación

Cada cambio requiere un escenario concreto con entorno, configuración, resultado
esperado y observado. No presentes una preferencia como verificada sin evidencia.

## Seguridad

No incluyas credenciales, tokens, conversaciones privadas ni datos de cuenta. Usa
ejemplos ficticios. La política del proyecto y la lista de modelos no sustituyen
un sandbox del sistema operativo.
