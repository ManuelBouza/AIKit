---
name: aikit-setup
description: Configura las preferencias de AIKit en el perfil global de Codex o en el repositorio actual cuando el usuario solicita configurar AIKit.
---

# Configurar AIKit

Usa esta skill cuando el usuario solicite configurar AIKit. Instalar el complemento por sí solo no aplica las preferencias.

Presenta estas cinco preferencias y sus efectos:

- `--go`: propone la próxima tarea e interpreta `go` según las reglas de autorización.
- `--context7`: prioriza Context7 para documentación actualizada cuando corresponda.
- `--investigacion`: consulta documentación oficial y fuentes fiables antes de decidir cómo realizar una tarea.
- `--escritura`: usa el estilo del usuario para escritos en su nombre destinados a terceros; aprovecha `write-like-me` cuando esté disponible.
- `--visualizacion`: cuando se sugiera `visualize` sin petición previa, solicita autorización antes de usarlo; una solicitud expresa de la visualización ya la autoriza dentro del alcance.

Para cada preferencia sin decisión explícita, pregunta si desea activarla, conservarla o desactivarla, y en qué ámbito: global, proyecto o ambos. Reúne las decisiones en una sola consulta cuando sea posible. No presupongas que ejecutar setup autoriza opciones que no se hayan elegido.

Global usa `CODEX_HOME` o `~/.codex`; proyecto usa la raíz Git del directorio de trabajo actual. No sustituyas el directorio de trabajo del proyecto por el del complemento. Una opción sin decisión conserva cualquier bloque existente; no implica desactivarlo. Para desactivar explícitamente un bloque gestionado usa `--quitar-go`, `--quitar-context7`, `--quitar-investigacion`, `--quitar-escritura` o `--quitar-visualizacion`. La retirada no elimina instrucciones fuera del bloque y no garantiza desactivar reglas equivalentes en otros ámbitos o archivos.

Localiza la raíz del complemento instalado subiendo dos directorios desde esta skill. Requiere Node.js. Para cada ámbito con activaciones o desactivaciones elegidas, ejecuta una vista previa con `installer/dist/cli.js install --global --dry-run` o `install --project --dry-run`, añadiendo únicamente los argumentos de activación y retirada correspondientes. Si una preferencia está activa en otro ámbito, indícalo cuando lo sepas; no prometas su desactivación efectiva global. No ejecutes el instalador para ámbitos sin selecciones, pues sin argumentos de preferencia aplica las tres preferencias históricas por compatibilidad. Pasa la ruta del script como argumento separado y conserva el directorio de trabajo actual. Comprueba código de salida y JSON y muestra los destinos y cambios previstos. Si una vista previa falla o no es válida, detente e informa.

Cuando el usuario haya autorizado aplicar la selección y los permisos lo permitan, ejecuta por ámbito el mismo comando sin `--dry-run`. Comprueba el código de salida y el JSON; comunica destinos y respaldos. Si un ámbito falla, detente e informa cuáles se aplicaron y cualquier ruta de recuperación; no borres archivos ni reintentes automáticamente. No se garantiza atomicidad entre ámbitos.

## Herramientas recomendadas

Consulta [la lista de herramientas recomendadas](references/herramientas.md). Para cada una, consulta el gestor de complementos disponible y comprueba su identidad exacta, instalación, habilitación y ámbito. Las herramientas expuestas en este chat son evidencia de disponibilidad aquí, pero no bastan para afirmar que están instaladas globalmente. Si una consulta falla o es incompleta, comunica que el estado es desconocido; no lo confundas con ausente.

Informa de las herramientas ya instaladas y habilitadas. Para cada herramienta ausente o deshabilitada, explica su utilidad y propone la acción concreta; pide aprobación antes de instalarla o habilitarla, salvo que el usuario ya haya autorizado expresamente esa acción. No instales si la rechaza o si el estado o la identidad son inciertos.

Con aprobación, usa la capacidad disponible del cliente para instalar el complemento exacto y completar su conexión. Si el cliente solo permite presentar una sugerencia o requiere interacción del usuario, hazlo e informa de lo que falta; no simules instalación. Vuelve a consultar el estado y confirma instalación y ámbito solo con evidencia. Indica si es necesario iniciar otro chat para disponer de las herramientas. Una herramienta que ya esté instalada y habilitada no se reinstala.

No actives Delegating to OpenCode. No exijas ni actives metodologías o herramientas de terceros como requisito general de AIKit; respeta las preferencias y el contexto de cada proyecto.
