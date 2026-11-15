# aikit-setup como centro de activación de capacidades

Fecha: 2026-11-15.
Estado inicial: Pendiente de debatir.

## Solicitud del usuario

Implementar un mecanismo que asegure que todas las preferencias y skills que
desarrollemos para AIKit queden incorporadas a aikit-setup. Debe ser el centro
desde el que el usuario descubre y activa cada capacidad, sin omisiones cuando
se añadan funcionalidades nuevas.

La necesidad surge porque coordinacion-chats está instalada y puede activarse
mediante una petición explícita, pero aikit-setup no ofrece todavía su activación.
El usuario indica que esta falta de integración no debe repetirse.

## Criterios para el diseño posterior

- Incluir la integración en setup como requisito de entrega de cada preferencia
  o skill propia de AIKit, tanto nueva como existente.
- Inventariar las capacidades distribuidas y contrastarlas con las que presenta
  setup, empezando por coordinacion-chats. Evitar mantener listas independientes
  que puedan divergir sin detectar la omisión.
- Definir un control automático de cobertura que detecte capacidades sin entrada
  o ruta de configuración en setup antes de dar por terminada una entrega.
- Presentar propósito, requisitos, estado de activación y ámbito permitido de
  cada capacidad. Respetar su naturaleza: la coordinación es local al proyecto;
  otras preferencias pueden admitir ámbito global, local o ambos.
- Distinguir instalación, disponibilidad de una skill y activación de una
  preferencia o mecanismo. Incluir activación, conservación, desactivación o
  revisión de configuración según proceda, sin activar capacidades por instalarlas.
- Reutilizar las skills y herramientas existentes desde setup; no duplicar su
  lógica ni convertir herramientas opcionales de terceros en requisitos generales.
- Conservar las decisiones del usuario, la configuración ajena y los permisos
  efectivos. Una entrada en setup no concede por sí sola nuevas autorizaciones.
- Documentar y verificar el recorrido completo desde setup hasta la activación
  efectiva y la comprobación de su estado; reflejar limitaciones reales.

## Relaciones y alcance

- [018 — Herramientas recomendadas en setup](018-herramientas-recomendadas-setup.md).
- [024 — Setup BMAD y patrón de integraciones](024-setup-bmad-patron-integraciones.md).
- [025 — Coordinador global y chats autónomos](025-coordinador-global-chats-autonomos.md).
- [034 — Preferencias por lenguaje en setup](034-setup-preferencias-python-typescript.md).
- [035 — aikit-help: guía de capacidades](035-aikit-help-guia-capacidades.md).
- [038 — Autonomía para Git y GitHub](038-autonomia-git-github-setup.md).

Esta nota registra el requisito para una implementación posterior. No modifica
aikit-setup, no activa capacidades ni da por elegido el diseño del mecanismo.
