# AIKit 0.1.6 — avisos por impacto operativo

Fecha: 2026-11-17.
Estado: actualización privada instalada y descubrimiento verificado en el perfil habitual.
Encargo: [IMP-0007](../coordinacion/tareas/IMP-0007/TAREA.md).
Contenido funcional aceptado: `af67aa79b64749d5f8fd3e51ba7197e223b0d162`;
manifiesto de distribución actualizado a 0.1.6.

## Aplicación habitual — 2026-11-17

El Coordinador ejecutó el helper exacto aceptado por la revisión previa:
`404705db65a63eb1265752267daf68b3c6679bb37adbd6455f00f5270fb6ffca`.
Preflight, respaldo privado y los tres pasos del gestor terminaron con código0.
El resultado identifica el perfil real `C:/Users/Manuel/.codex`, versión0.1.6,
fuente activa `.aikit/044-actualizacion-0.1.6` y tres skills habilitadas
descubiertas. Los 28 archivos instalados coinciden con la candidata.

La revisión posterior independiente aceptó configuración e instrucciones
conservadas, fuente0.1.5 intacta, respaldo de configuración y ZIP íntegros y
DACL protegida con los tres SID previstos. La única diferencia TOML permitida
es el origen del catálogo privado. La caché0.1.5 ya no está; la secuencia usa
únicamente el gestor y no realiza borrado manual. Se conserva su fuente y ZIP
para recuperación. Sin setup ni inferencia; no acredita lectura de las
instrucciones por todas las conversaciones abiertas.

Evidencia privada: `.aikit/044-aplicacion-0.1.6/resultado.json` y
`.aikit/044-revision-0.1.6/post-aplicacion.md`, este último SHA256
`e01e84bffb48b6fa51bee2393301e417e513016800d42599c3a535876a3528cc`.
La candidata es ahora fuente activa y no se debe limpiar como temporal.

## Cambio distribuido

El filtro 044 compartido por Coordinador y Chats de Tarea exige identificar una
acción o decisión operativa del receptor, o un riesgo que empeore si se espera,
antes de activar otro agente. Los avances ordinarios se conservan para la siguiente
revisión pertinente; informar por informar o actualizar el registro no justifica
por sí solo un envío. Se mantienen las solicitudes necesarias de coordinación,
revisión, integración, preservación y cierre.

El Coordinador consulta evidencias e historiales accesibles cuando corresponde,
sin pedir mensajes que repitan datos disponibles. El tablero representa el estado
incorporado y no promete consulta reciente de cada chat. Se conserva la autonomía
de las tareas, la autoridad del usuario y el registro canónico único. No se añaden
servicios, buzones, vigilancia, automatizaciones ni canales de comunicación.

La instalación no reanuda los chats 028/040 ni justifica avisos informativos sin
acción pendiente. No ejecuta setup, activa proyectos nuevos o prepara BMAD.
Alcance y aceptación funcional: [nota 044](../notas/044-notificaciones-por-impacto-y-coste.md)
y [validación de la mejora](validacion-avisos-044.md). Esta preparación comprueba
la distribución del contenido ya aceptado, sin implementar otras ideas ni repetir
su revisión técnica.

## Identidad y contenido exportado

- Versión del manifiesto fuente y candidata: 0.1.6.
- Selector conservado: `aikit-preferencias@aikit-setup-prueba-20261108`.
- Fuente activa instalada: `C:/Manuel/Projects/AIKit/.aikit/044-actualizacion-0.1.6`.
- Fuente anterior preservada: `C:/Manuel/Projects/AIKit/.aikit/043-actualizacion-0.1.5`.
- Estado habitual previo comprobado: selector habilitado, fuente anterior y caché 0.1.5.
- Desktop observado: 26.1111.2228.0; CLI incluida: `codex-cli 0.169.0-alpha.11.1`.

La exportación contiene exactamente los **29 archivos** de la lista explícita:
28 del plugin y el catálogo. Cada contenido coincide con la fuente revisada,
incluido el manifiesto versionado; solo cambia el nombre del catálogo exportado
para mantener la identidad privada instalada. Se incluyen las tres skills y las
referencias de coordinación, incluido seguimiento; no se copian tickets, notas,
datos canónicos, evidencias privadas ni runtime del tablero.

Se consultaron de nuevo la [documentación oficial de empaquetado](https://developers.openai.com/plugins/build/plugins)
y los [comandos de desarrollo](https://learn.chatgpt.com/docs/developer-commands?surface=cli).
También se comprobaron versión y ayuda de la CLI incluida con un perfil ficticio.
El procedimiento usa sus comandos locales observados, no instala desde todo el
checkout ni publica un catálogo público.

## Ensayos comprobados

Sin inferencia ni nuevas dependencias; cada perfil ficticio tiene su propio
`CODEX_HOME` bajo la evidencia privada:

1. Instalación nueva de 0.1.6: registro del catálogo e instalación correctos.
2. Instalación 0.1.5 y migración a 0.1.6: mismos selector y habilitación.
3. Descubrimiento mediante app-server y `skills/list` con recarga: tres skills
   habilitadas desde caché 0.1.6, sin errores y con todos los archivos idénticos
   a la candidata.
4. Recuperación del perfil de migración a 0.1.5: instalación, descubrimiento y
   contenido correctos; el perfil de instalación nueva conserva 0.1.6.
5. Ensayo completo del helper de aplicación en otro perfil y destino nuevos:
   DACL protegida y tres SID autorizados, respaldo de configuración y ZIP de
   caché verificado antes de cambiar el registro; después, comparación TOML
   con solo el cambio previsto de origen, instrucciones y fuente anterior
   conservadas, archivos iguales y descubrimiento correcto.
6. Perfil habitual, AGENTS.md y fuente/caché 0.1.5: hashes iguales a la captura
   inicial después de los ensayos.

La variante ensayada solo sustituye las rutas `PROFILE` y `E` del helper real.
Su resultado identifica el perfil ficticio; la salida genérica «actualización
habitual» del script no acredita una aplicación al perfil habitual.

Se conserva el arreglo verificado de `PSModulePath`: se retira únicamente del
entorno del hijo Windows PowerShell, con errores terminantes y comprobación de
código y descriptor. No se modifica el entorno global ni se rebajan las guardias.
Véase la explicación documentada en la [entrega 0.1.3](actualizacion-aikit-0.1.3.md).

## Helper aplicado y límites

Helper habitual **revisado y ejecutado con código0**: `.aikit/044-aplicar-paquete016.py`.
SHA-256: `404705db65a63eb1265752267daf68b3c6679bb37adbd6455f00f5270fb6ffca`.

El helper exige CLI exacta, fuente anterior, selector y candidata de 29 archivos
con hashes esperados. Reserva una carpeta exclusiva y verifica su DACL antes de
copiar datos sensibles: solo usuario, SYSTEM y Administradores, sin ACE heredadas
y con control total. Verifica el ZIP antes de retirar el registro del catálogo
identificado, registrar la fuente nueva e instalar el mismo selector.

Comprueba después versión, ruta de caché, habilitación, instrucciones, fuente
anterior y configuración ajena. La comparación TOML solo admite el cambio de
origen del catálogo. Descubre las tres skills con recarga, sin setup ni inferencia.
Ante un fallo conserva fase y evidencia y se detiene; no reintenta ni restaura
configuración a ciegas. La secuencia de cambios no es una transacción atómica.

Instalación, descubrimiento y lectura efectiva en conversaciones abiertas son
resultados distintos. Estos ensayos no prueban recepción por los chats pausados,
transporte silencioso ni ahorro cuantificado de inferencia o tiempo.

## Recuperación y conservación

Recuperación ensayada mediante gestor: retirar únicamente el registro identificado,
registrar la fuente 0.1.5 conservada e instalar el mismo selector; comprobar origen,
versión, habilitación y contenido. Reconciliar cambios concurrentes antes de
restaurar cualquier configuración. No usar `plugin remove` ni borrar manualmente
cachés, fuentes o respaldos como parte de esta actualización.

Evidencia privada ignorada: `.aikit/044-preparacion-0.1.6/` y
`.aikit/044-prueba-final-0.1.6/`. La aplicación habitual reservó
`.aikit/044-aplicacion-0.1.6/`, con configuración y respaldos privados: no publicar
ni añadir a Git. Preservar la candidata mientras sea origen activo del catálogo
y conservar la fuente anterior para recuperación. El gestor puede retirar la
caché anterior al instalar; la recuperación no depende de que esta permanezca.
