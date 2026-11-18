---
title: 'Modernizar el tablero de ideas y tareas'
type: 'feature'
created: '2026-11-18'
status: 'done'
route: 'dispatch'
baseline_commit: '36cbde57eff20dde73a968e44665957178e4aaa0'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problema:** La consulta del tablero resulta fría y el detalle bajo las columnas dificulta su lectura.

**Solución:** Modernizar jerarquía, tarjetas y controles; abrir ideas y tareas en un diálogo centrado accesible, adaptable a pantallas pequeñas.

## Boundaries & Constraints

**Siempre:** Conservar fuentes Markdown, generación local segura, vistas Ideas/Tareas, filtros, referencias y navegación entre relaciones del contrato 043. Mantener claridad de secciones históricas y estados literales.

**Nunca:** Instalar herramientas, publicar, integrar en main, añadir conexiones externas o convertir el tablero en editor. Sites queda fuera.

## I/O & Edge-Case Matrix

| Escenario | Entrada / estado | Resultado esperado | Manejo |
|---|---|---|---|
| Abrir | Activar tarjeta de idea o tarea | Diálogo centrado con título y contenido | Foco inicial en título |
| Navegar relaciones | Elegir idea, tarea o dependencia en detalle | Mantener filtros y mostrar destino en el diálogo | Si cambia la vista, conservar navegación |
| Cerrar | Escape o botón cerrar | Cerrar diálogo y devolver foco al origen | Si el origen desapareció, enfocar control lógico |
| Pantalla estrecha | Ancho 320 CSS px o zoom | Contenido accesible en una columna | Desbordamiento localizado en contenido ancho |
| Sin coincidencias | Filtro sin resultados | Mensaje claro y forma de limpiar | No perder datos |

</frozen-after-approval>

## Code Map

- `scripts/tablero_notas.html`: estilos, vistas, filtros, tarjetas y detalle; conservar CSP y relaciones de `showNote` y `showTask`.
- `scripts/tablero_notas.py`: render seguro y publicación atómica; no alterar sin necesidad.
- `tests/test_tablero_notas_dom.py`: pruebas de filtros, relaciones y ausencia de red; adaptar interacción modal y comprobar foco.
- `tests/test_tablero_notas.py`: cobertura del generador y protección ante fallo.
- `docs/tablero-notas.md`: documentar interacción y validación sin exigir dependencias nuevas al usuario.
- `_bmad-output/specs/spec-seguimiento-ideas-tareas/`: contrato funcional 043, conservado.

## Tasks & Acceptance

**Execution:**
- [x] `scripts/tablero_notas.html` -- rediseñar cabecera, controles, tarjetas y diálogo accesible conservando el comportamiento existente.
- [x] `tests/test_tablero_notas_dom.py` -- verificar relaciones, filtros y ciclo de foco del diálogo en escritorio y móvil.
- [x] `docs/tablero-notas.md` -- explicar el detalle centrado, teclado y alcance de búsqueda.
- [x] Ejecutar controles pertinentes y comprobación visual con datos ficticios.

**Acceptance Criteria:**
- Dado un tablero generado, al alternar vistas y aplicar filtros, se conservan datos y filtros de cada vista según el contrato previo.
- Dada una idea o tarea abierta, al navegar relaciones, se presenta el destino sin borrar los filtros.
- Dado un diálogo abierto, al usar teclado o cierre visible, el foco permanece utilizable y vuelve a un lugar lógico.
- Dado un dispositivo estrecho, al consultar tarjetas y detalle, el contenido se adapta y conserva funcionalidad.
- Dado contenido de fuentes, al generar y consultar, no se realizan conexiones externas ni se debilitan las comprobaciones de seguridad.

## Implementation Notes

Implementado diálogo nativo, tarjetas, contadores, filtros y navegación entre relaciones. Se preservan filtros de la vista opuesta y se distingue una colección vacía de una búsqueda sin coincidencias. Validación con Edge y datos ficticios en 1280 y 320 px; Python 3.14.9 y Playwright existentes. Controles focales: 54 aprobadas, sin omisiones; Ruff correcto en el test modificado. Las tres revisiones detectaron las mejoras registradas abajo y se aplicaron las correcciones.

## Spec Change Log

## Review Triage Log

- **Bajo, conservar:** al reconstruirse la tarjeta original durante navegación de relaciones, el foco vuelve al selector de vista. Es el fallback previsto cuando el nodo invocador ya no existe; no se promete mantener identidad visual tras reconstruir.
- **Medio, corregir:** limpiar filtros eliminaba también filtros ocultos de la otra vista, alterando el contexto conservado.
- **Bajo, corregir:** una colección sin tareas se presentaba como filtro sin coincidencias y ofrecía una acción inútil.
- **Medio, corregir:** la prueba no ejercitaba Tab ni Shift+Tab; tampoco validaba contenido ancho en el diálogo a 320 px ni limpieza desde Ideas. Los hallazgos de foco de las tres revisiones coinciden en este déficit.
- **Medio, corregir documentación:** la ruta habitual puede omitir Playwright. La entrega exige ejecución sin omisiones; se documentará cómo exigirla sin instalar componentes, fuera del alcance de cambiar la verificación general.

## Verification

- `uv run --locked pytest tests/test_tablero_notas.py tests/test_seguimiento_tareas.py tests/test_tablero_notas_dom.py` -- controles focales correctos; DOM sin omisión cuando Playwright esté disponible.
- Comprobar visualmente escritorio y móvil, navegación con teclado y errores del navegador.
