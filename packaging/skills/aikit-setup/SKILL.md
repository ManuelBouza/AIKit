---
name: aikit-setup
description: Configura las preferencias de AIKit en el perfil global de Codex o en el proyecto actual y guía la coordinación local cuando el usuario solicita configurar AIKit.
---

# Configurar AIKit

Usa esta skill cuando el usuario solicite configurar AIKit. Instalar el complemento por sí solo no aplica las preferencias.

Presenta estas cinco preferencias y, por separado, la coordinación local descrita
más abajo. La coordinación no es una opción del instalador de preferencias.

- `--go`: propone la próxima tarea e interpreta `go` según las reglas de autorización.
- `--context7`: prioriza Context7 para documentación actualizada cuando corresponda.
- `--investigacion`: consulta documentación oficial y fuentes fiables antes de decidir cómo realizar una tarea.
- `--escritura`: usa el estilo del usuario para escritos en su nombre destinados a terceros; aprovecha `write-like-me` cuando esté disponible.
- `--visualizacion`: explica expresamente ambas situaciones al presentar esta opción: si se sugiere `visualize` sin petición previa, se solicita autorización antes de usarlo; si el usuario solicita expresamente la visualización, esa solicitud ya autoriza crearla dentro del alcance.

Para cada preferencia sin decisión explícita, pregunta si desea activarla, conservarla o desactivarla, y en qué ámbito: global, proyecto o ambos. Reúne las decisiones en una sola consulta cuando sea posible. No presupongas que ejecutar setup autoriza opciones que no se hayan elegido.

Para estas cinco preferencias, global usa `CODEX_HOME` o `~/.codex`; proyecto usa la raíz Git del directorio de trabajo actual. No sustituyas el directorio de trabajo del proyecto por el del complemento. Una opción sin decisión conserva cualquier bloque existente; no implica desactivarlo. Para desactivar explícitamente un bloque gestionado usa `--quitar-go`, `--quitar-context7`, `--quitar-investigacion`, `--quitar-escritura` o `--quitar-visualizacion`. La retirada no elimina instrucciones fuera del bloque y no garantiza desactivar reglas equivalentes en otros ámbitos o archivos.

Localiza la raíz del complemento instalado subiendo dos directorios desde esta skill. El instalador de estas preferencias requiere Node.js. Para cada ámbito con activaciones o desactivaciones elegidas, ejecuta una vista previa con `installer/dist/cli.js install --global --dry-run` o `install --project --dry-run`, añadiendo únicamente los argumentos de activación y retirada correspondientes. Si una preferencia está activa en otro ámbito, indícalo cuando lo sepas; no prometas su desactivación efectiva global. No ejecutes el instalador para ámbitos sin selecciones, pues sin argumentos de preferencia aplica las tres preferencias históricas por compatibilidad. Pasa la ruta del script como argumento separado y conserva el directorio de trabajo actual. Comprueba código de salida y JSON y muestra los destinos y cambios previstos. Si una vista previa falla o no es válida, detente e informa.

Cuando el usuario haya autorizado aplicar la selección y los permisos lo permitan, ejecuta por ámbito el mismo comando sin `--dry-run`. Comprueba el código de salida y el JSON; comunica destinos y respaldos. Si un ámbito falla, detente e informa cuáles se aplicaron y cualquier ruta de recuperación; no borres archivos ni reintentes automáticamente. No se garantiza atomicidad entre ámbitos.

## Coordinación del proyecto

Al explicar esta capacidad, aclara que el usuario continúa directamente con cada
Chat de Tarea. Con un encargo ejecutable autorizado y contexto comprobado, este
trabaja sin otra orden de arranque; aplica el filtro de impacto de coordinación
para reportar solicitudes accionables y conserva avances ordinarios para revisión.
El Coordinador gestiona dependencias e integración, sin intermediar cada paso.
Incluye su deber de notificar cambios relevantes a los chats afectados sin pedir
aprobación por cada aviso dentro de la autorización humana acordada. Ambos roles
envían solo ante acción o decisión operativa ahora, o riesgo que empeore al esperar;
actualizar el registro no justifica por sí solo activar otro chat. Al preparar
el contrato local, registra esa autorización y su evidencia, alcance y límites
de destinatarios y cauces; conserva una decisión ya vigente y pregunta solo si
falta una decisión material. Leer o activar la skill no inventa consentimiento
de mensajería. Los avisos informativos no reanudan tareas pausadas.

Presenta la coordinación como capacidad local para que un coordinador reparta
encargos, documente y reutilice Chats de Tarea y gestione avisos, integración y
cierre. No tiene ámbito global. Consulta
[coordinacion-chats](../coordinacion-chats/SKILL.md) y su referencia de
responsabilidades al preparar esta selección.

Comprueba las instrucciones locales y el registro existente para identificar
raíz canónica, coordinador vigente, modalidad y estado real. Informa si está
activa, ausente o no se puede determinar; una skill instalada o un nombre de
chat no demuestran activación. No crees un registro o coordinador duplicados.
Si no hay decisión explícita, pregunta si desea activar, conservar o revisar la
coordinación en este proyecto; una solicitud de setup no elige por sí sola.
Reúne esta elección con las demás cuando proceda, respetando decisiones previas.

La ruta actual es guiada y manual, no un flag de `installer/dist/cli.js`.
No ejecutes ese instalador si solo se ha elegido coordinación. No exige Git,
Node.js, BMAD ni el auxiliar experimental para operar manualmente. Antes de
aplicar, identifica raíz local absoluta y coordinador autorizado y acuerda el
formato y límites del registro manual, alcance y cauces de comunicación, usando
la estructura mínima de la referencia de responsabilidades: contrato de proyecto,
asignaciones y avisos/acuses con referencias recuperables. Si no
hay contrato, prepara una propuesta concreta con esos datos, destinos y cambios
en instrucciones locales y registro, y solicita la decisión que falte. Conserva
las instrucciones ajenas, respaldos necesarios y cualquier registro previo.

Con las decisiones y aplicación autorizadas, realiza solo esos cambios mediante
las herramientas disponibles. Relee los archivos y comprueba que la identidad,
raíz única y modalidad coincidan; comunica destinos, respaldo y resultado real.
Separar «archivos aplicados y releídos» de «instrucciones reconocidas en la sesión
destino»: lo segundo requiere evidencia verificable de lectura y reconocimiento
de raíz, coordinador y modalidad por esa sesión, según capacidades del cliente.
Si exige una sesión nueva, informar de esa comprobación pendiente sin crearla
automáticamente. Si no puedes escribir, facilita el contenido para aplicación
manual; si puedes escribir pero no acreditar reconocimiento, conserva los cambios
autorizados e informa de la validación pendiente. No afirmes activación verificada
solo porque se guardaron archivos. La activación por sí sola no inicia chats,
envíos, archivados ni automatizaciones. Una notificación requiere además un
cambio que supere ese filtro, destinatario contrastado y autorización humana aplicable.

Si se solicita desactivar, concreta antes cómo detener nuevas asignaciones y
conservar tareas, entregas y registro; no borres historial ni retires reglas por
inferirlo de otra selección. Este setup no implementa un ciclo automático de
alta, relevo y retirada del registro ni garantías del auxiliar v1.

## Herramientas recomendadas

Consulta [la lista de herramientas recomendadas](references/herramientas.md). Para cada una, consulta el gestor de complementos disponible y comprueba su identidad exacta, instalación, habilitación y ámbito. Las herramientas expuestas en este chat son evidencia de disponibilidad aquí, pero no bastan para afirmar que están instaladas globalmente. Si una consulta falla o es incompleta, comunica que el estado es desconocido; no lo confundas con ausente.

Informa de las herramientas ya instaladas y habilitadas. Para cada herramienta ausente o deshabilitada, explica su utilidad y propone la acción concreta; pide aprobación antes de instalarla o habilitarla, salvo que el usuario ya haya autorizado expresamente esa acción. No instales si la rechaza o si el estado o la identidad son inciertos.

Con aprobación, usa la capacidad disponible del cliente para instalar el complemento exacto y completar su conexión. Si el cliente solo permite presentar una sugerencia o requiere interacción del usuario, hazlo e informa de lo que falta; no simules instalación. Vuelve a consultar el estado y confirma instalación y ámbito solo con evidencia. Indica si es necesario iniciar otro chat para disponer de las herramientas. Una herramienta que ya esté instalada y habilitada no se reinstala.

No actives Delegating to OpenCode. No exijas ni actives metodologías o herramientas de terceros como requisito general de AIKit; respeta las preferencias y el contexto de cada proyecto.

## Seguimiento del proyecto

Presenta separadamente el seguimiento local de ideas y tareas. Consulta
[seguimiento](../coordinacion-chats/references/seguimiento.md) antes de proponer
altas. Detecta primero el tracker canónico; reutilízalo sin duplicar fuentes.
La instalación no activa ni migra. La selección es guiada, sin nuevo flag del
instalador. Con decisión explícita, fija raíz, identidad, fuentes y generación
y verifica lectura, escritura y salida en el alcance autorizado; conserva
estado previo ante fallo. Explica herramientas ausentes, traslado manual y
visibilidad pendiente sin afirmar sincronización ni imponer Python/BMAD/Git.
