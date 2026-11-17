---
title: Seguimiento local de ideas y tareas
type: feature
created: 2026-11-17
status: done
baseline_commit: 922b4bce01c6affb4a89ac7aba6838de0b629620
route: dispatch
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/specs/spec-seguimiento-ideas-tareas/SPEC.md'
---

<frozen-after-approval reason="alcance humano aprobado al elegir opción 1 y go de implementación">

## Intent

**Problem:** El tablero mezcla ideas con resúmenes de ejecución y no permite
seguir encargos independientes antes de implementarlos.

**Approach:** Implementar el contrato SPEC-seguimiento-ideas-tareas y sus dos
compañeros: tickets Markdown locales, vistas Ideas/Tareas conectadas, integración
en setup y migración inicial conservadora.

## Boundaries & Constraints

**Always:** Fuente canónica única por ticket bajo coordinacion; solo el
Coordinador escribe registros reales. Separar idea/tarea/chat, fase/atención/
autorización. Conservar notas, datos, permisos, originales y pruebas. Registrar
antes de implementar y generar antes de afirmar visibilidad. Arranque trazado
en coordinacion/implementacion-seguimiento-043.md mientras falta la nueva vista.
Reutilizar herramientas y dependencias existentes; controles deterministas.
028 confirmó ausencia de cambios y reserva del cambio funcional a 043.

**Never:** Ejecutar la preparación BMAD de worktrees, ampliar 028/040, instalar
en perfil, publicar o hacer push. No crear chats, conectores, servidor, editor
web ni framework. No imponer Python/BMAD/Git al usuario portable. No modificar
el contrato bmad-spec fuera de su memoria y derivación.

## I/O & Edge-Case Matrix

| Escenario | Entrada | Resultado | Error |
| --- | --- | --- | --- |
| Alta | Encargo directo sin idea | Ticket identificado y visible sin permiso implícito | No implementar si falta registro/vista |
| Relaciones | Una idea con varias entregas | Enlaces inversos derivados; estados independientes | Rechazar enlaces inválidos y ciclos |
| Contenido | Metadata, rutas o Markdown hostiles | Validación estricta y representación segura | Conservar última salida válida |
| Migración | 028/040/BMAD y repetición | Estados contrastados, sin duplicados ni trabajo implícito | Conservar preestado y escrituras parciales |
| Setup | Proyecto existente o herramienta ausente | Reutilizar fuente y explicar límites verificables | No declarar activación o sincronización inexistente |

</frozen-after-approval>

## Code Map

- scripts/tablero_notas.py: read_notes/generate y publicación atómica existentes.
- scripts/tablero_notas.html: filtros y detalle seguro; conservar estilo de 028.
- scripts/seguimiento_tareas.py: nuevo lector/validador sin mutación de registros.
- tests/test_tablero_notas.py y nuevo test_seguimiento_tareas.py: invariantes y errores.
- packaging/skills/coordinacion-chats y aikit-setup: roles/avisos/activación ya cubiertos; falta seguimiento.
- scripts/build_aikit.py: allowlist explícita; tests/test_build_aikit.py comprueba exportación.
- docs/tablero-notas.md: fuentes, generación y límites de instantánea.

## Tasks & Acceptance

**Execution:**
- [x] scripts/seguimiento_tareas.py y tests/test_seguimiento_tareas.py: contrato estricto de datos y relaciones.
- [x] scripts/tablero_notas.py/html y pruebas de tablero/DOM ficticio: vistas conectadas y fallo seguro compatible.
- [x] packaging/skills/coordinacion-chats/references/seguimiento.md y callers/setup: registro previo y activación honesta.
- [x] scripts/build_aikit.py y tests/test_build_aikit.py: distribuir referencia reutilizada sin copiar runtime del proyecto.
- [x] docs/tablero-notas.md y evidencia de comportamiento: documentar y demostrar consulta local.
- [x] coordinacion/tareas y registros existentes: Coordinador simula, respalda y migra 028/040/BMAD y este encargo sin duplicados.

**Acceptance Criteria:**
- Given un encargo nuevo autorizado, when se registra, then es visible antes de implementar sin inventar idea.
- Given una idea y varios tickets, when se consulta, then aparecen relaciones y estados independientes.
- Given datos inválidos o un fallo al publicar, when se genera, then retorna error y preserva bytes de la última vista.
- Given cambios humanos posteriores al snapshot, when se migra, then conserva estado vigente sin reanudar por accidente.
- Given un proyecto con tracker o sin herramientas de generación, when setup prepara seguimiento, then no duplica fuente ni declara capacidades no verificadas.

## Implementation Notes

Implementación delegada en seguimiento043_builder; revisión en tres capas y
triage independiente. Candidato corregido aceptado por seguimiento043_edge;
evidencia de checks, fuentes y límites en docs/validacion-seguimiento-043.md.
Verificación conjunta final: 988 pruebas aprobadas, incluida DOM; Ruff lint y
formato correctos; mypy global (74 archivos) y dos módulos explícitos correctos.
Migración real del Coordinador: cuatro tickets, vista generada y repetición de
inventario sin altas; procedimiento reproducible en coordinacion/MIGRACION-043.md.

Investigación delegada: Python/Mistune y JSON estándar cubren parsing/publicación;
Playwright aislado ya instalado permite comprobar DOM. Skills existentes cubren
coordinación y setup; se amplían sin nueva skill ni flags. La migración escribe
solo nuevos tickets y enlaces, con copia previa; no es irreversible ni externa.
No hay decisiones materiales abiertas. Alcance único transversal autorizado;
el contrato funcional ya fue formalizado y aprobado para implementar.

## Spec Change Log

## Review Triage Log

Triage técnico independiente realizado por seguimiento043_edge tras recibir las
tres revisiones; el Coordinador conserva sus evidencias y rutas. Cada hallazgo
se clasificó antes de agrupar duplicados.

| Origen | Veredicto | Evidencia y decisión |
| --- | --- | --- |
| B1 | high | Fixture con raíz canónica distinta admitido; contrastar raíz del contrato antes de publicar. Patch. |
| B2 | medium | Seguimiento activo con carpeta ausente devuelve lista vacía; fallar conservando salida. Patch. |
| B3 | medium | Offset +00:99 normalizado por fromisoformat; validar límites RFC3339. Patch. |
| B4 | medium | Encabezados solo dentro de fence indentado aceptados; excluir código al extraer secciones. Patch. |
| B5 | maybe-false | Campo motivo vacío no demuestra pérdida: contrato permite razón en Historial/autorización. No endurecer metadata sin requisito; rechazado como obligación no acreditada. |
| B6 | low | Cadena válida de unos 1010 tickets produce RecursionError; recorrido iterativo sin nueva superficie. Patch. |
| B7 | low | Filtrar excluye tarjeta pero conserva detalle seleccionado; reconciliar selección ante cambio de filtros. Patch. |
| B8 | false | Navegación explícita sí muestra destino en detalle; contrato no exige borrar filtros. Conservar comportamiento. |
| B9 | low | Registro de arranque duplicaba estado; Coordinador ya lo convirtió en contexto con enlace canónico. Corregido. |
| B10 | low | Migración manual prevista; faltaba evidencia reproducible de repetición con cambios posteriores. Procedimiento añadido a MIGRACION-043.md, sin inventar migrador automático. |
| E1 | medium | Reproducción de fecha igual a B3; agrupar tras clasificar. Patch. |
| E2 | medium | Reproducción de fence igual a B4; agrupar tras clasificar. Patch. |
| E3 | low | Selección obsoleta igual a B7; agrupar tras clasificar. Patch. |
| G1 | medium | DOM privado sobre datos reales no es regresión compartida; publicar prueba reproducible con fixtures ficticios y ruta documentada. Patch. |
| G2 | medium | Guard de enlace externo sin regresión; probar rechazo y conservación de HTML con enlace aislado. Patch. |

Grupos: B3/E1, B4/E2, B7/E3. Resto independiente. No hay cambio de intención
ni de contrato público; correcciones acotadas de guardas y pruebas sobre estados
reproducidos. Evaluación de instrucciones en proyecto vacío, encargo nuevo y
tracker externo conserva activación explícita, autonomía y fuente única.

## Verification

- uv run --locked pytest tests/test_seguimiento_tareas.py tests/test_tablero_notas.py tests/test_build_aikit.py: comportamientos y compatibilidad.
- uv run --locked ruff check . y ruff format --check .: calidad Python.
- uv run --locked mypy y control explícito de módulos nuevos: tipos.
- quick_validate.py para las dos skills modificadas y exportación aislada: estructura y recursos.
- Playwright aislado: vistas, filtros, relaciones, teclado y ausencia de cargas externas.
- Simulación, migración y segunda ejecución: estados conservados y cero altas duplicadas.
