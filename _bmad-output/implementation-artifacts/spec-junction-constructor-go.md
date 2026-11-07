---
title: 'Rechazo de junction en constructor go'
type: 'bugfix'
created: '2026-11-07'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** La CLI resuelve su ruta antes de inspeccionar la raíz, por lo que
acepta una junction del checkout, en contra del contrato.

**Approach:** Preservar la ruta sin resolver hasta validar sus componentes y
probar la CLI real, incluyendo junctions reales de Windows cuando se permitan.
Conservar todos los cambios previos y no instalar, hacer commit ni usar OpenCode.

</frozen-after-approval>

## Implementation Notes

- `SOURCE_ROOT` conserva la ruta léxica para detectar junctions antes de resolverla.
- Pruebas de CLI y junction real en origen y destino; omisión explícita si el
  sistema no permite crearlas. En Windows, con temporal bajo `.aikit/` y permisos
  adecuados, 34 pruebas del constructor e instalador pasaron sin omisiones.
- Ruff y formato correctos; mypy sin incidencias en los dos archivos.
- Revisión independiente sin defectos demostrables. No se hizo commit ni push.
