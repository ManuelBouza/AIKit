# Tablero local de notas

Desde PowerShell en la raíz del repositorio, prepara el entorno con
`uv sync --locked`. Después genera y abre la vista de consulta con:

```powershell
uv run --locked python scripts/tablero_notas.py
```

Para regenerar sin abrir el navegador, añade `--sin-abrir`. El archivo generado
está en `.aikit/tablero-notas/index.html`, ignorado por Git. El tablero incluye
los cambios locales sin commit y muestra su fecha de generación. Vuelve a ejecutar
el comando después de cambiar las notas; no se actualiza automáticamente.

El índice `notas/IDEAS.md` es la fuente de las tarjetas. Las secciones del índice
son agrupaciones históricas y el estado detallado se reproduce literalmente. Las
notas se muestran con formato, pero sus enlaces e imágenes se presentan como
texto con sus rutas para evitar abrir destinos o cargar contenido externo.
El tablero no edita archivos ni ejecuta acciones y no implica aprobar tareas.

Una fila inválida, una ruta insegura o una nota inexistente abortan la generación;
se informa el error, se conserva la última salida y no se abre como si fuera nueva.
La preparación inicial de dependencias puede requerir red; una vez sincronizado
el entorno, el generador y la página no necesitan conectarse a Internet.

## Ideas y tareas conectadas

La misma instantánea incluye la vista Tareas desde
`coordinacion/tareas/<IMP-id>/TAREA.md`; la identidad se contrasta con
`coordinacion/PROYECTO.md`. La raíz de lectura es la raíz explícita del proyecto,
no el cwd. El lector no escribe registros. El Coordinador mantiene los tickets;
las tareas solicitan cambios por el cauce acordado. No hay un segundo índice
editable: las relaciones inversas entre ideas y tickets se calculan al generar.

Las tarjetas abren un diálogo centrado: el foco pasa al título, Tab recorre sus controles y Escape o Cerrar lo cierran. Al cerrar, el foco vuelve a la tarjeta de origen o, si ya no está visible, al selector de vista. Los botones de relaciones cambian el detalle sin borrar los filtros. En pantallas estrechas las tarjetas forman una columna y el contenido ancho se desplaza dentro del diálogo.

La búsqueda de Ideas abarca número, título, estado y resumen; la de Tareas abarca identificador, título, responsable, fase, atención y origen. Si no hay coincidencias, «Limpiar filtros» permite recuperarlas. Tareas filtra fase, atención, responsable e idea. El detalle muestra alcance,
aceptación, chat, autorización, dependencias y evidencias. Sus botones enlazan
ideas y dependencias dentro de la página; las referencias no abren rutas ni red.
Completar una entrega no completa su idea ni otros tickets del mismo chat.
Regenera también después de editar tickets y recarga cualquier página abierta.

El contrato v1 está en
`_bmad-output/specs/spec-seguimiento-ideas-tareas/datos-y-flujo.md`.
Metadata desconocida, fechas o tipos inválidos, claves duplicadas, rutas inseguras,
ideas inexistentes, dependencias ausentes o ciclos abortan antes de publicar.
La publicación usa reemplazo atómico del único HTML; un error devuelve código
no cero, conserva sus bytes anteriores y no abre esa salida como nueva.
No se garantiza transacción entre los archivos fuente ni frescura continua.
La fecha acredita generación desde el estado incorporado, no consulta reciente
de cada chat. Puede haber novedades ordinarias pendientes: el Coordinador las
recoge en revisión pertinente sin activar tareas solo para refrescar el tablero.

Setup reutiliza un tracker canónico existente y requiere acuerdo local y pruebas
para activar esta modalidad. El complemento distribuye la referencia de flujo,
no este runtime ni datos de proyecto. Instalar no activa ni migra el seguimiento.

## Regresión DOM reproducible (opcional)

La prueba compartida `tests/test_tablero_notas_dom.py` genera dos ideas y tres
entregas ficticias en un directorio temporal, sin leer los tickets reales.
Comprueba teclado, filtros de fase/atención/responsable/idea, ciclo de foco del diálogo en escritorio y móvil y navegación explícita entre ideas y dependencias aunque
los filtros actuales excluyan el destino. Comprueba ausencia de errores JS y de
peticiones externas. Usa Playwright y un navegador ya instalados: no descarga
componentes ni añade requisitos al runtime del tablero. Si Playwright no está
disponible, pytest indica la omisión. Un navegador no disponible hace fallar la
comprobación para no declarar validación sin evidencia.

En este checkout con las herramientas aisladas existentes:

```powershell
$env:AIKIT_PLAYWRIGHT_PATH = (Resolve-Path .aikit/browser-test-deps).Path
$env:AIKIT_REQUIRE_DOM = '1'
$env:AIKIT_BROWSER_EXECUTABLE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
uv run --locked pytest tests/test_tablero_notas_dom.py
```

Con `AIKIT_REQUIRE_DOM=1`, la prueba falla si Playwright no está disponible en vez de omitirse; comprueba también que pytest no indique omisiones. No se modifica la verificación global.

En otro entorno, omite AIKIT_PLAYWRIGHT_PATH si Playwright ya es importable, y
ajusta AIKIT_BROWSER_EXECUTABLE al navegador instalado. Sin esa variable se usa
Edge en Windows y Chromium instalado en los demás sistemas. No se instala nada.
La comprobación necesita permiso para lanzar el navegador; este sandbox de
Windows requiere ejecutar la prueba fuera de él con autorización aplicable.

El contrato `Raíz canónica` de PROYECTO.md identifica el directorio `coordinacion`
absoluto de este proyecto y se contrasta antes de leer tickets. Una copia en un
worktree no se convierte en fuente canónica. Si el contrato declara seguimiento
local y falta `coordinacion/tareas`, la generación falla y conserva el HTML;
un proyecto heredado sin seguimiento puede continuar mostrando solo notas.
