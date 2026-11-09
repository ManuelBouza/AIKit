# Configuración global de AIKit: opción documentada

## Requisito y límite del cliente

AIKit debe instalar sus bloques `go` y Context7 en el `AGENTS.md` global al
instalar el complemento liberado, preservando contenido ajeno. La instalación
aislada con Codex CLI 0.153.4 no escribió ese archivo. La documentación de
OpenAI describe `onboardingSkill`, que se ejecuta cuando el usuario inicia la
configuración después de instalar; no describe una ejecución automática en el
instante de la instalación. Por tanto, iniciar configuración es un paso adicional
y no cumple literalmente el requisito de instalación automática.

Fuentes: [empaquetado y onboarding](https://developers.openai.com/plugins/build/plugins),
[instrucciones AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
y [evidencia local](../_bmad-output/implementation-artifacts/validacion-complemento-aikit.md).

## Propuesta revisable

Ofrecer una configuración asistida del complemento, iniciada por el usuario tras
la instalación, que instale ambos bloques con `scripts/install_go.py` y
`scripts/install_context7.py` ya existentes. No duplicar el motor de bloques.
El perfil se determina mediante `CODEX_HOME` o el perfil predeterminado del
cliente, sin inferir que el directorio del proyecto sea global. Respetar los
permisos del entorno y comunicar qué archivo se actualizará. Si un instalador
falla, detenerse, mostrar cuál terminó y cuál falló, y no presentar la
configuración como completa; no revertir contenido ajeno ni repetir a ciegas.
Los instaladores ya crean respaldos y son idempotentes por bloque; ejecutar dos
operaciones independientes no es una transacción atómica.

En el manifiesto portable, el punto de entrada documentado sería:

```json
"extensions": {
  "com.openai": {
    "onboardingSkill": "./skills/aikit-setup/SKILL.md"
  }
}
```

La declaración se ha integrado conservando el resto de `com.openai`. La skill
tiene un propósito acotado:
configurar AIKit cuando el usuario ejecute su configuración, descubrir su
propio directorio instalado, llamar a los instaladores incluidos, y verificar
sus resultados. No debe instalar ni invocar Delegating to OpenCode ni Context7;
solo instala la preferencia sobre Context7.

## Comprobaciones antes de liberarlo

1. Verificar que el cliente reconoce la skill de configuración incluida en la
   distribución, con un perfil temporal y sin iniciar inferencia de OpenCode.
2. Probar ambos instaladores desde el paquete instalado en perfiles ficticios:
   instalación nueva, existente, repetición, contenido ajeno, errores de
   marcadores y override; registrar también resultados de una falla parcial.
3. Comprobar el flujo real de configuración en el cliente destinatario con un
   perfil aislado. Sin esa prueba, no afirmar que la interfaz lo ejecuta bien.
4. Resolver y verificar actualización, retirada selectiva, coexistencia y
   migración antes de retirar el paquete histórico o modificar un perfil real.

## Decisión y estado

El usuario aceptó iniciar la configuración después de instalar y solicitó probarla
en este Codex. El manifiesto declara la skill `aikit-setup`, que reutiliza los dos
instaladores. En Codex CLI/App Server 0.153.4 se descubrió la skill en un perfil
ficticio; la respuesta de metadatos de esa versión no expuso el campo de
onboarding. Aún no se ha comprobado que la interfaz gráfica inicie la skill ni
se ha modificado el perfil global real. La [evidencia](../_bmad-output/implementation-artifacts/verificacion-onboarding-aikit.md)
recoge las pruebas y sus límites.
