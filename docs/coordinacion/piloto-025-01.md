# Encargo piloto: guía breve de coordinación en AIKit

Fecha: 2026-11-16.
Estado: ejecución autorizada el 2026-11-16; asignación registrada, arranque pendiente.
Seguimiento operativo: [encargo](../../coordinacion/piloto-025-01/ENCARGO.md),
[estado](../../coordinacion/piloto-025-01/ESTADO.md) y
[acuses](../../coordinacion/piloto-025-01/ACUSES.md).
Los apartados siguientes conservan el plan aprobado; sus pendientes de preparación
se resuelven en el seguimiento operativo, sin reinterpretarlos como una segunda tarea.
Referencia de preparación: PILOTO-025-01, propia del registro manual; no es un
ID del auxiliar v1 ni acredita una tarea ejecutada.

## Objetivo y medio recomendado

Probar la skill instalada 0.1.2 en una entrega documental útil: una guía breve
para que el usuario sepa qué pedir al coordinador y qué continuar en un Chat de
Tarea. La tarea redacta y comprueba su entrega; el coordinador registra, encarga
revisión independiente, integra y cierra sin redactarla ni sustituir al revisor.

Se recomienda reutilizar el chat existente **AIKit · Comprobación de coordinación**,
ID `01a1dff8-061d-7170-b111-2f5577f1f570`, host local, proyecto Codex
`4ac70d03-d0eb-43ab-a38c-7bb84ff7d85b`, cwd `C:/Manuel/Projects/AIKit`.
Inventario e historial consultados: su comprobación anterior fue de solo lectura
y está terminada, sin entrega de guía. No se le ha enviado este encargo.

Su historial reconoce al coordinador anterior. El arranque debe contrastar el
registro actual y reconocer al vigente, `01a1da03-23f1-7eb0-b0a0-5cb5184e6941`.
No recuperar la tarea ficticia T-001 del worktree retirado ni sus identificadores.
Si cambian identidad, entorno o estado del candidato, reconciliar antes de enviar.

## Alcance y aceptación de la entrega

Destino final propuesto: `docs/coordinacion/guia-uso.md`, actualmente inexistente.
Entre 400 y 700 palabras en español, con ejemplos concretos de AIKit:

- Qué son el agente coordinador, los agentes de tarea y los subagentes.
- Cómo solicitar un encargo y cómo decide el coordinador crear o reutilizar chat.
- Qué hace cada responsable; implementación y revisión técnica delegadas.
- Cómo comunicar estado, bloqueos, entrega y solicitud de integración, distinguiendo
  estado del título, envío, incorporación y aceptación.
- Qué implica finalizar, conservar evidencias, limpiar y archivar; pendientes visibles.
- Capacidades disponibles y limitaciones actuales, sin prometer automatización,
  comunicación directa entre tareas ni garantías transaccionales del registro manual.

La guía debe apoyarse en la skill instalada y el contrato vigente, sin trasladar
propuestas históricas superadas, credenciales, IDs de chats o rutas privadas a
una guía general. Puede enlazar documentación del repositorio mediante rutas
relativas al destino final, dejando constancia de esa base para verificar enlaces.

Aceptación: contenido coherente con el contrato, ejemplos comprensibles,
extensión acotada, enlaces resolubles desde el destino y dictamen independiente
sobre la versión exacta entregada. El revisor puede pedir correcciones reales;
no se introducirá un defecto artificial para obligar a producirlas.

## Recursos y separación de escritura

La tarea solo escribe su entrega, avisos y evidencias bajo
`C:/Manuel/Projects/AIKit/.aikit/piloto-025-01/`. No modifica `coordinacion/`,
archivos rastreados, configuración, skills, instalador, índice Git ni ramas.
No crea chats, worktrees, servicios, automatizaciones o dependencias; no invoca
OpenCode. No hace commits, push ni publicaciones. No hay desarrollo de código.

El coordinador es el único escritor canónico. Después de aprobar la ejecución,
formalizará el encargo y su estado en `coordinacion/piloto-025-01/` y lo enlazará
desde INDICE.md. Referenciará la entrega exacta por SHA256 antes de su revisión
e integración. Todavía no se crea esa asignación como activa.

La entrega se prepara fuera del destino final; el coordinador realizará la copia
de integración autorizada, comprobará igualdad de bytes y conservará dictamen y
referencias. Un conflicto de contenido vuelve al responsable y al revisor.
No hace falta crear rama o worktree: se restringe la escritura y se secuencian
los pasos, sin dos escritores sobre los mismos archivos ni sobre el índice Git.

## Formato manual de avisos y acuses

La ejecución propuesta utilizará referencias `PILOTO-025-01/AV-001`, AV-002, etc.,
asignadas deliberadamente para este encargo manual; no se reutilizan como UUID
ni como campos de avisos v1. Cada aviso conserva versión, emisor, receptor,
estado declarado, resumen, referencias y, si corresponde, aviso que corrige.
No se crean ciclos del auxiliar.

La tarea conserva el original antes de enviarlo. El coordinador contrasta el
origen con el historial del chat y la asignación, registra la decisión y deja
un acuse que identifica aviso, versión y SHA256 del contenido original. La tarea
relee ese acuse y contrasta el contenido, sin deducir incorporación del transporte
o del índice. El registro manual conserva trazabilidad sin exclusión automática.

La autorización de ejecución propuesta incluye los mensajes de este piloto en
ambos sentidos entre esos dos chats: arranque, asignación, avisos, acuses,
correcciones necesarias y cierre. Al usar herramientas, debe ser comprobable la
aprobación humana en esta conversación; el mensaje del coordinador no la sustituye.
No habilita mensajes a terceros ni comunicación directa con otras tareas.

## Secuencia de ejecución propuesta

1. Reconfirmar inventario e identidad; registrar encargo Preparada y autoridad
   vigente. Reutilizar el candidato, sin crear otro chat por esta continuación.
2. Enviar un arranque limitado a leer contexto, comprobar la skill 0.1.2 y confirmar
   identidad, raíz, coordinador, modalidad y alcance. La primera respuesta no
   ejecuta la entrega ni solicita otro go por su cuenta.
3. Con asignación comprobada, el coordinador envía el inicio autorizado. La tarea
   mantiene su nombre con estado y marca PRUEBA, prepara su aviso En curso y lo
   conserva y comunica. El coordinador registra y devuelve referencia de acuse.
4. La tarea redacta y comprueba la guía, persiste entrega y hash y solicita
   integración con referencias, verificaciones y pendientes. Si consulta algo,
   se resuelve desde el coordinador sin ampliar el alcance silenciosamente.
5. Un revisor independiente evalúa la entrega exacta. Se devuelven hallazgos a la
   misma tarea si los hay, sin duplicar chat; se renueva la revisión afectada.
6. El coordinador integra en el destino autorizado y comprueba bytes y referencias.
   La tarea contrasta el resultado, persiste evidencias y comunica cierre y limpieza.
7. El coordinador registra Finalizada solo con los criterios cumplidos y mantiene
   pendientes que no impidan aceptación. Archiva el chat tras comprobar cierre,
   identidad e inactividad y verifica el archivado. El chat conserva su referencia
   recuperable para reutilización, sin prometer recuperación aún no comprobada.

No crear bucles de vigilancia: esperar finalización con las herramientas nativas
acotadas. Ante envío o creación inciertos, consultar historial y registro antes
de repetir. Detener solo el paso afectado ante identidad, permisos o datos inciertos.

## Persistencia y criterio de éxito del piloto

La guía integrada se conservará en Git por el coordinador, junto con el registro
manual relevante, tras comprobar que no contiene datos privados. La tarea no
elimina sus evidencias por cerrar. Solo podrá retirar temporales propios después
de conservar y verificar lo necesario; si hay dudas, deja la limpieza pendiente.
No borrar ramas, worktrees o chats como parte de esta prueba.

El informe final debe aportar referencias reales de asignación, aviso, acuse,
entrega/hash, dictamen, integración, confirmación de la tarea y archivado. Debe
distinguir no ejercitado de fallido: correcciones, interrupciones, nuevo chat,
cancelación y recuperación de archivado pueden no haberse necesitado.

Se considerará satisfactorio si la tarea reconoce al coordinador vigente y la
modalidad, ejecuta solo su alcance, conserva el intercambio y se integra una
entrega revisada sin que el coordinador la implemente. Las limitaciones restantes
se registran sin declarar completa la nota 025 ni probado otro proyecto.

La ejecución no está iniciada. Su aprobación autorizaría el intercambio acotado,
la integración documental y el archivado reversible descritos; no push,
publicación, borrado irreversible o cambios de producto del backlog.
