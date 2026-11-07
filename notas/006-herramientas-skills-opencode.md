# Herramientas y skills de Codex disponibles en OpenCode

Fecha: 2026-10-31.
Estado: pendiente de debatir.

## Idea

Instalar o habilitar en OpenCode las mismas herramientas y skills que se usan en
Codex, incluyendo Superpowers, Context7 y el propio AIKit.

El usuario observa que un subagente de Codex tiene acceso a las mismas
herramientas, mientras que OpenCode actualmente no. Investigar cómo gestionar
esta diferencia para que el ejecutor disponga de las capacidades necesarias para
su tarea. La equivalencia real de acceso queda pendiente de verificar en ambos
entornos.

## Alternativa propuesta: AIKit solo en Codex

Tal vez AIKit deba instalarse únicamente en Codex. En ese caso, su instalador
debería escribir en el `AGENTS.md` de OpenCode las instrucciones necesarias para
que el ejecutor esté alineado con Codex y AIKit, sin instalar allí todo AIKit.

Esta alternativa queda pendiente de evaluar. Distinguir las instrucciones que
OpenCode necesita para ejecutar su tarea de las responsabilidades de coordinación
que permanecen en Codex.

## Para debatir e investigar después

- Inventariar las herramientas, skills e integraciones disponibles para Codex,
  sus subagentes y las sesiones de OpenCode; distinguir instalación de acceso
  efectivo durante una tarea.
- Consultar la documentación oficial de OpenCode, Superpowers, Context7 y AIKit
  para determinar los mecanismos compatibles de instalación, configuración y
  activación, sin asumir que basta con copiar la configuración de Codex.
- Decidir cómo mantener versiones y configuraciones reproducibles, y cómo
  comprobar que las capacidades funcionan dentro de una sesión delegada.
- Evaluar la alternativa de AIKit solo en Codex: identificar qué `AGENTS.md` carga
  OpenCode y en qué ámbito, qué instrucciones debe escribir el instalador y cómo
  actualizarlas o retirarlas conservando el contenido ajeno y las reglas existentes.
- Determinar qué partes de AIKit necesita el ejecutor y cuáles corresponden al
  coordinador, conservando la prohibición de redelegar y evitando ciclos de
  delegación.
- Mantener los roles y archivos de Superpowers; investigar cómo aplicar sus
  instrucciones al papel acotado del ejecutor sin duplicar la coordinación.
- Gestionar permisos y autenticación por entorno sin copiar credenciales ni
  ampliar el acceso a datos sensibles de forma automática.

Relacionada con la nota [002](002-opencode-como-subagente-acotado.md), sobre el
alcance de OpenCode como subagente, la [004](004-guardarrailes-privacidad-opencode.md),
sobre privacidad, y la [005](005-prompts-concisos-opencode.md), sobre evitar repetir
en los prompts instrucciones ya disponibles en el entorno.

La investigación queda pendiente. Guardar esta nota no autoriza instalaciones,
cambios de configuración ni modificaciones de herramientas o skills.
