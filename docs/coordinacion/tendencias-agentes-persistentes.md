# Agentes persistentes e interconexión de conversaciones

Consulta: 2026-11-15. Investigación documental para la nota 025.
Identidades: Dot de OpenAI y Grok Bot de xAI, este último confirmado por Manuel.
Se añaden OpenClaw, Cursor y A2A por sus aportes al diseño, sin proponer instalar
estos productos. No se han probado sus funciones ni la disponibilidad en la cuenta.

## Hallazgos documentados

### Dot: continuidad principal y contexto específico de cada tarea

La [guía oficial](https://help.openai.com/en/articles/20001530-getting-started-with-your-dot)
describe trabajo persistente y creación de tareas Work o Codex con el acceso
correspondiente. Aclara que cada tarea tiene conversación propia y no recibe
automáticamente todas las conversaciones con Dot. Esto respalda preparar contexto
explícito para cada encargo. No acredita una memoria global sincronizada entre
todos los chats ni documenta aquí un protocolo general entre pares.

### Grok Bot: responsable principal y especialistas duraderos

[Create and manage Bots](https://docs.x.ai/grok-bot/bots) describe un Bot con
trabajo, conversación y contexto propios; el principal coordina a los demás.
[How Grok Bot works](https://docs.x.ai/grok-bot/how-grok-bot-works), actualizado
2026-11-13, recomienda un Bot propio cuando un trabajo recurrente necesita
fuentes, reglas o calendario propios. Distingue memoria particular de ciertos
datos comunes. También advierte que los Bots comparten ordenador y no están
aislados entre sí: personalidad y conversación separadas no garantizan aislamiento.

[Message and collaborate](https://docs.x.ai/grok-bot/chat-and-collaboration),
actualizado 2026-11-12, documenta mensajes asíncronos que activan al receptor y
grupos para resultados compartidos. Recomienda un responsable por etapa para
evitar duplicaciones y ruido. Es una capacidad específica de ese producto;
no demuestra que nuestros chats puedan activarse o compartir grupos igual.

### OpenClaw: separar dirección de conversación y contexto de ejecución

Las [herramientas de sesión](https://docs.openclaw.ai/concepts/session-tool)
distinguen sesión, conversación, consulta de historial y ejecución en otra sesión.
Documentan creación independiente, apoyos supervisados y envío con espera opcional.
El timeout de espera del emisor no equivale a cancelar la ejecución receptora.
La enseñanza para AIKit es distinguir entrega de mensaje, inicio de trabajo y
resultado final, con identidad y reconciliación antes de repetir. Las políticas
de admisión siguen siendo necesarias; una dirección conocida no concede permiso.

### Cursor: separar planificación de ejecución y reconocer los costes

[Towards self-driving codebases](https://cursor.com/blog/self-driving-codebases),
2026-02-05, relata que asignar demasiados roles al ejecutor central provocó
conductas indeseadas. Su diseño posterior separó planificadores que no programan
y workers con entregas de retorno. También retiró un integrador central por
cuello de botella y aceptó compromisos de corrección para aumentar rendimiento.
Es una investigación a gran escala, no una receta para AIKit. Podemos aprovechar
la separación de roles sin adoptar su política de integración ni sus compromisos.

### A2A: mensaje, tarea y contexto son entidades distintas

[Life of a Task](https://a2a-protocol.org/latest/topics/life-of-a-task/) distingue
interacciones inmediatas mediante mensajes y trabajo con estado mediante tareas.
Un contexto puede agrupar varias tareas. Tras un estado terminal, una continuación
se representa como otra tarea relacionada, no reactivando la anterior. Es una
distinción útil para conservar historial. No obliga a crear otro chat visible
ni a adoptar A2A o cambiar el esquema de avisos existente.

Las páginas sin fecha editorial se consideran documentación vigente consultada
en esta fecha. Se revisó también el changelog oficial de OpenAI; no se dedujeron
de él capacidades de Dot ausentes de la guía. Son fuentes primarias de producto
y una experiencia de ingeniería; describen mecanismos, no comparaciones
independientes de eficacia. No hay evidencia aquí de que uno sea el mejor sistema.

## Consecuencias propuestas para AIKit

Las siguientes son inferencias de diseño, no capacidades ya implementadas.
Mantienen la decisión del usuario: el coordinador coordina y no implementa ni
hace code review.

### Responsabilidad, conversación y ejecución

- Responsabilidad: quién responde por un ámbito o una entrega.
- Chat: contexto de interacción y continuidad con el usuario y el coordinador.
- Encargo/ciclo: unidad delimitada de trabajo dentro de esa responsabilidad.
- Ejecución: intento concreto, que puede fallar o interrumpirse sin perder el
  encargo ni justificar repetirlo automáticamente.

No imponer una equivalencia entre estas entidades. Reutilizar un chat para una
corrección relacionada puede conservar contexto; identificar una nueva entrega
o ciclo evita sobrescribir lo terminado. El auxiliar actual no implementa nuevos
ciclos ni reasignación: no simularlos modificando sus datos a mano.

Un especialista persistente por área podría ser útil si aparece trabajo
recurrente con fuentes y reglas propias. No se propone crearlo por defecto ni
sustituir ahora los Chats de Tarea por departamentos permanentes.

### Interconexión

Recomendar inicialmente comunicación coordinador-tarea y retornos de apoyos
acotados, con un solo responsable del siguiente paso. Cada traspaso debe expresar
resultado solicitado, contexto pertinente, referencias/versiones, límites,
dependencias, destino de respuesta y condición de aceptación.

Distinguir informar de pedir ejecución y de trasladar una decisión humana. Definir
esas intenciones al preparar encargos no añade campos al aviso v1 ni permisos.
Registrar la relación con tarea/ciclo, emisor y receptor, evitando usar títulos
como identidad. Consultar antes de reenviar ante una respuesta incierta.

No abrir comunicación libre entre todos los chats por defecto. Si una tarea
necesita a otra, el coordinador resuelve el reparto. Un canal directo futuro
podría limitarse a intercambio técnico autorizado y trazable, sin facultad para
crear encargos, cambiar prioridades o integrar. Eso requiere decisión y prueba
separadas; no está habilitado por este informe.

La operación asíncrona necesita transporte y ejecución del cliente: una skill y
archivos compartidos por sí solos no despiertan un chat. Usar herramientas nativas
cuando existan y traslado manual cuando no. Mantener el registro canónico separado
de memoria personal y conversación, y no confundir aislamiento de contexto con
aislamiento de archivos, permisos o recursos externos.

### Ejecución directa y delegación

| Situación | Responsable/medio propuesto |
| --- | --- |
| Priorizar, aclarar alcance, asignar, registrar estado, coordinar dependencias e integración | Coordinador directamente, con herramientas. |
| Investigación o revisión técnica delimitada, sin continuidad propia | Subagente autorizado, con entrega al coordinador. El coordinador recibe el dictamen, no repite el code review. |
| Implementación con iteraciones, decisiones de trabajo y seguimiento | Chat de Tarea. Reutilizar el responsable existente si corresponde. |
| Comando, prueba o corrección dentro del encargo de una tarea | Ese Chat de Tarea directamente, sin otro chat por cada paso. |
| Trabajo recurrente con contexto específico estable | Evaluar reutilización; considerar responsable persistente solo si aporta beneficio y se aprueba ese modelo. |
| Trabajo muy dependiente del mismo contexto o recurso | Mantenerlo unido en su responsable y secuenciar; no llevar la implementación al coordinador. |

Para evaluar un apoyo de una sola ejecución: resultado definido, entradas
disponibles, límites claros y sin responsabilidad continua con el usuario. Si
requiere iteraciones extensas y coordinación propia, tratarlo como tarea, sin
encadenar apoyos efímeros para ocultar esa continuidad.

## Qué adoptar, qué posponer

1. Recomendado: aclarar entidades, reutilización y traspasos con responsable único;
   mantener separación entre coordinación, implementación y revisión técnica.
2. Posponer: red libre entre pares, especialistas permanentes, jerarquías recursivas
   y operación siempre activa. Añaden requisitos que todavía no hemos validado.

Prueba posterior: una tarea recibe un encargo, solicita una aclaración, entrega
resultado, recibe corrección y conserva su contexto. El coordinador solicita
revisión independiente, integra cuando corresponda y registra el cierre. Comprobar
ausencia de doble ejecución, contexto suficiente y pendientes visibles. Probar
interrupciones sin atribuir al registro manual garantías transaccionales.

Este informe no crea chats, envía mensajes, instala productos ni modifica el
contrato o las skills instaladas. El piloto queda pendiente de preparación.
