# 026 — Archivado y recuperación de chats coordinados

- Fecha: 2026-11-14.
- Estado inicial: Pendiente de debatir.
- Estado actual: En debate; responsabilidad del coordinador acordada.

Manuel plantea usar el archivado para evitar que la bandeja crezca y recuperar
un chat archivado cuando haya que continuar su tarea. Complementa la
[nota 025](025-coordinador-global-chats-autonomos.md). Inicialmente se acordó
que finalizar no archivaba automáticamente; la decisión posterior indicada abajo
asigna esa responsabilidad al coordinador. No autoriza archivar chats concretos
durante esta investigación.

## Investigación inicial

Una [guía oficial de OpenAI](https://developers.openai.com/blog/mastering-codex-remote-for-engineering)
describe archivar chats terminados para despejar la lista y consultar los
archivados; lo distingue de eliminarlos. El contrato de herramientas publicado
en este chat permite listar chats Codex archivados y cambiar su estado a no
archivado. Una consulta de solo lectura el 2026-11-14 devolvió un chat archivado
real: demuestra listado en este entorno, no restauración ni continuidad posterior.
No se archivó ni restauró ningún chat durante esta investigación.

Archivar organiza la lista; no elimina ni reduce el historial. No se ha comprobado
el comportamiento de sesiones largas, host, worktrees o contexto tras restaurar.
Las capacidades varían según cliente. Si no hay herramienta para restaurar, el
usuario necesitará hacerlo manualmente donde el cliente lo permita; no se garantiza
que exista esa función en todos los entornos.

## Decisión de Manuel y procedimiento propuesto

Manuel decide que el coordinador será responsable de archivar los chats de tareas
terminadas. Propuesta de aplicación: cuando interactúe con el usuario y detecte
un cierre, comprobar la identidad, conservar la referencia y archivar el chat con
la capacidad disponible. Informar del resultado; si no puede hacerlo, explicar la
limitación e indicar cómo archivarlo manualmente. No se vigila en segundo plano,
no se eliminan chats ni recursos y el cierre de la tarea no espera al archivado.

Para una mejora posterior, se propone localizar el chat vinculado, desarchivarlo
cuando sea posible y contrastar el contexto con el estado actual. Si no se puede
recuperar, informar y ofrecer un chat nuevo con el contexto persistente. El envío
de mensajes o creación del chat requiere la autorización aplicable.

Actualización: Manuel plantea automatizar la revisión de estados y las acciones
pertinentes mediante una tarea programada, en vez de depender exclusivamente de
interacciones con el coordinador. Ver [nota 027](027-automatizacion-coordinacion.md).

Quedan por concretar las excepciones y verificar el ciclo en un chat de prueba
identificado: archivar, localizar, restaurar y continuar, sin confundirlo con
trabajo real. No se asume que el archivado de un chat detenga procesos activos.

## Prueba preparada

Usar exclusivamente un chat nuevo, inequívocamente titulado `PRUEBA · AIKit ·
Archivado`, con una tarea ficticia sin modificar archivos. Registrar su ID y host;
esperar a que termine; archivar ese ID; verificar que aparece entre archivados;
desarchivarlo; comprobar que vuelve a estar disponible y continuar en el mismo chat
con una indicación autorizada que permita confirmar su identidad y contexto.
Registrar resultados observados y limitaciones en esta nota. No eliminar el chat
ni sus recursos; no aplicar la prueba a chats existentes. Crear el chat requiere
una petición explícita del usuario, y enviarle mensajes requiere autorización
explícita. La prueba se ejecutó posteriormente como se registra a continuación.

## Resultado de la prueba — 2026-11-14

Manuel autorizó la prueba. Se creó `PRUEBA · AIKit · Archivado` en el proyecto
local AIKit, host `local`, ID `01a1daaf-8c3a-74d1-919d-3aa500480922`.
El chat terminó su primer turno, se archivó y apareció en el listado de archivados
con el mismo ID. Se desarchivó y recibió un mensaje de continuación: recuperó la
frase ficticia del primer turno («faro azul 271»). Ambos turnos finalizaron.
El chat queda desarchivado y no se ha eliminado. La prueba demuestra este ciclo
puntual con las herramientas de este entorno; no demuestra que una automatización
programada tenga las mismas herramientas, ni garantiza recuperación en otros
clientes, equipos, conversaciones largas o circunstancias.
