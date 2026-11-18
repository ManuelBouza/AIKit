---
title: 'Contraste documental del Director de Ideas'
type: 'feature'
created: '2026-11-17'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent">

## Intent

**Problem:** La investigación inicial del Director de Ideas no exige contrastar la idea ya madurada antes de recomendar su materialización.

**Approach:** Incorporar un contraste documental proporcional a la idea y sus decisiones, con fuentes vigentes, comparación verificable y devolución de cambios materiales al usuario, conforme a la nota 040.

</frozen-after-approval>

## Implementation Notes

- `packaging/skills/director-de-ideas/SKILL.md` ya cubre contexto inicial, hechos y supuestos, proporcionalidad y autorización. Añadir la fase posterior sin duplicar esos principios ni exigir BMAD, Context7 o herramientas concretas; mantener su utilidad para ideas no técnicas.
- La nota `notas/040-director-ideas-contraste-documental.md` fija vigencia, fuentes primarias y especializadas pertinentes, compatibilidad, alternativas, límites y distinción entre hechos e inferencias. Reutilizar investigación vigente y devolver cambios materiales sin pedir aprobaciones entre pasos autorizados.
- BMAD Forge Idea y Deep Recon cubren exploración e investigación más amplia; no imponerlos ni duplicar sus flujos. Las preferencias de investigación y Context7 de este proyecto no están garantizadas en el entorno portable.
- Verificar estructura con `skill-creator` y escenarios de comportamiento, sin afirmar selección real. Revisión independiente sobre la versión exacta; no instalar, modificar setup, backlog ni registro canónico.
- Se añadió el contraste a la skill fuente. El validador estructural pasó con Python 3.13 y PyYAML disponible en el intérprete del sistema; los dos entornos virtuales examinados carecían de PyYAML. Los escenarios se evaluaron por lectura independiente, sin ejecución real.

## Review Triage Log

- Medio, corregido: la revisión detectó que no se distinguían explícitamente capacidades disponibles de experimentales; se incorporó esa distinción.
- Medio, corregido: la revisión detectó que la compatibilidad con herramientas existentes era implícita; se pide valorarla expresamente.
- Bajo, corregido: la revisión posterior señaló que la búsqueda de prácticas actuales y la justificación del enfoque eran implícitas; se explicitaron.
- Bajo, corregido: el análisis de escenarios señaló que la falta de acceso a fuentes no impedía afirmar un contraste completo; ahora exige declarar la limitación y la comprobación necesaria.
