# Instalador experimental de AIKit

Paquete local privado; todavía no está publicado y no existe un comando `npx`
público. En Windows se ha probado con Node 20.0.0, 20.20.2 y 24.22.1. Para
probarlo desde este checkout, use un
directorio de perfil ficticio:

```powershell
npm ci --prefix packages/aikit-installer
npm run build --prefix packages/aikit-installer
node packages/aikit-installer/dist/cli.js install --codex-home RUTA_FICTICIA --dry-run
node packages/aikit-installer/dist/cli.js install --codex-home RUTA_FICTICIA
node packages/aikit-installer/dist/cli.js status --codex-home RUTA_FICTICIA
npm test --prefix packages/aikit-installer
```

También se ha verificado el paquete local con `npx` sin conexión. Tras crear un
directorio temporal y generar el tarball, puede probarse así:

```powershell
npm pack ./packages/aikit-installer --pack-destination DIRECTORIO
$env:CODEX_HOME = 'RUTA_DE_PERFIL_FICTICIO'
npx --offline --yes --package 'RUTA_DEL_TARBALL.tgz' aikit install --dry-run
npx --offline --yes --package 'RUTA_DEL_TARBALL.tgz' aikit install
npx --offline --yes --package 'RUTA_DEL_TARBALL.tgz' aikit status
```

Use una terminal de prueba para que `CODEX_HOME` no afecte otras operaciones.
Esta es una prueba de un paquete local, no una instalación pública desde npm.

El código fuente es TypeScript estricto; el paquete npm contiene el JavaScript
generado. `npm ci` instala únicamente las dependencias de desarrollo necesarias
para compilar y probar el proyecto.

Sin `--codex-home`, el destino es `CODEX_HOME` o `~/.codex`. La vista previa
devuelve la ruta y el contenido anterior y posterior; la instalación informa
de versión y respaldo en JSON. El estado compara los bloques y lee el marcador
de versión, que no acredita la autoría del contenido. La actualización vuelve a
ejecutar `install` desde la versión deseada del paquete; la obtención de versiones
y su publicación no están implementadas.

Se rechazan enlaces y junctions reconocidos por Node; se verificaron junctions
reales en Windows. Esto no garantiza detectar todos los puntos de reanálisis.
Un bloqueo evita instalaciones simultáneas de AIKit y se comprueba si el
archivo cambió antes de sustituirlo. No impide que un editor externo escriba
entre esa comprobación y la sustitución. Si queda un archivo
`.aikit-instructions.lock` tras una interrupción o un fallo de sustitución,
compruebe que no hay una instalación activa y examine los archivos y respaldos
indicados en el diagnóstico antes de retirarlo manualmente. Un fallo de
`File.Replace` mantiene también el archivo temporal y los respaldos existentes;
no intente de nuevo antes de determinar qué archivo contiene sus instrucciones.

En Windows se usa `File.Replace` para archivos existentes, con una copia previa
y un respaldo adicional `windowsBackup` generado por Windows. Esta vía pretende
conservar las ACL, pero no se han verificado todas sus variaciones. En sistemas
POSIX se conservan los bits de modo, pero no se garantiza preservar todos los
metadatos. No se ha verificado la compatibilidad fuera de Windows.
