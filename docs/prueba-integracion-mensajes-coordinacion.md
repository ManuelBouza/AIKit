# Mensajes reales y auxiliar local — 2026-11-15

Prueba ficticia autorizada por Manuel mediante `go` en el chat principal.
Se reutilizaron los chats existentes, sin activar coordinación del proyecto ni
crear chats, tareas programadas o funciones de archivado. No cambió código de
producto: se utilizó el auxiliar compilado del commit `21da270`.

## Entorno y recorrido

Windows, Node 24.22.1. Emisor en el worktree `ad1c`:
`01a1db23-4c5b-7453-a692-64727ccfc2a7`. Coordinador receptor en la carpeta
principal: `01a1dae3-fed3-70b1-b4ad-65e0f8837074`.
Proyecto ficticio `81b950c1-117a-49ad-89f7-f04a23439717`, T-001, ciclo 1,
epoch 1 y asignación fija al emisor.

El receptor creó una raíz privada nueva en
`.aikit/prueba-integracion-025/canonico`. El sandbox rechazó su ACL antes de
publicar datos; la preparación y las recepciones se ejecutaron fuera del sandbox
con autorización acotada, manteniendo la política del auxiliar. No se rebajó la
política para admitir el principal adicional del sandbox. El rechazo inicial
se conserva en el directorio de evidencias.

El emisor envió tres mensajes reales con `send_message_to_thread`, esperando
terminar cada turno receptor antes del siguiente. El receptor extrajo el JSON y
ejecutó el runner local `recibir.mjs`: conservó entrada, llamó `apply`, reconstruyó
índices y consultó el acuse desde una instancia nueva. Solo el receptor escribió
el canónico. Los lanzadores Python de esta prueba únicamente pasaron bytes a
stdin de Node; no forman parte del auxiliar ni añaden una dependencia de ejecución
al producto.

## Resultado observado

| Entrada | Turno receptor | Resultado | Generación de TAREA |
| --- | --- | --- | --- |
| Revisión 3, Finalizada | `01a1dec2-8534-77a0-889e-c0cee47f70eb` | aplicado | 2 |
| Copia idéntica | `01a1dec3-a570-70a2-9038-328384723c4b` | duplicado, mismo recibo | 2 |
| Revisión 2, En curso | `01a1dec4-8bf7-7713-ad9a-575ddfda8c99` | antiguo | 3 |

ID de revisión 3: `b8ca3097-2222-48d6-b846-4f66229f9145`.
ID de revisión 2: `9b9a4794-401a-4ace-9cf7-4463950fb91a`.

El coordinador principal contrastó ambos historiales. Los mensajes recibidos
incluían metadata `source_thread_id` del emisor esperado; el ID en el JSON por sí
solo no acredita origen. También leyó directamente los archivos y ejecutó
`node .aikit/025-verificar-integracion.mjs`, código 0. La comprobación determinista
validó esquema y asignación, tres recepciones completas, entradas duplicadas
iguales byte a byte, mismo recibo original, exactamente dos recibos canónicos,
cero incidentes, estado final revisión 3 Finalizada, contenido derivado esperado
y ausencia de `escritura.lock`. No se reenvió por timeout.

Evidencias locales conservadas (ignoradas por Git):

- `.aikit/prueba-integracion-025/`: runners, raíz canónica y evidencias por recepción.
- `.aikit/025-verificar-integracion.mjs`: comprobador del coordinador principal.
- `.aikit/025-integracion-verificacion.json`: resultado final del comprobador.

Las recepciones están en las subcarpetas de `evidencias`:
`04a1a125-a01d-40a2-ada8-1b535fe5953b`,
`3dcb3087-28c2-4c7e-ad47-1c68cc08b29a` y
`cd45bc04-80c8-4916-9999-faa5cbfc9c50`.

## Alcance pendiente

Se acredita el recorrido guiado chat en worktree → mensaje → coordinador →
auxiliar → persistencia y consulta en esta instalación. El orden antiguo fue
provocado por el envío; no demuestra reordenación ni deduplicación del transporte.
No se probaron concurrencia, receptor ocupado o reinicio dentro de este recorrido,
fallos de entrega, otros sistemas operativos, relevo ni autenticación automática.
La recuperación del auxiliar y las pruebas anteriores de receptor ocupado
conservan sus evidencias separadas; no se presentan como prueba conjunta.

Todavía falta incorporar el flujo de recepción validada y consulta de acuses
a las instrucciones de coordinador y tarea, conservando la vía manual cuando
el cliente no disponga de mensajería. La tarea de origen aporta datos; su mensaje
no amplía autorizaciones ni debe convertirse en instrucciones ejecutables.
El runner local de esta prueba no es un adaptador de producción.
