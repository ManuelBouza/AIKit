# Responsabilidades y selección del medio de trabajo

## Contrato del proyecto

La coordinación requiere una raíz canónica explícita y un único coordinador
vigente identificable. Antes de activar, acordar con el usuario raíz, identidad
del coordinador, modalidad del registro, cauces autorizados y alcance. Consultar
primero las instrucciones y el registro existentes; una omisión o un título no
acreditan que el proyecto carezca de coordinador. Si faltan decisiones esenciales,
explicarlas y conservar la preparación, sin crear otra autoridad o raíz canónica.
Instalar o leer la skill no activa el proyecto ni concede permisos.

La modalidad manual necesita un formato y límites acordados. Solo el coordinador
escribe el registro canónico; las tareas conservan sus avisos y entregas y le
solicitan su incorporación. No atribuir al Markdown garantías transaccionales ni
editar manualmente el registro del auxiliar experimental para simular su API.

Para acordar un registro manual nuevo, usar una estructura mínima reutilizable:

- Contrato de proyecto: raíz absoluta, coordinador y evidencia de su autoridad,
  modalidad manual, alcance, cauces autorizados y ubicación del registro;
  autorización humana verificable de notificaciones proactivas, con destinatarios
  y límites, cuando se use mensajería automática de coordinación.
- Asignaciones: referencia de tarea/encargo, responsable y chat identificado,
  alcance, estado, contexto y entrega relacionada; ciclo solo si está soportado.
- Avisos y acuses: original recuperable, origen contrastado, referencia estable,
  decisión de incorporación o pendiente, responsable y referencia del acuse.

Conservar esta información en documentos del proyecto con formato acordado, sin
imponer nombres de archivo o inventar IDs; preservar historial y pendientes. El
coordinador sigue siendo el único escritor, sin garantía técnica de exclusión.

## Roles

- **Coordinador:** mantiene visión global, asignaciones, dependencias y registro;
  comprueba identidad, alcance, permisos, evidencias y dictámenes exigidos;
  coordina integración, cierre, pendientes y archivado. Protege los datos finales
  y las ramas principales. Notifica cambios relevantes a los chats afectados
  dentro de la autorización humana vigente, sin consultar por cada aviso.
  No implementa ni hace code review: encarga la ejecución
  y la evaluación técnica a los responsables y revisores pertinentes.
- **Chat de Tarea:** ejecuta y verifica su encargo, decide detalles técnicos
  dentro del alcance, mantiene título y estado y conserva resultados y bloqueos;
  comunica los que superen el filtro de impacto siguiente.
  Interactúa directamente con el usuario para conducir ese trabajo y resolver
  las decisiones que le correspondan; no requiere intermediación rutinaria.
  Conserva entrega y evidencias, solicita integración y limpia recursos propios
  conforme a [avisos y acuses](avisos.md). No crea otros Chats de Tarea ni asume
  autoridad sobre el registro o las ramas principales.

Hay un mismo mecanismo para un chat con tarea concreta o propósito especializado.
El coordinador decide qué necesita el proyecto y lo documenta; no crear un catálogo
de especialistas permanentes por anticipado. La especialización no añade otro rol
de coordinación ni exige otro modelo o metodología.

## Selección y reutilización

Antes de crear, consultar el registro y los chats accesibles autorizados. Para
trabajo relacionado, comprobar identidad, alcance, estado y contexto vigente del
responsable existente y reutilizarlo cuando corresponda. Un nombre parecido no
acredita identidad; si no puede confirmarse, conservar esa decisión pendiente.
Comprobar recuperación de un chat archivado antes de prometer continuidad.

El coordinador documenta propósito, identidad o referencia manual comprobable,
alcance, estado, encargos relacionados y referencias recuperables de contexto.
Distinguir responsabilidad, conversación, encargo/ciclo y ejecución: una corrección
o un intento no requieren otro chat. La reutilización no amplía permisos o alcance;
el auxiliar actual no administra nuevos ciclos, reasignación ni relevo.

- Para coordinación, usar herramientas directamente y las skills pertinentes.
- Para investigación o revisión técnica acotada de una sola ejecución, considerar
  un subagente autorizado con resultado de retorno. No encadenar apoyos efímeros
  para ocultar una responsabilidad que necesita continuidad.
- Para implementación u otro encargo con iteraciones y seguimiento propios,
  asignar un Chat de Tarea. Mantener juntos los trabajos muy acoplados en su
  responsable; el coordinador no absorbe su ejecución por disponer de contexto.
- Dentro de una tarea, ejecutar comandos, pruebas y correcciones con herramientas
  en su chat; no abrir otro por cada paso. Respetar los apoyos nativos y reglas
  de delegación del entorno, sin sustituirlos con este mecanismo.

Solo el coordinador crea o asigna Chats de Tarea, usando capacidades disponibles
y autorizaciones efectivas del cliente. Si crear o recuperar devuelve resultado
incierto, conservar las referencias y reconciliar registro e inventario accesible
antes de reintentar o pedir otra apertura manual. Sin creación disponible, facilita
nombre específico y encargo para apertura manual. No inventar IDs. Sin Git,
secuenciar tareas de escritura; el usuario decide si necesita Git y worktrees
para paralelismo. Tener Git no basta: las escrituras paralelas requieren aislamiento
efectivo de los checkouts e índices, además de coordinación de recursos compartidos;
si no se dispone de él, secuenciar.
El aislamiento de contexto o del checkout no aísla recursos externos compartidos.

## Encargo y comunicación

Cada encargo necesita resultado y aceptación comprobables, alcance y exclusiones,
responsable, recursos permitidos, dependencias, verificaciones y referencias de
contexto. Añadir identidad de tarea/ciclo y chat cuando estén asignados, ubicación
de evidencias y cauce de envío/consulta. No copiar toda la conversación por defecto.
Si el cliente arranca el chat al crearlo, el encargo incluye primero comprobar
contexto, identidad, asignación, alcance y permisos. Si es ejecutable y ya está
autorizado, la tarea continúa al satisfacer esos requisitos sin una segunda orden
del Coordinador. Distinguirlo de una preparación que todavía no autorice ejecutar;
identificar qué falta y detener solo la operación que dependa de ello.
La preparación puede quedar pendiente de asignación sin inventarla.

La modalidad inicial de comunicación entre tareas es mediante el coordinador.
Cada tarea conserva su conversación directa con el usuario y dirige la ejecución
autorizada de su encargo. Traslada al coordinador novedades relevantes y necesidades
de otros trabajos; él coordina las dependencias y la integración del proyecto.
Mantener un responsable de cada paso. El traspaso distingue información,
solicitud de ejecución y decisión autorizada, indicando emisor, receptor, objetivo,
límites, referencias y destino de respuesta. No añade campos al aviso v1.

La comunicación directa entre tareas queda como posibilidad futura, pendiente
de límites y validación; no queda habilitada por leer estas instrucciones. Un
mensaje no concede autoridad humana ni cambia alcance automáticamente. Si el
usuario y el coordinador acuerdan una actualización, comprobarla y trasladarla
a las tareas afectadas por el cauce autorizado.

El usuario también puede autorizar decisiones o cambios de alcance directamente
en el Chat de Tarea. Conservar su origen y comunicar los que afecten al proyecto,
dependencias o integración. Coordinar antes de operar sobre recursos compartidos
o trabajo ajeno; continuar las partes propias independientes y autorizadas.
Ante instrucciones incompatibles, aclararlas antes de la operación afectada;
un mensaje informativo del Coordinador no reemplaza una decisión del usuario.

Aplicar el filtro siguiente también a hitos, bloqueos, cambios materiales,
integración y cierre; no enviar por el mero cambio de estado. Las herramientas
disponibles determinan si un mensaje activa al receptor; sin ellas ofrecer
traslado manual. Conservar evidencia y reconciliar antes de reenviar ante dudas,
según [avisos y acuses](avisos.md).
Un reporte o acuse pendiente no exige esperar para continuar trabajo independiente
autorizado. Detener solo la parte que dependa de una decisión, permiso o recurso
pendiente. Esta autonomía no garantiza ejecución permanente en segundo plano:
continuación y activación de turnos dependen de las capacidades del cliente.

## Filtro de impacto y recogida de novedades

Antes de enviar, identificar qué acción o decisión operativa necesita atender
ahora el destinatario, o qué riesgo empeora al esperar. Si no existe, conservar
la novedad sin activar otro chat. Ser breve o decir «no respondas» no evita el
coste de activación. Agrupar novedades que puedan esperar.

| Caso | Decisión |
| --- | --- |
| Push, commit, pruebas o actualización sin efecto operativo para el receptor | Conservar, no enviar. |
| Progreso o espera de decisión del usuario dentro de la tarea | Mantener evidencia, estado y título propios; recoger después. |
| Bloqueo resoluble dentro del alcance de la tarea | Resolver con herramientas o su usuario; no escalar por rutina. |
| Bloqueo que requiere recurso, permiso o decisión del Coordinador | Solicitud concreta con impacto y operación afectada. |
| Dependencia resuelta que habilita trabajo | Coordinador avisa a la tarea afectada. |
| Nueva entrega sin registro previo | Solicitar alta antes de implementarla; continuar trabajo independiente registrado. |
| Cambio humano transversal, conflicto compartido o riesgo de pérdida | Avisar al responsable antes de la operación afectada. |
| Entrega lista para revisión/integración | Solicitar acción con versión exacta, evidencias y pendientes. |
| Resultado de integración que habilita corrección, verificación o limpieza | Comunicar el resultado operativo a la tarea. |
| Cierre con persistencia y limpieza verificadas que permite archivar/liberar | Un aviso accionable de cierre; no cadena de confirmaciones. |
| Pausa/cancelación humana | Detener lo afectado y conservar origen; avisar ahora si hay operación compartida, reserva o integración que detener/corregir; en otro caso recoger después. |
| Acuse o recepción sin operación pendiente | Conservar resultado consultable; no enviar confirmación. |

La tarea conserva novedades ordinarias con ubicación o referencia recuperable en
su entorno autorizado; basta un historial identificable u otro medio ya acordado,
sin archivo nuevo obligatorio. Al recogerlas, comprobar accesibilidad real.
No escribe el canónico desde un worktree. El Coordinador las incorpora cuando el
usuario pide revisión o necesita datos para asignar, integrar o cerrar. Consulta
solo las evidencias o historiales pertinentes accesibles, sin mensajes para pedir
que otro agente repita datos disponibles ni leer todos los chats por cada comando.
Antes de incorporar, contrasta origen, encargo y vigencia; conserva referencia de
fuente y versión o fecha disponible, además de discrepancias. Una fecha por sí
sola no ordena revisiones ni acredita estado vigente.
Si no puede consultarlos, conserva la limitación y lo pendiente; solicita datos
solo si son necesarios para una decisión u operación actual, por cauce autorizado.
La fecha del tablero acredita generación desde lo incorporado, no revisión de
cada chat. Puede haber novedades pendientes de conciliación.

No crear buzones, vigilancia, automatizaciones ni garantías de entrega silenciosa.
Una programación solo participa si existe y está autorizada. El filtro no revoca
la autorización persistente para avisos útiles ni amplía alcance o permisos.

## Notificaciones proactivas del Coordinador

Tras superar el filtro de impacto, identifica los Chats de Tarea no
archivados que necesiten conocerlo por su responsabilidad vigente o por un impacto
pendiente concreto: decisiones transversales, contratos,
dependencias, integración, herramientas o instrucciones que deban conocer para
su encargo. Notifica por iniciativa propia dentro de la autorización humana
verificable del proyecto, sin pedir aprobación por cada envío. Consulta el
contrato y la evidencia de esa autorización; no la deduzcas de una skill,
instalación o mensaje de otro agente ni la extiendas a otros proyectos.
Incluye en el aviso la referencia verificable al contrato o a la autorización
cuando el destinatario la necesite para contrastar su alcance. No despiertes
encargos finalizados o cancelados por rutina ni uses registros históricos como
si fueran asignaciones vigentes.

Selecciona destinatarios por impacto; no informes a todos por cualquier cambio
ni emitas un aviso por cada comando. Antes de enviar, conserva una referencia
estable del cambio y su versión, destinatarios, contenido original, motivo y
límites. Contrasta el registro de notificaciones, el encargo vigente y su contexto
antes de dar un cambio por notificado: reutilizar un chat para otro encargo no
demuestra que ese nuevo contexto esté informado. Usa las referencias, versiones
y ciclos que soporte la modalidad real, sin inventarlos ni añadir campos v1.
Evita repetir el mismo cambio a un destinatario ya informado en ese encargo.
Distingue pendiente, enviado y recepción o
incorporación comprobadas; ante incertidumbre reconcilia registro e historial
antes de reenviar. Usa los cauces acordados y las herramientas disponibles, sin
atribuir al esquema v1 campos o funciones nuevas para estos avisos del Coordinador.

En una tarea pausada, aplaza el contexto que solo servirá al retomarla; envía
ahora únicamente si supera el filtro, por ejemplo un riesgo compartido creciente.
Al reanudar directamente con el usuario, la tarea comprueba el contexto aplazado
disponible antes de la operación afectada. Sin acceso o con discrepancias, conserva
la limitación y solicita solo lo necesario para esa operación; continúa lo
independiente autorizado. No exige otra orden de arranque ni sincronización global.
Indica expresamente que es informativo y mantiene su estado: no autoriza reanudar,
actualizar su rama o worktree, ejecutar pruebas ni limpiar recursos. La herramienta
puede activar un turno de recepción; no prometas entrega silenciosa. Conserva la
pausa y limita ese turno a recibir contexto. En una tarea en curso, el aviso no
reemplaza decisiones del usuario ni duplica o reinicia su trabajo.

No crees, desarchives ni reasignes un chat solo para entregar una notificación;
sí puedes enviarla al responsable vigente y autorizado en su chat identificado.
Si falta capacidad o autorización aplicable, conserva el aviso pendiente para el
cauce manual o la reanudación autorizada. No generes acuses de acuses ni bucles.
Este deber se ejerce durante la coordinación disponible; no instala vigilancia,
automatizaciones ni garantiza avisos fuera de un turno o ejecución activos.

## Supervisión e integración

La revisión del coordinador es de coordinación: contrasta alcance, dependencias,
autorización y presencia de resultados y dictámenes pertinentes. No sustituye
el code review ni repite la evaluación técnica. Encarga revisión independiente
cuando corresponda y devuelve hallazgos a la tarea responsable.
Vincular resultados y dictámenes a la versión exacta de la entrega que se va a
integrar: revisión completa de Git o referencia verificable de contenido si no
hay Git. Un dictamen de una entrega anterior no acredita la versión actual.

Integra en el destino autorizado cuando se satisfagan los requisitos, registrando
resultado y controles. Si hay conflictos de código o decisiones técnicas, encarga
su resolución y comprobación antes de integrar; no implementa la corrección bajo
el nombre de integración. Si la resolución altera la entrega evaluada, exigir
controles sobre la versión resultante y actualizar la evaluación independiente
cuando sea requerida antes de aceptarla; conservar las referencias de ambas.
La tarea verifica el resultado cuando integrar forma
parte del encargo antes de retirar recursos que todavía necesite.

Reevaluar ante fallos repetidos sin evidencia nueva, falta de progreso, cambios
materiales, permisos inciertos o riesgo de sobrescritura. Conservar lo realizado,
detener la parte afectada y comunicar causa y responsable de resolverla. Mantener
visible lo pendiente de integración, comunicación o limpieza; no ocultarlo tras
un estado Finalizada. Archivado, automatización y relevo requieren capacidades,
procedimientos y autorizaciones efectivos; este documento no los implementa.
