# Preferencia de autonomía para Git y GitHub

Fecha: 2026-11-15.
Estado inicial: Pendiente de debatir.

## Solicitud del usuario

Agregar a aikit-setup una preferencia configurable globalmente o para un
proyecto que permita al agente gestionar autónomamente las operaciones técnicas
de Git y GitHub. Elegir las opciones más adecuadas al uso y al estado de cada
proyecto, preservar la información y consultar al usuario únicamente cuando sea
estrictamente necesario. Evitar confirmaciones rutinarias que interrumpan el trabajo.

La autonomía debe abarcar el ciclo de trabajo con las herramientas disponibles:
estado e historial, ramas, commits, integración, worktrees, stash y operaciones
de colaboración en GitHub, según el alcance configurado. Estos ejemplos orientan
el diseño; no constituyen todavía una lista de operaciones habilitadas.

## Criterios para el diseño posterior

- Elección explícita en setup del ámbito global o local y posibilidad de
  conservar o desactivar la preferencia, respetando configuración ajena.
- Resolver decisiones técnicas con evidencia del proyecto y herramientas
  deterministas, manteniendo trabajo ajeno, cambios no integrados y evidencias
  ignoradas. Un estado Git limpio no acredita que sea seguro retirar una carpeta.
- Priorizar operaciones recuperables y preservar información antes de limpiar;
  comunicar los resultados y los pendientes sin preguntar entre pasos rutinarios.
- Definir qué hace estrictamente necesaria una consulta: decisión material que
  no pueda deducirse del contexto, información imprescindible ausente, o acción
  cuyo alcance y consecuencias excedan la autorización configurada.
- Concretar expresamente cómo se relaciona la preferencia con go y las reglas
  de acciones sensibles: push, publicación o exposición, borrados, reescritura
  de historial e integración remota. El objetivo es evitar fricción innecesaria,
  sin confundir autorización de trabajo técnico con decisiones de producto.
- Respetar las políticas y permisos efectivos de cada cliente y repositorio;
  la preferencia no permite eludir controles ni garantiza herramientas inexistentes.
- Coordinar responsabilidades: el coordinador protege los datos finales y las
  ramas principales; cada tarea gestiona su rama y solicita integración.
- No exigir Git o GitHub en proyectos que no los necesiten; aplicar la
  preferencia cuando estén presentes y sean pertinentes.

## Contexto y relaciones

Surge durante la revisión de seis worktrees y un stash: main limpio coexistía
con trabajo pendiente y evidencias fuera del seguimiento de Git. El usuario
quiere que el agente resuelva autónomamente esas operaciones técnicas,
preservando información y preguntando solo cuando sea indispensable.

- [019 — Go y acciones sensibles](019-go-autoriza-proxima-tarea.md).
- [025 — Coordinador global y chats autónomos](025-coordinador-global-chats-autonomos.md).
- [031 — Aislamiento sin Git](031-aislamiento-sin-git.md).
- [034 — Preferencias por lenguaje en setup](034-setup-preferencias-python-typescript.md).
- [037 — Captura de prácticas efectivas](037-captura-practicas-efectivas-aikit.md).

Esta entrega registra la preferencia solicitada para implementarla después;
no modifica setup ni activa ahora nuevas autorizaciones de Git/GitHub.
