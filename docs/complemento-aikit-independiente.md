# Complemento AIKit independiente

Este paquete contiene las preferencias `go`, Context7 e investigación previa,
sin MCP ni skill de
delegación. Su identidad `aikit-preferencias` es distinta de la histórica
`aikit`. La coexistencia, actualización y migración entre ambas no se han
validado. Conserve el complemento y configuración históricos hasta decidir y
probar la migración.

La skill `director-de-ideas` ayuda a madurar ideas y aclarar decisiones antes de
materializarlas. No exige BMAD ni reemplaza las autorizaciones vigentes. Su
selección automática y convivencia con otras skills aún requieren verificación.

Desde el repositorio fuente, instale las dependencias de compilación y construya
un catálogo en una ruta nueva. Se necesitan Node.js y npm en el constructor:

```powershell
npm ci --prefix packages/aikit-installer
python scripts/build_aikit.py --output <directorio-nuevo>
```

El README exportado acompaña al paquete; el constructor solo está en el
repositorio fuente. Para probar la instalación en un perfil ficticio, en una
sesión PowerShell use rutas absolutas y registre el directorio del catálogo:

```powershell
$env:CODEX_HOME = "C:/ruta/absoluta/perfil-ficticio"
$catalogo = "C:/ruta/absoluta/catalogo-exportado"
codex plugin marketplace add $catalogo
codex plugin add aikit-preferencias@aikit-preferencias-local
```

Use una sesión de proceso aislada para evitar cambiar el perfil habitual. El
paquete exportado está en `$catalogo/aikit-preferencias`.
Instalar el complemento no instala por sí mismo instrucciones en `AGENTS.md`.
El manifiesto declara la skill `aikit-setup` como `onboardingSkill`: el usuario
puede iniciar la configuración después de instalar. La skill selecciona ámbito
global o proyecto y ejecuta el instalador Node incluido en una sola operación.
La ejecución gráfica de este recorrido no está verificada; descubrir los
metadatos y ejecutar los instaladores por CLI no demuestra que la interfaz lo
inicie correctamente. El setup agrega la preferencia de Context7 y consulta las
herramientas recomendadas. Si Context7 falta, propone instalarlo y requiere
aprobación; según el cliente, completar la instalación puede requerir interacción
del usuario. No ejecuta OpenCode.

Para un perfil ficticio aislado, pruebe el instalador incluido con Node:

```powershell
node "$catalogo/aikit-preferencias/installer/dist/cli.js" install --global --dry-run
node "$catalogo/aikit-preferencias/installer/dist/cli.js" install --global
```

Para el proyecto actual use `install --project` desde el repositorio Git; primero
pruébelo en uno ficticio. Las operaciones conservan el contenido ajeno, crean respaldos cuando cambian el
archivo y son idempotentes; rechazan marcadores inválidos y un
`AGENTS.override.md` no vacío. Compruebe el resultado y los respaldos antes de
usar cualquier perfil. La instalación global automática no está verificada.
La retirada selectiva de bloques gestionados se prueba en perfiles ficticios;
la desinstalación completa y la migración permanecen pendientes; desinstalar el complemento no garantiza retirar bloques.
La evidencia de CLI previa está en el repositorio fuente, en
`_bmad-output/specs/spec-complementos-independientes/instalacion-y-migracion.md`.
# Preferencia de investigación

El instalador incluye un bloque gestionado que prioriza documentación oficial y
fuentes especializadas cuando aporten valor antes de experimentar, manteniendo
las pruebas necesarias para verificar resultados. Una instalación anterior debe
actualizarse y ejecutar setup para aplicar el nuevo bloque.

## Preferencias opcionales de comunicación

Al ejecutar `aikit-setup`, el usuario elige para cada preferencia si se aplica
globalmente, al proyecto, a ambos o a ninguno. Las opciones son `--go`,
`--context7`, `--investigacion`, `--escritura` y `--visualizacion`. El
instalador acepta una selección por invocación y ámbito; setup ejecuta una por
ámbito con selecciones. Usa `--dry-run` para revisar los cambios. Por
compatibilidad, una invocación sin opciones de preferencia aplica `go`, `context7` e
`investigacion`: no la
uses para representar «ninguna». Los bloques sin decisión se conservan. Para retirar un bloque gestionado de un
ámbito, usa `--quitar-go`, `--quitar-context7`, `--quitar-investigacion`,
`--quitar-escritura` o `--quitar-visualizacion`, con vista previa y respaldo.
La retirada no elimina reglas equivalentes en otros archivos o ámbitos. Las aplicaciones a varios ámbitos no son atómicas.
La escritura utiliza `write-like-me` si está disponible sin exigir instalación;
la visualización sugerida requiere autorización previa, mientras que una petición
expresa ya la autoriza dentro de su alcance. Estas instrucciones dependen del
cliente y de sus prioridades; las pruebas no demuestran su cumplimiento en una
conversación real.

Cobertura consultada: `write-like-me` busca referencias de estilo y puede continuar
sin muestras adecuadas; `visualize` crea visualizaciones en conversación. Ambas
capacidades cubren su ejecución; las plantillas solo expresan las preferencias
que faltaban, sin duplicar ni instalar esas skills.

Validación (Windows, 13-11-2026): `npm test` con perfiles y repositorios
ficticios: 40 pruebas correctas y dos omitidas por no poder crear junctions;
`pytest tests/test_build_aikit.py`: 15 correctas, incluyendo exportación y
divergencias. Se esperaba preservar el contenido ajeno y las opciones no elegidas,
rechazar marcadores inválidos y evitar respaldo al repetir; así se observó. No
se ha probado el comportamiento conversacional ni la aplicación efectiva de las
instrucciones en clientes; no se modificó el perfil real.
