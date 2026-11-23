# Responsabilidad única de los chats

Fecha: 2026-11-22.
Estado inicial: Pendiente de debatir.
Estado actual: Revisión de activación integrada en main; paquete verificado; interfaz pendiente.

El 2026-11-23 se preparó la candidata privada 0.1.10 a partir de `a97124a`.
La actualización del catálogo 0.1.9 a 0.1.10 y la vista previa de activación
se verificaron por CLI con un perfil y un proyecto ficticios. El perfil
habitual y la versión del manifiesto en el repositorio se conservaron.
La prueba de activación desde la interfaz sigue pendiente.

Para la siguiente revisión se aplicará el [criterio de la nota 039](039-setup-centro-activacion-capacidades.md#criterio-para-clasificar-capacidades-en-setup):
como esta opción escribe en el `AGENTS.md` local, su activación y retirada
deben seguir `install --project`. El flujo guiado puede pedir la raíz
compartida, y las operaciones del inventario siguen siendo independientes.

En el perfil ficticio, el servidor de Codex descubrió `aikit-setup` 0.1.10
habilitada y el manifiesto instalado apuntó a esa skill para iniciar setup.
Tras activar por CLI en el proyecto ficticio, `codex debug prompt-input`
mostró el bloque de responsabilidad única en el contexto del proyecto, donde
antes no estaba. No se usó inferencia. La prueba gráfica sigue pendiente y
no se cambió el perfil habitual.

Cada chat tiene una responsabilidad única y consultable por los demás. Una
petición fuera de ese alcance debe encaminarse al chat que ya cubre la materia,
a un chat nuevo si basta un resumen o a un fork nativo si el historial es
necesario. El chat de origen conserva su encargo.

El resultado debe formar parte de AIKit y funcionar con las capacidades
nativas de Codex y las instrucciones globales y locales de `AGENTS.md`.
Queda por decidir cómo se configura desde `aikit-setup`, qué datos conserva
el inventario y cómo se comprueba que cada chat pueda consultarlo. El alcance
no incluye recuperar el mecanismo retirado de Coordinador y Chats de Trabajo.

Primero se madura la idea con el usuario y se contrastan las capacidades
nativas con documentación oficial y fuentes especializadas. Después se define
el alcance, se planifica con el flujo BMAD pertinente y, con autorización,
se implementa, verifica e integra en AIKit.

El borrador aplicado prematuramente en el proyecto se retiró. Esta nota
conserva la propuesta para seguir el proceso establecido.

## Propuesta para debatir

- Preferencia optativa de proyecto desde `aikit-setup`. El bloque local
  de `AGENTS.md` explica la regla y dónde consultar el inventario. Usar
  un inventario por proyecto en vez de uno global entre proyectos.
- Registrar por chat su ID nativo completo como clave, título, responsabilidad
  en una frase y estado. En un fork, registrar el ID nuevo y el ID de origen.
  El inventario no copia conversaciones. Si el cliente no expone el ID, dejar
  el alta pendiente de verificación en vez de identificar el chat por título.
- Una responsabilidad puede abarcar varias tareas relacionadas. Si la
  solicitud encaja, se atiende en el chat actual. Si hay otro responsable
  vigente, se recomienda ese chat. Cuando no lo hay, se recomienda uno nuevo
  si basta un resumen y un fork si el historial es necesario. Una coincidencia
  dudosa o un registro inaccesible se comunica sin asumir que no hay otro chat.
- Recomendar un destino y ejecutar el traslado son pasos distintos. Usar las
  acciones nativas cuando estén disponibles y autorizadas. Si faltan, indicar
  el destino o facilitar un resumen para trasladarlo manualmente. El chat de
  origen conserva su responsabilidad. Compartir historial mediante un fork no
  aísla los archivos de un checkout compartido.

Para validar la propuesta, dos chats de un proyecto de prueba deben poder
consultar el mismo inventario y distinguir sus respectivas responsabilidades.
Los escenarios deben cubrir solicitud dentro de alcance, reutilización,
chat nuevo, fork y acceso insuficiente, sin exigir una herramienta externa.
El lugar y formato del inventario, su acceso desde entornos aislados y las
escrituras concurrentes se concretarán en la planificación.

## Identidad, título y estado acordados

Cuando se registra un chat, renombrarlo con el formato
`[Estado] Proyecto · Responsabilidad breve`. Ejemplo:
`[En curso] AIKit · Inventario de capacidades`. El ID permanece en el
inventario. El nombre breve describe la responsabilidad y permanece estable
cuando cambia solo el estado.

Estados acordados:

- **Disponible:** puede recibir trabajo dentro de su responsabilidad.
- **En curso:** tiene trabajo en marcha.
- **En espera:** espera una decisión, información o dependencia identificada.
- **Pausado:** se ha decidido detener el trabajo hasta retomarlo.
- **Cerrado:** la responsabilidad ya no está activa.

El inventario es la referencia del estado de trabajo. Guarda la fecha de
actualización y, en espera o pausa, el motivo y la condición para continuar.
Cada chat actualiza su entrada al cambiar de estado y refleja ese cambio en el
prefijo del título con la acción nativa de renombrado cuando esté disponible.
Si no puede actualizar el título, el estado registrado sigue siendo válido y
el título queda pendiente de sincronizar. El estado de trabajo se registra
aparte de señales del cliente como un turno activo o el archivado.

Comprobar que el mismo ID se conserva al renombrar, que dos chats con títulos
iguales se distinguen por ID y que un cambio de estado se refleja en el
inventario y, cuando el cliente lo permite, en el título visible.

El usuario aprobó con `go` el formato y estos cinco estados. La decisión
queda como entrada para la planificación de su incorporación a AIKit.

El [plan de incorporación a AIKit](../_bmad-output/planning-artifacts/plan-047-responsabilidad-unica-chats.md)
define la entrega, el flujo BMAD y sus criterios de aceptación.
La [especificación Build](../_bmad-output/implementation-artifacts/spec-047-responsabilidad-unica-chats.md)
concreta la escritura segura del inventario y las comprobaciones de la entrega.

## Contraste documental

- [Guía de Codex sobre AGENTS.md](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide)
  describe cómo se cargan instrucciones globales y del proyecto. Esto permite
  proponer un bloque local que remita a un archivo compartido. Su lectura desde
  otro checkout o cliente deberá comprobarse en el entorno de destino.
- [Guía de OpenAI sobre flujos en Codex](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex)
  usa archivos de proyecto para guardar objetivos y acuerdos. Es un precedente
  para separar las instrucciones duraderas del inventario cambiante.
- [Guía de trabajo remoto con Codex](https://developers.openai.com/blog/mastering-codex-remote-for-engineering)
  describe el fork nativo para conservar historial al tomar otra dirección.
  La herramienta expuesta en esta sesión confirma que el fork conserva el
  historial y puede hacerse en el mismo directorio. No se creó ningún chat
  para este contraste.
