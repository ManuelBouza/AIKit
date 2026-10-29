# Plan de implementación: Codex diseña, OpenCode ejecuta y verifica

> **Para ejecutores:** usar `superpowers:executing-plans` para coordinar estas
> tareas en orden. La ejecución técnica y su revisión se delegan a sesiones
> independientes de OpenCode; conservar subagentes nativos cuando el flujo
> aplicable los exija. No sustituir el método de ejecución aprobado por el usuario.

**Objetivo:** implantar el reparto aprobado sin degradar modelos y con retorno
automático a Codex por falta de capacidad o disponibilidad en OpenCode.

**Arquitectura:** instrucciones de enrutamiento y contratos compactos de evidencia;
una utilidad determinista comprueba su vigencia y completitud. Se reutiliza la
instalación de bloques globales. Sin nuevo servidor, selector automático de
modelos, supervisor de agentes ni cambios del núcleo de delegación.

**Tecnología:** Python 3.10+, biblioteca estándar, uv, pytest, Ruff y mypy.

**Diseño aprobado:** [Codex diseña y coordina; OpenCode ejecuta y verifica](../specs/2026-10-29-codex-disena-opencode-ejecuta.md).

## Restricciones globales

- Codex conserva conversación, arquitectura, contratos, planificación y selección.
- OpenCode explora, implementa, corrige, revisa y ejecuta/analiza verificaciones.
- Capacidad y esfuerzo primero; después Free, Go y otras opciones suficientes.
  Si no hay opción apropiada disponible, continuar en Codex sin nueva aprobación.
- Bloquear solo el proveedor directo `openai`; no cambiar cuentas ni privacidad.
- Anunciar cada intento con objetivo, modelo, variante/default y tarifa acreditada
  o desconocida. Revisar parciales y procesos vivos antes de reintentar.
- No alterar Superpowers, interceptar subagentes ni permitir que workers redeleguen.
- No repetir en Codex la revisión técnica normal; comprobar evidencias y coordinar.
- Mantener la CLI stdlib, las herramientas MCP existentes y sus límites actuales.
- Conservar el bloque `go`, los respaldos y la configuración ajena byte a byte.
- La implementación técnica será OpenCode; la revisión técnica también. El retorno
  nativo se aplica por función y conserva un revisor independiente cuando proceda.

## Focos de revisión y pruebas correspondientes

1. Aprobación de archivos que cambiaron después: invalidar evidencia (tarea 2).
2. Autor revisándose a sí mismo o inventando sesión: rechazar identidad incoherente
   con las sesiones realmente lanzadas por el coordinador (tarea 2).
3. Pruebas omitidas, comandos distintos o código no cero: no aceptar (tarea 2).
4. Modelos Free insuficientes o todos los adecuados indisponibles: elegir una
   alternativa suficiente o retornar, sin degradar ni detener el trabajo (tarea 4).
5. Actualizar enrutamiento global dañando `go` u otras preferencias: preservar
   bloques, idempotencia y respaldo, incluidos errores concurrentes (tarea 3).

## Tarea 1: política y contratos de ejecución

**Archivos:** modificar `AGENTS.md`, `README.md`, `docs/principios-aikit.md`,
`skills/delegating-to-opencode/SKILL.md` y `references/carga-opencode.md` de esa
skill; crear `skills/delegating-to-opencode/references/revision-opencode.md` y
`docs/orquestacion-opencode.md`. No reescribir evidencia histórica como actual.

**Interfaz:** contratos de implementador y revisor para las tareas 2 y 4.

- [ ] Ejecutar antes del cambio escenarios en seco con las instrucciones actuales:
  quién diseña, quién revisa, Free insuficiente y falta de opciones adecuadas.
  Registrar decisiones observadas sin presentarlas como pruebas de ejecución.
- [ ] Actualizar únicamente instrucciones contradictorias: diseño en Codex,
  revisión y verificación en OpenCode; el retorno automático no necesita agotar
  modelos descartados ni nueva aprobación. Preservar permisos y roles existentes.
- [ ] Definir entrega en `review.json`: `role: reviewer`, `session`, `snapshot`,
  `verdict: accepted|needs_corrections`, `checks`, `findings` y `limitations`.
  Cada check contiene `id`, `command`, `cwd`, `exit_code` y `summary`.
  Cada hallazgo contiene `severity: blocker|warning|info` y `description`.
- [ ] El revisor recibe diseño, aceptación y archivos; usa sesión nueva y ejecuta
  sus comprobaciones. Las correcciones invalidan la aceptación anterior.
  Si necesita otro diseño, devuelve la decisión a Codex, sin rediseñar por su cuenta.
- [ ] Repetir los escenarios con instrucciones nuevas. Documentar cobertura de
  Superpowers y carencia cubierta por AIKit; no crear otra skill de planificación.
- [ ] Revisar esta tarea desde otra sesión OpenCode antes de integrarla.

## Tarea 2: comprobar evidencias sin otra revisión técnica en Codex

**Archivos:** crear `scripts/review_evidence.py`, `tests/test_review_evidence.py`;
añadir el script a mypy y documentar su CLI en `docs/orquestacion-opencode.md`.

**Interfaces Python:**

```python
@dataclass(frozen=True)
class ReviewExpectation:
    snapshot: dict[str, str | None]
    implementer_session: str
    reviewer_session: str
    checks: dict[str, str]  # id -> comando requerido

def capture_snapshot(root: Path, files: Sequence[str]) -> dict[str, str | None]: ...
def validate_review(root: Path, report: dict[str, Any], expected: ReviewExpectation) -> dict[str, Any]: ...
```

**Contrato:** SHA256 por ruta relativa explícita, `None` para archivos eliminados.
Rechazar rutas fuera de raíz, enlaces y entradas que no sean archivos regulares.
No recorrer indiscriminadamente el repositorio ni incluir secretos/archivos ignorados.
El coordinador fija la lista relevante a partir del alcance y cambios entregados;
no permite que el revisor omita archivos del manifiesto para aprobarlos.

Las sesiones esperadas provienen de los resultados reales del adaptador, no del
JSON escrito por el worker. El snapshot se obtiene al cerrar la implementación.
El informe registra además el commit base cuando corresponda; la huella vincula
los cambios sin commit. Estas comprobaciones no prueban autoría ni calidad.

- [ ] Escribir pruebas antes de implementar, con estas aserciones de contrato:

```python
assert validate_review(root, valid_report, expected)["status"] == "accepted"
assert validate_review(root, stale_report, expected)["code"] == "snapshot_mismatch"
assert validate_review(root, failed_checks, expected)["code"] == "checks_failed"
assert validate_review(root, missing_checks, expected)["code"] == "checks_missing"
```

- [ ] Añadir casos: archivo cambiado tras snapshot, archivo eliminado, ruta que
  escapa, symlink, misma sesión autor/revisor, sesión distinta de la lanzada,
  comando no requerido, cwd ajeno a la raíz, esquema malformado y blocker abierto.
  Esperar rechazo en todos los casos adversos; definir fixtures tipadas de informe.
- [ ] Ejecutar `uv run pytest tests/test_review_evidence.py -q` y observar fallos
  antes del código. Implementar solo las funciones y el contrato descritos.
- [ ] CLI: `snapshot --root R --files F.json` lee lista JSON de rutas; `validate
  --root R --report review.json --expectation expected.json` lee el contrato
  anterior. JSON compacto en stdout; salida 0 solo al capturar o aceptar, 1 al
  rechazar. No ejecutar comandos contenidos en informes ni interpretar instrucciones.
- [ ] Aceptar únicamente informe del revisor esperado, snapshot íntegro que siga
  vigente, veredicto accepted, todos los checks requeridos con comando exacto,
  cwd de raíz y salida 0, sin blockers. Errores de validación devuelven status/error
  y código estable; los códigos de las cuatro aserciones anteriores son obligatorios.
- [ ] Ejecutar pruebas, Ruff y mypy en OpenCode; revisar desde otra sesión.
  Esta utilidad verifica metadatos, no decide modelos ni lanza workers.

## Tarea 3: preferencia global portable sin alterar go

**Archivos:** crear `config/codex/routing.md`, `scripts/global_instructions.py`,
`scripts/install_routing.py`, `tests/test_install_routing.py`; modificar
`scripts/install_go.py`, `scripts/build_plugin.py`, `pyproject.toml`, `plugin.json`,
`uv.lock`, `README.md`, `docs/plugin-aikit.md` y `docs/orquestacion-opencode.md`.

**Interfaz compartida:**
`install_block(codex_home: Path, template: Path, begin: str, end: str,
backup_prefix: str) -> Path | None` en `global_instructions.py`. Reutilizar la
implementación probada de instalación, sin copiar dos variantes de seguridad.
`install_go` conserva firma, CLI, marcadores y prefijo `go-` actuales.
`install_routing(codex_home: Path, template: Path) -> Path | None` usa marcadores
`<!-- AIKIT:ROUTING:BEGIN -->` / `<!-- AIKIT:ROUTING:END -->` y prefijo `routing-`.

- [ ] Escribir casos de instalación routing con `go` y texto ajeno previos:
  conservar sus bytes y respaldo exacto, reemplazar solo routing, segundo run
  sin mtime/respaldo nuevo; orden go→routing y routing→go con resultado equivalente.
- [ ] Repetir rechazo sin escrituras ante override global no vacío, marcadores
  inválidos y enlaces; simular edición durante temporal/respaldo y conservarla.
- [ ] Observar fallos; extraer el motor común y conservar todas las pruebas de
  `test_install_go.py`. Mantener detección concurrente antes de replace y su
  límite TOCTOU documentado, sin prometer bloqueo mutuo.
- [ ] Añadir CLI routing compatible con `--codex-home` y `--template`; resolver
  plantilla por `__file__`, no por cwd. No ejecutar durante carga del plugin.
- [ ] La plantilla distingue conversación/diseño de ejecución/verificación,
  describe selección suficiente y retorno, y remite a la skill cuando disponible.
  Si la skill o el transporte faltan, informar y continuar nativamente según el
  diseño; no asumir rutas personales ni activar otra cuenta.
- [ ] Exportar plantilla, tres scripts de instalación, utilidad de evidencia,
  referencia de revisión y guía nueva mediante `PACKAGE_FILES`. Probar la CLI
  desde el paquete exportado y otro cwd en un perfil temporal, nunca el real.
- [ ] Versión 0.1.4 coherente en manifiesto/proyecto/lock, sin dependencias nuevas.
  Actualizar mypy y ejecutar pruebas/lint/tipos en OpenCode; revisión independiente.

## Tarea 4: validación real, publicación local y evidencia

**Archivos:** crear `docs/validacion-orquestacion-opencode.md`; evidencias de cada
ejecución en `.aikit/`, sin credenciales ni transcripciones. Añadir enlace desde
la guía y el archivo de validación a la lista permitida del exportador.

**Consume:** política (1), contrato/validador (2), paquete e instaladores (3).

- [ ] En directorio aislado preparar especificación y prueba de un defecto
  conocido. Encargar a OpenCode una entrega inicial que lo contenga, marcada
  como fixture adversa. Otro OpenCode debe detectarlo y ejecutar la prueba que
  falla. Encargar corrección; un revisor independiente debe repetir comprobación
  y aprobar la nueva huella. No sembrar defectos en el producto real.
- [ ] Rechazar en la utilidad la aprobación antigua tras cambiar el archivo,
  la omisión de un check requerido y la evidencia de un autor que se declara revisor.
- [ ] Simular catálogo con Free insuficiente y Go suficiente: seleccionar Go y
  esfuerzo suficiente sin llamar al Free descartado. Simular ausencia de capacidad
  y ausencia de disponibilidad en opciones adecuadas: continuar la función en
  Codex, anunciar/registrar motivo y mantener revisión independiente. Conservar
  explícita la diferencia entre simulación de selección y validación real.
- [ ] Comprobar un subagente nativo como coordinador cuando lo exija el flujo,
  y el bloque routing junto a `go` fuera del repositorio. No afirmar que las
  sesiones de OpenCode son subagentes nativos ni que la política se impone sola.
- [ ] Revisor OpenCode de la entrega final ejecuta `uv sync --locked`,
  `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .` y
  `uv run mypy`; aporta comandos/salidas, hallazgos y snapshot. Codex comprueba
  esas evidencias; no repite el análisis técnico salvo retorno justificado.
- [ ] Con evidencias aceptadas, exportar limpio, actualizar complemento instalado
  con respaldo y aplicar routing al perfil real mediante su instalador. Verificar
  idempotencia y que `go` y ajustes ajenos permanecen intactos. La aprobación de
  ejecutar este plan incluye ese despliegue local conservador, no un push.
- [ ] Registrar resultados, entorno, modelos/esfuerzos, casos no cubiertos y
  límites. Si un caso falla, corregir antes de declarar la preferencia verificada.
  Guardar commits por tarea tras revisión; push solo con autorización del usuario.

## Autorrevisión del plan

La política corresponde al diseño aprobado; los cinco focos tienen pruebas
asignadas. El contrato y las firmas se definen una vez y las tareas posteriores
los consumen. No se añade selección automática ni se modifica el backend.
Las pruebas históricas no sustituyen la ejecución adversa y su revisión real.
El método ya elegido es implementación y verificación en OpenCode, con diseño
y coordinación de Codex y retorno nativo únicamente cuando proceda.

Estado: plan para revisión. Ningún paso de implementación se ha ejecutado todavía.
