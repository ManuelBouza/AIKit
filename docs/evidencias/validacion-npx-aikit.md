# Validación del paquete local AIKit con npx

Fecha: 2026-11-07. Entorno: Windows, Node 24.22.1 y npm 11.19.1.

Se generó un tarball local con `npm pack` y se ejecutó mediante `npx --offline
--yes --package`, con caché npm y `CODEX_HOME` ficticios bajo `.aikit`. Un
archivo previo contenía una instrucción ajena. No se publicó ningún paquete ni
se utilizó el perfil real.

Resultados: vista previa `preview`; instalación `changed`; segunda instalación
`unchanged`; consulta `current`, versión 0.1.0. La instrucción ajena y ambos
bloques se conservaron; los respaldos previo y de Windows contenían el texto
original. El tarball contenía el ejecutable compilado, módulos de sustitución y
recuperación y las dos plantillas.

La prueba con `npx` cubre únicamente esta versión y entorno; no verifica la publicación,
actualización desde un registro remoto ni otras plataformas. No prueba
todos los tipos de ACL ni elimina los límites de concurrencia documentados en
`docs/diseno-replacefile-windows.md`.

El 2026-11-07 se ejecutaron la compilación TypeScript y la suite completa con
Node 20.0.0 y 20.20.2 en Windows: en cada versión, 26 pruebas aprobadas y dos
omitidas por falta de permisos para crear junctions. Las pruebas usan perfiles
ficticios e incluyen invocaciones del instalador.

Con Node 20.0.0 y npm/npx 9.6.4 se empaquetó y ejecutó el tarball local sin
conexión, con caché y perfil ficticios. `install` devolvió `changed` y `status`
devolvió `current` con versión 0.1.0. No se probó actualización desde registro
remoto ni se modificó el perfil real.
