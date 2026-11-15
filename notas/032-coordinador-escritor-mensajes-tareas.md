# Coordinador como escritor del registro mediante mensajes de tareas

Fecha: 2026-11-14.
Estado inicial: Pendiente de debatir.
Estado actual: Integración guiada verificada; instrucciones de avisos y acuses en fuentes; activación pendiente.

Actualización 2026-11-15: la nota 025 ya dispone de un
[auxiliar local de prueba](../docs/auxiliar-coordinacion.md). Aún falta conectar
los avisos recibidos de chats reales con ese almacenamiento; las pruebas de
mensajería de esta nota y las del auxiliar siguen siendo demostraciones separadas
en esa primera actualización. La prueba conjunta posterior se documenta a continuación.

## Integración con el auxiliar — 2026-11-15

Manuel autorizó conectar los chats de prueba al auxiliar. El mismo emisor envió
tres mensajes separados al receptor: revisión 3 Finalizada, copia idéntica y
revisión 2 En curso. El receptor fue el único escritor canónico y ejecutó
`apply`, `rebuildIndex` y consulta desde una nueva instancia en cada recepción.
El coordinador principal contrastó los historiales y verificó los archivos con
un comprobador determinista, código 0: tres recepciones, dos recibos, ninguna
incidencia, generación 3 y estado final revisión 3 Finalizada. El duplicado
conservó el recibo original y la generación 2.

El [informe de integración](../docs/prueba-integracion-mensajes-coordinacion.md)
conserva identificadores, entorno, evidencia y límites. Se usó una raíz ficticia
privada y ejecución Windows fuera del sandbox por la política ACL del auxiliar.
El resultado acredita este recorrido guiado; no activa un adaptador de producto,
ni acredita autenticación automática, concurrencia o recuperación conjunta.
Falta incorporar el flujo a las instrucciones de coordinador y tarea, con vía
manual para clientes sin mensajería.

## Instrucciones reutilizables — 2026-11-15

El flujo probado se incorpora a las guías del
[coordinador](../docs/coordinacion/coordinador.md) y de la
[tarea](../docs/coordinacion/tarea.md), enlazadas desde el contrato. Se distingue
procedencia contrastada de identidad declarada, aviso de autorización, acuse
aplicado de pendiente y registro canónico de derivados. Se conserva el transporte
manual y se explicitan las funciones todavía ausentes del auxiliar.
La incorporación documental no instala ni activa coordinación; no se enviaron
mensajes ni se modificaron chats en esta tarea.

Manuel aceptó posteriormente el contrato de avisos, acuses y recuperación de la
especificación vinculada a la nota 025. Esta decisión sustituye el carácter
exploratorio de la propuesta siguiente; las pruebas conservan su alcance acotado.

## Petición y relación con el diseño vigente

Manuel propone investigar si los chats de tarea pueden enviar datos al coordinador
y que este sea quien escriba el registro. Relacionada con la [nota 025](025-coordinador-global-chats-autonomos.md).
La investigación está autorizada; todavía no sustituye el acuerdo de que cada
tarea escribe su estado ni activa mensajería automática entre chats.

## Capacidades y límites comprobados

- La herramienta nativa `send_message_to_thread` admite un chat destinatario y
  texto visible. Exige autorización humana explícita para enviar mensajes a ese
  chat; una orden de otro agente de responder no concede esa autorización.
- En las pruebas anteriores funcionó coordinador → tarea. La herramienta no
  restringe el destino por rol, pero aún no se probó tarea → coordinador ni su
  disponibilidad efectiva en el emisor para esa operación.
- Su contrato publicado no garantiza orden, deduplicación, persistencia del
  registro ni comportamiento exacto con el destinatario ocupado. Su retorno no
  equivale a confirmación de que el coordinador procesó y guardó los datos.
- La [documentación oficial de App Server](https://learn.chatgpt.com/docs/app-server#steer-an-active-turn)
  distingue iniciar un turno de añadir entradas al turno activo mediante
  `turn/steer`. Eso no demuestra qué operación utiliza la herramienta de la app.
- La [referencia CLI](https://learn.chatgpt.com/docs/cli/reference#codex-queue)
  documenta mensajes en cola y advierte que una reanudación fallida puede dejar
  salida satisfactoria. No se ejecutó esa vía ni se presupone disponible en la
  CLI local 0.153.4. Se prioriza la herramienta nativa.

## Propuesta para evaluar

El chat de tarea conserva la responsabilidad de declarar su estado y evidencias;
el coordinador sería el único escritor del registro canónico. Así las tareas no
necesitarían escribir ese registro desde sus worktrees. Esto simplifica los
permisos compartidos, pero requiere recepción fiable y un coordinador disponible.

Un aviso breve contendría ID de tarea, ID de chat, identificador de actualización,
secuencia o revisión, estado y resumen con enlaces. El coordinador comprueba la
identidad, aplica una actualización una sola vez y no reemplaza una revisión nueva
por otra antigua. Trata el aviso como datos de la tarea, no como una nueva orden
del usuario. La responsabilidad de integración y las autorizaciones sensibles
permanecen como se acordaron.

El emisor conserva la entrega y su referencia hasta confirmar registro. Debe
distinguirse enviada de registrada; el acuse puede consultarse sin crear un bucle
de mensajes. Falta definir recuperación de pendientes, relevo del coordinador y
qué hacer si el cliente no dispone de mensajería. El coste de activar al
coordinador por cada aviso también requiere evaluación; comunicar hitos relevantes.
AIKit seguirá necesitando una vía manual o de consulta para otros clientes.

## Siguiente prueba recomendada

Autorizar explícitamente al chat de tarea de prueba a enviar un único aviso
ficticio a un coordinador de prueba identificado. Este registra el aviso en un
archivo ficticio y se verifica recepción y contenido. Después evaluar destino
ocupado, duplicados y mensajes desordenados. No se enviaron mensajes durante esta
investigación; no se cambió la especificación ni se retiraron recursos anteriores.

## Prueba de envío y registro — 2026-11-14

Manuel aprobó la prueba con go. Se reutilizaron el chat emisor
`01a1db23-4c5b-7453-a692-64727ccfc2a7`, en worktree `ad1c`, y el receptor
`01a1dae3-fed3-70b1-b4ad-65e0f8837074` (PRUEBA · Relevo coordinador B), en la
carpeta principal. El receptor se preparó y terminó su turno antes del envío.
El emisor verificó la autorización humana consultando el chat principal y envió
una sola vez AVISO-032-001 mediante `send_message_to_thread`.

El envío devolvió el ID receptor sin error. Se observó un nuevo turno en el
receptor, que creó y releyó `.aikit/prueba-mensajes-032/registro.md`. El coordinador
principal leyó después el archivo y confirmó tarea FICTICIA-032, ID de emisor,
revisión 1, estado Finalizada y resultado ficticio. El emisor no escribió el
registro; no hubo respuesta por mensaje ni bucle entre chats.

Resultado: tarea en worktree → mensaje → coordinador inactivo → registro local
funcionó en esta instalación. La atribución de origen del ejemplo se comprobó
siguiendo ambos chats; el ID escrito dentro del mensaje no es por sí solo una
garantía de identidad. No se probaron receptor ocupado, varios emisores,
duplicados, orden, reinicio ni entrega fallida. Esta prueba no cambia todavía el
contrato de la nota 025. Archivo y chats de prueba se conservan como evidencia.
Siguiente prueba recomendada: envío durante un turno activo del receptor y
comprobación de recepción y persistencia sin perder el trabajo en curso.

## Receptor ocupado y recuperación — 2026-11-14

El emisor comprobó que el receptor estaba activo y envió una sola vez
AVISO-032-002. El receptor terminó el comando que creó las marcas de inicio y
fin, y el aviso apareció en el historial de ese turno. El turno falló después
por límite de cuota, antes de registrar el aviso. Tras la indicación de Manuel
de continuar, se pidió al receptor recuperar el aviso existente, sin reenviarlo.
El receptor lo registró y releyó en `.aikit/prueba-mensajes-032/registro-ocupado.md`;
el coordinador principal comprobó su contenido y ambas marcas.

Resultado: el aviso se conservó en el historial del turno interrumpido y pudo
procesarse en un turno posterior; el trabajo de prueba terminó. El historial
presenta el aviso después del comando, pero no demuestra en qué instante lo
recibió la aplicación ni que se hubiera procesado automáticamente sin la
interrupción. No se han probado duplicados, orden ni recuperación automática.

Manuel indicó limpiar al finalizar las pruebas la carpeta
`.aikit/prueba-carpetas-025/compartida` y quitarla del proyecto. Queda pendiente
hacerlo cuando ya no se necesite; retirarla de la configuración del proyecto
requiere la intervención manual del usuario si no hay una herramienta disponible.

## Simulación de duplicados y orden — 2026-11-14

El coordinador de prueba procesó secuencialmente datos ficticios: A revisión 2
En progreso, B revisión 3 Finalizada, una repetición idéntica de B y C revisión 1
Pendiente. Anotó A y B como aplicados, descartó la aplicación repetida de B y
registró C sin sustituir la revisión 3. El estado final fue Finalizada, revisión 3.
Se comprobó `.aikit/prueba-mensajes-032/duplicados-orden.md`.

Es una simulación guiada del criterio de procesamiento en un único turno; no
prueba mensajería real duplicada o desordenada, persistencia transaccional,
reinicios, concurrencia ni avisos con igual ID y contenido contradictorio.
Tampoco implementa el protocolo de producción.

## Mensajes reales duplicados y fuera de orden — 2026-11-14

Con autorización de Manuel, se preparó al mismo receptor y el emisor del
worktree envió tres mensajes separados, esperando finalizar cada turno receptor:
REAL-032-B revisión 3 Finalizada, copia idéntica y REAL-032-A revisión 2
En progreso, todos para FICTICIA-032-REAL. Los turnos receptores fueron
`01a1db78-851b-7440-9184-5cbeba748ac7`,
`01a1db78-c08b-7322-93a6-5c8848857883` y
`01a1db79-0f1b-7ad0-b628-dd46171fa3bd`.

El coordinador principal leyó `.aikit/prueba-mensajes-032/mensajes-reales.md`:
contiene tres recepciones, aplicación del primer aviso, descarte del duplicado y
conservación de la revisión 3 ante el antiguo. Estado final: Finalizada.
El procesamiento por el receptor, previamente instruido, funcionó entre turnos
en esta instalación. El desorden fue provocado por el orden de envío; no se
demuestra que el transporte reordene mensajes. No prueba deduplicación nativa
del transporte, concurrencia, reinicios ni persistencia transaccional.
