# aikit-setup como centro de activación de capacidades

Fecha: 2026-11-15.
Estado inicial: Pendiente de debatir.
Estado actual: Integrada en fuentes; validación de interfaz pendiente.

## Solicitud del usuario

Implementar un mecanismo que asegure que todas las preferencias y skills que
desarrollemos para AIKit queden incorporadas a aikit-setup. Debe ser el centro
desde el que el usuario descubre y activa cada capacidad, sin omisiones cuando
se añadan funcionalidades nuevas.

La necesidad surgió al detectar una capacidad distribuida sin una ruta en setup.
El inventario y el control de cobertura se conservan para las capacidades
vigentes del complemento. El 2026-11-22 se retiraron los flujos de coordinación.

## Alcance acordado el 2026-11-18

- Mantener un inventario estructurado de las capacidades propias distribuidas,
  sus propósitos y su tratamiento en setup, incluidas las que no requieren
  configuración. Definir su ubicación y conexión con las pruebas durante el diseño.
- Usar setup como centro de descubrimiento y configuración: explicar disponibilidad,
  requisitos, ámbitos, configuración y comprobación del estado cuando corresponda.
  Instalar, tener disponible y activar son estados distintos.
- Comprobar automáticamente la cobertura antes de entregar: detectar capacidades
  distribuidas sin entrada o tratamiento explícito y referencias o rutas declaradas
  inexistentes. Complementar el control con pruebas del recorrido real; una
  referencia existente por sí sola no demuestra que el flujo funcione.
- Guiar hacia los flujos especializados existentes sin duplicar su lógica ni imponer
  herramientas opcionales. Por ejemplo, presentar el Director de Ideas sin inventar
  un interruptor que no necesite.
- Respetar configuración, decisiones y permisos existentes. El inventario y setup
  no activan capacidades ni conceden autorizaciones por sí mismos.

## Contraste documental

La documentación de OpenAI describe las [skills como instrucciones y recursos
reutilizables](https://developers.openai.com/plugins/concepts/skills) y el
[empaquetado del complemento](https://developers.openai.com/plugins/build/plugins)
como mecanismo de distribución. Esto respalda mantener separadas disponibilidad,
configuración y uso, sin concluir que instalar equivalga a activar una preferencia.
OpenAI también recomienda [evaluar sistemáticamente las skills](https://developers.openai.com/blog/eval-skills),
lo que respalda complementar la cobertura automática con pruebas de comportamiento.
El inventario estructurado y su control son una propuesta de AIKit, no una
funcionalidad garantizada por esas fuentes.

## Criterios para el diseño posterior

- Incluir la integración en setup como requisito de entrega de cada preferencia
  o skill propia de AIKit, tanto nueva como existente.
- Inventariar las capacidades distribuidas y contrastarlas con las que presenta
  setup. Evitar mantener listas independientes
  que puedan divergir sin detectar la omisión.
- Definir un control automático de cobertura que detecte capacidades sin entrada
  o ruta de configuración en setup antes de dar por terminada una entrega.
- Presentar propósito, requisitos, estado de activación y ámbito permitido de
  cada capacidad. Las preferencias pueden admitir ámbito global, local o ambos.
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
- [034 — Preferencias por lenguaje en setup](034-setup-preferencias-python-typescript.md).
- [035 — aikit-help: guía de capacidades](035-aikit-help-guia-capacidades.md).
- [038 — Autonomía para Git y GitHub](038-autonomia-git-github-setup.md).

El inventario y la comprobación de cobertura están integrados. El recorrido de
inicio desde la interfaz queda pendiente de validación.
