# AIKit: complemento e inicio de configuración

Decisión de Manuel: el complemento AIKit distribuye sus procedimientos y skills.
Una skill de inicio, invocada por el usuario desde Codex, selecciona el ámbito
global o del proyecto y ejecuta un instalador determinista para revisar y aplicar
las preferencias. El instalador TypeScript existente es la base a reutilizar;
se conserva `npx` como vía alternativa, no como requisito para el usuario de la
interfaz del complemento. La distribución se limita inicialmente a sus PC.

El ámbito global apunta a `CODEX_HOME/AGENTS.md` o `~/.codex/AGENTS.md`; el de
proyecto, a `AGENTS.md` de la raíz Git actual. La skill debe aclarar el ámbito
cuando no esté indicado, mostrar la ruta, ejecutar el script y comunicar
resultado y respaldos. El script conserva contenido ajeno, valida conflictos,
ofrece vista previa y mantiene el comportamiento seguro de recuperación. No
debe asumir que instalar el complemento ejecuta la configuración.

Estado actual: el complemento de prueba se visualizó en Codex Desktop y mostró
`Aikit Setup`; no se ha demostrado que el botón de la interfaz lo invoque. La
skill existente usa dos instaladores Python globales por separado; el instalador
TypeScript dispone de pruebas y respaldo, pero aún carece de selección de ámbito
proyecto. Su comportamiento de sustitución y recuperación Windows tiene límites
documentados en `docs/diseno-replacefile-windows.md`.

Trabajo preparado para implementación:

1. Adaptar el instalador TypeScript para ámbito global o raíz Git del proyecto,
   con vista previa, rechazo fuera de Git y pruebas de override, respaldos,
   conflictos e idempotencia. Determinar y probar respaldo del proyecto fuera de
   rutas versionables sin alterar la configuración ajena.
2. Adaptar el constructor del complemento para incluir el instalador compilado,
   plantillas y recursos necesarios sin incluir Delegating to OpenCode. Documentar
   y verificar el requisito de Node en cada equipo.
3. Actualizar `aikit-setup` tras revisar las instrucciones aplicables de creación
   de skills: selección de ámbito, ruta, ejecución determinista, verificación de
   salida y recuperación de errores. No instalar Context7 ni activar OpenCode.
4. Probar el paquete instalado con perfiles y repositorios ficticios, incluidos
   fallos; verificar de forma separada la invocación real desde Codex Desktop.
   Una captura o descubrimiento de la skill no demuestra que se haya ejecutado.
5. Documentar instalación y actualización del complemento privado en otros PC;
   no prometer sincronización automática ni publicar en npm.

Avance: el instalador incluye selección global/proyecto y el constructor exporta
su versión compilada con la skill actualizada. Las pruebas automatizadas usan
perfiles ficticios; la invocación real de la nueva versión en Codex Desktop y
la distribución privada en otro PC siguen sin verificarse. El complemento de
prueba instalado anteriormente no se ha actualizado con estos cambios.

Referencias históricas: `docs/distribucion-personal-aikit.md`,
`_bmad-output/specs/spec-instalador-aikit-npx/SPEC.md` y
`_bmad-output/implementation-artifacts/verificacion-onboarding-aikit.md`.
La decisión actual sustituye la preferencia anterior por npx como interfaz
principal, sin borrar esas pruebas ni reescribir especificaciones históricas.

## Herramientas recomendadas — 2026-11-09

El setup consulta una lista ampliable de herramientas recomendadas. Primero
comprueba identidad, instalación, habilitación y ámbito; luego propone las
acciones necesarias y las realiza solo con aprobación explícita. Context7 es la
única recomendación inicial y su ámbito deseado es global. BMAD se activa solo
en proyectos donde se necesite. Una sugerencia o solicitud de conexión no prueba
instalación: se vuelve a consultar el estado. Si el cliente exige interacción,
se informa al usuario y se deja el resultado como pendiente. Este flujo no
cambia las preferencias ni instala herramientas sin la aprobación necesaria.
