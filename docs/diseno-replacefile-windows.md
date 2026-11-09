# Sustitución de AGENTS.md en Windows

Estado: integrado experimentalmente para archivos existentes en Windows.

Para un archivo existente se prepara el contenido nuevo en el mismo
volumen y llamar a `ReplaceFileW` sin indicadores que ignoren errores de mezcla
de ACL. La API admite un respaldo del original y puede fallar dejando distintos
estados de los archivos; se deben informar las rutas conservadas y no borrar el
reemplazo ni el respaldo hasta identificar el resultado. La creación inicial de
un archivo inexistente necesita una ruta separada. La comparación previa y el
bloqueo cooperativo actuales no impiden todas las escrituras de otros programas.

Se invoca Windows PowerShell con un script fijo y rutas en el entorno para usar
`[System.IO.File]::Replace(reemplazo, destino, respaldo, $false)`. Si falla o la
salida no es verificable se conservan el bloqueo y los archivos de recuperación;
no se recurre silenciosamente a `rename`. Se han probado Windows PowerShell 5.1
y Node 24; quedan por verificar otras versiones y entornos.

El 2026-11-07 se ejecutaron dos pruebas aisladas en `.aikit` con PowerShell
7.6.9: ACL heredada y ACL con una regla explícita de lectura para el usuario
actual. En ambas `[IO.File]::Replace` conservó el SDDL observado, sustituyó el
contenido y creó el respaldo esperado. Esto no prueba todas las ACL, SACL,
volúmenes, errores parciales ni versiones de Windows; tampoco es una prueba del
instalador. No se modificó el perfil real.

Se automatizaron tres pruebas con Windows PowerShell 5.1: ACL heredada, regla
explícita, respaldo en rutas Unicode y rechazo con destino bloqueado. La última
verifica un fallo sin sustitución, no reproduce los errores parciales 1175,
1176 ni 1177 y no comprueba SACL. La suite se omite fuera de Windows o cuando
Windows PowerShell no está disponible.

El código actual de .NET para Windows llama a `ReplaceFileW` con cero indicadores
cuando `ignoreMetadataErrors` es `false`; esto no demuestra por sí solo el
comportamiento de todas las versiones de .NET Framework o PowerShell.

El módulo experimental `packages/aikit-installer/src/replace-recovery.ts`
clasifica observaciones de rutas tras fallos con respaldo: 1175 y 1176 con
destino y reemplazo presentes; 1177 con respaldo y reemplazo presentes y destino
ausente. Ante diferencias, rutas inaccesibles o códigos desconocidos declara el
estado no verificado. Solo informa: no restaura, borra ni reintenta, y la
distribución observada no demuestra contenido ni identidad. El instalador usa
este diagnóstico al fallar la sustitución. Las pruebas simulan esos estados;
no provocan los errores parciales reales de Windows.

El fallo real por destino bloqueado se probó a través del instalador: conserva
original, temporal y bloqueo y devuelve el diagnóstico. Quedan por verificar la
distribución, las variantes de PowerShell y los fallos parciales reales; la
comparación previa no evita todas las escrituras concurrentes de otros procesos.

Fuentes: [ReplaceFileW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew),
[File.Replace](https://learn.microsoft.com/en-us/dotnet/api/system.io.file.replace),
[implementación Windows de .NET](https://github.com/dotnet/runtime/blob/main/src/libraries/System.Private.CoreLib/src/System/IO/FileSystem.Windows.cs),
[interoperabilidad ReplaceFileW](https://github.com/dotnet/runtime/blob/main/src/libraries/Common/src/Interop/Windows/Kernel32/Interop.ReplaceFile.cs).
