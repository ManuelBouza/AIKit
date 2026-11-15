# 027 — Revisión programada de la coordinación

- Fecha: 2026-11-14.
- Estado inicial: Pendiente de debatir.
- Estado actual: En debate; intención de automatización registrada.

Manuel indica que el proceso de coordinación se automatizará con una tarea
programada de Codex: revisará los estados y tomará las acciones pertinentes,
incluido el archivado de chats terminados. Desarrolla las notas
[025](025-coordinador-global-chats-autonomos.md) y
[026](026-archivado-chats-coordinacion.md).

La intención de automatizar cambia la hipótesis anterior de consulta únicamente
cuando Manuel interactúe con el coordinador. No define aún la frecuencia, el
destino de ejecución, todas las acciones permitidas ni autoriza crear o activar
una automatización concreta en este momento. Las decisiones materiales, creación
de chats, mensajes y acciones sensibles siguen sujetas a sus autorizaciones.

## Capacidades y límites investigados

La [documentación oficial](https://learn.chatgpt.com/docs/automations) indica que
las tareas programadas de escritorio pueden usar proyectos locales y skills; los
proyectos sin control de versiones se ejecutan directamente en su directorio. Para
acceder a archivos locales, el equipo y la aplicación deben estar encendidos. Una
tarea independiente crea un chat por ejecución; una tarea ligada a un chat usa su
contexto. La elección afecta a la acumulación de chats y sigue pendiente.

Las automatizaciones usan los permisos y sandbox disponibles. No está comprobado
que cada ejecución disponga de herramientas para listar o archivar chats, ni que
pueda escribir los registros sin conflictos con chats activos. Si una capacidad
falta o falla, debe informar sin fingir que actuó. La coordinación debe conservar
una vía manual para entornos sin programación; Codex y BMAD no son requisitos
universales de AIKit. No se ha creado ninguna automatización.

Antes de programar, definir estados, acciones autorizadas, exclusiones, cadencia,
tratamiento de errores, concurrencia y avisos; probar manualmente y revisar las
primeras ejecuciones, como recomienda la documentación oficial. No crear chats,
enviar mensajes ni aprobar cambios de alcance por mera detección automática.

## Propuesta de acciones por estado — 2026-11-14

La ejecución consulta el índice y los registros canónicos pertinentes. El título
visible es orientativo; no reemplaza el estado de `TAREA.md`. El coordinador no
escribe el estado de una tarea ya asignada ni revisa técnicamente sus entregas.

Actualización posterior: Manuel asigna al coordinador la revisión e integración
coordinada de los cambios solicitados por los chats, como en una PR. Esta revisión
de integración sustituye la exclusión anterior; los chats conservan sus propias
verificaciones. Véase la [nota 031](031-aislamiento-sin-git.md).

| Estado | Actuación propuesta |
| --- | --- |
| Preparada | Comprobar alcance, dependencias y si ya tiene chat. Presentar o preparar la selección conforme a los criterios acordados; el coordinador puede crear chats dentro de su autorización y las reglas efectivas del cliente. Evitar duplicados y no empezar el trabajo por cuenta del chat de tarea. |
| Esperando al usuario | Identificar la intervención requerida y comunicar novedades relevantes. No contestar por Manuel ni enviar instrucciones al chat sin autorización aplicable. |
| En curso | Consultar cambios significativos o entregas disponibles; no interrumpir ni cambiar el estado por una lectura puntual o por el título. |
| Bloqueada | Registrar administrativamente el impedimento y avisar si requiere intervención o cambió. No levantar el bloqueo ni decidir el alcance por el chat responsable. |
| Pausada | Respetar la pausa; no reanudar, reasignar ni crear trabajo derivado automáticamente. |
| Finalizada | El chat responsable persiste lo necesario y gestiona la limpieza autorizada según las herramientas utilizadas, informando de pendientes. El coordinador consulta la entrega y registra el acuse sin aprobarla; comprueba identidad y archiva el chat terminado si puede. |
| Cancelada | Tras la limpieza autorizada o el registro de pendientes, comprobar identidad e inactividad y archivar el chat; conservar historial y motivo. |

El usuario ha autorizado al coordinador a crear chats cuando lo considere
pertinente. La tarea programada debe respetar además las reglas efectivas de sus
herramientas; esa autorización no equivale a autorizar mensajes entre chats ni
acciones sensibles. Una decisión expresa de Manuel sobre alcance puede trasladarse
mediante la bandeja conforme a la nota 025, sin fingir que se ha recibido.

## Límites y fallos propuestos

- Una ejecución no debe depender de otra aún activa: impedir solapamientos o
  terminar informando, con recuperación verificable ante interrupción. Respetar
  los mecanismos de escritura compartida definidos para los registros; no suponer
  que la comprobación previa evita carreras.
- Verificar identidad y estado justo antes de archivar; si el chat sigue trabajando,
  el estado es incierto o hay discrepancia, no archivarlo y comunicar el motivo.
  Confirmar el resultado, conservar referencia y evitar repetir acciones ya hechas.
- Consultar solo lo necesario para detectar cambios y no copiar registros ni
  conversaciones. Guardar acuses administrativos y errores indispensables;
  informar de cambios relevantes, fallos o decisiones, no de cada revisión vacía.
- Si faltan archivos, capacidades, permisos o hay conflicto de escritura, conservar
  los datos, no inventar estados y notificar. El uso manual debe seguir siendo
  posible sin tarea programada o herramienta concreta.

Esta matriz es una propuesta para el diseño, no un permiso general para actuar
sobre chats existentes ni una automatización configurada. Quedan por decidir
cadencia, destino de ejecución y criterios para
seleccionar encargos preparados. Hay que probar el acceso a herramientas y la
sincronización en una ejecución programada real antes de afirmar que funciona.

## Selección de encargos y cancelaciones — 2026-11-14

### Propuesta para seleccionar tareas preparadas

1. Considerar solo encargos registrados como `Preparada`, con alcance suficiente,
   dependencias satisfechas, autorización vigente y sin chat responsable activo
   ni creación pendiente. Si falta información, reflejar la condición pendiente;
   no inventar alcance ni interpretar la existencia de una nota como autorización.
2. Aplicar primero la prioridad explícita fijada por Manuel y después las
   dependencias conocidas. Una tarea habilitadora puede preceder a su dependiente
   cuando la relación está registrada y ambas están autorizadas. No convertir el
   orden del índice, la antigüedad o una valoración automática en prioridad.
3. Si queda una única opción elegible o existe una prioridad explícita suficiente,
   el coordinador puede abrir el chat de acuerdo con su autorización y las reglas
   del cliente. Si hay varias opciones sin criterio suficiente o un conflicto de
   recursos, presentar las opciones y pedir a Manuel que decida; no crear una por
   elección arbitraria. La ausencia de capacidad para crear se trata manualmente.
4. Antes de crear, volver a comprobar identidad, asignación y dependencias bajo
   el mecanismo de coordinación aplicable. Una creación en curso con ID provisional
   no autoriza duplicar; resolver su resultado antes de reintentar. Estas medidas
   requieren pruebas de concurrencia y recuperación; no son garantía por sí solas.

#### Criterio propuesto ante recursos compartidos — 2026-11-14

Antes de seleccionar, comparar las responsabilidades y recursos conocidos de los
encargos elegibles y de los chats activos: archivos o registros que escribirán,
checkout o worktree, puertos, servicios y otros recursos exclusivos cuando se
conozcan. Compartir un proyecto no demuestra por sí solo que exista conflicto;
trabajar en ramas distintas tampoco garantiza que no lo haya. Identificar el
recurso y la operación que compiten cuando sea posible.

- Si no hay solapamiento conocido y las tareas y su inicio están autorizados,
  el coordinador puede organizar trabajo independiente sin convertir el número
  de chats en una prioridad ni superar los límites del cliente o del proyecto.
- Si compiten por un recurso exclusivo, aplicar una prioridad o secuencia que
  Manuel ya haya establecido; mantener pendiente la otra tarea, sin cambiar su
  estado canónico por cuenta del chat responsable. Si no existe tal decisión,
  presentar alternativas y su impacto y pedir a Manuel que elija.
- Si no se puede determinar si habrá conflicto, consultar o investigar el recurso
  antes de lanzar las tareas afectadas en paralelo. Avanzar con otras tareas
  independientes ya autorizadas cuando las haya; no declarar seguro un caso por
  falta de información.
- Ante prioridades igualmente válidas y recursos suficientes, una decisión de
  Manuel de ejecutar ambas permite hacerlo; si no se sabe si desea ese paralelismo,
  preguntar en vez de elegir una por antigüedad o iniciar ambas arbitrariamente.
  Revalidar las condiciones antes de crear un chat y evitar duplicar una creación
  cuyo resultado siga pendiente.

Ejemplos: dos tareas que solo leen el mismo archivo no tienen por ello conflicto
de escritura; dos tareas que modificarán el mismo registro canónico sí requieren
reparto o secuencia. La matriz es una propuesta de trabajo, no una garantía técnica
de detección exhaustiva ni una decisión ya aceptada.

Manuel pregunta por alternativas a worktrees en proyectos sin Git. Se recogen en
la [nota 031](031-aislamiento-sin-git.md); su elección y validación quedan abiertas.

### Propuesta para chats cancelados

Manuel aclara que cancelar requiere su autorización y que el chat responsable debe
efectuar la limpieza correspondiente con las herramientas disponibles y las
autorizaciones del proyecto. La cancelación no autoriza por sí sola acciones
sensibles que requieran una autorización específica. El chat registra qué limpió
y cualquier recurso pendiente o impedimento; no se presume limpieza completa.

Manuel acepta que el coordinador archive también un chat `Cancelada` cuando la
cancelación esté expresamente registrada por Manuel, el chat haya concluido la
limpieza autorizada o comunicado sus pendientes, esté inactivo y su identidad sea
inequívoca. Conservar motivo, estado e historial; archivar no elimina ni revierte
cambios. Si el chat sigue trabajando o hay dudas, informar y esperar a resolverlas;
no presumir que archivar detiene procesos.

Una eventual reapertura requiere una decisión de Manuel y un nuevo ciclo o encargo
relacionado, según se concrete; se puede localizar y desarchivar el chat anterior
cuando proceda. La decisión forma parte del diseño; no se ha archivado ningún chat
como consecuencia de ella.

## Frecuencia y destino propuestos — 2026-11-14

Para la primera implantación se recomienda una tarea programada vinculada al chat
coordinador del proyecto, con una revisión cada hora mientras la automatización
esté activa. Es una propuesta inicial, no una frecuencia acordada ni una garantía
de respuesta inmediata. Debe poder pausarse o modificarse y avisar solo ante
cambios relevantes, errores o decisiones necesarias. Evitar solapar ejecuciones.

La alternativa independiente inicia un chat por ejecución y separa sus resultados;
puede resultar útil si se desea aislamiento, pero acumula chats y no responde tan
bien al objetivo actual. La [documentación oficial](https://learn.chatgpt.com/docs/automations)
indica que una tarea dentro de un chat reutiliza su contexto; una independiente
inicia un chat por ejecución. La opción recomendada requiere verificar que el
coordinador conserve acceso a los registros y herramientas al ejecutarse.

Los archivos canónicos permanecen en la raíz local del proyecto. Si el ordenador,
la aplicación o el proyecto no están disponibles, no se presupone ejecución ni
recuperación automática de ciclos perdidos; se informa según la capacidad real.
Un proyecto sin tareas elegibles no justifica crear chats ni cambios. La frecuencia
debe poder elegirse para cada proyecto y el mecanismo manual debe seguir disponible.

La selección final de cadencia y destino necesita la decisión de Manuel. No se ha
creado ninguna automatización; antes de activarla deben concretarse y probarse el
prompt, permisos, ejecución sin solapamiento, acceso a chats y recuperación.

## Decisión de Manuel: frecuencia y relevo — 2026-11-14

- La tarea programada estará vinculada al chat coordinador. No se utilizará una
  tarea independiente que cree un chat nuevo por ejecución para este proceso.
- El setup preguntará al usuario la frecuencia deseada para cada proyecto, según
  su uso. Para el uso considerado por Manuel, una revisión diaria es suficiente;
  no se impone como frecuencia universal ni se ha acordado todavía una hora.
- Si se cambia el chat coordinador, la tarea programada debe apuntar al nuevo chat.
  El relevo conserva sus ajustes y evita que la automatización antigua siga
  ejecutándose en paralelo. Antes de confirmar el cambio hay que verificar el
  destino y comunicar cualquier fallo; si la herramienta no permite trasladarla,
  diseñar una sustitución controlada sin perder la configuración ni duplicar
  ejecuciones. La capacidad concreta de migración todavía no se ha comprobado.
- El setup debe respetar la activación explícita del proyecto y explicar las
  capacidades disponibles. En un entorno sin tareas programadas, la coordinación
  seguirá ofreciendo un modo manual; no exige Codex o un programador específico.

Esta decisión sustituye la recomendación anterior de revisar cada hora y resuelve
la elección de destino. No crea ni activa una automatización real; el horario,
permisos y pruebas siguen pendientes para una instalación concreta.

## Comprobación del relevo de la tarea programada — 2026-11-14

La [documentación oficial](https://learn.chatgpt.com/docs/automations) confirma
que una tarea puede estar vinculada a un chat y que las tareas pueden actualizarse,
pero no especifica en esa página si se puede cambiar el chat de destino de una
tarea existente. El contrato publicado en esta sesión permite crear una tarea
vinculada a un chat y consultar o actualizar automatizaciones; la representación
visible del esquema de actualización no demuestra que acepte cambiar el destino.
No se ha creado, actualizado ni ejecutado una automatización para esta comprobación.

Protocolo candidato de relevo: identificar la tarea exacta y el coordinador nuevo;
guardar su configuración y estado; pausar la ejecución anterior y comprobar que
no quede una ejecución activa; intentar actualizar el destino solo si la capacidad
está documentada o se verifica en una prueba aislada; comprobar destino y ajustes
antes de reactivar. Si no se puede actualizar, evaluar una sustitución vinculada
al nuevo chat, inicialmente pausada, manteniendo la anterior pausada hasta verificar
la nueva. Ante un fallo, conservar la configuración, evitar duplicados y comunicar
el estado real. La retirada de la antigua se decide según permisos y política;
no se presupone que se borre automáticamente.

Esto es una propuesta de recuperación, no un procedimiento validado: falta una
prueba real de cambio de destino o sustitución, y de los permisos y disponibilidad
de herramientas durante la ejecución programada. La automatización no se ha
activado para AIKit.

## Prueba aislada de cambio de destino — 2026-11-14

Con autorización de Manuel se crearon los chats locales `PRUEBA · Relevo
coordinador A` (`01a1dae3-efcf-7480-9f05-ce796ad4d6db`) y `PRUEBA · Relevo
coordinador B` (`01a1dae3-fed3-70b1-b4ad-65e0f8837074`). Se creó una tarea
programada ficticia pausada, `prueba-relevo-coordinador-pausada`, vinculada a A,
con instrucción de no hacer cambios. Su configuración confirmó estado pausado y
destino A. La herramienta aceptó actualizar el destino a B; la lectura posterior
de su configuración confirmó el mismo ID de automatización, destino B, estado
pausado y conservación del nombre, instrucción y frecuencia diaria de prueba.

Resultado: el cambio de destino de una tarea vinculada pausada funciona en este
entorno y versión para los valores probados; no hizo falta crear una sustitución.
No se activó ni ejecutó la tarea, por lo que no se ha comprobado que una ejecución
despierte el nuevo chat ni el comportamiento con una ejecución activa o un fallo.
Ambos chats y la automatización de prueba permanecen; esta última sigue pausada.
No hay una automatización de coordinación real activada por esta prueba.
