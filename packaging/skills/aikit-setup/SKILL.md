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
bloques existentes si falta una decisión.

El ámbito global usa `CODEX_HOME` o `~/.codex`. El ámbito de proyecto usa
la raíz Git del directorio de trabajo actual. Si una preferencia está activa
en otro ámbito, indícalo cuando lo sepas. La retirada afecta solo al bloque
gestionado del ámbito elegido. Las reglas equivalentes en otros archivos o
ámbitos pueden seguir aplicándose.

Localiza la raíz del complemento instalado subiendo dos directorios desde
esta skill. Ejecuta con Node.js el [instalador incluido](../../installer/dist/cli.js).
Pasa la ruta del script como argumento separado y conserva el directorio de
trabajo actual. Para cada ámbito con cambios elegidos, ejecuta `install --global
--dry-run` o `install --project --dry-run`. Añade solo `--<id>` para activar o
actualizar y `--quitar-<id>` para retirar las preferencias elegidas. Omite ámbitos
sin selecciones, pues sin argumentos de preferencia el instalador aplica los
tres valores históricos. Comprueba el código de salida y el JSON. Muestra los
destinos y cambios previstos y, si la vista previa falla, detente e informa.

Cuando el usuario haya autorizado aplicar la selección y los permisos lo
permitan, ejecuta el mismo comando por ámbito sin `--dry-run`. Comprueba código
de salida y JSON. Comunica destinos y respaldos. Cada ámbito se aplica por
separado. Si falla uno, detente e informa de los ámbitos aplicados y de las
rutas de recuperación. Conserva los archivos y el estado del fallo.

Para comprobar el estado, lee el `AGENTS.md` del ámbito y localiza el par de
marcadores del bloque que corresponda al id en mayúsculas. Distingue bloque
presente, ausente o estado incierto (por ejemplo, marcadores inválidos o
`AGENTS.override.md`). Una vista previa compara el contenido con la selección
pedida y permite detectar actualizaciones pendientes. Comprueba de nuevo los
bloques tras cualquier aplicación autorizada. El resultado describe archivos
locales. Para afirmar que otra sesión usa la preferencia, comprueba que esa
sesión reconoce las instrucciones.

## Herramientas recomendadas

Sigue esta sección cuando el usuario solicite configurar AIKit en general
o pida consultar o configurar estas herramientas. Si pregunta por una
herramienta concreta, limita la consulta a esa herramienta.

Consulta [la lista de herramientas recomendadas](references/herramientas.md). Para cada una, consulta el gestor de complementos disponible y comprueba su identidad exacta, instalación, habilitación y ámbito. Las herramientas expuestas en este chat son evidencia de disponibilidad aquí, pero no bastan para afirmar que están instaladas globalmente. Si una consulta falla o es incompleta, comunica que el estado es desconocido; no lo confundas con ausente.

Informa de las herramientas ya instaladas y habilitadas. Para cada herramienta ausente o deshabilitada, explica su utilidad y propone la acción concreta; pide aprobación antes de instalarla o habilitarla, salvo que el usuario ya haya autorizado expresamente esa acción. No instales si la rechaza o si el estado o la identidad son inciertos.

Con aprobación, usa la capacidad disponible del cliente para instalar el complemento exacto y completar su conexión. Si el cliente solo permite presentar una sugerencia o requiere interacción del usuario, hazlo e informa de lo que falta; no simules instalación. Vuelve a consultar el estado y confirma instalación y ámbito solo con evidencia. Indica si es necesario iniciar otro chat para disponer de las herramientas. Una herramienta que ya esté instalada y habilitada no se reinstala.

No actives Delegating to OpenCode. No exijas ni actives metodologías o herramientas de terceros como requisito general de AIKit; respeta las preferencias y el contexto de cada proyecto.
