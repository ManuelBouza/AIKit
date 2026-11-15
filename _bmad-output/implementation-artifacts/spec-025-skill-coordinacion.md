---
title: 'Skill portable de avisos y acuses'
type: 'chore'
created: '2026-11-15'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
---

<frozen-after-approval reason="human-owned intent">

## Intent

Empaquetar las instrucciones de coordinación como skill autocontenida en fuentes,
validar su comportamiento y revisar el resultado. Autorizado por los go del usuario;
no instalar ni activar la skill, ni distribuir el auxiliar como producto terminado.

</frozen-after-approval>

## Implementation Notes

- Reutiliza las guías de docs/coordinacion, el contrato y las capacidades nativas;
  no duplica transporte, subagentes, BMAD ni scripts de almacenamiento. Skill-creator
  y catálogo bmad-help consultados. Continúa el alcance documental mediante oneshot.
- Fuentes: packaging/skills/coordinacion-chats/SKILL.md y references/avisos.md.
  No incluye rutas privadas, dependencias de runtime ni enlaces fuera del paquete.
- Validación estructural con quick_validate.py. Revisión independiente y evaluación
  textual de cuatro escenarios mediante subagentes, sin mensajes o mutaciones reales.
  La prueba textual no acredita activación ni integración del cliente.

## Review Triage Log

- medium, corregido: raíz ambigua. Se exige configuración verificada y ruta
  absoluta, sin deducirla del mensaje o worktree.
- medium, corregido: origen del acuse omitido. Se exige canónico o referencia
  comprobable y se excluyen índices derivados como prueba de incorporación.
- medium, corregido: limpieza antes de integración. Se exige esperar y verificar
  la integración requerida antes de retirar sus recursos.
- low, corregido: revisión sin ámbito. Se precisa tarea/ciclo y fechas informativas.
- medium, corregido: modalidad manual indefinida. Se exige formato y límites
  acordados y se prohíbe simular el auxiliar con edición libre de documentos v1.

## Validación

- quick_validate.py: correcto. Enlace interno de SKILL.md comprobado.
- Evaluación independiente textual de cuatro escenarios: no se confundió envío
  con incorporación, no se ejecutaron instrucciones del resumen sin origen,
  no se aceptó duplicado de recibo pendiente como aplicado y se propuso secuencia
  sin Git/Node. El caso de limpieza se evaluó antes de la corrección de integración:
  esa condición quedó reforzada por el hallazgo independiente, sin atribuir a la
  primera evaluación una comprobación posterior.
- git diff --check correcto. No se ejecutaron mensajes ni se instaló la skill.
  La fuente queda lista para una prueba aislada de carga; no está incorporada al
  exportador histórico del complemento, que usa una lista explícita de archivos.
