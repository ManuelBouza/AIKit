---
id: SPEC-complementos-independientes
companions:
  - ../../../docs/limites-delegacion-aikit.md
  - ../../../docs/plan-monorepositorio.md
  - ../../../docs/inventario-monorepositorio.md
  - ../../../docs/contrato-artefacto-go.md
  - instalacion-y-migracion.md
sources: []
---

# Complementos independientes en un monorepositorio

## Why

El complemento histórico mezcla preferencias generales y delegación a OpenCode.
Manuel necesita desarrollar ambos en el mismo repositorio y poder instalar,
actualizar y utilizar cada complemento de forma independiente, manteniendo las
instrucciones y datos existentes.

## Capabilities

- **CAP-1**
  - **intent:** Disponer de un complemento AIKit para las configuraciones,
    preferencias e instrucciones generales de ChatGPT como agente y sus skills propias.
  - **success:** AIKit se distribuye y funciona sin instalar Delegating to OpenCode;
    su contenido excluye el MCP y las skills exclusivas de delegación. La primera
    versión incluye `go` y la preferencia de documentación mediante Context7.
- **CAP-2**
  - **intent:** Gestionar las instrucciones propias de AIKit en el `AGENTS.md`
    global, conservando las instrucciones y configuraciones ajenas.
  - **success:** Primero se prueban las instrucciones en `AGENTS.md` local; al
    instalar el complemento liberado sus instrucciones se instalan globalmente.
    Una prueba en perfil temporal demuestra instalación, actualización y retirada
    selectiva sin pérdida de contenido ajeno. El mecanismo efectivo del cliente
    debe verificarse; una instalación incompleta no se presenta como satisfactoria.
- **CAP-3**
  - **intent:** Disponer de un complemento Delegating to OpenCode independiente
    que instale el MCP y las skills necesarias para su funcionamiento.
  - **success:** Su distribución se construye e instala sin requerir AIKit y
    contiene las piezas necesarias para descubrir MCP y skills.
- **CAP-4**
  - **intent:** Usar Delegating to OpenCode solo por indicación expresa del
    usuario o por instrucciones aplicables de `AGENTS.md` sobre cómo y cuándo usarlo.
  - **success:** Los casos de activación, ausencia de indicación y restricciones
    superiores se verifican sin convertir la mera instalación en autorización de uso.
- **CAP-5**
  - **intent:** Conservar configuración, datos y convivencia al pasar del
    complemento histórico a las dos distribuciones independientes.
  - **success:** Las pruebas de migración y coexistencia en entornos temporales
    comprueban preservación, compatibilidad y ausencia de instalaciones duplicadas.

## Constraints

- Un monorepositorio; dos complementos con instalación, actualización y retirada
  independientes. AIKit puede detectar la integración opcional sin exigirla.
- La prohibición temporal de utilizar Delegating to OpenCode en este desarrollo
  sigue vigente hasta nuevo aviso. La especificación no autoriza invocarlo.
- La indicación expresa del usuario sobre activación sustituye las políticas
  históricas que asumían delegación habitual; las instrucciones de mayor prioridad
  y las restricciones vigentes prevalecen.
- Preservar marcadores, instrucciones ajenas, configuraciones, sesiones, estado y
  respaldos; ningún perfil real se modifica sin autorización específica.
- Mantener el complemento histórico hasta verificar los dos nuevos; migrar de forma
  explícita e idempotente y evitar instancias duplicadas del servidor. Conservar
  identidades y rutas necesarias para compatibilidad hasta probar su transición.
- Conservar roles y capacidades nativas y de Superpowers; reutilizar lo existente.
- Los compañeros son contexto histórico y de límites. En caso de contradicción,
  esta especificación y las instrucciones más recientes del usuario prevalecen.

## Non-goals

- Crear repositorios separados, instalar en el perfil real o activar delegación
  como consecuencia de esta especificación.
- Afirmar que el empaquetado independiente ya existe o que la prueba portable de
  `go` demuestra la separación completa.

## Success signal

Dos artefactos independientes construidos desde fuentes verificadas superan
pruebas aisladas de contenido y de instalación en perfiles temporales; la
convivencia y migración preservan la configuración y los datos existentes.
Los casos de activación de delegación respetan CAP-4 y las restricciones vigentes.

## Open Questions

- ¿Qué mecanismo verificable del cliente permitirá completar la instalación global
  como parte de la instalación de AIKit? La documentación consultada no demuestra
  que la instalación de un plugin escriba automáticamente `AGENTS.md`; una prueba
  con `codex plugin add` y `onboardingSkill` tampoco lo produjo. Queda por verificar
  el flujo de onboarding en la interfaz y el mecanismo completo de instalación.
- ¿Qué identificadores y versiones finales deben elegirse tras verificar las
  reglas de actualización y convivencia del cliente? La compatibilidad de las
  rutas y del servidor histórico debe probarse antes de cambiarlos.
