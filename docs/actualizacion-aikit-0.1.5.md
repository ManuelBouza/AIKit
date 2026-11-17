# AIKit 0.1.5 — registro previo y seguimiento de tareas

Fecha: 2026-11-17.
Estado: actualización privada instalada y descubrimiento verificado en el perfil habitual.
Encargo: [IMP-0005](../coordinacion/tareas/IMP-0005/TAREA.md).
Base de contenido: `4dc0ab9c8f34c9ffd69055a7157d99daffbc599c`, con el
manifiesto de distribución actualizado a 0.1.5.

## Aplicación habitual — 2026-11-17

El Coordinador ejecutó el helper revisado
`f15d0da75af8b10fe913b7c36764267ef027fa5f59f6ffa7110ca44063bf5f0b`.
Preflight, respaldo privado y los tres pasos del gestor terminaron con código 0.
El resultado identifica el perfil real `C:/Users/Manuel/.codex`: versión 0.1.5,
tres skills habilitadas descubiertas con recarga y archivos iguales a la candidata.
La comparación TOML confirma solo el cambio de origen del catálogo privado;
instrucciones y configuración ajena conservadas. Sin setup ni inferencia.

El gestor retiró la caché 0.1.4 anterior; se conserva el ZIP privado verificado
y la fuente anterior para recuperación. La fuente activa es ahora
`.aikit/043-actualizacion-0.1.5` y no debe limpiarse como temporal.
La evidencia real está en `.aikit/043-aplicacion-0.1.5/resultado.json` y su
respaldo privado. Descubrimiento no equivale a confirmar la lectura de las
instrucciones por todas las conversaciones abiertas.

## Contenido y límites

La entrega incorpora a coordinación y setup las instrucciones de registro previo
y seguimiento de la mejora 043: buscar o registrar un encargo identificable antes
de comenzar una implementación nueva, reutilizarlo ante actualizaciones, separar
ideas de tareas y comprobar su visibilidad. Solo el Coordinador escribe las fuentes
canónicas; registrar una tarea no autoriza ejecutar ni levanta pausas.

Se distribuye `references/seguimiento.md` mediante la lista explícita del
exportador. El paquete no incluye tickets, notas privadas, datos de coordinación
ni el runtime del tablero del repositorio. Instalar el complemento no activa ni
migra un tracker ni instala su generador. Se reutilizan las herramientas del
proyecto y se conserva la vía manual cuando no existe generación disponible.
No se impone Python, Git o BMAD como requisito universal del complemento.

La actualización no ejecuta setup, no activa proyectos nuevos ni reanuda los
trabajos 028/040. Tampoco prepara BMAD en sus worktrees. El alcance y la validación
funcional ya terminada están en el [diseño 043](diseno-ideas-tareas-043.md) y la
[evidencia de implementación](validacion-seguimiento-043.md). Los ensayos de esta
entrega comprueban distribución e instalación, sin repetir las pruebas de runtime.

## Identidad y fuentes

- Manifiesto fuente y candidata: 0.1.5.
- Selector: `aikit-preferencias@aikit-setup-prueba-20261108`.
- Fuente activa instalada: `C:/Manuel/Projects/AIKit/.aikit/043-actualizacion-0.1.5`.
- Fuente anterior conservada: `C:/Manuel/Projects/AIKit/.aikit/042-actualizacion-0.1.4`.
- Estado habitual previo verificado: selector habilitado, fuente anterior y caché 0.1.4.
- Desktop observado: 26.1111.2228.0; CLI incluida: `codex-cli 0.169.0-alpha.11.1`.

El paquete contiene exactamente los **29 archivos** de `build_aikit.py`.
Sus bytes coinciden con las fuentes, incluido `plugin.json`; solo se ajusta el
nombre del catálogo exportado para conservar la identidad privada instalada.
No se instala desde la raíz completa del checkout ni se publica un catálogo público.

Se contrastaron la [documentación oficial del paquete](https://developers.openai.com/plugins/build/plugins)
y los [comandos de desarrollo](https://learn.chatgpt.com/docs/developer-commands?surface=cli).
La versión y ayuda de la CLI incluida se capturaron de nuevo con un perfil ficticio;
el procedimiento usa los comandos locales observados, sin inferencia.

## Ensayos aislados observados

Todos los pasos usan `CODEX_HOME` de perfiles ficticios bajo la evidencia privada:

1. Instalación nueva de 0.1.5: registro del catálogo y plugin correctos.
2. Migración 0.1.4→0.1.5: pasos del gestor correctos, selector conservado.
3. Descubrimiento con app-server y `skills/list` con recarga: las tres skills
   habilitadas desde caché 0.1.5, sin errores; todos los archivos coinciden con
   la candidata, incluida la referencia de seguimiento.
4. Recuperación del perfil de migración a 0.1.4: instalación, descubrimiento y
   contenido correctos. El perfil de instalación nueva mantiene 0.1.5.
5. Ensayo completo del helper de aplicación en otro perfil y destino nuevos:
   ACL protegida, tres SID autorizados con control total, respaldo privado de
   configuración y ZIP de caché verificado antes de cambiar el registro; después,
   TOML con solo cambio de origen previsto, AGENTS.md y fuente anterior intactos,
   archivos instalados iguales y descubrimiento correcto.
6. Configuración e instrucciones habituales y fuente/caché 0.1.4: hashes iguales
   a la captura inicial después de todos los ensayos.

La variante ensayada solo sustituye las rutas de perfil y evidencia del helper
habitual. Su resultado identifica el perfil ficticio; la salida genérica del
script no acredita una actualización del perfil habitual.

Se reutiliza el arreglo de `PSModulePath` ya documentado en la
[entrega 0.1.3](actualizacion-aikit-0.1.3.md): eliminación únicamente en el entorno
del hijo Windows PowerShell, errores terminantes y comprobación del descriptor.
Las guardias de privacidad y parada no se rebajan ni se modifica el entorno global.

## Helper preparado para revisión y aplicación

Helper habitual revisado y ejecutado con código 0:
`.aikit/043-aplicar-paquete015.py`.
SHA-256: `f15d0da75af8b10fe913b7c36764267ef027fa5f59f6ffa7110ca44063bf5f0b`.

Preflight exige versión de CLI exacta, candidata de 29 archivos con hashes
esperados, catálogo privado, fuente anterior y selector habilitado. Reserva un
destino exclusivo, verifica su DACL antes de respaldar información sensible y
verifica el ZIP antes de retirar únicamente el registro del catálogo identificado.

Después registra la fuente nueva, instala el mismo selector, compara configuración
y contenido y descubre las skills. Detiene cualquier fallo conservando fase y
evidencia; no reintenta automáticamente ni restaura toda la configuración a ciegas.
El helper y el contenido fueron aceptados por revisión independiente antes de
la aplicación. El contraste posterior confirmó el perfil real y su configuración,
los 28 archivos del plugin instalado (29 en el catálogo exportado), la referencia
de seguimiento y las tres skills descubiertas. El respaldo conserva DACL
protegida con los tres SID previstos, ZIP íntegro y fuente 0.1.4 intacta.

## Recuperación y conservación

La recuperación ensayada usa el gestor: retirar solo el registro identificado,
registrar la fuente 0.1.4 conservada e instalar el mismo selector. Comprobar
origen, habilitación, versión y contenido; reconciliar cambios concurrentes antes
de restaurar cualquier configuración. No ejecutar `plugin remove` ni borrar
fuentes, respaldos o cachés manualmente durante la actualización.

Evidencias privadas ignoradas: `.aikit/043-preparacion-0.1.5/` y
`.aikit/043-prueba-final-0.1.5/`. La aplicación habitual reservó
`.aikit/043-aplicacion-0.1.5/`, con configuración y respaldos privados; no publicar
ni añadir a Git. Preservar la candidata mientras sea origen activo del catálogo
y mantener la fuente anterior para recuperación.

Instalación, descubrimiento y reconocimiento efectivo por cada conversación son
resultados distintos. Los ensayos no acreditan que todas las sesiones abiertas
hayan leído las instrucciones nuevas ni sustituyen las verificaciones de la 043.
