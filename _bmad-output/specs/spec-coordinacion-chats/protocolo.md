# Protocolo y límites de coordinación

## Instrucciones de uso — 2026-11-15

El flujo de avisos y acuses se concreta en las guías del
[coordinador](../../../docs/coordinacion/coordinador.md) y del
[chat de tarea](../../../docs/coordinacion/tarea.md), con
[formato e interpretación compartidos](../../../docs/coordinacion/flujo-avisos.md).
El [auxiliar local](../../../docs/auxiliar-coordinacion.md) implementa una parte
del contrato y la [prueba conjunta](../../../docs/prueba-integracion-mensajes-coordinacion.md)
verificó el recorrido guiado entre chats. Esto actualiza las menciones históricas
a implementación pendiente que aparecen abajo: no acredita todavía el conjunto
de capacidades, ni activa una skill, transporte automático o programación.

## Roles y registros acordados

- Coordinador: mantiene visión global e índice administrativo, identifica encargos y chats, consulta entregas y registra acuses sin aprobar el cierre. Manuel le autoriza a crear chats cuando sea pertinente, sujeto a las reglas del cliente. Coordina y realiza la integración solicitada por los chats, revisándola como en una PR, sin sustituir sus verificaciones propias.
- Datos y ramas: el coordinador es responsable de la integridad y salud de los datos finales y de prevenir su pérdida. En proyectos con Git gestiona las ramas principales definidas por el proyecto, como `master` o `develop`; cada chat de tarea gestiona su propia rama. Esto no autoriza por sí solo push, eliminación irreversible ni otras acciones sensibles.
- Chat de tarea: gestiona su encargo con el usuario, mantiene estado, título, entrega, revisiones y limpieza. El arranque presenta comprensión y espera al usuario. Cada chat puede usar sus propias capacidades y subagentes sin convertirlos en chats de tarea nuevos.
- Estado canónico: `TAREA.md`, escrito por el coordinador a partir de las declaraciones del chat asignado. Estados: Preparada, Esperando al usuario, En curso, Bloqueada, Pausada, Finalizada y Cancelada. Registrar fecha y motivo o intervención necesaria cuando corresponda.
- Estructura mínima aceptada: `coordinacion/INDICE.md` y por tarea `TAREA.md` y `ENTREGAS.md`. El índice enlaza tareas y última entrega consultada; no duplica estados. Una entrega breve por ciclo conserva resultado, evidencias y pendientes pertinentes.
- Registros compartidos: existe una única carpeta canónica `coordinacion/` en la raíz local del proyecto, también con worktrees; solo el coordinador la escribe. Las tareas reciben referencias y cauces de aviso y consulta autorizados, con alternativa manual y sin duplicar el estado canónico. El seguimiento en Git y la privacidad se deciden por proyecto; permisos, concurrencia y recuperación requieren pruebas.
- El usuario y el coordinador pueden decidir un cambio de alcance y trasladarlo en una entrada persistente. El chat responsable procesa la decisión y comunica su actualización al coordinador. Las entradas no cambian alcance por sí solas ni garantizan interrupción inmediata.
- Al finalizar o cancelar con autorización del usuario, el chat persiste lo necesario y limpia recursos según herramientas y permisos disponibles, informando de pendientes. Operaciones sensibles conservan autorización específica. El coordinador archiva chats finalizados y cancelados inactivos después de la limpieza autorizada o registro de pendientes; no elimina recursos al archivar.
- Si queda limpieza pendiente, el chat registra cada recurso, motivo y acción necesaria. Puede finalizar si el pendiente no impide cumplir el alcance ni los criterios de cierre; si sí los impide, espera la autorización necesaria o queda bloqueado según corresponda. El coordinador mantiene visibles esos pendientes aunque archive el chat.
- Un chat archivado puede recuperarse cuando el cliente lo permita; se contrasta el contexto actual. Si no es posible, se informa y se ofrece continuidad manual o un chat nuevo según las reglas del cliente.
- Una mejora con la misma responsabilidad y resultado general usa el mismo ticket y un nuevo ciclo, con entrega propia y cierres anteriores conservados; se prioriza reutilizar el chat anterior. Un encargo con resultado o seguimiento independiente usa un ticket relacionado. Si el chat no es adecuado o accesible, se conserva el ticket y se registra su sustituto. Ante una ambigüedad material se consulta a Manuel.
- El usuario elige entre una tarea de escritura a la vez sin Git o habilitar Git y worktrees cuando necesite escritura paralela. No se exige Git a todos los proyectos. Los chats solicitan la integración al coordinador mediante el mecanismo persistente; el coordinador integra y revisa coordinadamente, respetando autorizaciones. La integración y los recursos externos aún requieren diseño y pruebas.
- Solicitud de integración: el chat de tarea registra identidad, ciclo, alcance, destino, versión exacta si hay Git, verificaciones y pendientes antes del cierre cuando integrar forme parte del encargo. El coordinador ordena según dependencias y prioridades conocidas, revisa contenido y evidencias como una PR, protege cambios preexistentes e integra en el destino autorizado. Detiene y consulta decisiones materiales; conserva datos ante fallos, verifica el resultado y registra versiones, comprobaciones y pendientes para que el chat cierre y limpie lo autorizado. Una solicitud o acuse no autoriza `push`, publicación ni eliminaciones irreversibles. Sin Git se verifica en la carpeta del proyecto con una sola tarea de escritura a la vez.

## Activación y automatización

La capacidad se activa solo en proyectos elegidos, mediante instrucciones locales y una skill. El setup deja elegir la frecuencia por proyecto; Manuel considera suficiente una revisión diaria para el uso conversado, sin imponerla universalmente. La tarea programada pertenece al chat coordinador y su destino se actualiza en un relevo; se evita ejecutar duplicados. Sin capacidad de programación, se conserva una vía manual.

La revisión respeta pausas y estados canónicos, detecta cambios relevantes y verifica identidad e inactividad antes del archivado. Solo envía mensajes con autorización aplicable y no decide cambios materiales por mera detección. Ante permisos insuficientes, archivos faltantes o conflicto informa y conserva los datos.

## Propuestas pendientes de validación o aceptación

- Título de tarea: `[Estado] T-001 · Nombre breve`; título de coordinador: `<Proyecto> · Coordinador principal`. Una prueba puntual confirmó autorrenombrado, no sincronización completa.
- Entradas identificadas y acuses separados; publicación completa, exclusión de escritores y recuperación requieren diseño y pruebas. No prometer garantías por un simple reemplazo o lectura previa.
- Considerar solo tareas preparadas autorizadas, sin duplicados y con dependencias satisfechas; aplicar prioridades explícitas y consultar al usuario cuando no haya criterio suficiente.
- Desarchivar antes de reutilizar un chat archivado para una mejora; las excepciones adicionales de archivado siguen abiertas.
- Durante el relevo, pausar y verificar la tarea, cambiar destino y comprobarlo antes de reactivar. Se comprobó cambiar el destino de una tarea pausada; falta probar ejecución real, solapamientos y fallos.

Las notas adoptadas distinguen decisiones confirmadas de propuestas e investigación. Sus enunciados históricos sustituidos no prevalecen sobre las decisiones posteriores resumidas aquí.

## Contrato de avisos, acuse y recuperación

Aceptado por Manuel mediante go; pendiente de implementación y validación técnica.
Sustituye la escritura canónica por tareas y la exclusión absoluta de mensajería
de los acuerdos históricos. No activa el mecanismo en ningún proyecto.

1. La tarea conserva una copia recuperable del aviso antes de enviarlo: proyecto,
   tarea, ciclo, chat emisor, ID estable, revisión creciente dentro de la tarea y
   ciclo, estado, resumen y referencias. Un reenvío conserva ID y contenido; una
   corrección usa otro ID y referencia el anterior. Una fecha no sustituye la revisión.
2. El coordinador comprueba proyecto, asignación e identidad por las referencias
   disponibles, sin confiar solo en el ID declarado dentro del texto. Si no puede
   verificarlos o faltan datos, conserva el aviso pendiente e informa. Recibir un
   aviso no concede nuevas autorizaciones ni cambia el alcance por sí solo.
3. El coordinador es el único escritor del registro canónico. Aplica una revisión
   nueva, reconoce una repetición idéntica sin reaplicarla y conserva el estado ante
   una revisión antigua. Igual ID con contenido distinto, o igual revisión con
   estados incompatibles, queda como conflicto sin reemplazo automático.
4. Tras guardar y releer el resultado, publica un acuse consultable con ID del
   aviso, tarea/ciclo, decisión (aplicado, duplicado, antiguo, conflicto o pendiente),
   revisión vigente y referencia al registro. Solo aplicado o duplicado de un aviso
   ya aplicado confirma incorporación; antiguo confirma recepción sin aplicación.
   El acuse no aprueba la entrega ni autoriza integración o acciones sensibles.
5. La tarea distingue preparado, enviado, recibido y registrado. El retorno del
   transporte acredita solo lo que su contrato documente. Conserva aviso y evidencia
   de envío hasta reconciliar el acuse. Si no puede consultar el registro, comunica
   esa limitación; no interpreta silencio como éxito ni fracaso.
6. Ante interrupción o envío incierto se consulta primero el registro, el acuse y
   el historial accesible. Si el estado ya quedó guardado y falta acuse, el
   coordinador reconstruye este tras verificarlo. Si sigue incierto, conserva el
   pendiente y evita reenvíos ciegos. Un reenvío autorizado y justificado reutiliza
   el ID; no crea una actualización nueva para ocultar incertidumbre.
7. En un relevo se pausa la automatización, se comprueba que el coordinador anterior
   dejó de escribir y se transfieren registro, identidad y avisos pendientes.
   El nuevo coordinador reconcilia antes de actuar; después se verifica el nuevo
   destino programado. Si no se puede confirmar exclusividad, se detiene la escritura
   afectada y se informa. No se presupone protección por cambiar el título del chat.
8. Sin mensajería o consulta autorizada, el usuario puede trasladar el mismo aviso
   al coordinador y devolver o consultar el acuse. Las tareas conservan entregas y
   evidencias locales; no requieren permiso de escritura sobre el registro común.

Se comprueba al retomar trabajo, en hitos pertinentes y en la revisión configurada;
no exige sondeo continuo ni mensajes de respuesta automáticos. El cierre de una
tarea sigue sus criterios propios y muestra por separado cualquier registro pendiente.
Las pruebas de la nota 032 verifican casos guiados con el receptor preparado;
faltan interrupciones entre guardado y acuse, reinicios, conflictos y relevo con
pendientes. El almacenamiento, exclusión y publicación recuperable siguen el
[diseño aceptado](../../planning-artifacts/architecture/architecture-coordinacion-almacenamiento/ARCHITECTURE-SPINE.md),
adoptado como complemento obligatorio de esta especificación. Sus AD-1 a AD-5
fijan las invariantes; los detalles de implementación y sus pruebas siguen pendientes.
