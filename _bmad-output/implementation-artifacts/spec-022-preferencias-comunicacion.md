---
title: 'Preferencias opcionales de comunicación'
type: 'feature'
created: '2026-11-13'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '158dbc1fe61fc826cb8c9a9782a218d5758dd4be'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Las preferencias de Manuel sobre estilo al escribir y autorización
previa para visualizaciones aún no pueden configurarse mediante AIKit.

**Approach:** Integrar dos preferencias opcionales e independientes en el
instalador y exportador existentes, sin duplicar ni requerir skills externas.

## Boundaries & Constraints

**Always:** Escritura en nombre del usuario para terceros sigue su estilo salvo
indicación distinta; usa `write-like-me` si está disponible y no inventa muestras.
Proponer `visualize` y esperar autorización si el usuario no lo solicitó; una
petición expresa ya autoriza la visualización dentro del alcance. Selección
independiente de cada preferencia; ámbito global o proyecto; vista previa,
respaldo, idempotencia, conservación de contenido ajeno y validación de marcadores.
Usar perfiles ficticios para pruebas. Respetar instrucciones de mayor prioridad.

**Never:** Instalar o activar complementos de terceros, usar OpenCode, cambiar
configuración real, publicar o modificar skills de terceros. La aprobación de
esta tarea no autoriza instalar las preferencias en el perfil real.

## I/O & Edge-Case Matrix

| Caso | Entrada | Resultado |
| --- | --- | --- |
| Sin opciones | Instalación existente | Preserva preferencias opcionales sin añadirlas ni borrarlas. |
| Una o ambas | Selección explícita | Añade o actualiza solo las seleccionadas, además de bloques base. |
| Vista previa | Opciones elegidas | Muestra cambios sin escribir. |
| Repetición | Mismas opciones | `unchanged` sin respaldo adicional. |
| Marcadores inválidos | Duplicados o cruzados | Error sin modificar destino. |

</frozen-after-approval>

## Code Map

- `packages/aikit-installer/src/cli.ts`: `validateCrossed`, opciones, bucle de
  bloques, vista previa, status y escritura atómica con respaldo existentes.
- `packages/aikit-installer/templates/`, `config/codex/`: copias idénticas de
  plantillas; no reescribir preferencias anteriores.
- `scripts/build_aikit.py`: lista explícita y comprobación de igualdad; exportar
  ambas copias nuevas y mantener fallos anticipados por divergencia.
- `packaging/skills/aikit-setup/SKILL.md`: coordina alcance y vista previa; debe
  aceptar elecciones explícitas e indagar solo las preferencias no decididas.
- `packages/aikit-installer/test/install.test.cjs`, `tests/test_build_aikit.py`:
  pruebas existentes de instalación y exportación.

## Tasks & Acceptance

**Execution:**
- [x] Añadir plantillas de escritura y visualización con marcadores distintos.
- [x] Extender CLI con `--escritura` y `--visualizacion` independientes;
  validar marcadores opcionales incluso cuando no estén seleccionados.
- [x] Extender constructor, skill de setup y documentación sin alterar terceros.
- [x] Probar combinaciones, ámbitos, errores, preservación e idempotencia con
  perfiles ficticios; revisar y comprobar que no se haya modificado perfil real.

**Acceptance Criteria:**
- Dado setup explícito, cuando se elige una preferencia, solo esa preferencia
  opcional se añade; la otra conserva su estado previo.
- Dado un proyecto sin una skill externa, cuando se leen las instrucciones,
  no se exige su instalación y el comportamiento sigue siendo útil.
- Dado un perfil con texto ajeno, cuando se instala y repite, el texto y los
  bloques ajenos se conservan y la repetición no produce cambios.

## Implementation Notes

Se probaron perfiles ficticios: 40 pruebas Node aprobadas y dos omitidas por
junctions; 15 pruebas de exportación aprobadas. No se modificó el perfil real.

## Spec Change Log

## Review Triage Log

- medium, corregido: setup debe aclarar que una negativa no desactiva un bloque
  existente; ahora indica informar tras examinar la vista previa.
- medium, corregido: faltaba probar preservación del bloque de escritura al
  omitir su opción; se añadieron casos con y sin opción de visualización.
- false: ampliar autorización a cualquier medio gráfico excedería la preferencia
  acordada, referida a la skill `visualize`.
- No se validó una conversación real ni el comportamiento de setup en otro cliente.

## Verification

`npm test` en `packages/aikit-installer`; pytest de `tests/test_build_aikit.py`;
pruebas focalizadas de combinaciones y validación de exportación. Registrar
limitaciones de pruebas conversacionales y de uso efectivo en clientes.
