# Paquete AIKit 0.1.2 preparado para el perfil habitual

Actualización posterior, 2026-11-16: [0.1.3 instalada y verificada](actualizacion-aikit-0.1.3.md).
Este documento conserva el historial de la entrega 0.1.2.

Fecha: 2026-11-16.
Estado: actualización aplicada al perfil habitual; instalación y descubrimiento verificados.
Fuente: commit `92935edb9045db7eeccb34ec4ff4fce2af035252`.

## Resultado de aplicación — 2026-11-16

Aplicación autorizada por Manuel mediante go tras la preparación. Preflight
confirmó CLI y versión de Desktop, selector habilitado, origen 0.1.1 y hashes de
los 28 archivos de la candidata. Se respaldaron config.toml y la caché anterior
en una carpeta privada con ACL limitada al usuario, SYSTEM y Administradores;
el ZIP de caché se verificó contra sus hashes antes de cambiar el registro.

Marketplace remove/add y plugin add terminaron con código 0. El resultado
identifica la versión 0.1.2 y su ruta esperada. Todos los archivos instalados
coinciden con la candidata. La comparación TOML solo permite el cambio de origen
del catálogo identificado; el resto de la configuración y los hashes de AGENTS.md
global y del proyecto permanecen iguales.

App-server con el perfil habitual y skills/list forceReload confirma habilitadas
aikit-setup, coordinacion-chats y director-de-ideas desde la caché 0.1.2.
Sin inferencia, onboarding ni activación de otros proyectos. Este descubrimiento
no demuestra aún el comportamiento en una tarea real ni que el inventario de
esta conversación se haya recargado automáticamente.

El gestor retiró la caché 0.1.1; se conservan su fuente completa y el ZIP privado
verificado para recuperación. La fuente de 0.1.2 debe conservarse como origen
del catálogo activo, no limpiarse como temporal prescindible.

Evidencias privadas ignoradas:
`C:/Manuel/Projects/AIKit/.aikit/025-aplicacion-0.1.2/`. Contienen respaldo de
configuración, ZIP de caché, hashes, resultados y transcript del descubrimiento.
No publicar ni incluir en Git. Piloto en AIKit y prueba en otro proyecto pendientes.

## Identidad y contenido preparados — inventario anterior a la aplicación

- Instalado y habilitado según configuración y manifiesto de caché: 0.1.1.
- Selector conservado: `aikit-preferencias@aikit-setup-prueba-20261108`.
- Catálogo actual: `C:/Manuel/Projects/AIKit/.aikit/025-actualizacion-0.1.1`.
- Candidata: `C:/Manuel/Projects/AIKit/.aikit/025-actualizacion-0.1.2`.
- CLI observada: 0.169.0-alpha.11.1, incluida en Desktop 26.1111.2228.0.
- Ejecutable: `C:/Program Files/WindowsApps/OpenAI.Codex_26.1111.2228.0_x64__2p2nqsd0c76g0/app/resources/codex.exe`.

El exportador independiente generó 28 archivos. Se comparó el conjunto completo
con su lista explícita y cada contenido con las fuentes; solo se ajustaron en la
salida la versión del manifiesto a 0.1.2 y el nombre del catálogo al ya instalado.
Se conservaron nombre del plugin y rutas internas. Incluye responsabilidades.md,
los avisos actualizados y la entrada local guiada en aikit-setup.

La versión del manifiesto en fuentes sigue siendo 0.1.0: esta candidata tiene
identidad de entrega propia y no debe regenerarse suponiendo que el exportador
hereda la versión o el nombre de catálogo de otra salida. No instalar desde el
checkout ni sustituir la candidata por una copia de toda la raíz.

SHA256 de los dos metadatos modificados:

- plugin.json: `dadadf679947cc89418c109465c66c3c8a6768b0030ed90d3f46b40831bfe84a`.
- marketplace.json: `d91b015a62f779ce7570b4f035c28872130eabb038f80ccfda2efb20ffc54c96`.

Los hashes de los 28 archivos están en la evidencia privada de preparación.
Conservar las fuentes 0.1.1 y 0.1.2 mientras sus catálogos se utilicen.

## Ensayos realizados

Todos los procesos de ensayo usaron CODEX_HOME de perfiles ficticios bajo
`.aikit/025-preparacion-0.1.2/`; no se copiaron credenciales ni configuración del
perfil habitual. Las variables solo se establecieron para el proceso.

1. Instalación nueva de 0.1.2 mediante marketplace add y plugin add: código 0.
2. Instalación ficticia de 0.1.1 y migración con remove/add del registro de
   catálogo y plugin add de 0.1.2: todos los códigos 0.
3. App-server con skills/list en ambos perfiles: las tres skills de AIKit están
   habilitadas desde las rutas de caché 0.1.2 esperadas; cada archivo instalado
   coincide con el paquete. Sin inferencia ni ejecución de onboarding.
4. Recuperación del perfil ficticio de migración a 0.1.1 mediante el gestor:
   código 0, selector habilitado, origen anterior y todos los archivos coincidentes.
   El otro perfil de instalación nueva conserva la candidata 0.1.2.
5. Hashes anteriores y posteriores de config.toml y AGENTS.md habituales, AGENTS.md
   del proyecto, fuente 0.1.1 y archivos de su caché: idénticos.

Una comprobación inicial se detuvo antes de modificar la candidata porque la
ruta del catálogo usa el prefijo Windows de ruta extendida y la comparación
de objetos Path lo consideró distinto. Se confirmó la identidad del directorio
con [os.path.samefile, documentado para Windows](https://docs.python.org/3/library/os.path.html#os.path.samefile).
No se cambió el destino ni se forzó una ruta alternativa.

Evidencias privadas ignoradas: `.aikit/025-preparacion-0.1.2/`, incluidos hashes,
resultados, salidas de comandos y transcripts del descubrimiento. No publicarlas.
No acreditan que un modelo haya leído o aplicado las instrucciones ni sustituyen
la prueba real de coordinación, archivado o integración.

## Procedimiento de aplicación utilizado

La ejecución aplicó únicamente la actualización del complemento siguiendo el
procedimiento preparado a continuación. No ejecutó setup ni activó otros proyectos;
tampoco modificó AGENTS.md. Se conserva el procedimiento como referencia de esa aplicación.

### Preparar y comprobar

1. Reconfirmar raíz habitual, ruta/versión de CLI, selector habilitado y origen
   actual 0.1.1. Comprobar que los hashes de la candidata coincidan con la evidencia.
   No aplicar si la identidad o el contenido difieren sin reconciliar el cambio.
2. Capturar de nuevo los hashes de configuración, instrucciones y caché, no usar
   esta instantánea como permiso para sobrescribir cambios posteriores.
3. Respaldar config.toml en ubicación privada con ACL limitada al usuario, SYSTEM
   y Administradores; conservar el inventario y fuente anterior. No mostrar su
   contenido ni incluirlo en Git. La copia de configuración no respalda la caché.
4. Preparar descubrimiento sin inferencia: app-server initialize/initialized y
   skills/list, siguiendo el intercambio ya usado en los perfiles de ensayo.
   Para la ejecución habitual usar su perfil explícito, sin heredar CODEX_HOME
   de los ensayos. Una escritura fuera del workspace requiere permiso efectivo.

### Cambiar el registro y actualizar

Ejecutar cada comando comprobando su código y salida antes del siguiente. Esta
secuencia está ensayada en el perfil ficticio; no es atómica. Las variables del
ejemplo afectan solo al proceso PowerShell que la ejecute.

```powershell
$env:CODEX_HOME = 'C:/Users/Manuel/.codex'
$cliAIKit = 'C:/Program Files/WindowsApps/OpenAI.Codex_26.1111.2228.0_x64__2p2nqsd0c76g0/app/resources/codex.exe'
& $cliAIKit plugin marketplace remove aikit-setup-prueba-20261108
# Comprobar éxito antes de continuar.
& $cliAIKit plugin marketplace add 'C:/Manuel/Projects/AIKit/.aikit/025-actualizacion-0.1.2'
# Comprobar éxito antes de continuar.
& $cliAIKit plugin add 'aikit-preferencias@aikit-setup-prueba-20261108' --json
```

No ejecutar plugin remove ni borrar cachés o fuentes. El gestor puede retirar la
versión antigua al actualizar: la recuperación se basa en la fuente conservada,
no en prometer que su caché permanezca disponible. El catálogo ajeno
`aikit-preferencias-local` y las demás preferencias deben permanecer intactos.

### Verificar y comunicar

- Comprobar versión 0.1.2 en caché, selector habilitado y origen de catálogo nuevo.
- Comparar todos los archivos instalados con la candidata, incluidas las dos
  referencias de coordinación y setup; consultar skills/list con recarga para
  verificar las tres skills habilitadas desde esa caché, sin inferencia.
- Comparar configuración TOML anterior y posterior: solo puede variar el origen
  del catálogo identificado. Instrucciones y configuración ajena deben conservarse.
- Informar por separado actualización instalada, descubrimiento por el cliente
  y comportamiento observado. Si este chat necesita recarga o una conversación
  nueva, indicarlo sin afirmar que ya usa las instrucciones nuevas.

## Recuperación ante fallo

Detenerse ante un error y conservar la salida. Inspeccionar primero el estado
resultante: no repetir plugin add ni sustituir config.toml a ciegas. Si procede
volver a 0.1.1, retirar únicamente el registro del catálogo identificado, registrar
`C:/Manuel/Projects/AIKit/.aikit/025-actualizacion-0.1.1` y ejecutar plugin add con
el mismo selector. Este retorno fue ensayado en el perfil ficticio.

Comprobar caché 0.1.1, archivos, origen, habilitación y configuración ajena. Si
hubo cambios concurrentes, reconciliarlos antes de restaurar una copia; no perderlos
para recuperar el complemento. Conservar tanto el respaldo como la candidata.

Después de una actualización aplicada y comprobada, preparar el piloto en AIKit
y luego la prueba en otro proyecto. La cobertura general automática de setup de
la nota 039 y la mejora del Director de Ideas de la nota 040 siguen pendientes.
