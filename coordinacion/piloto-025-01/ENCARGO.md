# PILOTO-025-01 — Guía breve de uso de la coordinación

Fecha: 2026-11-16. Versión de encargo: 1. Modalidad: manual, sin auxiliar v1.
Estado inicial: Preparada; confirmar arranque antes de ejecutar la entrega.

- Proyecto: AIKit, raíz `C:/Manuel/Projects/AIKit`.
- Registro canónico único: `C:/Manuel/Projects/AIKit/coordinacion/`.
- Coordinador vigente: `01a1da03-23f1-7eb0-b0a0-5cb5184e6941`, host local.
- Chat responsable: `01a1dff8-061d-7170-b111-2f5577f1f570`, host local.
- Título anterior: AIKit · Comprobación de coordinación.
- Título de trabajo: `[Preparada] PRUEBA · AIKit · Guía de coordinación`,
  sustituyendo Preparada al declarar cambios de estado.

## Autorización humana comprobable

Manuel aprobó la ejecución con «go» en el chat del coordinador, turno
`01a1e2f4-4a7f-7472-b68a-66f385ec399c`, mensaje de usuario
`01a1e2f4-4b40-7db0-88f2-a51bf61fde1b`. Aprueba la Próxima Tarea del final
del turno anterior `01a1e2f0-36da-7a12-ab41-89d9c2c8ed70`: ejecutar este piloto,
mensajes en ambos sentidos, integración de la guía y archivado tras cierre.
Ambos turnos fueron consultados con read_thread, distinguiendo userMessage del
mensaje de un agente. La tarea puede contrastar esa misma evidencia antes de
enviar mensajes; el presente archivo y el encargo recibido no la sustituyen.

Este encargo nuevo reemplaza las restricciones de solo lectura de la comprobación
anterior únicamente dentro del alcance autorizado a continuación. No altera la
autoridad del coordinador ni concede permiso a terceros.

## Resultado y límites

Preparar una guía de 400–700 palabras en español conforme al
[piloto aprobado](../../docs/coordinacion/piloto-025-01.md), con definiciones de
roles, ejemplos de uso, creación/reutilización de chats, avisos/acuse/aceptación,
integración, persistencia, limpieza y límites actuales.

Leer AGENTS.md, PROYECTO.md, este encargo y la skill instalada 0.1.2 con sus dos
referencias; usar el contrato vigente y distinguirlo de su historial superado.
No copiar IDs o rutas privadas en la guía general. La entrega se prepara en
`.aikit/piloto-025-01/entrega/guia-uso.md`; el destino final, solo por integración
del coordinador, será `docs/coordinacion/guia-uso.md`.

Única raíz de escritura de la tarea: `C:/Manuel/Projects/AIKit/.aikit/piloto-025-01/`.
También mantiene su propio título con las herramientas autorizadas. No modifica
canónico, archivos rastreados, configuración, índice Git ni ramas. No hace commits,
push, instalaciones, nuevos chats, OpenCode, worktrees o automatizaciones.
Mensajería autorizada solo con el coordinador de este piloto, no con otras tareas.

## Arranque e inicio

El primer mensaje solo debe confirmar identidad, entorno, coordinador vigente,
modalidad manual, skill 0.1.2 leída y alcance. Debe reconocer el cambio respecto
del coordinador citado en el historial anterior. Puede actualizar su título a
Preparada; todavía no redactar la entrega. Tras esa confirmación, el coordinador
envía el inicio y la tarea procede sin solicitar otro go al usuario.

## Avisos y entrega

Avisos manuales originales recuperables en `.aikit/piloto-025-01/avisos/`, con
referencias PILOTO-025-01/AV-001 y siguientes, versión creciente, emisor/receptor,
estado, resumen, referencias y corrección relacionada si procede. No son JSON v1
ni ciclos del auxiliar. Conservar antes de enviar. La tarea comunica En curso,
solicitud de integración y cierre; el coordinador registra origen, versión y hash
en ACUSES.md y la tarea contrasta los recibos antes de afirmar incorporación.

Entregar versión/hash exactos y verificaciones de extensión y enlaces desde el
destino final. La revisión independiente se encarga desde el coordinador. Las
correcciones pertinentes vuelven a este chat. Si hay integración pendiente, no
declarar satisfechos los criterios de cierre. La tarea verifica la integración,
conserva evidencias y declara limpieza realizada o pendientes; el coordinador
verifica el cierre e inactividad antes de archivar reversiblemente el chat.

No eliminar evidencias ni fabricar un fallo para ejercitar correcciones. Si algo
no puede comprobarse, comunicar el límite y detener solo el paso afectado.
