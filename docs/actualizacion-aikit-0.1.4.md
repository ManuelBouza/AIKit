# AIKit 0.1.4 — notificaciones proactivas del Coordinador

Fecha: 2026-11-16.
Estado: actualización privada instalada y descubrimiento verificado en el perfil habitual.
Base de preparación: `a5c0e3ccf3f7dc29f918904f93f20c0bd052130a`, con las fuentes
de la mejora 042 revisadas y fijadas antes de exportar.

## Resultado de aplicación — 2026-11-16

El Coordinador aplica la mejora solicitada mediante el helper con la huella
revisada `80aa77ae636f64cee6be7061b991f7a1dafa85ac7797c247e3d2b2ff2459cfae`.
Preflight y respaldo privado verificados; los tres pasos de actualización terminan
con código 0. Resultado `passed`: 0.1.4 instalada, archivos iguales al paquete,
tres skills habilitadas y descubiertas desde su caché con recarga. Comparación
TOML confirma solo el cambio de origen del catálogo; configuración ajena,
AGENTS.md y fuente anterior conservados. Sin setup ni inferencia en la instalación.

El gestor retira la caché antigua 0.1.3; se conserva su ZIP privado verificado y
la fuente anterior para recuperación. La fuente 0.1.4 es ahora origen activo y
no debe limpiarse como temporal.

El Coordinador informa de 0.1.4 a los chats 028/040 sin otra consulta al usuario,
con referencia a la autorización humana del proyecto. Ambos reconocen recepción
y siguen Pausados. Véanse [avisos y reconocimiento](../coordinacion/paralelo-028-040/ACUSES.md).
No se afirma que todas las conversaciones abiertas hayan recargado instrucciones.

## Cambio incluido

El Coordinador notifica por iniciativa propia los cambios relevantes a los
Chats de Tarea afectados, dentro de la autorización humana verificable del
proyecto, sin consultar por cada aviso. Conserva contenido y versión, destinatario,
motivo y resultado; distingue envío de reconocimiento y reconcilia incertidumbres
antes de repetir. Selecciona destinatarios por responsabilidad e impacto vigente,
sin despertar encargos históricos por rutina ni confundir reutilización del chat
con conocimiento del cambio en el encargo actual.

Un aviso informativo a una tarea pausada mantiene la pausa: no autoriza investigar,
implementar, actualizar su rama, ejecutar pruebas ni limpiar recursos. El cliente
puede activar un turno de recepción; no se promete entrega silenciosa. El ajuste
no añade vigilancia, servicios ni automatizaciones y no concede permisos por leer
la skill o instalar AIKit. Sin mensajería o autorización, conserva la vía manual.

Se mantienen la autonomía de los Chats de Tarea, las decisiones directas del
usuario, la revisión técnica delegada y la integración centralizada. Esta entrega
no reanuda los chats 028/040, no prepara BMAD en sus worktrees ni activa setup.
Véanse la [nota 042](../notas/042-notificaciones-proactivas-coordinador.md) y
su [especificación](../_bmad-output/implementation-artifacts/spec-042-notificaciones-coordinador.md).

## Identidad y contenido

- Versión del manifiesto fuente y candidata: 0.1.4.
- Selector conservado: `aikit-preferencias@aikit-setup-prueba-20261108`.
- Fuente nueva: `C:/Manuel/Projects/AIKit/.aikit/042-actualizacion-0.1.4`.
- Fuente anterior preservada: `C:/Manuel/Projects/AIKit/.aikit/041-actualizacion-0.1.3`.
- Versión habitual observada antes de aplicar: 0.1.3.
- CLI incluida: 0.169.0-alpha.11.1, Desktop 26.1111.2228.0.

El exportador produce los 28 archivos de su lista explícita. Todos coinciden con
las fuentes, incluido el manifiesto; solo se ajusta el nombre del catálogo en la
salida para conservar su identidad privada. No se copia todo el checkout ni se
publica en un catálogo público.

Antes de exportar se verificó la huella fijada de `responsabilidades.md`:
`4ca17e52ef9deefe52946fb18c91f6e4086ac6791a5f59591c38e1aba02691b6`.
Los hashes de todos los archivos se conservan en la evidencia privada.

## Ensayos realizados sin inferencia

Cada perfil ficticio usa su propio `CODEX_HOME`, dentro del workspace:

1. Instalación nueva de 0.1.4: registro del catálogo y plugin correctos.
2. Migración de 0.1.3 a 0.1.4: mismos selector y habilitación, pasos correctos.
3. Descubrimiento mediante app-server y `skills/list` con recarga: tres skills
   habilitadas desde caché 0.1.4, sin errores y con todos los archivos iguales
   al paquete.
4. Recuperación del perfil de migración a 0.1.3: gestor, descubrimiento y contenido
   comprobados. El perfil de instalación nueva conserva 0.1.4.
5. Ensayo del helper final en un perfil y destino nuevos: ACL privada comprobada,
   respaldo de configuración y ZIP de caché verificado, actualización, comparación
   TOML, igualdad de archivos y descubrimiento correctos.
6. Configuración e instrucciones del perfil habitual y fuente/caché anterior:
   hashes sin cambios durante los ensayos.

La variante de ensayo del helper solo sustituye las rutas de perfil y evidencia.
El resultado del ensayo identifica expresamente ese perfil ficticio, aunque la
salida genérica del helper denomine la fase «actualización habitual».

Se reutiliza el arreglo comprobado de 0.1.3 para ejecutar la consulta de ACL desde
Python: se retira `PSModulePath` solo del entorno del hijo Windows PowerShell,
se usan errores terminantes y se comprueba su código y descriptor. No se modifica
el entorno global ni se rebaja la guardia. La explicación y la documentación
oficial están en la [entrega 0.1.3](actualizacion-aikit-0.1.3.md).

Estos ensayos verifican distribución y descubrimiento, no garantizan por sí solos
la aplicación de las instrucciones en todas las conversaciones abiertas. La
verificación de la mejora 042 y los avisos reales tiene su trazabilidad en la nota
y el registro del proyecto.

## Procedimiento aplicado

Helper habitual revisado y ejecutado con código 0:
`.aikit/042-aplicar-paquete014.py`.
SHA-256: `80aa77ae636f64cee6be7061b991f7a1dafa85ac7797c247e3d2b2ff2459cfae`.

Preflight exige CLI, fuente anterior, selector y candidata exactos. El helper
reserva una carpeta de aplicación exclusiva y comprueba su DACL protegida,
limitada al usuario, SYSTEM y Administradores, antes de copiar datos sensibles.
Verifica el ZIP antes de retirar únicamente el registro del catálogo privado,
registrar la fuente nueva e instalar la candidata.

Después comprueba que el único cambio TOML sea el origen del catálogo identificado,
que AGENTS.md y configuración ajena se conserven, que los archivos instalados
coincidan y que se descubran las tres skills sin inferencia ni onboarding.
Se detiene ante un fallo; no reintenta ni restaura toda la configuración a ciegas.

## Recuperación y conservación

La recuperación a 0.1.3 fue ensayada mediante el gestor: retirar solo el registro
identificado, registrar la fuente anterior conservada e instalar el mismo
selector, comprobando versión, habilitación y contenido. Reconciliar cambios
concurrentes antes de restaurar cualquier configuración. No ejecutar `plugin remove`
ni eliminar fuentes o respaldos como parte de esta actualización.

Evidencia privada ignorada: `.aikit/042-preparacion-0.1.4/` y
`.aikit/042-prueba-final-0.1.4/`. La aplicación habitual se conserva en
`.aikit/042-aplicacion-0.1.4/`; contiene configuración y respaldo privado y no
debe publicarse ni añadirse a Git. Conservar la nueva fuente mientras sea origen
activo del catálogo y preservar la anterior para recuperación.
