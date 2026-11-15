# Coordinador global y chats de tarea autónomos

Especificación BMAD en preparación:
[`spec-coordinacion-chats`](../_bmad-output/specs/spec-coordinacion-chats/SPEC.md).
Conserva cuestiones abiertas y no implica autorización de implementación.

Fecha: 2026-11-14.
Estado inicial: Pendiente de debatir.
Estado actual: Auxiliar e integración guiada verificados; instrucciones de roles en fuentes; activación pendiente.
La coordinación completa conserva capacidades y cuestiones abiertas pendientes.

Actualización de empaquetado 2026-11-15: la
[skill de avisos y acuses](../packaging/skills/coordinacion-chats/SKILL.md) está
preparada en fuentes, con validación estructural, evaluación textual de cuatro
casos y revisión independiente corregida. Véase la
[evidencia de alcance](../_bmad-output/implementation-artifacts/spec-025-skill-coordinacion.md).
No está instalada ni incluida en el exportador histórico; falta la prueba aislada
de carga. Esta skill acotada no implementa todas las capacidades de la nota 025.

Manuel autorizó implementar y probar el primer auxiliar en un proyecto ficticio.
El alcance está en la [especificación de implementación](../_bmad-output/implementation-artifacts/spec-025-auxiliar-registro.md).
Esta entrega no activa la mensajería, archivado o programación de chats reales.
Actualización 2026-11-15: el [auxiliar y su uso](../docs/auxiliar-coordinacion.md)
incluyen esquema estricto, diario, acuses y recuperación supervisada. Tipos, lint,
formato y 83 pruebas pasan; seis omisiones documentadas y tres sondas Windows
nativas adicionales sin omisiones. POSIX real sigue pendiente. La coordinación
completa aún no está implementada; el prototipo usa asignación fija y primer ciclo.

Actualización posterior 2026-11-15: la [prueba conjunta con mensajes reales](../docs/prueba-integracion-mensajes-coordinacion.md)
conectó el emisor en worktree con el receptor y el auxiliar. Se verificaron aviso
aplicado, copia idéntica y revisión antigua, con tres recepciones, dos recibos y
estado final revisión 3 Finalizada. La prueba guiada no activa coordinación de
producción; falta incorporar la recepción validada a las instrucciones de ambos roles.

Las [instrucciones del coordinador](../docs/coordinacion/coordinador.md) y del
[chat de tarea](../docs/coordinacion/tarea.md), con su
[flujo compartido](../docs/coordinacion/flujo-avisos.md), incorporan ahora envío
recuperable, contraste de origen, escritura única, consulta de acuses y límites
del auxiliar. Son fuentes documentales; falta distribuirlas y activarlas mediante
el mecanismo de producto que se implemente. No se instaló una skill ni se activó
la coordinación. La automatización, relevo y demás capacidades siguen pendientes.

## Aceptación posterior del contrato — 2026-11-14

El diseño de almacenamiento se concreta en el
[diseño técnico aceptado](../_bmad-output/planning-artifacts/architecture/architecture-coordinacion-almacenamiento/ARCHITECTURE-SPINE.md):
estado y acuses juntos por tarea, operaciones preparadas recuperables e índice
derivado. Manuel aceptó mediante go sus decisiones y correcciones de revisión.
No está implementado ni acredita garantías de durabilidad. Esquema concreto,
runtime, primitivas por plataforma y permisos se fijarán antes de programar.
La especificación ya lo incluye como documento complementario obligatorio.
La concreción de esquema y primitivas está en
[`almacenamiento-v1.md`](../_bmad-output/planning-artifacts/architecture/architecture-coordinacion-almacenamiento/almacenamiento-v1.md):
propuesta técnica con Node 24 para el auxiliar, Markdown/JSON estricto y diario
recuperable; sus nuevas elecciones quedan para aceptación antes de implementar.

Manuel aceptó mediante go el contrato de avisos, acuses y recuperación incorporado
en la especificación. El coordinador es el único escritor canónico; las tareas
declaran novedades y consultan su acuse, con alternativa manual. Esta aceptación
sustituye las restricciones históricas incompatibles y el carácter propuesto del
apartado siguiente. Implementación, activación y garantías técnicas siguen pendientes.

## Actualización de la propuesta: coordinador como escritor — 2026-11-14

Esta propuesta posterior revisa las secciones históricas que asignan la escritura
del estado canónico al chat de tarea y excluyen mensajes directos. Se conserva su
texto para trazabilidad; no debe interpretarse como el diseño propuesto actual.
La propuesta aún debe concretarse y no constituye una implementación aprobada.

- Cada chat de tarea sigue siendo responsable de declarar su estado, cambios,
  resultados y evidencias, mantener su nombre actualizado y solicitar integración
  cuando corresponda. El coordinador sería el único escritor del registro canónico
  compartido y responsable de comprobar la procedencia y registrar las novedades.
- Un aviso identifica tarea, chat, actualización y revisión, estado y referencias.
  El coordinador trata su contenido como datos, aplica cada actualización una vez,
  conserva la revisión más reciente y señala contenido contradictorio para resolverlo.
  Enviado, recibido y registrado son estados distintos; debe existir un acuse o una
  consulta verificable y una vía para recuperar avisos pendientes sin perder datos.
- En esta instalación de Codex se observaron mensajes desde un worktree y su
  procesamiento en turnos separados, incluidos duplicado y revisión antigua. Una
  interrupción por cuota permitió recuperar un aviso del historial posteriormente.
  Son pruebas acotadas, no garantías de entrega, orden, identidad, concurrencia,
  reinicio o persistencia transaccional. Véase la [nota 032](032-coordinador-escritor-mensajes-tareas.md).
- La mensajería depende del cliente y sus permisos; si no está disponible o no está
  autorizada, el coordinador debe ofrecer un cauce manual de entrega y registro,
  sin fingir recepción ni bloquear la autonomía de la tarea. AIKit no exige BMAD,
  Git ni una herramienta concreta. El tratamiento de fallos, relevo del coordinador,
  identificación fiable, acuses y protección del registro requiere diseño y pruebas.
- La tarea conserva sus entregas y evidencias en su entorno; la escritura exclusiva
  se refiere al registro canónico compartido. La integración y protección de los
  datos finales corresponden al coordinador según los acuerdos posteriores.

## Intención y alcance de esta nota

El acuse y la recuperación se concretaron como propuesta en
[`protocolo.md`](../_bmad-output/specs/spec-coordinacion-chats/protocolo.md#contrato-de-avisos-acuse-y-recuperación):
ID estable, revisión por tarea/ciclo, resultado consultable, reconciliación antes
de reenvío, detección de contradicciones, relevo con un solo escritor y alternativa
manual. El contrato fue aceptado; sigue pendiente validar sus garantías técnicas.

Organizar el proyecto mediante un chat coordinador principal y chats independientes
por encargo, como una feature completa, una investigación o una corrección. El
usuario trabaja directamente en cada chat de tarea. El coordinador conserva la
visión global y un registro de responsabilidades, contexto y estados.

Se utilizó Director de Ideas para madurar la propuesta. Esta nota conserva lo
discutido, distinguiendo acuerdos de propuestas pendientes. No es una
especificación aprobada ni autoriza implementar el mecanismo, activar políticas,
crear chats o enviarles mensajes. El usuario pidió persistir antes de continuar
el afinado.

## Traspaso al coordinador

El usuario aclara que este chat debía limitarse a registrar la idea y que la
conversación avanzó más de lo previsto en su diseño. Se termina de documentar
para entregarla al coordinador, sin continuar aquí la investigación, el afinado
ni el desarrollo. Esta nota es el documento de traspaso; no se ha enviado a otro
chat ni se ha abierto una tarea de ejecución.

El coordinador debe recibir:

- **Objetivo:** coordinar encargos mediante chats autónomos, identificados y
  reutilizables, con seguimiento global liviano y presencia del usuario.
- **Restricciones:** activación explícita solo por proyecto, instrucciones en
  `AGENTS.md` local, procedimiento futuro en una skill, Markdown local portable
  sin dependencia de Git, bajo coste documental y sin mensajes directos por ahora.
- **Acuerdos conservados:** roles, bootstrap y espera del usuario, estado canónico
  mantenido por cada chat de tarea, cierre autónomo, entrega por ciclo, acuse de
  lectura sin aprobación y estructura mínima aprobada más abajo.
- **Trabajo pendiente:** investigar los aspectos no resueltos y decidir el cauce
  adecuado para retomarlos con el usuario. La lista al final conserva las dudas;
  no es un plan aprobado ni obliga a resolverlas todas antes de seleccionar alcance.

Las aprobaciones parciales de la conversación se conservan como decisiones de
diseño. No convierten la nota en una especificación completa ni autorizan su
implementación o activación. El protocolo de `entradas/` quedó propuesto como
siguiente asunto, pero no fue desarrollado ni aprobado.

## Decisiones confirmadas por el usuario

### Coordinador principal

**Actualización posterior:** Manuel asignó al coordinador la integración de los
cambios solicitados por chats de tarea y su revisión coordinada como en una PR.
Esa decisión sustituye las exclusiones históricas de integración y revisión de
integración indicadas en esta sección y la asignación a un chat especializado.
Los chats mantienen su responsabilidad de revisión y verificación del trabajo.
Véase [031](031-aislamiento-sin-git.md).

Manuel precisa que el coordinador es responsable de la integridad y salud de los
datos finales y de prevenir su pérdida. En proyectos que usan Git, es responsable
de las ramas principales del flujo, como `master` o `develop`; cada chat de tarea
es responsable de su propia rama. Los nombres concretos dependen del proyecto.
Esta responsabilidad no presupone Git ni elimina las autorizaciones para push,
eliminación irreversible u otras acciones sensibles. Los procedimientos concretos
de integración, protección y recuperación aún deben definirse y verificarse.

- Solo coordina chats y contexto global del proyecto. No programa, modifica las
  entregas ni dirige los pasos internos de las tareas.
- Puede actualizar el registro administrativo del proyecto.
- Selecciona el siguiente encargo apropiado de la lista y abre o retoma el chat
  responsable. Los criterios concretos de selección están por definir.
- Registra el encargo, chat y responsabilidad; debe conocer qué se hizo, cuándo
  se hizo y en qué estado está cada trabajo.
- No revisa técnicamente las entregas ni aprueba el cierre de las tareas.
- Cuando el usuario interactúa con él, consulta novedades y actualiza su visión
  global. No se presupone observación continua en segundo plano.

### Chats de tarea

- Son independientes y tienen autoridad operativa sobre su encargo con las
  herramientas disponibles, dentro de su alcance y autorizaciones vigentes.
- El usuario entra en el chat identificado y continúa allí el trabajo.
- Cada chat puede usar sus subagentes, incluido el coordinador para sus propias
  responsabilidades de coordinación.
- Cada chat realiza o encarga sus revisiones y verificaciones. Termina su tarea
  sin depender de revisión o aprobación técnica del coordinador.
- Cuando corresponda, gestiona rama, worktree, pull, merge, PR y limpieza de sus
  recursos. Esta responsabilidad no elimina las autorizaciones específicas para
  push, publicación o eliminación irreversible.
- La integración conjunta entre ramas principales, por ejemplo `develop → master`
  cuando ese flujo exista, corresponde a un chat especializado; el coordinador
  registra y encamina el encargo.

### Maduración de ideas y tipos de chat

Las ideas se maduran en un chat distinto del coordinador. Así el usuario puede
explorarlas mientras el coordinador sigue disponible para otros encargos. El
coordinador trabaja con la lista de tareas preparadas.

Se contempla distinguir chats habituales y chats genéricos por encargo. Candidatos
discutidos: ideas, coordinación, integración, features, investigaciones y
correcciones. El catálogo de roles, sus nombres y los límites precisos siguen
pendientes de definir.

### Lanzamiento y arranque

1. El coordinador crea el chat con un nombre identificable y un prompt inicial
   que describa encargo, alcance, restricciones y contexto necesario.
2. Registra los identificadores y responsabilidades, sin esperar la respuesta
   del chat de tarea para continuar coordinando.
3. El chat de tarea realiza un bootstrap: lee el contexto necesario, presenta su
   comprensión del encargo y espera a que el usuario entre antes de ejecutar.
4. A partir de esa interacción, el chat de tarea dirige su trabajo con el usuario.

El usuario confirmó que la autoridad operativa es del chat de tarea; una referencia
inicial a la autoridad del «chat principal» fue aclarada en ese sentido.

### Retorno de resultados y contexto entre tareas

- **Estado canónico confirmado el 2026-11-14:** cada chat de tarea escribe y
  mantiene su propio estado. El coordinador lo consulta; no mantiene una segunda
  versión ni modifica ese estado. Su registro administrativo enlaza al estado
  de la tarea y puede indicar cuándo lo consultó por última vez.
- Se acepta una entrega persistente vinculada al ticket. El chat de tarea registra
  el resultado, evidencias, verificaciones, recursos relacionados y pendientes.
  El coordinador consulta esa entrega para conocer el estado y las consecuencias
  globales, sin repetir la revisión técnica.
- Se confirma una entrega por ciclo y un acuse de lectura separado de cualquier
  aprobación. El cierre nunca depende de que el coordinador lea la entrega.
- El coordinador puede aportar información valiosa procedente de otros encargos,
  pero el chat receptor decide cómo afecta a su trabajo y consulta al usuario si
  implica cambiar el alcance.
- Se acepta una bandeja persistente por tarea para ese contexto adicional. Se
  propuso registrar procedencia, información e impacto posible, y que el receptor
  indique si la incorporó, no aplica o necesita decisión del usuario.
- Por ahora se excluyen los mensajes directos entre chats: el usuario estará
  presente en todos ellos, manteniendo intervención humana. Los avisos directos
  podrían estudiarse en otro nivel de automatización; no están autorizados aquí.

### Entregas por ciclo y consulta acordadas

El usuario acepta una entrega persistente por ciclo de trabajo, enlazada desde el
estado canónico y escrita por el chat de tarea. Una mejora posterior produce una
nueva entrega vinculada a la anterior. Las correcciones de entregas publicadas se
identifican, evitando cambios silenciosos.

El contenido propuesto abarca identidad y fecha, alcance cumplido, resultado y
enlaces, verificación y limitaciones, decisiones relevantes, pendientes, impacto
en otras tareas y recursos cuando existan. Se aplica la restricción de ligereza
indicada después: estos conceptos no exigen secciones o archivos independientes,
ni rellenar campos vacíos o irrelevantes. No se reproduce la conversación.

Cuando el usuario interactúa con el coordinador, este consulta el índice y el
estado de los encargos pertinentes. Si hay una entrega nueva, lee el resumen y
solo los enlaces necesarios para comprender sus consecuencias globales. Registra
una referencia inequívoca de la entrega consultada y la fecha de lectura. El
acuse significa «conocido», nunca «revisado» o «aprobado», y no duplica la entrega
ni el estado canónico. El detalle del indicador de cambios sigue por definir.

El coordinador deposita contexto relevante en las bandejas de otras tareas y
plantea al usuario las nuevas decisiones materiales de prioridad o alcance.

### Restricción transversal: mecanismo liviano

El usuario requiere bajo coste de tokens y tiempo: documentar únicamente lo
indispensable para mantener saludable el sistema, no todo lo realizado.

- No convertir cada acción, turno o comprobación en una actualización documental.
  Registrar cambios significativos, bloqueos, decisiones relevantes y cierre.
- Mantener resúmenes breves y referencias a resultados o evidencias ya existentes;
  no copiar logs, conversaciones o documentos ni repetir revisiones técnicas.
- No imponer formularios extensos, campos sin utilidad ni archivos vacíos por
  cumplir una plantilla. La estructura debe crecer solo cuando haga falta.
- Consultar selectivamente novedades y tareas pertinentes; evitar releer todo el
  histórico o el proyecto completo por rutina.
- No añadir sondeos, notificaciones o inferencias extra para mantener registros.
- Evaluar la estructura y los procedimientos por su utilidad para continuar y
  coordinar el trabajo frente a su coste documental, de tokens y de tiempo.

Los umbrales concretos y la estructura definitiva quedan pendientes; no se fija
una longitud arbitraria ni se promete un coste sin medirlo.

### Estados y transiciones acordados

El usuario aceptó el 2026-11-14 los estados y el cierre autónomo propuestos:

| Estado | Significado |
| --- | --- |
| Preparada | Encargo madurado, pendiente de abrir o retomar su chat. |
| Esperando al usuario | Bootstrap completado o decisión necesaria pendiente de la intervención del usuario. |
| En curso | El chat está trabajando en el encargo. |
| Bloqueada | Una dependencia o impedimento externo no permite avanzar. |
| Pausada | El usuario decidió detener temporalmente el trabajo. |
| Finalizada | El chat completó el alcance, sus revisiones y la entrega persistente. |
| Cancelada | El usuario decidió abandonar el encargo. |

Al cancelar con autorización de Manuel, el chat responsable hace la limpieza
correspondiente con las herramientas y autorizaciones disponibles en el proyecto,
e informa de lo realizado y de los recursos pendientes. Las acciones sensibles
conservan sus requisitos de autorización específica. Véase la
[nota 027](027-automatizacion-coordinacion.md).

Manuel acepta que el coordinador archive también los chats de tareas canceladas,
una vez terminada la limpieza autorizada o registrados sus pendientes, si el chat
está inactivo y su identidad es inequívoca.

Manuel añade que el cierre satisfactorio también exige que el chat responsable
persista lo necesario que aún no se haya persistido y realice la limpieza
correspondiente de los recursos creados: por ejemplo, ramas, worktrees u otros
elementos, según las herramientas utilizadas y las condiciones del proyecto.
Debe informar de lo realizado y de lo pendiente o impedido. Las eliminaciones
irreversibles y demás acciones sensibles requieren su autorización específica;
no se presupone que todos los recursos se puedan eliminar ni se borra trabajo
sin persistir. El coordinador puede registrar y archivar el chat después, sin
suplantar la responsabilidad operativa del chat de tarea.

- Registrar fecha, motivo y condición para avanzar; en espera del usuario,
  concretar qué intervención se necesita. Para estados terminales, indicar si no
  hay continuación pendiente.
- El chat de tarea actualiza el estado. Puede finalizar cuando cumple los
  criterios del encargo y sus autorizaciones, sin aceptación del coordinador.
- Una PR o integración pendiente impide finalizar solo si pertenece al alcance
  acordado. La integración se representa como resultado o pendiente del encargo,
  no como estado general obligatorio; el mecanismo sigue siendo ajeno a Git.
- Finalizar conserva entrega e historial y no elimina recursos. Decisión posterior:
  el coordinador es responsable de archivar los chats de tareas terminadas, según
  la [nota 026](026-archivado-chats-coordinacion.md); no depende de una revisión
  técnica ni de una observación continua del coordinador.
- Una mejora posterior se registra como un nuevo ciclo de trabajo, con alcance
  y fechas, conservando el cierre anterior. La relación exacta entre ciclos y
  tickets sigue pendiente de concretar.
- Antes de asignar el chat, el coordinador mantiene la entrada Preparada. Una vez
  asignada, el chat de tarea es propietario de su estado.

### Decisión: cierre con limpieza incompleta — 2026-11-14

Se plantean dos opciones cuando el objetivo está cumplido pero queda un recurso
por limpiar o una acción sensible pendiente:

1. **Cierre con pendientes visibles (recomendada):** el chat persiste la entrega,
   realiza la limpieza autorizada y registra cada recurso restante, motivo y acción
   necesaria. Si el pendiente no impide cumplir el alcance acordado, puede finalizar;
   el coordinador lo mantiene visible y el archivado no elimina el pendiente. Si
   la limpieza es criterio de aceptación o depende de una autorización necesaria
   para completar el alcance, permanece esperando al usuario o bloqueada según
   corresponda. No se interpreta silencio como autorización.
2. **Cierre solo con limpieza completa:** cualquier recurso pendiente impide
   finalizar, aunque el objetivo principal esté cumplido. Ofrece un cierre más
   estricto, pero puede mantener abiertas tareas por recursos que deban conservarse.

Ejemplo: un worktree con trabajo ya integrado pero cuya eliminación requiere una
autorización aún no recibida quedaría registrado como pendiente; bajo la opción 1
solo impide finalizar si su eliminación pertenece al alcance o criterios de cierre.
Manuel elige la opción 1: cierre con pendientes visibles, siempre que la limpieza
restante no impida cumplir el alcance y los criterios de cierre acordados.

### Reutilización como ticket

Si aparece una mejora de un trabajo anterior, priorizar volver al chat que lo
realizó para aprovechar su contexto, como volver a encargar una mejora al equipo
que conoce la obra. Contrastar ese contexto con los archivos actuales.

Manuel aceptó la siguiente regla para reabrir el mismo ticket, crear uno relacionado
o sustituir el chat si ya no resulta adecuado o accesible.

#### Decisión: ciclos y tickets — 2026-11-14

- **Mismo ticket, nuevo ciclo:** una corrección o mejora mantiene la misma
  responsabilidad y resultado general. Se conserva el ID y cada cierre previo;
  el nuevo ciclo registra su alcance y fechas y produce su propia entrega. Se
  prioriza recuperar el chat anterior y contrastar su contexto con el proyecto.
- **Ticket relacionado:** el nuevo encargo tiene un resultado, responsabilidad o
  seguimiento que conviene gestionar de forma independiente. Se crea un ID nuevo
  y se enlazan ambos tickets; la relación no implica dependencia ni prioridad si
  no se han establecido. El coordinador prepara o abre el chat correspondiente.
- **Chat anterior no adecuado o inaccesible:** mantener la identidad del ticket y
  sus entregas; registrar la sustitución y el nuevo chat, con el contexto persistido
  necesario. No presumir que el historial del chat anterior sea portable o que
  vuelva a estar disponible. Respetar las reglas del cliente y de autorización.
- Si la clasificación afecta materialmente al alcance o hay varias opciones sin
  criterio suficiente, el coordinador consulta a Manuel antes de elegir. Una nueva
  propuesta o la existencia de un cierre previo no autoriza por sí sola el trabajo.

Esta regla no modifica cierres anteriores ni implica que exista ya el mecanismo.

### Activación exclusivamente por proyecto

- La capacidad debe activarse mediante su setup en cada proyecto que la necesite.
- Su bloque se guarda en el `AGENTS.md` local del proyecto.
- No se instala globalmente ni se activa en todos los proyectos por defecto.
- Debe funcionar con archivos Markdown locales, sin depender de Git ni de otro
  control de versiones. Las operaciones de Git son responsabilidades opcionales
  cuando el proyecto las utiliza, no requisitos de la coordinación.
- Debe usar el sistema de archivos del usuario en Windows, Linux o macOS, con
  archivos `.md` locales dentro del proyecto. Obsidian y Spaces de ChatGPT son
  referentes de organización, no dependencias ni requisitos de instalación.

### Materialización futura: skill e instrucciones locales

El usuario identifica este mecanismo como un procedimiento que debe
materializarse en una skill acompañada de las instrucciones pertinentes en el
`AGENTS.md` local. Se registra esta dirección; no se está creando ni instalando
la skill durante el afinado de la nota.

Reparto previsto para desarrollar: la skill describe el procedimiento y remite a
referencias o plantillas según sea necesario; el bloque breve de `AGENTS.md`
establece su activación, roles, límites y ubicación de los registros. Los archivos
Markdown del proyecto guardan estado, encargos, entregas y contexto, sin duplicar
el procedimiento completo en cada archivo.

El setup local activa la capacidad únicamente en los proyectos elegidos. Antes
de desarrollar la skill se debe comprobar la cobertura instalada y reutilizar
las capacidades existentes, sin duplicar los flujos de BMAD u otras herramientas.
Esta skill de coordinación se distingue de la eventual skill de mantenimiento
de Markdown, cuya conveniencia todavía debe investigarse.

## Propuestas pendientes de aceptación

### Nombre de las piezas de AIKit

Todavía no hay un nombre formal acordado para las instrucciones que el complemento
incorpora a `AGENTS.md`. Se propusieron:

1. **Adaptaciones de AIKit (recomendada):** piezas activables con instrucciones,
   ámbito y recursos propios. Esta sería la adaptación de coordinación de chats.
2. **Perfiles de AIKit:** más apropiado para conjuntos completos de configuración.

Una adaptación podría contener un bloque breve de instrucciones, procedimientos
en skills y registros de proyecto. La distribución exacta está por concretar;
no debe duplicar capacidades existentes.

### Identidad y registro

Se propuso un identificador de ticket estable, independiente del ID del chat,
con título, función, objetivo, estado, fechas, dependencias y referencias al chat.
Rama, worktree y PR serían datos opcionales. El nombre visible no sustituye el ID.

Las herramientas publicadas de Codex permiten crear chats, obtener IDs y títulos,
consultar estado y retomar conversaciones. Su creación puede iniciar un turno:
el prompt de bootstrap debe delimitar la espera del usuario. Un identificador
provisional de creación no debe confundirse con el ID definitivo del chat.
No se ejecutó una prueba completa del mecanismo durante esta exploración.

Registrar el ID no conserva la transcripción ni garantiza acceso desde otra
instalación. La información necesaria para continuar debe quedar en los archivos
del proyecto; el chat permanece como referencia de la aplicación.

### Estructura mínima aprobada

El usuario aprueba esta base como diseño, sin autorizar su implementación.
Sustituye la propuesta inicial con archivos separados de encargo y estado y una
carpeta de roles creada de antemano.

```text
proyecto/
  AGENTS.md
  coordinacion/
    INDICE.md
    tareas/
      T-001/
        TAREA.md
        ENTREGAS.md
```

| Archivo | Responsabilidad | Responsable |
| --- | --- | --- |
| `AGENTS.md` | Activación local, límites y referencia a la skill y al índice. | Setup autorizado. |
| `INDICE.md` | ID, nombre, responsabilidad y enlace de cada tarea; referencia y fecha de última entrega consultada. | Coordinador. |
| `TAREA.md` | Encargo, chat e ID, estado vigente, fecha de actualización y siguiente paso necesario. | Coordinador al abrir; después, chat de tarea. |
| `ENTREGAS.md` | Resúmenes breves de cierre por ciclo, con fecha, resultado y enlaces indispensables. | Chat de tarea. |

El índice no copia los estados: el coordinador consulta los archivos `TAREA.md`
pertinentes. Hay dos archivos base por tarea, evitando formularios o divisiones
innecesarias.

#### Decisión: registros con worktrees separados — 2026-11-14

Cada worktree tiene su propia carpeta de archivos; una ruta `coordinacion/` dentro
de cada copia no constituye automáticamente un registro compartido. Mantener una
única carpeta canónica `coordinacion/` en la raíz local del proyecto coordinado,
identificada explícitamente por el setup, independientemente de la carpeta de
código de cada tarea. El encargo de cada chat debe incluir esa ubicación y la ruta
de su propio worktree; el identificador y la propiedad de cada registro permanecen
inalterados. Sin Git se usa la misma carpeta canónica en la raíz elegida.

Antes de asignar tareas aisladas, comprobar que coordinador y chat de tarea tienen
acceso autorizado de lectura y escritura a los registros compartidos. Un worktree
separado puede quedar fuera de las raíces de escritura del sandbox: no presumir
acceso ni eludir restricciones. Si no se dispone de él, comunicar la limitación y
usar un flujo manual coordinado o no lanzar paralelismo hasta resolverla; no copiar
un estado local y tratarlo como canónico. Validar la identidad y la ruta para no
escribir en otro proyecto, y manejar cambios simultáneos e interrupciones con el
protocolo de integridad por diseñar.

No asumir que el contenido de la carpeta canónica se incluye o excluye de Git:
decidir su seguimiento y privacidad por proyecto, respetando información sensible
y permisos antes de compartir o publicar. Distinguir estos registros operativos de
las ramas de código y de las entregas; la integración de una rama no sincroniza
automáticamente los registros canónicos. Evitar depender de una ruta fija dentro
de `.git`: Git comparte ciertos metadatos entre worktrees, pero los archivos de
trabajo son copias separadas. Ver [documentación de Git worktree](https://git-scm.com/docs/git-worktree).

Manuel acepta esta ubicación como diseño; no es una capacidad comprobada. Deben probarse permisos entre
worktrees, identificación de raíz, concurrencia, ejecución programada y recuperación
en Windows, Linux y macOS; no se garantiza que todos los clientes los permitan.

**Prueba local — 2026-11-14:** en Windows se creó un worktree temporal bajo
`.aikit/` en `fe36f66` y un registro ficticio separado bajo la raíz local del
proyecto. Un proceso iniciado desde el worktree leyó `estado: preparado`, escribió
`estado: en curso` en el registro común y leyó el resultado esperado. Ambos
directorios estaban dentro de la raíz de escritura de esta sesión: la prueba no
simula un chat con sandbox limitado solo al worktree, ni concurrencia, enlaces,
ejecución programada o Linux/macOS. No se modificó la configuración del proyecto.

La retirada de la carpeta del worktree funcionó, pero Git informó un error al
eliminar sus metadatos y dejó una entrada huérfana. La vista previa de limpieza
identificó únicamente esa entrada; `git worktree prune` con acceso ampliado la
retiró. Se eliminaron los datos ficticios y el listado confirmó que los demás
worktrees seguían presentes. El error y la recuperación forman parte de la evidencia.

**Prueba en chat con worktree propio — 2026-11-14:** el chat `PRUEBA · Permisos
worktree`, ID `01a1db11-31aa-76e1-bc82-1645174a7ee4`, trabajó en
`C:\Users\Manuel\.codex\worktrees\cd3d\AIKit`. Su sandbox permitía escribir
en ese worktree, en su carpeta de visualizaciones y en temporales habilitados,
pero no en la raíz principal `C:\Manuel\Projects\AIKit`. Pudo leer el registro
ficticio bajo `.aikit/`, pero al intentar actualizarlo recibió
`System.UnauthorizedAccessException` y código 3; no pidió permisos ampliados. El
coordinador verificó que seguía con el contenido original y retiró el registro
ficticio. El chat terminó y conserva su worktree de prueba; no se ha limpiado ni
archivado ese recurso. El identificador provisional de creación se resolvió al
chat definitivo por el directorio de trabajo; el título inicialmente no quedó
aplicado y el coordinador lo corrigió para identificarlo como prueba.

Resultado: la lectura compartida funcionó, pero la escritura canónica desde un
worktree con este sandbox no; la prueba local anterior no era suficiente. Hace
falta diseñar un mecanismo autorizado o flujo manual sin copias canónicas ni
eludir el sandbox. No demuestra comportamiento de otros clientes o configuraciones.

**Investigación de acceso autorizado — 2026-11-14:** la documentación oficial
de [sandbox de Codex](https://learn.chatgpt.com/docs/sandboxing) describe raíces
de escritura adicionales, y la de [perfiles de permisos](https://learn.chatgpt.com/docs/permissions)
describe reglas de escritura para rutas absolutas. Esto ofrece una vía candidata:
conceder al chat acceso limitado a la carpeta canónica `coordinacion/` además de
su worktree, si el cliente, la política y el usuario permiten configurarlo. No
exige quitar el sandbox ni convertir toda la raíz del proyecto en escribible.
Se requiere comprobar su compatibilidad real con los chats de la aplicación y
perfiles gestionados; la documentación general no demuestra que este entorno
permita configurarlo ni que el permiso alcance a una tarea programada.

Como alternativa, el chat puede preparar su actualización en su zona autorizada y
el coordinador aplicarla a los registros canónicos por un cauce explícito y
verificable; habría que concretar cómo recibe el contenido sin mensajería directa
ni atribuirle al coordinador la propiedad del estado de tarea. Si no se cuenta con
ninguna de esas capacidades, se informa y se usa coordinación manual o secuencial.
No se deben copiar registros y tratarlos como una segunda fuente canónica ni usar
permisos ampliados por rutina para eludir la política vigente.

Recomendación provisional: probar primero una raíz escribible limitada a una
carpeta ficticia, con configuración aislada y autorización apropiada, conservando
el worktree como raíz de trabajo. Comprobar lectura/escritura de esa carpeta y
denegación fuera de ella, sin modificar la configuración global o del proyecto.
La carpeta compartida accesible para varios chats no impone por sí sola la
propiedad por archivo ni evita carreras; siguen siendo necesarios el protocolo de
integridad y sus pruebas. No se ha aplicado ningún cambio de permisos.

**Intento de prueba aislada — 2026-11-14:** con Codex CLI 0.153.4 en Windows se
prepararon directorios ficticios de trabajo, compartido y control. Se intentó
ejecutar `codex sandbox` con perfil `:workspace` y una raíz adicional para la
carpeta ficticia, mediante opciones de proceso y sin modificar configuración
global ni del proyecto. El sandbox anidado no inició: informó
`orchestrator_helper_exit_nonzero` y código 1. El script de escritura no se
ejecutó; ambos archivos de control conservaron su contenido. Se retiraron los
archivos y carpetas ficticios creados para el intento.

Resultado inconcluso: el error de arranque no demuestra ni permiso ni denegación
de la raíz adicional y no comprueba el comportamiento del chat de escritorio.
No se amplió el sandbox para sortear el fallo. Quedan por investigar el origen
del error y una vía de prueba compatible con el cliente y la política del entorno.

**Diagnóstico del arranque — 2026-11-14:** con la misma CLI 0.153.4 y el sandbox
de este chat se ejecutó un control mínimo `codex sandbox` con perfil de trabajo y
un comando que solo imprimiría una marca, sin raíz adicional. También terminó con
código 1 y `orchestrator_helper_exit_nonzero`; la marca no apareció. Por tanto el
fallo no requiere la raíz adicional probada, aunque eso no identifica su causa.
El aviso previo indicó además acceso denegado al crear alias temporales de la CLI.
El registro local consultado no aportó una causa inequívoca para ese intento.

La [fuente pública actual de Codex](https://github.com/openai/codex/blob/main/codex-rs/windows-sandbox-rs/src/setup_error.rs)
describe ese código como salida fallida del asistente de configuración sin un
informe estructurado; no demuestra por sí sola que la CLI local tenga la misma
implementación ni cuál fue el fallo concreto. La
[documentación del sandbox de Windows](https://learn.chatgpt.com/docs/windows/windows-sandbox)
describe diferencias de versión y de entorno. No se cambió la configuración ni se
ejecutó el asistente fuera del sandbox. Una prueba posterior necesita una vía
admitida por el cliente para conceder una raíz ficticia a un chat de prueba y
comprobarla realmente; si no está disponible, la alternativa de actualización
mediada debe diseñarse sin duplicar la fuente canónica ni saltarse permisos.

**Nueva revisión documental — 2026-11-14:** Manuel pidió contrastar de nuevo
documentación oficial y fuentes especializadas. Resultado: existe una vía de
interfaz documentada que aún no hemos probado en esta instalación; la capacidad
de escritura compartida sigue sin validarse.

- [Proyectos y chats, documentación oficial](https://learn.chatgpt.com/docs/projects#use-local-projects-for-folders-and-codebases):
  `Edit project → Add folder` adjunta carpetas al proyecto local. La documentación
  describe lectura y edición en las secundarias y su conservación al abrir un
  chat en worktree. Git y el descubrimiento automático de instrucciones parten
  de la carpeta principal; el sandbox sigue imponiendo los permisos efectivos.
  Es una configuración del proyecto, no una concesión exclusiva a un chat. Para
  aislar una prueba conviene un proyecto de prueba con carpetas ficticias.
- [App Server, solicitudes de permisos](https://learn.chatgpt.com/docs/app-server#permission-requests):
  `request_permissions` permite solicitar acceso acotado; el cliente devuelve
  el subconjunto concedido y el alcance `turn` o `session`. El segundo conserva
  la concesión para turnos posteriores de esa sesión; no acredita persistencia
  tras reinicios o reanudaciones. Esta sesión no publica `request_permissions`;
  `create_thread` tampoco ofrece un parámetro de raíces adicionales. La existencia
  del protocolo no equivale a una herramienta utilizable aquí.
- [Perfiles de permisos](https://learn.chatgpt.com/docs/permissions): los perfiles
  nuevos y `sandbox_mode` / `sandbox_workspace_write` no se componen; las políticas
  gestionadas pueden imponer perfiles y limitar los elegibles. La prueba previa
  mezcló perfil y opciones antiguas: tampoco permite inferir que su raíz adicional
  se habría aplicado. El control sin raíz adicional ya falló al arrancar, por lo
  que esa mezcla no identifica la causa del error observado. La CLI disponible
  sigue siendo 0.153.4; no se presupone que coincida con el runtime de la app.

Contraste especializado y reportes de primera mano:

- Se consultó la [guía de Meli AI Mentoring](https://ai.thomasmeli.com/walkthroughs/create-codex-workspace),
  que describe el mismo flujo de carpetas y enlaza sus fuentes oficiales. Se usa
  como contraste de uso; la afirmación técnica se fundamenta en OpenAI.
- [Incidencia 35260](https://github.com/openai/codex/issues/35260), abierta al
  consultar: usuarios de macOS describen carpetas secundarias visibles que no se
  propagan a las raíces escribibles. Incluye observaciones posteriores en Work;
  no demuestra un defecto idéntico en nuestro chat Codex de Windows.
- [Incidencia 41355](https://github.com/openai/codex/issues/41355), abierta:
  reporte Windows de raíces configuradas que no se aplican, con posible error de
  ubicación de una clave TOML. No permite atribuir nuestro fallo a esa causa.
- [Incidencia 58914](https://github.com/openai/codex/issues/58914), abierta:
  reporte Windows del 2 de noviembre sobre solicitudes acotadas que devuelven
  `file_system: null`. No identifica la capa que impidió la concesión; tampoco
  demuestra que el mecanismo falle siempre. No se adopta acceso completo como
  solución para AIKit.

**Siguiente prueba recomendada, no ejecutada:** comprobar el control de carpetas
en la interfaz y preparar un proyecto local desechable con repositorio ficticio
principal y una carpeta compartida ficticia secundaria. Crear un chat de prueba
en worktree y darle desde su arranque la instrucción de comprobar sus raíces,
escribir y releer un marcador en la secundaria y verificar que una carpeta de
control externa sigue sin permiso de escritura. No usar una carpeta temporal que
ya sea escribible como control negativo. Verificar también un turno posterior
antes de afirmar continuidad. Conservar solo evidencia breve y retirar únicamente
los recursos ficticios creados cuando termine la prueba. Si falta el control o
no se propagan los permisos, registrar la limitación sin ampliar acceso global.
Esta investigación no cambió permisos, configuración ni carpetas adjuntas, no
creó chats y no repitió el sandbox anidado. La especificación sigue abierta.

**Límite de ejecución de la prueba de interfaz — 2026-11-14:** Manuel aprobó
probar las carpetas secundarias con un proyecto ficticio y un chat en worktree.
Antes de operar se leyó la skill Computer Use instalada y su guía
`C:/Users/Manuel/.codex/plugins/cache/openai-bundled/computer-use/26.1106.51428/docs/guidance.md`.
Esta prohíbe expresamente automatizar la interfaz de ChatGPT desktop, la CLI de
Codex y sus extensiones dentro de aplicaciones Windows. No se inició automatización
ni se intentó otra vía de interfaz para eludir esa restricción. Las herramientas
nativas disponibles no exponen creación de proyectos locales ni adjuntar carpetas
secundarias. No se crearon recursos ficticios ni chats: sin el paso de adjuntar
carpetas no permitirían comprobar la hipótesis. No es un resultado negativo de
escritura ni un rechazo de revisión automática; la prueba sigue sin ejecutar.

Para continuar hace falta intervención manual en la aplicación: comprobar si el
menú de un proyecto local ofrece `Edit project → Add folder`. Si existe, preparar
el proyecto de prueba y adjuntar únicamente la carpeta ficticia compartida antes
de abrir su chat en worktree. La comprobación de permisos efectivos y escritura
se hará desde ese chat, con el alcance ficticio ya descrito; no se presupone que
el control esté presente en esta versión.

**Prueba real de carpeta secundaria — 2026-11-14:** Manuel confirmó en la
interfaz la opción de añadir carpeta y adjuntó la carpeta ficticia `compartida`
al proyecto AIKit. Se creó el chat `PRUEBA · Carpeta secundaria`, con worktree
`C:\Users\Manuel\.codex\worktrees\ad1c\AIKit`. El chat informó que su perfil
incluía ese worktree y la carpeta secundaria como raíces escribibles. Sin escalar
ni solicitar permisos, creó y releyó `prueba-chat.txt` con `prueba 025` en la
carpeta compartida. La creación en la carpeta hermana `control`, no adjuntada,
falló con `System.UnauthorizedAccessException`. El coordinador confirmó el
contenido y la ausencia del archivo de control. Resultado positivo para este
entorno y turno; no demuestra persistencia en turnos posteriores, concurrencia,
otros clientes ni integración completa. Los archivos, chat, worktree y carpeta
secundaria de prueba permanecen pendientes de limpieza coordinada.

**Segundo turno — 2026-11-14:** tras autorización de Manuel se continuó el mismo
chat y worktree. Las raíces declaradas seguían incluyendo la carpeta secundaria;
sin permisos adicionales el chat leyó el archivo anterior, creó y releyó
`segundo-turno.txt` con `segundo turno 025`. El intento equivalente en `control`
falló con `System.UnauthorizedAccessException`. El coordinador confirmó contenido
y ausencia en control. Esto verifica dos turnos de la misma sesión, no un reinicio,
concurrencia ni el comportamiento de otros entornos.

**Dos worktrees — 2026-11-14:** en el segundo chat, con worktree `5370`, la
carpeta secundaria figuraba como escribible. Sin escalar, leyó el archivo creado
por el primer chat y creó y releyó `segundo-worktree.txt` con `segundo worktree
025`. La escritura en la carpeta `control` no adjuntada fue denegada con
`System.UnauthorizedAccessException`. El primer chat, en worktree `ad1c`, leyó
después ese archivo y confirmó su contenido. Se demuestra intercambio sucesivo
mediante una sola carpeta y aislamiento de control en este entorno; no se han
probado escrituras simultáneas, recuperación ni otros clientes. Los dos chats,
worktrees, carpeta adjunta y archivos ficticios siguen pendientes de limpieza.

El coordinador crea archivos pequeños en `entradas/` dentro de la tarea solo
cuando necesita aportar contexto. El chat de tarea los consulta al retomar el
trabajo y registra su tratamiento. Separar esas entradas de `TAREA.md` evita que
ambos roles escriban simultáneamente en el estado vigente.

`TAREA.md` no acumula una bitácora. Cada ciclo tiene una sección identificable en
`ENTREGAS.md`. Cuando el historial dificulte la consulta, se divide en archivos
por ciclo conservando enlaces; no se anticipa esa división. Las decisiones o
evidencias extensas se separan únicamente cuando sea necesario.

La detección inicial de novedades compara la fecha de actualización y el
identificador de la última entrega con la última consulta del coordinador.
No requiere vigilancia continua ni lectura rutinaria del histórico completo.

El usuario ratifica que no resultan funcionales los monolitos Markdown de miles
de líneas: cada archivo debe tener una responsabilidad única. Investigar primero
soluciones existentes que ya resuelvan organización, recorrido y mantenimiento.
Evaluar si hay una skill adecuada para mantener estos documentos; solo si hay
una carencia y resulta provechoso, considerar una skill propia de AIKit. No está
decidida ni autorizada su creación.

La propiedad del estado canónico se conserva: lo mantiene el chat de tarea y el
coordinador lo consulta. Esta aprobación fija la estructura mínima, no acredita
todavía su validación operativa.

## Investigación inicial y límites

El usuario solicita investigar a fondo documentación oficial y fuentes
especializadas sobre estructura de archivos, límites de crecimiento,
responsabilidades, enlaces y carpetas. La consulta inicial aporta referencias,
pero no resuelve ni valida toda la arquitectura propuesta.

Aplicar [016 — Investigar antes de experimentar](016-investigacion-antes-de-experimentar.md):
consultar primero documentación oficial y fuentes especializadas pertinentes;
reservar experimentación y ensayo y error para cuestiones no resueltas por esas
fuentes, conservando las pruebas de verificación necesarias. Esta preferencia ya
tiene nota propia, por lo que no se crea otra para duplicarla.

- [Codex: AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md.md):
  ámbitos global/local y descubrimiento de instrucciones. Sin raíz reconocida se
  consulta el directorio actual; estudiar cómo fijar la raíz sin Git y qué ocurre
  al abrir subdirectorios. Los enlaces no garantizan carga automática de destinos.
- [Codex: comandos e IDs de chats](https://learn.chatgpt.com/docs/reference/commands)
  y [worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees): referencias
  de la aplicación; no convierten Git en requisito del mecanismo.
- [Obsidian: almacenamiento](https://obsidian.md/help/data-storage) y
  [enlaces](https://obsidian.md/help/links): archivos locales de texto y navegación
  entre notas. Se usa como referencia; no se propone exigir Obsidian.
- Spaces de ChatGPT: referente sugerido por el usuario; su organización todavía
  no se ha investigado para este mecanismo y no constituye una dependencia.
- [Michael Nygard: registros de decisiones](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions):
  precedente de documentos pequeños centrados en una decisión; no especifica
  este sistema de tickets.
- [Diátaxis](https://diataxis.fr/): separación de documentación por necesidades
  del lector; referencia para procedimientos, explicaciones y consulta.

Fuentes consultadas el 2026-11-14 y contratos de herramientas publicados en esta
sesión. No se ha demostrado persistencia perfecta del contexto, portabilidad de
chats entre instalaciones ni notificación automática en segundo plano.

## Decisiones y validaciones todavía pendientes

- Nombre formal de las adaptaciones y definición completa de cada rol.
- Detallar las condiciones de transición en los casos límite, respetando los
  estados, el cierre autónomo y la propiedad del estado canónico ya acordados.
- Concretar el protocolo liviano de retorno y detección de cambios, respetando la
  entrega por ciclo y el acuse de lectura ya aceptados.
- Estructura final, crecimiento, archivo histórico, enlaces y recuperación tras
  escrituras interrumpidas o actualizaciones simultáneas.
- Cobertura de skills existentes para mantenimiento de Markdown y conveniencia de
  una capacidad propia si no hay cobertura suficiente; sin crearla por defecto.
- Consulta y procesamiento de entradas nuevas, sin mensajes directos ni bloqueos
  indebidos del trabajo autónomo.
- Criterios para seleccionar el siguiente encargo y resolver dependencias o
  conflictos entre tareas; devolver al usuario las decisiones materiales.
- Límites del bootstrap y comprobación del traspaso a la interacción con el usuario.
- Setup exclusivamente local: detección de activación, actualización y retirada
  conservando instrucciones ajenas, también en carpetas sin Git.
- Validar con las herramientas disponibles el registro de identidad, la lectura
  de estado, la reutilización del chat y el trabajo simultáneo sin interferencias.

## Relaciones con el backlog

Desarrolla la idea de [021 — Chats, subagentes y relevo](021-coordinacion-chats-subagentes-relevo.md)
sin sustituir su historial. Relacionada con
[007 — Responsabilidades de AIKit](007-separar-delegacion-de-aikit.md),
[009 — Director de Ideas](009-metodo-director-de-ideas.md),
[015 — Backlog](015-backlog-ideas-bmad.md) y
[024 — Setup y patrón de integraciones](024-setup-bmad-patron-integraciones.md).
Esta capacidad tiene una restricción local más estricta: no admite instalación
global. No se modifica el estado de implementación de otras notas.

El archivado y la recuperación de chats se detallan en la
[nota 026](026-archivado-chats-coordinacion.md). Manuel asigna al coordinador la
responsabilidad de archivar los chats terminados; esta decisión sustituye la
propuesta anterior de no archivarlos automáticamente al finalizar.

Actualización posterior: Manuel plantea automatizar la revisión de estados y las
acciones pertinentes mediante una tarea programada de Codex. Esto reemplaza la
hipótesis de consulta solo al interactuar con el coordinador; alcance y límites
se investigan en la [nota 027](027-automatizacion-coordinacion.md).

La tarea programada se vinculará al chat coordinador; el setup permitirá escoger
la frecuencia para cada proyecto. En un relevo se actualizará su destino al nuevo
chat, conservando la configuración y evitando ejecuciones duplicadas. Manuel indica
que una revisión diaria es suficiente para el uso considerado; no es un valor
universal. Las capacidades reales de traslado y ejecución requieren validación.

Manuel decide además que cada chat de tarea mantenga su estado visible en su
nombre y actualice su registro. El estado canónico sigue perteneciendo al chat y
reside en `TAREA.md`; formato y recuperación ante fallos se concretarán en la
[nota 029](029-estado-visible-nombre-chat.md).

Para distinguir el chat coordinador se propone `<Proyecto> · Coordinador principal`;
la convención y los casos de prueba o relevo se recogen en la nota 029.

Manuel autoriza al coordinador a crear nuevos chats cuando lo considere pertinente;
esa responsabilidad corresponde al coordinador y no a los chats de tarea. La
creación debe respetar las capacidades y reglas aplicables del cliente. Esta
autorización no implica, por sí sola, autorización para enviar mensajes a chats.

## Investigación y protocolo mínimo propuesto — 2026-11-14

Investigación autorizada al retomar la nota; las propuestas de esta sección no
sustituyen los acuerdos anteriores ni constituyen implementación o validación.

### Cobertura y carencias observadas

- Las herramientas nativas publicadas permiten crear, listar y consultar chats.
  La creación exige petición explícita del usuario; el envío de mensajes a un
  chat existente también exige autorización explícita. Crear un chat inicia una
  tarea asíncrona y puede devolver un identificador provisional. La selección de
  un encargo no equivale por sí sola a autorización para crear un chat. No se
  crearon chats ni se probó el arranque en esta investigación.
- `aikit-setup` y el instalador existente ofrecen selección explícita, vista
  previa, bloques delimitados y respaldo. Sin embargo, el ámbito de proyecto
  actual usa la raíz Git y guarda respaldos en su área administrativa: no cubre
  proyectos sin Git. Reutilizar sus mecanismos exige adaptar y verificar esa
  limitación, no prometer que ya se cumple la portabilidad.
- `bmad-project-context` cubre instrucciones de proyecto y `bmad-spec` la
  especificación; ninguna de sus descripciones acredita el protocolo acordado
  de coordinación y propiedad de estados. Las herramientas nativas gestionan
  chats, pero no establecen por sí solas el registro local convenido. No se ha
  identificado una skill general de mantenimiento Markdown que justifique crear
  otra; terminar la evaluación antes de decidir su necesidad.
- La [documentación oficial de AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
  indica que, si no se encuentra raíz de proyecto, se comprueba solo el directorio
  actual; también existe prioridad de `AGENTS.override.md` y un límite de tamaño.
  En proyectos sin Git, iniciar desde la raíz elegida es una precaución propuesta,
  no una garantía de carga desde subdirectorios. Hay que comprobar el entorno real.
- La [documentación de skills](https://learn.chatgpt.com/docs/build-skills)
  describe carga progresiva y recursos opcionales. Esto apoya mantener una skill
  breve y referencias selectivas; no garantiza su activación automática.

### Propuesta de funcionamiento

1. El setup identifica una raíz local explícita, presenta los cambios previstos y
   activa el bloque solo allí. Ante raíz o instrucciones efectivas inciertas,
   informa y detiene esa operación. La instalación de la skill y la activación
   local son operaciones distintas; no se presupone su disponibilidad.
2. El coordinador registra un encargo preparado y presenta su alcance. La creación
   o reanudación mediante mensaje solo se realiza cuando la autorización humana y
   las reglas de la herramienta aplicable lo permitan. La creación registra el ID
   definitivo solo cuando exista; un ID provisional no se trata como definitivo.
3. El chat de tarea lee su encargo y contexto pertinente, explica su comprensión y
   espera al usuario. Después mantiene `TAREA.md`; el coordinador lee ese archivo
   y solo escribe el índice administrativo y entradas separadas.
4. Cada entrada nueva lleva identidad, origen, contexto e impacto posible; el chat
   receptor registra si la incorporó, no aplica o precisa decisión. Una entrada
   no altera automáticamente el alcance ni bloquea todo el trabajo independiente.
5. Al cerrar un ciclo, el chat registra una entrega identificable en `ENTREGAS.md`
   y actualiza su estado. Al interactuar con el usuario, el coordinador consulta
   selectivamente y anota qué entrega leyó; el acuse no es revisión ni aprobación.
6. La propiedad por archivo reduce conflictos, pero no los elimina: una instancia
   responsable a la vez y actualización con detección de cambios previos son
   candidatas para evitar sobrescrituras. Ante conflicto o interrupción, conservar
   los datos e informar; la técnica y recuperación deben diseñarse y probarse.

Siguen abiertos los detalles de concurrencia, recuperación, recuperación del ID,
estado del bootstrap, alcance de selección de encargos y reapertura de ciclos.
La recomendación BMAD preliminar es `[SPC] bmad-spec` para formalizar el contrato
cuando estén aclaradas las decisiones materiales, y `[BD] bmad-build` para su
implementación; no se ha creado todavía ninguna especificación.

## Independencia y protocolo de entradas y concurrencia — 2026-11-14

Manuel precisa que BMAD y otras herramientas pueden apoyar el desarrollo en
AIKit, pero no deben convertirse en requisitos del producto. La coordinación
debe poder adoptarse en un proyecto vacío sin BMAD, Git ni herramientas o
metodologías concretas. El procedimiento se apoyará en archivos Markdown locales
y en las capacidades efectivamente disponibles del entorno; no se puede prometer
crear o consultar chats cuando el cliente carezca de esa capacidad. En tal caso
se informa y se ofrece operación manual sin fingir automatización. La activación
local y las autorizaciones del usuario siguen siendo necesarias.

### Propuesta concreta para las entradas

- Una entrada es un archivo Markdown independiente en `entradas/`, creado solo
  cuando el coordinador tiene información pertinente. Su nombre incluye un ID
  único; contiene origen, fecha, información y posible impacto, sin copiar la
  conversación. El coordinador no edita `TAREA.md` de una tarea ya asignada.
- El chat de tarea consulta las entradas al retomar y antes de cerrar un ciclo;
  no hay vigilancia ni interrupción automática. Lee solo las nuevas o pendientes.
  Una entrada no cambia el alcance por sí sola: el chat decide su aplicación y
  consulta al usuario si hace falta una decisión material.
- El receptor deja un acuse breve por entrada: incorporada, no aplicable o
  pendiente de decisión, con referencia a la decisión cuando aporte valor. El
  coordinador conserva la entrada original; el receptor no reescribe su contenido.
  Las pendientes de decisión se mantienen visibles en `TAREA.md` solo mientras
  afecten al siguiente paso. Un bloqueo se declara únicamente si impide avanzar.
- Las entradas y acuses deben poder distinguirse sin confiar solo en fechas; un
  identificador estable evita perder dos cambios con la misma marca temporal. La
  ubicación concreta del acuse y el mecanismo de publicación se verifican en el
  diseño técnico para evitar escritores simultáneos o lecturas parciales.

### Propuesta concreta para la concurrencia y recuperación

- El coordinador es el único responsable lógico de `INDICE.md`; cada tarea
  asignada tiene un único chat responsable de `TAREA.md` y `ENTREGAS.md`.
  Los subagentes no escriben esos archivos compartidos simultáneamente. Antes de
  modificar, se relee la versión actual; si ha cambiado, se conserva y reconcilia
  con el responsable, sin sobrescribirla a ciegas.
- La separación de responsables es una regla de operación, no un bloqueo técnico.
  Una comprobación previa aislada no evita una carrera entre comprobar y escribir.
  El diseño técnico debe definir y probar un mecanismo de exclusión o detección
  adecuado para cada archivo compartido, publicación completa de entradas y
  recuperación tras interrupciones en los sistemas soportados. No se afirmará
  seguridad concurrente por la mera presencia de Markdown o reemplazos atómicos.
- Ante una escritura incompleta, conflicto o propiedad incierta, conservar los
  originales y evidencias recuperables, detener solo la actualización afectada e
  informar. No eliminar bloqueos presuntamente obsoletos ni elegir una versión
  automáticamente sin comprobar su estado. El cierre conserva entregas e historial.

Estas propuestas detallan el protocolo para debate; no son validación operativa
ni cambian las decisiones confirmadas. Falta decidir y verificar el mecanismo
concreto de escritura, recuperación y acuse, sin imponer una dependencia externa.

## Aclaraciones y propuesta de escritura — 2026-11-14

- Si el cliente no puede crear un chat, el coordinador indica al usuario que lo
  abra manualmente con un nombre específico y le facilita un texto de arranque.
  El nombre no sustituye un identificador fiable; si no está disponible, se
  registra la referencia manual como tal, sin inventar un ID ni afirmar que se
  puede recuperar el chat automáticamente.
- El usuario y el coordinador pueden decidir actualizar el alcance de una o más
  tareas. El coordinador registra la decisión y la traslada a la bandeja de cada
  tarea afectada. El chat responsable procesa la actualización y modifica su
  estado y alcance; informa de conflictos o decisiones que sigan pendientes. La
  entrada distingue una decisión expresa del usuario de información o propuestas
  sin aprobar y no amplía autorizaciones sensibles. Sin mensajería directa ni
  vigilancia, se procesa cuando el usuario retome el chat o en la comprobación
  acordada antes del cierre; no se garantiza una intervención inmediata.

### Acuse y publicación propuestos

Cada entrada recibe un identificador único y se publica completa antes de hacerse
visible como pendiente. El chat receptor crea un acuse separado por identificador,
con resolución y referencia breve si procede; el coordinador no modifica acuses.
Para una decisión pendiente, el acuse puede actualizarse por el mismo responsable
cuando se resuelva, conservando una mención breve del cambio. La entrada original
no se edita silenciosamente: una corrección se presenta como nueva entrada que la
referencia. Al procesar, el chat comprueba que cada entrada tenga su propio acuse;
las fechas son informativas, no el identificador de novedad.

### Escritura y recuperación propuestos

Reutilizar el patrón del instalador existente solo donde aplique: bloqueo exclusivo,
lectura de la versión actual dentro del bloqueo, preparación temporal en el mismo
directorio y sustitución controlada, preservando el original o respaldo necesario.
El mecanismo deberá aplicarse a todos los escritores participantes; un editor que
lo ignore no queda protegido por el bloqueo. La validación debe contemplar cambios
externos, fallos durante la sustitución y diferencias entre sistemas de archivos.
Un bloqueo abandonado no se borra solo por antigüedad: se inspeccionan propietario,
proceso y archivos recuperables antes de resolverlo. La operación manual sin ese
mecanismo requiere evitar escritores simultáneos y no ofrece la misma garantía.

Los archivos de entrada y acuse se preparan fuera del conjunto visible y se
publican de forma que el lector no interprete un archivo parcial como completo;
fallos e identificadores duplicados se notifican sin sobrescribir datos. La
elección de primitivas, durabilidad ante apagones y compatibilidad Windows, Linux,
macOS y sistemas de archivos concretos requieren diseño y pruebas: no se ha
demostrado una garantía universal. El protocolo no presupone Git ni BMAD; si un
auxiliar necesita un runtime, se debe declarar y diseñar una vía manual usable.

La [documentación oficial de Node.js](https://nodejs.org/api/fs.html) advierte
que comprobar un archivo antes de abrirlo introduce una carrera y describe la
apertura exclusiva; esto fundamenta el candidato, no valida todas las plataformas
ni convierte Node.js en dependencia decidida. El instalador actual contiene
implementaciones y pruebas de bloqueo y recuperación que se evaluarán para
reutilización, sin dar por probada su aplicación a este protocolo.
