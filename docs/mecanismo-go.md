# Mecanismo go

Guía oficial: [instrucciones globales de Codex](https://developers.openai.com/codex/guides/agents-md).

## Cobertura

Codex carga instrucciones globales desde `CODEX_HOME`. Superpowers cubre procesos.
AIKit aporta preferencia conversacional y despliegue conservador.

## Uso

Desde el repositorio:

```powershell
python scripts/install_go.py --codex-home C:\ruta\.codex --template config/codex/go.md
```

Desde el paquete exportado, usa las rutas correspondientes del paquete:

```powershell
python scripts/install_go.py --codex-home C:\ruta\.codex
```

La plantilla por defecto es `config/codex/go.md` junto al instalador.

## Alcance CODEX_HOME

El instalador solo modifica `CODEX_HOME/AGENTS.md`. Respeta `CODEX_HOME` si está
definido. No modifica perfiles reales automáticamente al instalar el complemento.

## Override global

Si `CODEX_HOME/AGENTS.override.md` contiene bytes no vacíos, bloquea la
aplicación del mecanismo global y el instalador rechaza la operación sin
modificarlo.

## Marcadores

El bloque instalado está delimitado por:

- `<!-- AIKIT:GO:BEGIN -->`
- `<!-- AIKIT:GO:END -->`

Un destino con marcadores malformados o duplicados se rechaza sin escribir.

## Idempotencia

Una segunda ejecución sin cambios devuelve `unchanged` y no crea respaldo ni
cambia la fecha de modificación del archivo.

## Respaldos y STATE.txt

El respaldo único vive en `CODEX_HOME/backups/aikit/go-<uuid>/`. Si
`AGENTS.md` existía, se guarda como `AGENTS.md` con sus bytes exactos. Si no
existía, se crea `STATE.txt` indicando que `AGENTS.md` no existía
originalmente.

## Restauración

Para retirar solo el bloque, elimina el texto entre los marcadores incluidos.
Para restaurar desde respaldo, compara manualmente con las ediciones posteriores;
no restaures una copia antigua a ciegas.

## Límites

No se añade skill, hook ni MCP. No hay autoinstalación al cargar el plugin.
La plantilla no garantiza obediencia en todos los chats. Perfiles con otro
`CODEX_HOME` requieren instalación propia. Sesiones abiertas pueden requerir
reinicio.

Queda una ventana TOCTOU sin bloqueo mutuo: el instalador revalida existencia,
symlink y bytes inmediatamente antes de `os.replace`, pero no promete exclusión
mutua.

## Red observado por el worker (antes del fix)

- `uv run pytest -q`: 4 fallos: `test_override_whitespace_rejects`,
  `test_concurrent_mutation_not_overwritten`, `test_cli_subprocess_changed`,
  `test_cli_subprocess_unchanged`; 232 pruebas pasaron.

## Validación independiente del 29 de octubre de 2026

- `uv run pytest`: 237 pruebas correctas, incluidas 22 del instalador.
- `uv run ruff check .`: All checks passed
- `uv run ruff format --check .`: 52 files already formatted
- `uv run mypy`: Success, no issues found in 22 source files

Entorno: Windows, Python 3.14.9 y AIKit 0.1.3. La revisión independiente
detectó una comprobación concurrente anterior al respaldo; OpenCode la movió
después de escribirlo. Codex amplió la prueba de verificación para simular
ediciones durante temporal y respaldo: ambas se conservan, sin temporales
residuales. La revisión final no encontró bloqueantes.

El evaluador interpretó en seco ocho casos: `go`, contexto compatible,
pregunta sin aprobación, cita de `go`, contexto fuera del alcance, ausencia
de tarea, `google` y decisión material pendiente. El resultado fue ejecutar
solo la tarea recomendada y compatible, manteniendo conversación en los demás.
Son simulaciones limitadas, no una garantía universal del comportamiento.

Instalación real: se incorporó el bloque a un `AGENTS.md` global inicialmente
vacío, con respaldo verificado fuera de rutas descubribles. El contenido
instalado coincide con la plantilla. La segunda ejecución devolvió
`unchanged`, conservó la fecha del archivo y no creó otro respaldo.
Evidencia local ignorada: `.aikit/go-profile-validation.json`.

Después de instalar, este chat recibió una cadena de instrucciones actualizada
que incluía el bloque global junto a las instrucciones del proyecto. Esto
acredita su carga en este chat; otros perfiles requieren instalación propia.
