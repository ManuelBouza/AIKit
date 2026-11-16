# AIKit 0.1.3 — autonomía de los Chats de Tarea

Fecha: 2026-11-16.
Estado: versión privada instalada y descubrimiento verificado en el perfil habitual.
Corrección fuente: commit `7eb88cfc2e30345a828f198af6cbbf8c8d24643d`.

## Resultado de aplicación — 2026-11-16

Actualización autorizada por Manuel al solicitar corregir el comportamiento en
AIKit y lanzar una nueva versión. El Coordinador ejecutó el aplicador con su
SHA-256 previamente contrastado con la revisión independiente accepted:
`cc0725f1b9ede651fad819c396299d34169d67bab5623346bcbcafac521358aa`.

Preflight, protección del respaldo y verificación del ZIP correctos. Retirada
del registro del catálogo, alta de la nueva fuente e instalación terminaron con
código 0. La versión instalada es 0.1.3 y todos sus archivos coinciden con el
paquete. La comparación TOML solo admite el cambio de origen del catálogo;
configuración ajena y AGENTS.md global y del proyecto permanecen iguales.

App-server confirma habilitadas las tres skills desde la caché 0.1.3 mediante
skills/list con recarga, sin inferencia ni setup. No se afirma recarga automática
de instrucciones en todas las conversaciones ya abiertas. Los chats 028 y 040
siguen pausados: sus estados nativos permanecen idle, con los mismos turnos de
confirmación de pausa y sin nuevas ejecuciones.

La fuente 0.1.2 sigue intacta. El gestor retiró su antigua caché; el ZIP privado
verificado permite conservarla para recuperación. Conservar también la fuente
0.1.3: ahora es el origen activo del catálogo, no un temporal prescindible.
Evidencia privada de aplicación: `.aikit/041-aplicacion-0.1.3/`.

## Cambio incluido

Un Chat de Tarea con encargo ejecutable autorizado comprueba su contexto y
continúa sin otra orden del Coordinador. Conversa directamente con el usuario
y reporta los hitos pertinentes; esperar un acuse no detiene trabajo propio
independiente. Se conservan autorizaciones, dependencias, registro único,
revisión técnica delegada e integración por el Coordinador.

Se distingue una preparación sin ejecución autorizada de un encargo ejecutable.
La actualización no reanuda los chats 028/040, pausados expresamente por Manuel,
ni resuelve o instala BMAD en sus worktrees. No activa otros proyectos, ejecuta
setup ni promete ejecución permanente o capacidades de mensajería no disponibles.

La versión del manifiesto fuente pasa de 0.1.0 a 0.1.3 para que el exportador
produzca la versión correcta sin retocar después ese manifiesto. La versión
habitual observada antes de aplicar era 0.1.2.

## Identidad y distribución privada

- Selector conservado: `aikit-preferencias@aikit-setup-prueba-20261108`.
- Fuente candidata: `C:/Manuel/Projects/AIKit/.aikit/041-actualizacion-0.1.3`.
- Fuente anterior conservada: `C:/Manuel/Projects/AIKit/.aikit/025-actualizacion-0.1.2`.
- CLI incluida: 0.169.0-alpha.11.1, Desktop 26.1111.2228.0.
- No se publica en un catálogo público ni se instala desde todo el checkout.

El paquete exporta los 28 archivos de la lista explícita de `build_aikit.py`.
Sus bytes coinciden con las fuentes, incluido `plugin.json`; solo cambia en la
salida el nombre del catálogo para conservar la identidad privada ya instalada.
Los hashes completos se conservan en la evidencia privada de preparación.

## Ensayos comprobados

Sin inferencia y con `CODEX_HOME` exclusivo de perfiles ficticios:

1. Instalación nueva de 0.1.3: marketplace add y plugin add correctos.
2. Instalación 0.1.2 y migración a 0.1.3: pasos correctos, mismos selector y
   preferencias habilitadas.
3. Descubrimiento por app-server, `skills/list` con `forceReload`: las tres
   skills habilitadas desde caché 0.1.3; todos sus archivos coinciden con el paquete.
4. Recuperación del perfil de migración a 0.1.2: gestor y descubrimiento correctos;
   contenido igual al paquete anterior.
5. Ensayo del helper final de aplicación con un perfil y destino nuevos ficticios:
   respaldo con ACL privada, ZIP de caché verificado, actualización, comparación
   TOML, igualdad de archivos y descubrimiento correctos. La variante ensayada
   difiere del helper habitual únicamente en las rutas del perfil y evidencia.
6. Hashes del perfil habitual, instrucciones y fuente/caché 0.1.2: sin cambios.

La validación de comportamiento de la corrección está en la
[nota 041](../notas/041-autonomia-chat-tarea-tras-asignacion.md) y su especificación.
Estos ensayos de distribución verifican instalación y descubrimiento; no prueban
por sí solos lectura efectiva de instrucciones por todas las sesiones abiertas.

## Incidencias de preparación y solución acotada

La primera comparación del paquete se detuvo antes de instalar los perfiles:
el helper reserializaba innecesariamente el manifiesto ya versionado, variando
sus bytes. Se eliminó esa reserialización y se conservó el archivo fuente exacto.

El primer ensayo del respaldo paró antes de copiar configuración o caché porque
la consulta de ACL no pudo cargar `Microsoft.PowerShell.Security`; produjo
`protected: null` y salida de proceso 0. No se rebajó la comprobación ni se
interpretó como permiso suficiente. El ensayo instrumental capturó stdout y
stderr y permitió identificar el problema de autoload.

Microsoft documenta que Windows PowerShell iniciado a través de Python hereda
las rutas de módulos de PowerShell 7 y puede resolver módulos incompatibles.
La solución recomendada es retirar `PSModulePath` únicamente del entorno del
proceso hijo. Se aplicó a la consulta de ACL, junto con errores terminantes y
comprobación explícita del código; no modifica variables globales ni la política
del sistema. [Documentación oficial de PSModulePath](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_psmodulepath?view=powershell-7.5).

El helper mantiene las guardias de ACL protegida y acceso exclusivo de usuario,
SYSTEM y Administradores antes de guardar respaldos sensibles, conforme a
[icacls](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls)
y [Get-Acl](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl?view=powershell-5.1).
El nuevo ensayo completo pasó sin cambios en el perfil habitual.

## Procedimiento aplicado y recuperación

Helper privado revisado y ejecutado: `.aikit/041-aplicar-paquete013.py`.
Aplicación completada con código 0 y resultado `passed`.

Preflight exige fuente anterior, selector habilitado, CLI esperada y candidata
con hashes exactos. Crea una carpeta de evidencia exclusiva; protege y comprueba
su ACL antes de respaldar `config.toml` y caché 0.1.2. Verifica el ZIP antes de
retirar el registro del catálogo, registrar la nueva fuente e instalar 0.1.3.

Comprueba que solo cambia el origen previsto del catálogo en el TOML, conserva
AGENTS.md y fuente anterior, compara los archivos instalados y descubre las tres
skills sin inferencia. Se detiene ante cualquier fallo y conserva la fase y la
evidencia; no reintenta ni restaura una configuración completa a ciegas.

Recuperación preparada y ensayada en el perfil ficticio: retirar solo el registro
identificado, registrar de nuevo la fuente 0.1.2 conservada e instalar el mismo
selector; comprobar origen, versión, habilitación y contenido. Reconciliar antes
los cambios concurrentes para no sobrescribirlos. No usar plugin remove ni
eliminar fuentes o respaldos como parte de esta actualización.

Evidencias privadas ignoradas: `.aikit/041-preparacion-0.1.3/` y
`.aikit/041-prueba-final-0.1.3/`. La aplicación habitual se conserva en
`.aikit/041-aplicacion-0.1.3/`, que contiene respaldos privados y no debe
publicarse ni añadirse a Git. Preservar la fuente candidata mientras sea origen
del catálogo activo.
