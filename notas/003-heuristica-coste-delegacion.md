# Heurística rápida para decidir cuándo delegar

Fecha: 2026-10-30.
Estado: pendiente de debatir.

## Idea

Evaluar si hace falta lanzar un subagente, tanto de Codex como de OpenCode.
Si el coste total de delegar supera el de resolver la tarea directamente en
Codex, preferir la ejecución directa. Evitar la delegación mecánica.

Definir una heurística que permita decidir rápidamente entre ejecución local y
subagente, sin gastar tokens en una deliberación adicional para cada tarea.

## Para debatir después

- Qué significa coste: tokens, dinero, tiempo de arranque, contexto transferido,
  coordinación y revisión del resultado.
- Qué señales simples permiten resolver la decisión sin otra llamada a un modelo.
- Cómo considerar la complejidad, el aislamiento y la necesidad de revisión
  independiente, además del ahorro inmediato.
- Cómo encajar esta preferencia con las reglas actuales de delegación de AIKit.

Guardar esta nota no modifica las reglas actuales ni autoriza su implementación.
