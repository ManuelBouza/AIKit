---
title: 'Preparar complemento AIKit independiente'
type: 'feature'
created: '2026-11-07'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'b799b12e6433ef4e5ea5a72d30253cee29377a36'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** El complemento histórico mezcla preferencias generales y OpenCode. AIKit necesita una distribución independiente con las preferencias ya aprobadas.

**Approach:** Preparar un paquete AIKit con las instrucciones `go` existentes y la preferencia Context7, sin dependencia de Delegating to OpenCode. Probar la instalación explícita de sus bloques en perfiles ficticios; la instalación global automática al liberar el complemento permanece pendiente de verificar.

## Boundaries & Constraints

**Always:** Preservar el complemento histórico, la configuración y el contenido ajenos; reutilizar el bloque `AIKIT:GO` y sus instaladores existentes. La preferencia Context7: priorizarla para documentación técnica actualizada cuando esté disponible, comprobar versión y recurrir a documentación oficial u otras fuentes primarias si no cubre la consulta, respetando las fuentes y restricciones del usuario. Probar exclusivamente perfiles temporales ficticios. No invocar Delegating to OpenCode.

**Never:** Modificar perfiles reales, prometer instalación global automática o retirada selectiva verificadas, instalar MCP de OpenCode, sustituir el paquete histórico, ni duplicar skills existentes. No crear una nueva skill de onboarding sin una necesidad demostrada y sin explorar las capacidades instaladas y las instrucciones de creación.

## I/O & Edge-Case Matrix

| Escenario | Entrada | Comportamiento esperado | Error |
| --- | --- | --- | --- |
| Exportar | Destino nuevo | Paquete y catálogo independientes con dos preferencias, sin MCP ni skill de OpenCode | Informar errores antes de exportar |
| Destino existente | Archivo o directorio | No sobrescribir ni borrar | Fallar |
| Instalación explícita | Perfil ficticio con contenido ajeno y bloque go | Añadir Context7 conservando texto y go; repetir sin cambios | Rechazar marcadores u override conflictivos |
| Perfil vacío | Perfil ficticio nuevo | Permitir instalar go y Context7 mediante pasos explícitos | Indicar error si una operación falla |
| Cliente | Instalar paquete en perfil aislado | Comprobar instalación del paquete y comunicar que instalarlo no modifica por sí mismo AGENTS.md | No declarar completada la escritura automática |

</frozen-after-approval>

## Code Map

- `scripts/build_go.py` y `tests/test_build_go.py`: exportador allowlist, tratamiento de symlinks y junctions, destino nuevo; reutilizar.
- `config/codex/go.md`, `scripts/install_go.py`, `scripts/global_instructions.py` y `tests/test_install_go.py`: bloque canónico e instalación idempotente con respaldo y preservación de contenido; no alterar contrato histórico.
- `C:/Manuel/Projects/AIKit/AGENTS.md`: preferencia Context7 local aprobada; trasladar solo esa preferencia a plantilla propia.
- `C:/Manuel/Projects/AIKit/_bmad-output/specs/spec-complementos-independientes/instalacion-y-migracion.md`: prueba de que instalación CLI no escribe automáticamente AGENTS y limitaciones del onboarding.
- `scripts/build_plugin.py`, `plugin.json`, `mcp.json`: paquete histórico; conservar sin cambios.

## Tasks & Acceptance

**Execution:**
- [ ] `config/codex/` y `scripts/` — añadir bloque Context7 e instalación explícita idempotente que reutilice motor de bloques, y constructor AIKit independiente seguro.
- [ ] `packaging/` — definir manifiesto y catálogo sin MCP de delegación; preservar identidad histórica y advertir sobre coexistencia no validada.
- [ ] `tests/` — comprobar exportación, exclusiones, destino ocupado, instalación, idempotencia, marcadores, override y conservación del contenido ajeno usando perfiles ficticios.
- [ ] `docs/` — documentar pasos explícitos, límites de instalación global automática, desinstalación y migración pendientes.
- [ ] `_bmad-output/implementation-artifacts/` — registrar validación y limitaciones sin datos privados.

**Acceptance Criteria:**
- Dado un destino nuevo, al exportar AIKit, el artefacto contiene go y Context7 sin incluir MCP ni código de OpenCode.
- Dado un perfil aislado con instrucciones ajenas y go existente, al instalar Context7 dos veces se conserva lo previo y la segunda ejecución no modifica el archivo.
- Dado el complemento histórico, al ejecutar sus pruebas, el constructor histórico continúa funcionando.
- Dado un perfil ficticio, la documentación distingue instalar el complemento de instalar las instrucciones en AGENTS.md y no afirma automatización sin evidencia.

## Implementation Notes

## Spec Change Log

## Review Triage Log

- `medium`: faltaban instrucciones de registro e instalación del catálogo;
  añadidas con un perfil ficticio y rutas absolutas.
- `medium`: el README exportado podía sugerir que el constructor se distribuye;
  ahora indica que se ejecuta desde el repositorio fuente.
- `false`: el instalador admite el perfil global por defecto, pero el requisito
  de usar perfiles ficticios restringe estas pruebas, no el uso futuro del producto.
- `medium`: el motor reutilizado no rechazaba junctions de Windows; ahora rechaza
  puntos de reanálisis y se probó el caso simulado sin tocar perfiles reales.
- `medium`: la prueba CLI de instalación es manual, no automatizada; queda
  documentada con su versión y limitaciones, sin presentarla como test continuo.
- `medium`: faltaban pruebas propias del exportador ante rutas enlazadas; añadidas
  para origen y destino.
- `medium`: faltaba contrastar que la ruta del catálogo apunta al manifiesto;
  añadida la comprobación en la prueba de exportación.

Revisión posterior: 55 pruebas aprobadas y 2 omitidas por permisos para crear
junctions reales; Ruff y mypy aprobados. No se invocó OpenCode ni se modificó
el perfil real. La instalación global automática y la retirada selectiva siguen
pendientes de verificar y no son resultados de este paquete preparado.

## Verification

Ejecutar pruebas pertinentes, Ruff y mypy. Si se prueba Codex CLI, usar CODEX_HOME ficticio y no iniciar sesiones de modelo ni OpenCode. Registrar versión y resultados. La evidencia no implica compatibilidad en clientes no probados.
