# Guía del repositorio

## Propósito

Este proyecto sirve para probar y documentar las preferencias personales de configuración de Codex de Manuel. El objetivo es poder reproducir en otras instalaciones el comportamiento validado aquí. Cada preferencia debe explicar qué se configura, por qué se elige y cómo comprobar su resultado.

## Estructura y organización

Actualmente solo existe esta guía. Al incorporar contenido, utiliza estas ubicaciones según sea necesario:

- `README.md`: objetivo, requisitos y pasos para reproducir la configuración.
- `config/`: configuraciones de referencia sin secretos ni datos personales.
- `docs/`: preferencias, decisiones y limitaciones conocidas.
- `tests/`: escenarios y resultados de las pruebas de comportamiento.
- `scripts/`: utilidades de instalación, comprobación o restauración, cuando existan.

Distingue las preferencias ya verificadas de los experimentos pendientes.

## Configuración y comandos

Todavía no hay comandos de instalación ni pruebas automatizadas. Documenta cada comando cuando se incorpore, indicando desde qué directorio se ejecuta, sus requisitos y los archivos que modifica. Para cada procedimiento de réplica, incluye cómo guardar la configuración anterior y restaurarla.

Identifica qué ajustes son personales, cuáles pertenecen al proyecto y cuáles dependen del equipo o del sistema operativo. Usa rutas parametrizadas en los ejemplos.

## Estilo y documentación

Escribe la documentación en español, con instrucciones breves y ejemplos reproducibles. Conserva los nombres originales de opciones, archivos y comandos. Utiliza nombres descriptivos para los archivos, como `preferencias-de-respuesta.md`. Explica la intención de cada ajuste y sus dependencias.

## Validación de preferencias

Prueba cada cambio con un escenario concreto. Registra la versión de Codex, el entorno, la configuración aplicada, el resultado esperado y el observado. Al replicar la configuración, repite el escenario en la instalación de destino y documenta las diferencias. No presentes una preferencia como verificada sin evidencias.

## Commits y solicitudes de cambios

Utiliza Git para versionar la configuración y su documentación. Escribe títulos breves en imperativo, como `Documenta las preferencias de respuesta`. Mantén cada cambio centrado en una preferencia o procedimiento. En las solicitudes de cambios, explica el motivo, las pruebas realizadas y las limitaciones de portabilidad.

## Seguridad

Excluye credenciales, tokens, conversaciones privadas y datos de cuenta. Comparte ejemplos con valores ficticios. Revisa las configuraciones antes de incorporarlas al repositorio.
