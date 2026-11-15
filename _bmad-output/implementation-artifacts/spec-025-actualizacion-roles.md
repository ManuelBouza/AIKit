---
title: 'Actualizar roles y selección de chats en coordinacion-chats'
type: 'feature'
created: '2026-11-15'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
---

<frozen-after-approval reason="human-owned intent">

## Intent

Actualizar en fuentes coordinacion-chats con los acuerdos de Manuel: un
coordinador dedicado a coordinación, implementación y revisión técnica delegadas,
y un mismo mecanismo de Chats de Tarea con propósito concreto o especializado.
El coordinador decide su creación/reutilización, documentando identidad, alcance,
estado y contexto; usa subagentes para apoyos de una sola ejecución. Comunicación
inicial mediante el coordinador; entre pares queda como posibilidad futura.

Incluir responsabilidades, selección/reutilización y traspasos, preservar avisos
y acuses, exportar los recursos y facilitar el descubrimiento y ruta de activación
local desde aikit-setup. Autoriza implementar y verificar en fuentes, con revisión
independiente, según docs/coordinacion/preparacion-actualizacion-skill.md.
No instalar, activar proyectos reales, crear chats, enviar mensajes, publicar,
hacer push ni implementar el bootstrap general, nuevos ciclos del auxiliar o
el control automático general de cobertura de la nota 039.

</frozen-after-approval>

## Implementation Notes

- bmad-help, catálogo y skill-creator consultados. Cambio acotado, sin lagunas
  de intención ni acciones irreversibles: ruta oneshot. El árbol previo contiene
  la preparación y decisiones elaboradas en esta conversación y ya autorizadas;
  se preservan, sin reset ni tratamiento como cambios ajenos por descartar.
  Base Git: fdbe3eb6b44c7404103526b46244488e29161077 en main.
- Investigación delegada a coord_skill_update: reutilizar skill actual y añadir
  references/responsabilidades.md; aclarar avisos.md y guías coordinador/tarea;
  entrada local en setup enlazada con la skill, sin flags nuevos ni requisitos
  de Git/Node para una activación manual. Selección/preparación sin asignación
  no debe exigir una tarea/ciclo inexistentes.
- Mapa: packaging/skills/coordinacion-chats/SKILL.md y references/avisos.md;
  nueva references/responsabilidades.md; packaging/skills/aikit-setup/SKILL.md;
  docs/coordinacion/coordinador.md y tarea.md; scripts/build_aikit.py y
  tests/test_build_aikit.py. Mantener esquema v1 y límites del auxiliar; sin
  duplicar transporte ni modificar Superpowers, BMAD o configuración ajena.
- Comprobar quick_validate en ambas skills, enlaces relativos, contenido exportado,
  pruebas de empaquetado y controles Python pertinentes. Evaluación independiente
  ficticia y revisión de la entrega; no equivalen al piloto real ni a instalación.
- La entrada de coordinación en setup es parte de esta entrega; el mecanismo
  general de cobertura de capacidades sigue pendiente en nota 039.
- Implementación delegada y terminada en los archivos previstos, con nueva
  references/responsabilidades.md. También se ajustó docs/coordinacion/flujo-avisos.md
  para distinguir las identidades del contrato manual y el esquema v1. Sin cambios
  de runtime, instalador o esquema de avisos. Caché habitual 0.1.1 preservada.

## Review Triage Log

Clasificación contrastada por el ejecutor; revisión técnica independiente por
roles_blind_review, con dictamen final accepted tras corregir R8. El coordinador
recoge el dictamen y sus evidencias sin repetir el code review.

| ID | Veredicto y evidencia de resolución |
| --- | --- |
| R1 | medium, corregido: controles y dictamen vinculados a la versión exacta de la entrega. |
| R2 | medium, corregido: conflictos o correcciones que alteran la entrega requieren revalidar la versión resultante. |
| R3 | medium, corregido: creación/recuperación incierta se reconcilia antes de reintentar o abrir manualmente. |
| R4 | medium, corregido: bootstrap limitado a contexto e identidad; ejecución después de asignación comprobada. |
| R5 | medium, corregido: Git por sí solo no habilita escritores simultáneos; aislamiento efectivo o secuencia. |
| R6 | medium, corregido: estructura manual mínima reutilizable y enlace desde setup. |
| R7 | medium, corregido: archivos aplicados/releídos distintos de reconocimiento en sesión destino. |
| F1 | low, corregido: confirmación inicial de avisos acotada a ejecución asignada/procesamiento, sin bloquear preparación. |
| R8 | medium, corregido: manual usa identificación/versionado acordados; v1 mantiene campos completos. Confirmado por revisión final independiente. |

No quedaron hallazgos diferidos ni requisitos nuevos fuera del alcance de esta
entrega. La actualización instalada y el piloto continúan pendientes.

## Validación

- Validador oficial quick_validate.py en ambas skills: código 0. PyYAML faltaba
  en el entorno; se usó overlay temporal de uv, sin modificar dependencias ni lock.
  Primer intento de descarga bloqueado por DNS; un intento acotado fuera del
  sandbox resolvió el acceso. No se alteraron permisos ni configuración global.
- Ruff check y format --check de scripts/build_aikit.py y tests/test_build_aikit.py:
  código 0, tras formato del test. mypy de esos dos archivos: código 0.
- pytest tests/test_build_aikit.py -q: 15 passed. Tras correcciones Markdown finales,
  test_export_and_install: 1 passed in 4.56s. No hubo otros cambios de código.
- Enlaces relativos comprobados y contenido exportado final íntegro; diff --check
  correcto. TypeScript sin cambios, sin repetición de sus controles.
- Evaluación independiente ficticia: seis casos sobre delegación, reutilización,
  setup manual, autoridad, envío incierto y preparación; addendum de los casos C/F
  tras aclarar bootstrap y reconocimiento. Sin efectos externos ni piloto real.
- Evidencia privada: .aikit/025-actualizacion-roles/validacion-ejecutor.md,
  triage-ejecutor.md, revision-final.md y evaluacion/forward-roles-independiente.md.
  No se distribuyen ni se incluyen en Git esas salidas temporales.
