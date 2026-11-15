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
  modalidad manual, alcance, cauces autorizados y ubicación del registro.
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
  y las ramas principales. No implementa ni hace code review: encarga la ejecución
  y la evaluación técnica a los responsables y revisores pertinentes.
- **Chat de Tarea:** ejecuta y verifica su encargo, decide detalles técnicos
  dentro del alcance, mantiene título y estado y comunica resultados y bloqueos.
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
Si el cliente arranca el chat al crearlo, su primer encargo debe limitarse a leer
el contexto y confirmar su identidad y asignación. No ejecutar la tarea hasta
que proyecto, coordinador, responsable, alcance y permisos estén comprobados.
La preparación puede quedar pendiente de asignación sin inventarla.

La modalidad inicial es comunicación mediante el coordinador. Las tareas le
trasladan novedades y necesidades de otros trabajos; él coordina el siguiente
paso. Mantener un responsable de cada paso. El traspaso distingue información,
solicitud de ejecución y decisión autorizada, indicando emisor, receptor, objetivo,
límites, referencias y destino de respuesta. No añade campos al aviso v1.

La comunicación directa entre tareas queda como posibilidad futura, pendiente
de límites y validación; no queda habilitada por leer estas instrucciones. Un
mensaje no concede autoridad humana ni cambia alcance automáticamente. Si el
usuario y el coordinador acuerdan una actualización, comprobarla y trasladarla
a las tareas afectadas por el cauce autorizado.

Comunicar en hitos, bloqueos, cambios materiales, solicitud de integración y
cierre; no por cada comando ni mediante vigilancia permanente. Las herramientas
disponibles determinan si un mensaje activa al receptor; sin ellas ofrecer
traslado manual. Conservar evidencia y reconciliar antes de reenviar ante dudas,
según [avisos y acuses](avisos.md).

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
