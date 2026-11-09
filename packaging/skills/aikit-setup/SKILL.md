---
name: aikit-setup
description: Configura las preferencias de AIKit en el perfil global de Codex o en el repositorio actual cuando el usuario solicita configurar AIKit.
---

# Configurar AIKit

Usa esta skill cuando el usuario solicite configurar AIKit. Instalar el complemento por sí solo no aplica las preferencias.

Si el usuario no ha indicado el ámbito, pregunta si desea configurarlo globalmente o en el repositorio actual. Global usa `CODEX_HOME` o `~/.codex`; proyecto usa la raíz Git del directorio de trabajo actual. No sustituyas el directorio de trabajo del proyecto por el del complemento.

Localiza la raíz del complemento instalado subiendo dos directorios desde la carpeta de esta skill. Requiere Node.js. Ejecuta el instalador incluido en `installer/dist/cli.js` con `install --global --dry-run` o `install --project --dry-run`, según el ámbito. Pasa la ruta del script como argumento separado y conserva el directorio de trabajo actual. Comprueba el código de salida y el JSON; muestra al usuario el destino y los cambios previstos. Si la vista previa falla o no es válida, detente e informa el error.

Cuando la solicitud del usuario ya autorice aplicar la configuración y los permisos del entorno lo permitan, ejecuta el mismo comando sin `--dry-run`. Comprueba que el código de salida sea cero y que el JSON indique `changed` o `unchanged`; comunica la ruta y los respaldos devueltos. Si falla o la salida es inválida, informa el error y cualquier ruta de recuperación; no borres archivos ni reintentes automáticamente. Respeta las instrucciones y permisos aplicables.

## Herramientas recomendadas

Consulta [la lista de herramientas recomendadas](references/herramientas.md). Para cada una, consulta el gestor de complementos disponible y comprueba su identidad exacta, instalación, habilitación y ámbito. Las herramientas expuestas en este chat son evidencia de disponibilidad aquí, pero no bastan para afirmar que están instaladas globalmente. Si una consulta falla o es incompleta, comunica que el estado es desconocido; no lo confundas con ausente.

Informa de las herramientas ya instaladas y habilitadas. Para cada herramienta ausente o deshabilitada, explica su utilidad y propone la acción concreta; pide aprobación antes de instalarla o habilitarla, salvo que el usuario ya haya autorizado expresamente esa acción. No instales si la rechaza o si el estado o la identidad son inciertos.

Con aprobación, usa la capacidad disponible del cliente para instalar el complemento exacto y completar su conexión. Si el cliente solo permite presentar una sugerencia o requiere interacción del usuario, hazlo e informa de lo que falta; no simules instalación. Vuelve a consultar el estado y confirma instalación y ámbito solo con evidencia. Indica si es necesario iniciar otro chat para disponer de las herramientas. Una herramienta que ya esté instalada y habilitada no se reinstala.

No actives Delegating to OpenCode. BMAD solo se activa en los proyectos donde se necesite; no es una recomendación global de AIKit.
