---
id: SPEC-instalador-aikit-npx
companions:
  - ../../../docs/distribucion-aikit-npx.md
sources: []
---

# Instalador de AIKit mediante npx

## Why

Manuel necesita aplicar y actualizar sus preferencias de Codex de forma reproducible en varios equipos mediante un comando, conservando la configuración existente.

## Capabilities

- **CAP-1**
  - **intent:** Instalar las preferencias aprobadas `go` y Context7 en un perfil de Codex.
  - **success:** En un perfil ficticio, ambos bloques aparecen y el contenido ajeno permanece intacto.
- **CAP-2**
  - **intent:** Actualizar las preferencias y conocer la versión aplicada.
  - **success:** Una actualización sustituye los bloques correspondientes, informa del resultado y respaldo; repetirla no duplica ni modifica contenido.
- **CAP-3**
  - **intent:** Revisar los cambios y resolver conflictos antes de modificar instrucciones.
  - **success:** Una vista previa muestra ambos bloques y la ruta; ante conflictos el proceso informa y no aplica cambios parciales.

## Constraints

- Distribuir mediante `npx` con instalador Node, sin requerir Python ni uv en destino. Planificar ambos bloques antes de escribir.
- Respetar `CODEX_HOME`, los marcadores, el BOM y el contenido ajeno; detectar override global, enlaces, junctions y cambios concurrentes. Crear respaldo antes de sustituir el archivo.
- Probar primero con perfiles ficticios; no modificar perfiles reales durante la implementación ni invocar OpenCode.
- Mantener Delegating to OpenCode independiente y conservar el complemento histórico y la configuración ajena.

## Non-goals

- Instalar o conectar Context7, instalar OpenCode o publicar el paquete.
- Afirmar compatibilidad con plataformas o comportamientos no verificados.

## Success signal

Una prueba reproducible con perfil ficticio demuestra instalación, actualización y repetición sin cambios ajenos, y verifica que un conflicto impide la escritura. Se informa de versión y respaldo.

## Assumptions

- La versión aplicada se identificará de forma verificable sin exponer información privada.

## Open Questions

- ¿Qué nombre y registro npm se usarán y cuál será la versión mínima de Node compatible?
- Además de Windows, ¿qué plataformas se incluirán en la primera versión verificada?
