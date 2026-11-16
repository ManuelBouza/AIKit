# Actualización preparada de AIKit — 2026-11-15

Preparación posterior, 2026-11-16: [candidata 0.1.2 y procedimiento](actualizacion-aikit-0.1.2.md).
La actualización descrita abajo corresponde a 0.1.1, que sigue instalada; la
candidata 0.1.2 solo se ha ensayado en perfiles ficticios.

Estado: actualización aplicada y descubrimiento verificado en el perfil habitual.

## Resultado de aplicación — 2026-11-15

Con autorización go se releyó la configuración y se respaldó config.toml en
una carpeta privada con ACL limitada al usuario, SYSTEM y Administradores.
Se sustituyó el registro del catálogo y plugin add instaló 0.1.1 correctamente.
La comparación TOML solo admite el cambio de origen del catálogo previsto:
la configuración ajena y los hashes de AGENTS.md global y de proyecto coinciden.

App-server 0.169.0-alpha.11.1, iniciado desde un proyecto temporal externo con
el perfil habitual, descubre habilitadas aikit-setup, director-de-ideas y
coordinacion-chats bajo aikit-preferencias. La última apunta a la caché 0.1.1;
SKILL.md y avisos.md coinciden byte a byte con las fuentes. Sin inferencia.

El gestor retiró la caché 0.1.0 durante la actualización, a diferencia de la
conservación esperada en la preparación. La fuente anterior
`.aikit/prueba-setup-20261108` sigue disponible para reinstalar mediante el gestor.
No se ejecutó borrado manual. El respaldo config no contiene una copia de la
caché y no representa una restauración completa del complemento.

Evidencias privadas ignoradas: `.aikit/025-actualizacion-real-respaldo/`, con
config respaldada, hashes, transcript de instalación y resultado de descubrimiento.
No publicar esta carpeta. No se ejecutó onboarding ni se activó coordinación.
La disponibilidad en el inventario de este chat puede requerir recarga o un chat nuevo.

Las secciones siguientes conservan el inventario previo y el procedimiento aplicado.

## Inventario confirmado

La CLI actual del paquete Desktop 26.1111.2228.0 informa 0.169.0-alpha.11.1.
Su `plugin list --json` confirma instalada y habilitada la identidad
`aikit-preferencias@aikit-setup-prueba-20261108`, versión 0.1.0, desde
`.aikit/prueba-setup-20261108`. El manifiesto en caché coincide y no contiene la
skill de coordinación. La consulta global tardó varios minutos, pero terminó.

El catálogo `aikit-preferencias-local` también está registrado, apuntando a
`.aikit/prueba-ui-aikit-20261107`; no se usa para esta actualización.

## Candidata concreta

Directorio absoluto:
`C:/Manuel/Projects/AIKit/.aikit/025-actualizacion-0.1.1`.

Se construyó mediante build_aikit.py, y se ajustaron únicamente en esa salida
el manifiesto a versión 0.1.1 y el catálogo a `aikit-setup-prueba-20261108`.
La versión de las fuentes sigue en 0.1.0. La candidata permite revisar y aplicar
esta entrega privada concreta; una futura exportación debe fijar expresamente
su versión e identidad, sin asumir que hereda estos ajustes de la salida.

No se instala desde la raíz del checkout. Se conserva el directorio exportado
como fuente del catálogo y la fuente anterior para recuperación.

## Ensayos realizados

- Instalación en `.aikit/025-perfil-actualizacion` con CODEX_HOME limitado al
  proceso. Resultado 0.1.1, identidad esperada y coordinación habilitada desde
  caché según skills/list. Referencia y SKILL.md idénticos a las fuentes.
- Migración en `.aikit/025-ensayo-migracion`: primero se instaló la 0.1.0 desde
  el catálogo anterior. Registrar directamente la nueva ruta fue rechazado con
  «already added from a different source». Se retiró el registro del catálogo
  en ese perfil, se registró la candidata y se instaló 0.1.1 correctamente.
- Evidencias privadas: discovery-result.json y discovery-transcript.json del
  primer perfil; transcript.json del segundo. Sin inferencia ni credenciales
  copiadas. El perfil habitual no se modificó.

## Aplicación propuesta

Antes de escribir, releer configuración y estado del plugin para comprobar que
siguen coincidiendo con este inventario. Respaldar config.toml en ubicación
privada y capturar los hashes de AGENTS.md y de configuración ajena pertinente.
Conservar la fuente y caché anteriores. Usar el ejecutable actual por ruta
absoluta y un proceso acotado, sin modificar PATH ni aceptar onboarding.

1. Retirar solo el registro `aikit-setup-prueba-20261108` con
   `plugin marketplace remove`; no ejecutar plugin remove ni borrar directorios.
2. Registrar `C:/Manuel/Projects/AIKit/.aikit/025-actualizacion-0.1.1` con
   `plugin marketplace add`.
3. Ejecutar `plugin add aikit-preferencias@aikit-setup-prueba-20261108 --json`.
4. Comprobar versión 0.1.1, habilitación, origen y descubrimiento de coordinación
   desde la caché nueva, junto con setup y Director de Ideas. Comparar configuración
   y hashes anteriores; no ejecutar setup ni activar coordinación por proyecto.

El cambio de registro tiene un intervalo sin ese catálogo: si un paso falla,
detenerse y conservar su salida. Para recuperación, volver a registrar la fuente
anterior y reinstalar la 0.1.0 mediante el gestor, inspeccionando primero el
estado resultante. El respaldo de config no sustituye la recuperación de cachés
y no debe restaurarse ciegamente sobre cambios concurrentes.

La aplicación puede requerir recarga o un nuevo chat para renovar skills; el
descubrimiento por app-server no acredita actualización del inventario de este
chat. La activación de coordinación y el auxiliar permanecen separados.
