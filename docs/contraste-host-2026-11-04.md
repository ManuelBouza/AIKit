# Contraste de distribución y host de AIKit

Fecha: 2026-11-04. Fuente: `ec2957e`. Alcance autorizado: nueva exportación limpia y comparación de solo lectura; sin instalación, recarga, modificación del host ni inferencia de prueba.

## Resultado

- Nueva distribución: `.aikit/ent002-clean-20261104/distribution/`; 42 archivos de paquete y un catálogo. Cero extras, `.pyc`, `__pycache__` o `.venv` en el paquete.
- Los 42 hashes coinciden con el candidato aceptado en Unidad 4. No se importaron ni ejecutaron sus módulos.
- Caché inspeccionada: `<CODEX_HOME>/plugins/cache/aikit-local/aikit/0.2.0+host.1`.
- Fuente estable inspeccionada: `<CODEX_HOME>/plugin-sources/aikit/0.2.0-host.1/aikit`.
- En cada comparación: 29 archivos idénticos, 13 distintos, ninguno ausente. Se comparó exclusivamente la lista permitida; el runtime del host quedó fuera.
- Cambios: README, documentación de carga/MCP, manifests, proyecto/lock y seis scripts de sesión. Una diferencia de hash no acredita por sí sola corrección funcional; el código ya tiene su aceptación independiente separada.

## Configuración y versión

El MCP instalado incorpora `AIKIT_STATE` y `AIKIT_OPENCODE_REGISTRATION`; ambas rutas referenciadas existen. Ese overlay debe preservarse para mantener el estado compartido y el registro de servicio explícitos. Se compararon nombres y forma de la configuración, sin publicar valores privados ni copiar credenciales. `${PLUGIN_ROOT}` es una variable del cliente: su presencia literal no demuestra una ruta rota.

Candidato: **0.2.0**. Manifiestos de caché y fuente estable: **0.2.0+host.1**. El código actualizado aún necesita un identificador de versión inequívoco antes de desplegar; se recomienda preparar **0.2.1**, conservando un overlay local explícito y una restauración revisable. No se ha cambiado ninguna versión ni se afirma una regla concreta de precedencia del cliente.

La preparación conserva paquete y catálogo separados según el [formato oficial de plugins](https://developers.openai.com/plugins/build/plugins). El paquete portable y las personalizaciones del host deben mantenerse distinguibles y reproducibles.

## Evidencia y límites

OpenCode: Beam por Kilo, esfuerzo **low**, gratuito según catálogo, sesión `ses_e57ddf720ffeDc36a60A1gyLQo`. Un primer turno dejó incompleta la comparación por pedir aprobación innecesaria; se completó en la misma sesión con el alcance de lectura ya autorizado, sin eludir una denegación real.

Artefactos ignorados: `.aikit/ent002-clean-20261104/{manifest,comparison,report,coordinator-acceptance}.json`. El coordinador comprobó conjunto exacto de archivos, hashes frente al candidato aceptado y recuentos de ambas ubicaciones. No se repitió la suite global, revisión técnica ni inferencia real.

La observación es estática: no acredita qué runtime ha cargado el chat ni el funcionamiento de la instalación nueva. ENT-002 permanece abierto para preparar versión/overlay y autorizar posteriormente el despliegue. No se alteraron otros plugins, Superpowers, cuentas, estado compartido ni servidor de OpenCode; DEF-001 sigue separado.
