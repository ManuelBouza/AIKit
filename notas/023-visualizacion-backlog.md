# 023 — Visualización y gestión de notas

- Fecha: 2026-11-13
- Estado inicial: Pendiente de debatir
- Estado actual: Tablero local implementado y verificado
- Actualización: generador local implementado; pruebas de navegador ejecutadas.

Manuel decidió conservar el backlog Markdown y no conectar otra herramienta de
gestión. Después propuso explorar una visualización propia mediante Sites, sin
construirla todavía y usando Director de Ideas.

## Exploración de Sites — 2026-11-13

La skill de Sites contempla páginas estáticas, aplicaciones con servidor y
almacenamiento; permite trabajo local o despliegue privado. Esto demuestra
opciones técnicas generales, no acceso automático a archivos locales del usuario
desde un sitio alojado. Cualquier alimentación de datos o sincronización debe
definirse y comprobarse. El backlog Markdown sigue siendo la fuente actual.

Inicialmente quedaba decidir si la vista permitiría cambios y cómo se
reflejarían en Git. El navegador no puede asumirse capaz de
modificar archivos del repositorio sin un mecanismo explícito. No se ha creado,
desplegado ni conectado ningún sitio.

## Decisiones del usuario — 2026-11-13

- El tablero será de consulta; Manuel solicitará cambios a Codex, que
  mantendrá las notas y el backlog Markdown como fuente de verdad.
- Se usará localmente en este PC, sin publicación. La forma de actualización,
  acceso y presentación concreta sigue por definir. Estas decisiones autorizan
  continuar el diseño, no construir el tablero todavía.

## Investigación de estructura — 2026-11-13

Las 23 notas usan nombres numerados estables, pero sus encabezados de fecha y
estado varían: `Estado`, `Estado actual` y listas Markdown, con descripciones
que pueden continuar en otra línea. `IDEAS.md` ya reúne número, enlace, estado
descriptivo e idea en tablas agrupadas. Algunos grupos son históricos y no
coinciden exactamente con cada estado; la nota 015 advierte que deben contrastarse.

Propuesta inicial: leer las filas del índice como fuente única del tablero,
usar número y ruta como identificador, mostrar literalmente título, estado y
resumen, y abrir el contenido de la nota al seleccionarla. No inferir estado a
partir del título de la sección ni reescribir la historia. Informar filas
inválidas, duplicadas o rutas ausentes y no presentar datos incompletos como
actuales. No se necesita modificar masivamente las notas para una primera vista.

Un generador local determinista puede crear una instantánea de solo lectura.
Una orden local la regeneraría y abriría; si falla, mostrar el error y conservar
la última instantánea identificada con su fecha de generación, sin ocultar que
puede estar desactualizada. El procedimiento exacto de apertura y la interacción
de rutas con el navegador se verificará en implementación. No requiere un modelo
para regenerarse. Un sitio alojado no es necesario para esta variante local.

## Propuesta de primera versión — 2026-11-13

- Abrir en el navegador del PC con una orden local; actualizar al abrir mediante
  un generador determinista, sin servicio permanente ni inferencia.
- Encabezado con nombre del tablero, hora de generación y número de notas.
- Vista de tarjetas agrupadas por las secciones existentes de `IDEAS.md`, con
  aviso de que son agrupaciones históricas; cada tarjeta muestra número, título,
  estado literal y resumen. No interpretar el grupo como estado adicional.
- Búsqueda local por número, título, estado y resumen, y filtro por sección;
  mostrar explícitamente cuando no haya coincidencias.
- Al seleccionar una tarjeta, mostrar el contenido de su nota en un panel de
  lectura. Tratar Markdown como datos no confiables y evitar ejecutar HTML o
  scripts incluidos en las notas; conservar sus rutas y evidencias originales.
- Detectar y comunicar número duplicado, fila no reconocida o nota ausente.
  Si falla la generación, informar y no abrir una salida antigua como actual.
- Diseño legible en ventana de escritorio y tamaños pequeños, navegación con
  teclado y texto seleccionable. No hay edición, publicación ni cuentas nuevas.

La salida es una instantánea local, no una base de datos adicional. La apertura
de enlaces locales y el contenido Markdown requieren validación real en el
navegador elegido. La selección de tecnología concreta y la construcción aún
no están autorizadas por este documento.

## Diseño técnico propuesto — 2026-11-13

1. Un script Python tipado de biblioteca estándar lee `notas/IDEAS.md` en
   UTF-8 y reconoce exclusivamente tablas de notas bajo secciones `##`. Valida
   número, ruta relativa dentro de `notas/`, unicidad y existencia; rechaza
   filas desconocidas en tablas de notas con diagnóstico de línea. No ignora
   entradas sin avisar. No modifica el índice ni las notas.
2. Lee cada nota y genera un único HTML autónomo en `.aikit/`, con datos
   incrustados de forma segura. El panel presenta Markdown con formato; debe
   seleccionarse y verificarse un renderizador que no ejecute HTML ni scripts
   procedentes de las notas. La interacción de enlaces debe comprobarse. El
   buscador y los filtros operan en el navegador sin peticiones de red.
3. Se escribe un temporal en el mismo directorio y se reemplaza la salida solo
   tras validar y terminar correctamente. En caso de error se informa, conserva
   la última instantánea y no se abre automáticamente. Se muestra hora con zona
   y se indica que refleja los archivos al generar, incluidos cambios sin commit.
4. Un comando explícito genera y abre el HTML con el navegador predeterminado.
   El generador no modifica configuraciones, no inicia servidores y no publica.
   Evitar lanzar ventanas de consola adicionales en Windows; comprobarlo durante
   la implementación. El modo sin apertura facilita pruebas y ejecución en CI.

### Plan de pruebas

- Pytest con archivos temporales: índice válido, secciones, UTF-8, duplicados,
  fila inválida, enlaces fuera de `notas/`, archivo ausente y directorio vacío.
- Casos con Markdown y texto que contengan HTML, `</script>` y caracteres
  especiales para comprobar que no ejecutan código ni alteran los datos.
- Error de lectura/escritura: diagnóstico, salida anterior preservada y ausencia
  de apertura automática; comprobar sustitución y fecha tras generación exitosa.
- Comprobar búsqueda, filtro, panel, navegación por teclado, legibilidad y
  ausencia de red en un navegador real; contrastar un subconjunto con el índice
  y las notas. Indicar explícitamente cualquier limitación del entorno.
- Ejecutar Ruff y mypy sobre el código nuevo. No repetir inferencia para mantener
  los datos; la generación solo consume recursos locales.

Manuel decidió mostrar Markdown con formato e incluir todas las notas, también
las de OpenCode, aunque su desarrollo permanezca pausado. Seleccionar y verificar
el renderizador es un paso técnico previo a la implementación. No implementar
todavía.

### Selección preliminar del renderizador — 2026-11-13

Se propone Mistune con `create_markdown(escape=True)` y soporte de tablas;
funciona en Python localmente una vez instalada la dependencia. Su documentación
indica que escapa HTML y bloquea protocolos inseguros por defecto, pero advierte
que no es un sanitizador general. No usar `mistune.html`, que no escapa HTML.
Controlar imágenes y enlaces externos, rutas locales e inserción de datos en el
HTML autónomo; verificar los casos adversos en pruebas antes de usarlo. Fijar
una versión compatible en el lock y comprobar instalación y funcionamiento sin
red tras la preparación. No se ha instalado ni ejecutado Mistune para esta tarea.

Fuentes: [modelo de seguridad de Mistune](https://mistune.lepture.com/en/latest/security.html)
y [API de Mistune](https://mistune.lepture.com/en/stable/api.html).

### Preferencia visual — 2026-11-13

Se mostró una propuesta interactiva con columnas por estado, búsqueda y detalle
de la nota seleccionada. Manuel indicó que así se ve muy bien. Se tomará como
referencia visual; las tarjetas de la demostración eran ejemplos y no estaban
conectadas a los datos reales. Los estados reales y su agrupación requieren
corresponderse con el índice sin inventar estados ni ocultar restricciones.

### Implementación local — 2026-11-13

Se añadieron `scripts/tablero_notas.py`, su plantilla HTML y pruebas. Mistune
3.4.0 quedó fijado en el lock; el generador lee 23 notas, muestra Markdown con
formato y presenta enlaces e imágenes como texto sin cargar recursos externos.
Instrucciones en `docs/tablero-notas.md`. En Windows se ejecutaron seis pruebas
de comportamiento, Ruff y mypy sobre los archivos nuevos. Una invocación del
control de navegador falló al inicializar el entorno; la revisión visual y la
interacción real quedan pendientes. No se publicó ni se inició un servidor.

### Hallazgos de revisión BMAD — 2026-11-13

Revisión independiente del cambio frente a esta nota; pendientes de corrección:

- [x] El lector puede omitir tablas o filas mal formadas sin avisar y generar
  una vista incompleta (`scripts/tablero_notas.py`).
- [x] El detalle muestra el texto de enlaces e imágenes pero descarta sus rutas,
  por lo que no conserva la referencia a evidencias.
- [x] Si el contenido incluye `__GENERATED__`, la sustitución posterior altera
  ese texto dentro de la nota renderizada.
- [x] Falta una prueba de interacción real que compruebe tarjetas, búsqueda,
  filtro y detalle; también faltan casos de error de escritura y apertura.

Las capas de revisión se repitieron con el diff en una ruta compartida después
de que el temporal original resultara inaccesible a los subagentes. El límite
de concurrencia exigió ejecutar la capa de aceptación después de las primeras.
No se ha probado visualmente el tablero ni se han corregido estos hallazgos.

### Correcciones — 2026-11-13

Se añadieron detección de notas ausentes del índice y filas fuera de tablas,
rutas de enlaces e imágenes como texto y sustitución del marcador antes de
insertar datos. Las pruebas cubren esos casos, el error de reemplazo y la
ausencia de apertura tras un fallo: 11 aprobadas; Ruff y mypy pasaron. Se
regeneró el tablero con 23 notas sin acceso a red. La prueba con Chrome y
Playwright en modo invisible no terminó de arrancar y se interrumpió; tampoco
fue posible inicializar el control del navegador. Sigue pendiente verificar
interacción, teclado y apariencia en un navegador real.

### Comprobación en navegador — 2026-11-13

En Windows se ejecutó Chrome invisible con Playwright: 23 tarjetas, búsqueda,
filtro, apertura de detalle con Enter, formato Markdown y ausencia de peticiones
HTTP o errores JavaScript. Se inspeccionaron capturas de escritorio y móvil. Se
corrigió el detalle obsoleto al filtrar y el desbordamiento en 375 píxeles; una
segunda prueba confirmó ambas correcciones. La comprobación es puntual, no una
prueba de navegador incorporada a la suite, y no cubre todos los navegadores.

## Objetivo

Manuel quiere consultar visualmente las notas y su avance, y que Codex pueda
tomarlas y desarrollarlas con un flujo similar al de un equipo de desarrollo.
Mantener trazabilidad con las notas Markdown, Git y los artefactos BMAD.

## Investigación inicial

GitHub Projects ofrece tablero, tabla y hoja de ruta para issues y solicitudes
de cambios, con campos y filtros configurables. El repositorio AIKit existente
es público. Un proyecto privado no vuelve privadas las incidencias de un
repositorio público. Debe decidirse qué información se publica antes de crear
incidencias; no trasladar automáticamente las notas.

Otras opciones son una vista local generada desde el backlog existente, que
conserva Git como fuente pero requiere mantener el generador y definir cómo
editar estados, o una herramienta externa con tablero, que introduce otra
integración y requiere evaluar acceso, coste y sincronización.

El backlog actual `notas/IDEAS.md` es canónico por la nota 015. Antes de usar
dos sistemas, decidir cuál registra el estado, cómo se reflejan cambios en el
otro, cómo se evitan duplicados y qué ocurre si falla la sincronización. Una
tarjeta o estado no constituye aprobación: se conserva el mecanismo `go`.

Para una prueba posterior, escoger pocas notas representativas, comparar
tablero y tabla, enlazar cada tarjeta con su nota y evidencia, y comprobar
permisos y acceso del agente antes de migrar. No crear, publicar o sincronizar
tarjetas como consecuencia de esta investigación.

Fuentes: [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects),
[vistas](https://docs.github.com/en/issues/planning-and-tracking-with-projects/customizing-views-in-your-project/changing-the-layout-of-a-view)
y [visibilidad](https://docs.github.com/en/issues/planning-and-tracking-with-projects/managing-your-project/managing-visibility-of-your-projects).
