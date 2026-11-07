# Inventario de contratos para la separación

Revisión estática del checkout principal, 2026-11-07. No se ejecutó Delegating
to OpenCode ni se inspeccionaron datos privados o estados reales. Los destinos
indicados son propuestas, no movimientos ya realizados.

## Empaquetado e identidad

| Fuente | Contrato observado | Consecuencia para la separación |
| --- | --- | --- |
| `plugin.json` | Identidad `aikit`, versión `0.2.1` e interfaz AIKit. | Diseñar identidades y versiones independientes antes de publicar. |
| `mcp.json` | Servidor `aikit-opencode`, ejecutado por `uv` desde `${PLUGIN_ROOT}` con extra `mcp`. | Mantener resolución portable y decidir compatibilidad del nombre anterior. |
| `scripts/build_plugin.py` | `PACKAGE_FILES` mezcla delegación, instaladores, configuraciones y documentos; exporta `aikit` en catálogo `aikit-local`. | Crear artefactos separados y permitir únicamente archivos de cada uno; no cambiar el exportador histórico a ciegas. |
| `tests/test_plugin_export.py` | Comprueba identidad, catálogo, manifestos, rutas e imports exportados. | Conservar la cobertura histórica mientras se añaden pruebas de aislamiento de cada distribución. |
| `pyproject.toml`, `uv.lock` | Proyecto `aikit`, extra MCP y rutas comunes de pytest/mypy. | Definir dependencias de desarrollo y de ejecución separables; actualizar el lock si cambia su configuración. |

## Configuración global y coordinación

| Fuente | Contrato observado | Destino o decisión |
| --- | --- | --- |
| `config/codex/go.md`, `scripts/install_go.py` | Bloque `AIKIT:GO`; instalador resuelve plantilla respecto a la raíz actual y respeta `CODEX_HOME`. | AIKit; preservar marcadores y comportamiento del bloque existente. |
| `config/codex/routing.md`, `scripts/install_routing.py` | Bloque `AIKIT:ROUTING` mezcla preferencias generales con instrucciones de OpenCode. | Delimitar su contenido antes de trasladarlo; no reinstalarlo automáticamente. |
| `scripts/global_instructions.py` | Motor usado por ambos instaladores; valida marcadores, rutas y respaldos en `backups/aikit`. | Mantener una sola implementación propietaria en AIKit; decidir la frontera de routing antes de reubicarla. |
| `tests/test_install_go.py`, `tests/test_install_routing.py` | Cubren instalación y coexistencia de los bloques, incluidos respaldos. | Conservar pruebas de coexistencia aunque los componentes se empaqueten por separado. |
| `scripts/review_evidence.py` | Exportado junto con la integración; su documentación lo vincula al contrato de revisión. | Examinar si el contrato es general antes de fijar propiedad; no duplicar. |

Las instrucciones globales efectivas pertenecen al usuario. La identidad de un
paquete no autoriza modificar o retirar bloques existentes. El bloque global
`go` se conserva; el routing global fue retirado anteriormente.

## Estado, sesiones y compatibilidad

- `service_identity.resolve_host_context()` exige `AIKIT_OPENCODE_REGISTRATION`
  y `AIKIT_STATE`, y usa `AIKIT_EXPECTED_OPENCODE_VERSION` con `2.2.0` como
  valor predeterminado. Es un contrato observado; su compatibilidad con cambios
  de versión debe estudiarse, no darse por garantizada.
- El estado de disponibilidad se identifica como `availability-state.json` bajo
  el estado configurado; los registros de host también usan `HostContext.aikit_state`.
  Las sesiones de proyecto y sus locks usan `.aikit/sessions` y
  `.aikit/session-locks` respectivamente. `.aikit/` está ignorado por Git.
- Renombrar rutas, variables, marcadores o el MCP puede desconectar información
  previa o crear instancias duplicadas. Mantener compatibilidad hasta diseñar y
  probar una migración explícita; no copiar, mover ni borrar datos reales como
  parte de esta revisión.
- `tests/conftest.py` importa módulos de la integración para fixtures; los tests
  no son automáticamente aislables solo por reorganizar carpetas.

## Primera unidad recomendada: artefacto aislado de `go`

Preparar una distribución de AIKit centrada en `go`, en una salida temporal,
sin activar instalaciones. Esta primera unidad incluiría la plantilla, el
instalador y su motor compartido, más las pruebas necesarias. Debe:

1. Preservar `AIKIT:GO`, el comportamiento existente y las instrucciones ajenas.
2. Probar instalación, repetición idempotente y coexistencia con un bloque
   routing ficticio usando un `CODEX_HOME` temporal; no escribir en el real.
3. Demostrar que el artefacto no contiene la skill, MCP, adaptador ni
   dependencias exclusivas de OpenCode y que funciona sin ellos.
4. Mantener el exportador histórico operativo hasta preparar su transición y
   no mover todavía el routing, las sesiones, el estado ni las notas.

Antes de implementarla, concretar el formato de ese artefacto y comprobar que
el mecanismo de distribución de Codex elegido admite sus archivos y su
instalación sin depender de la integración. Un artefacto aislado de `go` no
demuestra todavía que AIKit completo o la integración estén separados.

## Pendientes que no cambia este inventario

La nota 001 de disponibilidad, DEF-001 y las validaciones en vivo pendientes
siguen abiertos. La selección de tres candidatos continúa como requisito
pendiente. El registro `docs/pendientes.md` es histórico: su resultado de
instalación ENT-002 no implica que AIKit siga instalado tras su desinstalación.
La restricción de no utilizar Delegating to OpenCode sigue vigente hasta que el
usuario indique lo contrario.
