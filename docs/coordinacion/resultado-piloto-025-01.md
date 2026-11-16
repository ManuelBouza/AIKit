# Resultado del piloto de coordinación en AIKit

Fecha: 2026-11-16. Resultado: satisfactorio en el alcance probado.
Plan: [PILOTO-025-01](piloto-025-01.md).
Entrega útil: [guía breve de uso](guia-uso.md), 541 palabras.
Modalidad: registro manual y skill instalada 0.1.2; no se utilizó el auxiliar v1.

## Resultados observados

| Paso | Resultado y evidencia |
| --- | --- |
| Autorización | Go humano contrastado por ambos chats en el historial del coordinador; no se tomó el mensaje de otro agente como autorización humana. |
| Reutilización | Se reutilizó AIKit · Comprobación de coordinación en su cwd existente, sin crear chat, rama o worktree. Identidad contrastada mediante cliente e historial. |
| Arranque | La tarea leyó 0.1.2 y reconoció al coordinador vigente, distinto del recordado por su comprobación anterior. Esperó la señal de inicio antes de redactar. |
| Estado y título | La propia tarea mantuvo Preparada/En curso/Finalizada según las acciones ejercitadas; se observaron directamente los títulos En curso y Finalizada. No se afirma renombrado observado a Preparada. |
| Comunicación | Tres avisos originales conservados y enviados mediante herramientas nativas; el coordinador fue el único escritor canónico. No hubo comunicación entre tareas. |
| Acuses | La tarea contrastó los tres acuses con originales completos y hashes; distinguió transporte de incorporación y aceptación. No se generó un bucle de acuses. |
| Revisión | Revisor independiente: accepted sin hallazgos accionables sobre el hash exacto. El coordinador no redactó ni hizo revisión de contenido de la guía. |
| Integración | Copia mecánica en el destino inexistente, bytes iguales al artefacto revisado y enlace local resoluble; persistida en Git. |
| Cierre | La tarea verificó integración y dictamen, conservó evidencias y declaró Finalizada. La persistencia Git se contrastó por la tarea mediante evidencia del coordinador, sin lectura propia del blob. |
| Limpieza | No se crearon recursos que exigieran retirada. Se conservaron avisos, entrega y verificaciones; no hubo borrados. No se acreditan pruebas de limpieza de ramas/worktrees. |
| Archivado | El coordinador comprobó identidad, título Finalizada e inactividad; set_thread_archived devolvió archived:true y list_archived_threads confirmó el chat por ID. |

Registro: [encargo](../../coordinacion/piloto-025-01/ENCARGO.md),
[estado final](../../coordinacion/piloto-025-01/ESTADO.md),
[acuses y originales](../../coordinacion/piloto-025-01/ACUSES.md),
[dictamen](../../coordinacion/piloto-025-01/REVISION.md),
[integración](../../coordinacion/piloto-025-01/INTEGRACION.md) y
[verificaciones de la tarea](../../coordinacion/piloto-025-01/VERIFICACION-TAREA.md).

La guía se integró en `f94fa03639026ca693e693ed3a9145829306774d`; el aviso y
registro de cierre se conservaron en `a86c04411e7ece3e6f2177665758ae88ee3bc36c`.
La persistencia final de este informe incluye la comprobación de archivado y
la corrección de conservación exacta de originales descrita a continuación.

## Ajuste descubierto durante el piloto

Git normalizó saltos de línea al almacenar Markdown. En la guía se comprobó y
documentó equivalencia de contenido entre el artefacto revisado y el blob de Git,
distinguiendo sus hashes. Para los avisos originales esa normalización impedía
conservar en Git los bytes identificados por los acuses.

Se consultó la [documentación oficial de gitattributes](https://git-scm.com/docs/gitattributes)
y se añadió una regla limitada a `coordinacion/piloto-025-01/avisos/AV-*.md`:
`-text`, permitiendo CR al final de línea en sus controles de whitespace.
Se reaplicaron los atributos únicamente a esos tres avisos con add --renormalize;
comprobación automática del índice Git: bytes iguales a cada original y a su
copia canónica, con los mismos tres SHA256 de ACUSES.md. No se cambiaron los
avisos ni los acuses para hacerlos coincidir y no se reescribió historial.

Lección para el mecanismo: si la trazabilidad usa hashes de bytes originales,
el medio de persistencia debe conservarlos. La comparación solo con el archivo
de trabajo no demuestra identidad de lo almacenado. Esta corrección es local
al piloto; no se presenta como garantía general del registro manual.

## Límites y siguiente etapa

No se ejercitaron creación de un chat nuevo, paralelismo, corrección de una
entrega rechazada, interrupción de transporte, cancelación, retirada de recursos,
desarchivado o recuperación en otro proyecto. Tampoco automatización, relevo,
mensajería entre pares o transacciones del auxiliar. No hubo push ni publicación.

El chat queda archivado y documentado para posible reutilización; recuperarlo
en una próxima tarea requiere comprobar su identidad, contexto y capacidad real.
No se afirma desarchivado probado. La nota 025 conserva capacidades pendientes.

Próxima etapa: elegir con Manuel el otro proyecto donde contrastar la portabilidad,
sin activar coordinación allí ni ejecutar su backlog por esta prueba.
