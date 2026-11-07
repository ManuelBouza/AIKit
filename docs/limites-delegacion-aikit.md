# Límites entre Delegating to OpenCode y AIKit

Decisión actual del usuario: AIKit y Delegating to OpenCode continuarán en este
repositorio como componentes independientes. AIKit podrá utilizar la delegación
como integración opcional. Esta decisión sustituye la propuesta anterior de
desarrollar AIKit en otro proyecto y no implica que la separación física o la
migración ya estén hechas. Véase el [plan](plan-monorepositorio.md).

## Delegating to OpenCode

Responsable de conectar un coordinador compatible con OpenCode, sin sustituir
sus roles ni interceptar subagentes. Sus funciones incluyen:

- Ejecutar encargos mediante la skill, la CLI y el MCP; comunicar resultados,
  errores, costes conocidos y límites, sin inventar datos desconocidos.
- Descubrir proveedores y modelos conectados; mantener la tabla compartida de
  disponibilidad, variantes, precios, fuentes, caducidad y rendimiento observado.
- Exponer datos y mecanismos de selección de modelo y esfuerzo apropiados para
  una tarea; respetar las preferencias y restricciones del coordinador. La
  selección determinista de tres candidatos es un requisito pendiente, no una
  capacidad que se dé aquí por terminada.
- Gestionar sesiones, supervisión, espera, reconciliación y recuperación con
  sus identificadores, evitando duplicar ejecuciones y preservando el contexto.
- Aplicar las restricciones configuradas para la integración, proteger datos y
  ofrecer diagnóstico, pruebas, documentación e instalación independientes.

La programación diaria para actualizar la tabla, el contraste de fuentes públicas
y la recuperación desatendida pertenecen al alcance de disponibilidad de la
integración; su estado y las dependencias de Codex deben verificarse antes de
afirmar que funcionan.

## AIKit

Responsable de la forma de trabajo y las preferencias generales reutilizables:

- Distribuir configuraciones y skills propias, y gestionar su instalación,
  actualización y retirada sin alterar configuraciones ajenas.
- Mantener el mecanismo general `go` y, si se decide desarrollarlo, el método
  del Director de Ideas y otras capacidades generales.
- Definir preferencias generales de coordinación, elección entre herramientas,
  privacidad y revisión, sin duplicar procedimientos de una integración.
- Descubrir y utilizar capacidades instaladas, incluida la delegación a OpenCode,
  sin exigirla para funcionar y respetando otras skills y subagentes.

## Frontera de colaboración

AIKit o cualquier otro coordinador decide el encargo, las políticas aplicables
y la aceptación del resultado. La integración informa de opciones y ejecuta
conforme al contrato y las restricciones recibidas. La política de cuándo
delegar es del coordinador; el funcionamiento de OpenCode y su disponibilidad
son de la integración. Las reglas específicas de proveedor no deben convertirse
en condiciones ocultas para todas las herramientas de AIKit.

La configuración global `AGENTS.md` pertenece al usuario: AIKit solo debe
gestionar bloques propios cuando se autorice. Un `AGENTS.md` de proyecto define
el comportamiento local y no instala ni activa por sí solo la integración.

## Inventario y migración pendiente

| Elemento actual | Destino previsto | Estado |
| --- | --- | --- |
| `skills/delegating-to-opencode/`, adaptador, MCP y sus pruebas | Delegating to OpenCode | Permanecen en este repositorio. |
| Tabla, sesiones, supervisor y sus documentos y pruebas | Delegating to OpenCode | Permanecen; verificar cada entrega pendiente. |
| `config/codex/go.md`, `scripts/install_go.py` y sus pruebas | AIKit o mecanismo global independiente | Decidir traslado; `go` global existente se conserva. |
| `config/codex/routing.md` y `scripts/install_routing.py` | Dividir políticas generales y configuración específica de OpenCode | Revisar contenido y destinatario antes de mover. |
| `scripts/build_plugin.py`, manifiestos e instalación | Cada proyecto mantiene su propio empaquetado | Revisar y separar; hoy están acoplados. |
| Nota 009, Director de Ideas | AIKit | Idea pendiente de desarrollo. |
| Notas 001–006 y 008, 010–011 | Mayoritariamente integración OpenCode | Revisar caso por caso; criterios generales pueden pertenecer a AIKit. |
| Nota 007, separación | Ambos proyectos | Decisión de alcance tomada; migración pendiente. |

La nota 001 de disponibilidad sigue incompleta; DEF-001 del supervisor y las
validaciones en vivo pendientes no se cierran por esta decisión. El registro
histórico de pendientes y sus evidencias debe conservarse durante la migración.
La ubicación, distribución, versiones y compatibilidad de ambos componentes,
así como el traslado de notas y archivos, requieren concretarse. Los
documentos e instrucciones anteriores aún pueden describir el alcance antiguo.
