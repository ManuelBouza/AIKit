# Instalación y migración: decisiones y verificación

## AIKit

Primero se prueban las instrucciones en `AGENTS.md` local. Al instalar el
complemento liberado, el resultado requerido es que sus instrucciones queden
instaladas en el `AGENTS.md` global. La primera versión comprende el mecanismo
`go` y la preferencia de consultar documentación técnica actualizada con Context7,
con alternativa de fuentes oficiales cuando corresponda.

Inventario del 2026-11-07: el `AGENTS.md` global actual contiene el bloque
`AIKIT:GO`; la preferencia Context7 ya se aplica en el `AGENTS.md` de este
proyecto. Las reglas locales sobre BMAD, backlog y OpenCode son contexto del
proyecto o trabajo pendiente, no preferencias globales aprobadas. No se identificó
otra preferencia global de AIKit aprobada en esos archivos. Las skills futuras
se seleccionarán expresamente, evitando duplicar capacidades instaladas.

La documentación oficial describe una skill opcional de inicio posterior a la
instalación y hooks sujetos a revisión y confianza; no acredita una escritura
automática de `AGENTS.md` al instalar. Los hooks de plugin se documentan para
instalación manual en Codex desktop. No confundir `SessionStart` con un evento de
instalación ni asumir soporte equivalente en todas las superficies de ChatGPT.
La solución debe probarse en el cliente y perfil temporal relevantes; si no puede
completar la escritura como parte de la instalación, informar la limitación y
volver al usuario con evidencia, sin dar por cumplido el requisito.

Fuentes: [empaquetado de plugins](https://developers.openai.com/plugins/build/plugins),
[onboarding de plugins](https://developers.openai.com/plugins/deploy/submission) y
[descubrimiento de AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

### Prueba aislada — 2026-11-07

En Windows, con `codex-cli 0.153.4`, se creó un perfil temporal bajo `.aikit/`
con un `AGENTS.md` de contenido ajeno ficticio y un catálogo local nuevo. Se
instaló con `codex plugin add` un complemento ficticio mínimo y, en otro perfil,
una variante con `onboardingSkill`. Ambos registros e instalaciones devolvieron
código 0. En los dos casos el `AGENTS.md` permaneció idéntico tras la instalación.

Después se ejecutó explícitamente `scripts/install_go.py --codex-home <perfil>`
en el segundo perfil: primera ejecución `changed`, segunda `unchanged`; el texto
ajeno y el bloque `go` se conservaron. Esto demuestra el instalador existente y
su idempotencia para ese caso, no una instalación global automática desde el
plugin ni la instalación de Context7.

La prueba cubre la CLI y perfiles ficticios; no demuestra el comportamiento de
onboarding en la interfaz de Codex o ChatGPT, ni qué hace una skill al ejecutarse.
No se instaló el complemento real ni se modificó el perfil global del usuario.
Conclusión: la instalación automática deseada sigue sin demostrarse; investigar
el flujo de onboarding en el cliente sin confundirlo con el evento de instalación.

### Investigación del flujo de interfaz — 2026-11-07

La documentación oficial de [empaquetado](https://developers.openai.com/plugins/build/plugins)
indica que `onboardingSkill` se invoca cuando el usuario ejecuta la configuración
después de instalar, en una conversación nueva o en la existente si allí se instaló.
Por tanto, el flujo documentado requiere iniciar esa configuración; no acredita que
la instalación del complemento escriba directamente en `AGENTS.md` global.

Se inspeccionó el cliente de escritorio disponible, pero no se verificó una forma
de abrir una interfaz aislada asociada al `CODEX_HOME` temporal sin reutilizar la
sesión real. No se instaló el complemento ficticio en el perfil real ni se lanzó
su configuración desde la interfaz. La comprobación visual del onboarding y su
capacidad de completar la escritura global siguen pendientes; la prueba anterior
de CLI no sustituye ese recorrido.

## Estrategia de migración propuesta

1. Construir y verificar por separado los dos complementos con identidades propias,
   conservando el empaquetado histórico durante la transición.
2. Mantener inicialmente los nombres de servidor, rutas de estado, sesiones y
   respaldos existentes cuando sean necesarios para compatibilidad. Decidir y
   probar cualquier cambio antes de mover datos o eliminar identidades.
3. Ofrecer una transición explícita, idempotente y comprobable: detectar el
   complemento histórico y evitar que dos instancias del mismo MCP queden activas.
   No desinstalar ni modificar configuraciones ajenas automáticamente.
4. Ensayar instalación individual, coexistencia, actualización, recuperación y
   retirada en perfiles temporales con datos ficticios. Preservar el bloque
   `AIKIT:GO` existente y demostrar la conservación de instrucciones ajenas.
5. Solo después de validar y obtener autorización específica, abordar cualquier
   transición del perfil real. Conservar una vía de recuperación comprobada.

Estos pasos son una estrategia de diseño, no una afirmación de que las identidades,
la actualización del cliente o la reversión ya estén implementadas o verificadas.
