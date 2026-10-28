# Guía del repositorio

## Propósito

Reproducir y documentar preferencias de configuración de Codex. OpenCode permite
delegar tareas adecuadas a modelos gratuitos y complementa la coordinación,
los subagentes y la verificación de Codex y Superpowers.

## Estructura

- `skills/delegating-to-opencode/`: skill autocontenida, `policy.json` y
  `scripts/delegate.py`.
- `tests/`: pruebas `unittest` con transporte falso, sin inferencia real.
- `docs/`: investigación, validación, diseño y planes.
- `opencode.json`: limita proveedores y subdelegación interna de OpenCode.
- `.aikit/`: tareas locales ignoradas por Git.
- `README.md`: requisitos, uso, instalación y restauración.

## Regla de coordinación

Conserva los roles, subagentes, revisiones y pruebas de Codex y Superpowers.
El coordinador decide qué tareas ejecutar nativamente y cuáles externalizar;
prioriza OpenCode gratuito para subtareas adecuadas. Tanto el coordinador como
un subagente nativo autorizado pueden usar `delegating-to-opencode`. Quien lo
invoca verifica el diff y las pruebas; el resultado no sustituye una revisión
independiente requerida. Los workers de OpenCode no vuelven a delegar.

La skill se invoca con `$delegating-to-opencode` o se selecciona por coincidencia
con la tarea; no intercepta llamadas ni cambia modelos nativos. Si falla un
modelo gratuito, informa al rol que lo invocó; no hay fallback externo de pago.

## Comandos

Desde la raíz del repositorio:

```powershell
python -m unittest discover -s tests -v
python skills/delegating-to-opencode/scripts/delegate.py doctor --cwd .
python skills/delegating-to-opencode/scripts/delegate.py run --cwd . --task-file .aikit/tarea.md --model opencode/deepseek-v4.1-flash-free --agent build --timeout 600
```

El adaptador solo permite los tres modelos `-free` de `opencode` listados en
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
