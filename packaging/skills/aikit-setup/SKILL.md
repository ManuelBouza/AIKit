---
name: aikit-setup
description: Ayuda a descubrir las capacidades de AIKit y a configurar sus preferencias globales o de proyecto y sus flujos locales cuando el usuario lo solicita.
---

# Configurar AIKit

Lee el [inventario de capacidades](references/capacidades.json) antes de
presentar AIKit o tramitar una selección. Usa el propósito y la ruta de cada
entrada. Resuelve las rutas del inventario desde la raíz del complemento.

Adapta el recorrido a la solicitud. Para descubrir AIKit, presenta el inventario
o explica la capacidad preguntada. Para configurar AIKit en general, presenta
las opciones y reúne las decisiones pendientes. Para configurar capacidades
concretas, tramita solo esas selecciones y pide solo los datos que falten
para aplicarlas. Una consulta informativa termina tras explicar lo solicitado.

Distingue si el complemento está instalado, si esta sesión puede usar una skill
y si una preferencia o un flujo está configurado en su ámbito. Comprueba
instalación y disponibilidad con la evidencia que ofrezca el cliente.
Indica qué estados quedan por comprobar cuando esa evidencia falte.

- `preferencia`: presenta las opciones gestionadas de abajo. El id da el
  argumento y la ruta apunta a su plantilla.
- `guiada`: presenta el alcance del proyecto y lee el flujo indicado en
  `ruta` para comprobar el estado o preparar cambios. Si figura `skill`, usa
  sus instrucciones especializadas. Reúne las decisiones pendientes de los
  flujos elegidos con las de las preferencias cuando proceda.
- `skill`: explica cómo acceder a la skill cuando el cliente la exponga. Lee
  su ruta para aplicar el flujo solicitado. Para esta categoría basta el
  descubrimiento y uso en el chat. Carece de un ajuste de activación global
  o de proyecto.

## Preferencias gestionadas

Para cada preferencia incluida en la configuración sin decisión explícita,
pregunta si desea activarla,
conservarla o desactivarla, y en qué ámbito (global, proyecto o ambos).
Reúne las decisiones en una sola consulta cuando sea posible. Conserva los
bloques existentes si falta una decisión. Si el inventario indica un único
ámbito, ofrece solo ese ámbito.

El ámbito global usa `CODEX_HOME` o `~/.codex`. Las preferencias con plantilla
usan la raíz Git del directorio de trabajo actual para el ámbito de proyecto.
La responsabilidad única de los chats acepta una raíz local sin Git. Aplica
su [flujo de configuración](references/flujos/responsabilidad-chats.md)
para resolver la raíz local y la del inventario compartido. Si una preferencia está activa
en otro ámbito, indícalo cuando lo sepas. La retirada afecta solo al bloque
gestionado del ámbito elegido. Las reglas equivalentes en otros archivos o
ámbitos pueden seguir aplicándose.

Localiza la raíz del complemento instalado subiendo dos directorios desde
esta skill. Ejecuta con Node.js el [instalador incluido](../../installer/dist/cli.js).
Pasa la ruta del script como argumento separado y conserva el directorio de
trabajo actual. Para cada destino con cambios elegidos, ejecuta `install --global
--dry-run` o `install --project --dry-run`. Añade solo `--<id>` para activar o
actualizar y `--quitar-<id>` para retirar las opciones elegidas. Para Space
incluye el enlace según las instrucciones de abajo. Incluye los
argumentos de raíz que indique el flujo de chats. Agrupa las selecciones de
un mismo ámbito en una invocación cuando apunten al mismo `AGENTS.md`. Si
apuntan a archivos distintos, muestra ambos destinos y prepara un comando
por archivo. Omite ámbitos sin selecciones, pues sin argumentos de
preferencia el instalador aplica los tres valores históricos. Comprueba
el código de salida y el JSON de todos los comandos de vista previa antes de
aplicar cambios. Muestra los destinos y cambios previstos y, si una vista
previa falla, detente e informa.

Cuando el usuario haya autorizado aplicar la selección y los permisos lo
permitan, prepara la estructura de Space si forma parte de la selección. Luego
ejecuta el mismo comando por destino sin `--dry-run`. Comprueba código
de salida y JSON. Comunica destinos y respaldos. Si falla uno, detente e
informa de los destinos aplicados y de las
rutas de recuperación. Conserva los archivos y el estado del fallo.

Para comprobar el estado, lee el `AGENTS.md` del ámbito y localiza el par de
marcadores del bloque que corresponda al id en mayúsculas. Distingue bloque
presente, ausente o estado incierto (por ejemplo, marcadores inválidos o
`AGENTS.override.md`). Una vista previa compara el contenido con la selección
pedida y permite detectar actualizaciones pendientes. Comprueba de nuevo los
bloques tras cualquier aplicación autorizada. El resultado describe archivos
locales. Para afirmar que otra sesión usa la preferencia, comprueba que esa
sesión reconoce las instrucciones.

### Notas y memoria del proyecto en Space

Resuelve el Space antes de previsualizar. Reutiliza el enlace configurado
cuando proceda. Si el usuario da un nombre, localízalo con Pages. Si da un
enlace, comprueba con Pages que identifica la página raíz. Lee la raíz,
respeta sus instrucciones aplicables y toma su enlace canónico. Si el destino
es ambiguo, pregunta cuál debe usar el proyecto.

Lee la [plantilla de Space](../../installer/templates/space.md) para saber qué
cuatro entradas de memoria preparar. Prepara también el registro «Tareas»
según el apartado de abajo. Lista las subpáginas directas de la raíz, siguiendo
la paginación, y revisa los enlaces de la portada. Comprueba el propósito de las
páginas candidatas. Si ya existe una entrada equivalente, reutilízala. Si hay
varias candidatas válidas para una misma entrada y la portada no identifica
cuál usar, resuelve esa ambigüedad antes de escribir.

En la vista previa, muestra qué páginas se reutilizarán o crearán y qué
enlaces se añadirán, incluido el registro «Tareas». Ejecuta
`install --project --space <URL-raíz> --dry-run`
para comprobar el cambio local. Con la activación autorizada y la vista previa
correcta, usa Pages para crear únicamente las entradas que falten como
subpáginas de la raíz. Usa una clave de idempotencia estable por Space y
entrada, y conserva la misma clave si reintentas. Añade a cada una una frase
que explique qué guardar allí, según la plantilla. Asegura que la portada
enlace a cada entrada y añade los enlaces que falten bajo **Notas y memoria
del proyecto**. Conserva el
contenido, la jerarquía y los permisos existentes. Si ya hay una sección que
cumple esa función, completa esa sección. Usa lecturas recientes y los
mecanismos de control de cambios y reintentos de Pages. Si una escritura da
un resultado incierto, comprueba lo guardado antes de repetirla.

Comprueba que las cuatro entradas de memoria y el registro de tareas estén
enlazados en la portada y se puedan editar. Luego ejecuta el instalador local sin
`--dry-run`. Informa por separado del estado de la estructura y del bloque
en `AGENTS.md`. Al actualizar una preferencia ya activa, conserva el resumen
de estado que exista. La plantilla indica cuándo actualizarlo durante el
trabajo del proyecto.

Si Pages no permite comprobar o preparar la estructura,
deja pendiente la activación de Space y explica el punto que falta. Conserva
los cambios confirmados para que un reintento pueda reutilizarlos. Si el
usuario aprobó otras preferencias en la misma selección, vuelve a
previsualizar y aplica esas selecciones sin el argumento de Space.

Para la retirada, usa `install --project --quitar-space --dry-run` y el flujo
local de arriba. La retirada deja disponibles las páginas y sus contenidos.
El enlace configurado puede verse si se distribuye el `AGENTS.md`.

#### Registro de tareas en Space

Busca primero en la portada un enlace al registro de tareas. Si su página
pertenece al Space elegido y cumple esa función, úsala como registro del
proyecto. Si falta el enlace, busca entre sus subpáginas directas una entrada
«Tareas» o equivalente. Lee las candidatas antes de elegir. Si hay más de un
registro válido o una página con ese nombre tiene otra función, aclara el
destino antes de crear o cambiar páginas.

Cuando falte el registro y la activación esté autorizada, crea una subpágina
«Tareas» con una clave de idempotencia estable por Space. Incluye una tabla
editable vacía con **ID y resultado esperado**, **Estado**, **Siguiente
acción o bloqueo** y **Evidencia de cierre**. Añade una guía breve sobre el
uso de IDs estables y los estados **Pendiente**, **En curso**, **Hecha** y
**Cancelada**. En bloqueos o esperas conserva la fase e indica qué permitiría
reanudar. Al cerrar una tarea, registra el resultado o enlaza la evidencia.

Enlaza el registro desde la sección de tareas de la portada. Si no existe
esa sección, añade **Tareas** con el enlace. El resumen se actualiza desde
el registro y muestra trabajo activo, bloqueos y cierres recientes. Si el
registro ya existe, conserva sus filas, formato, título y resumen. Verifica
que el enlace llega a la página elegida y que se puede editar. Si falta
acceso, deja pendiente la preparación de Space según el flujo de arriba.

## Herramientas recomendadas

Sigue esta sección cuando el usuario solicite configurar AIKit en general
o pida consultar o configurar estas herramientas. Si pregunta por una
herramienta concreta, limita la consulta a esa herramienta.

Consulta [la lista de herramientas recomendadas](references/herramientas.md). Para cada una, consulta el gestor de complementos disponible y comprueba su identidad exacta, instalación, habilitación y ámbito. Las herramientas expuestas en este chat son evidencia de disponibilidad aquí, pero no bastan para afirmar que están instaladas globalmente. Si una consulta falla o es incompleta, comunica que el estado es desconocido; no lo confundas con ausente.

Informa de las herramientas ya instaladas y habilitadas. Para cada herramienta ausente o deshabilitada, explica su utilidad y propone la acción concreta; pide aprobación antes de instalarla o habilitarla, salvo que el usuario ya haya autorizado expresamente esa acción. No instales si la rechaza o si el estado o la identidad son inciertos.

Con aprobación, usa la capacidad disponible del cliente para instalar el complemento exacto y completar su conexión. Si el cliente solo permite presentar una sugerencia o requiere interacción del usuario, hazlo e informa de lo que falta; no simules instalación. Vuelve a consultar el estado y confirma instalación y ámbito solo con evidencia. Indica si es necesario iniciar otro chat para disponer de las herramientas. Una herramienta que ya esté instalada y habilitada no se reinstala.

No actives Delegating to OpenCode. No exijas ni actives metodologías o herramientas de terceros como requisito general de AIKit; respeta las preferencias y el contexto de cada proyecto.
