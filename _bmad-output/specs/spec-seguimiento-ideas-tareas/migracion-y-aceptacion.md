# Migración y aceptación inicial

Derivado de la memoria canónica; no ejecuta los trabajos descritos.

## Baseline y precedencia

El registro manual actual está en `coordinacion/`. No se migra todo el historial
ni se convierte cada nota en ticket. La aprobación de este contrato no autoriza
implementar, instalar, reanudar chats, modificar recursos o reintentar BMAD.

Snapshot conciliado del 2026-11-17, que debe contrastarse al ejecutar:

| Encargo | Ticket a incorporar, sin ID asignado todavía | Estado conocido |
| --- | --- | --- |
| 028 | Modernización del tablero, Idea 028, chat existente | Investigación/propuesta iniciada; Esperando al usuario por decisión visual; BMAD pendiente antes de implementar |
| 040 | Contraste documental del Director, Idea 040, chat existente | Trabajo reanudado; Bloqueada por disponibilidad aislada de BMAD/dependencias; no repetir el flujo fallido |
| Dependencia BMAD | Preparación aislada del entorno de tareas | Pendiente de solución concreta y permisos aplicables; bloquea implementación que requiere ese entorno |

La fase propuesta para 028/040 es en_curso porque ya comenzó investigación o
preparación autorizada, no porque se haya implementado código. Atención separada
esperando_usuario/bloqueada respectivamente. La dependencia nace pendiente;
se enlaza desde ambos tickets cuando su alcance concreto cubra ambos entornos.
Estos valores no son un mandato de congelar estados ni una orden de ejecución.

028 fue reanudada por Manuel en el turno
`01a1e822-ed79-7e02-94fd-dd2505eedaba`, mensaje
`01a1e822-ee3a-7091-b6d8-89e892af1841`. Su pausa anterior es historial.
040 fue reanudada en el turno `01a1e823-0b36-76c1-aa94-f43d57a2e516`,
mensaje `01a1e823-200e-7341-82f4-b129d503643a`. Contrastar con ENCARGOS.md,
ACUSES.md y los historiales nativos; conciliar cualquier contradicción antes de
escribir el recurso afectado. Conservar referencias humanas y avisos originales.

## Procedimiento futuro, acotado e idempotente

1. Inventariar solo estos encargos y la dependencia. Buscar tickets existentes
   por referencia estable del encargo y origen; una nota con varias entregas
   no identifica por sí sola una tarea. Conservar los registros documentales
   de diseño/especificación 043 como contexto enlazado, sin darlos por implementación.
2. Simular altas, referencias, estados y cambios de índices sin escribir. Mostrar
   fuentes, estados vigentes, discrepancias y operaciones previstas. Resolver las
   discrepancias materiales con el origen disponible o el usuario.
3. Con autorización de implementación/migración aplicable, conservar el preestado
   recuperable de los archivos que cambiarán; crear solo tickets ausentes y asignar
   IDs nuevos desde la secuencia real. Reutilizar existentes sin reemplazar decisiones
   posteriores con el snapshot. No modificar ramas o worktrees de tareas.
4. Validar el conjunto y generar la vista. Pasar los índices operativos a enlaces
   al ticket canónico; conservar los documentos anteriores como historial fechado,
   sin mantener dos estados editables vigentes de la misma entrega.
5. Verificar conteos, relaciones, evidencia y estado. Registrar resultado, cambios
   y límites y notificar solo lo pertinente por el cauce autorizado. No declarar
   completado si falla un paso; preservar evidencia de las escrituras parciales.
6. Al repetir, contrastar origen e IDs y actualizar solo lo que siga pendiente.
   No duplicar tickets ni borrar recursos para forzar éxito. La última vista válida
   se conserva si falla la generación; no se promete transacción multiarchivo.

Antes de cambiar el tablero, el Coordinador acuerda reparto de archivos y
contrato de datos con 028; una notificación informativa no amplía su encargo.
BMAD debe prepararse y verificarse en su propio trabajo autorizado; esta
migración solo registra la dependencia y conserva la condición de parada.

## Escenarios de aceptación

Usar fixtures ficticios aislados para comprobaciones deterministas y evidencia
manual proporcionada para decisiones de rol y autorización. No usar inferencia
para repetir parsing, tipos o enlaces que puede verificar una herramienta.

| Caso | Resultado exigido | Capacidades |
| --- | --- | --- |
| Encargo directo sin idea | Ticket pendiente con origen humano, ideas vacías, visible; no ejecución automática | CAP-1, CAP-3 |
| Una idea, dos entregas | Dos IDs y aceptación propia; enlaces inversos derivados; completar una no completa toda la idea | CAP-1, CAP-4 |
| Repetición o ajuste del mismo encargo | Reutiliza ticket; pregunta, comando auxiliar o corrección dentro del alcance no crea otro | CAP-1, CAP-3 |
| Ticket con revisión bloqueada y luego desbloqueada | Conserva en_revision; motivo y siguiente acción; retoma solo con condición resuelta | CAP-2 |
| Chat con dos tickets | Cerrar uno no archiva el chat ni cierra el otro; cambiar título no muta tickets | CAP-2 |
| Nueva entrega sin ticket desde chat de tarea | Solicita registro y espera solo implementación nueva; sigue trabajo independiente permitido | CAP-3 |
| Sin generación correcta de alta | Informa bloqueo de seguimiento y no comienza la nueva implementación | CAP-3, CAP-4 |
| Metadata inválida | Rechaza ID/ruta discrepante, ID repetido, clave duplicada, tipo incorrecto, versión o estado desconocido, booleano por entero, NaN/Infinity y fecha inválida | CAP-1, CAP-4 |
| Relaciones inválidas | Rechaza idea inexistente, dependencia ausente, duplicada, propia o ciclo; ninguna salida nueva | CAP-1, CAP-4 |
| Ruta o contenido hostil | Rechaza escape/enlace fuera de raíz; escapa HTML y no ejecuta/carga enlaces, imágenes o scripts | CAP-4 |
| Fallo de lectura/validación/publicación | Retorna error, conserva última vista válida y comunica desactualización sin abrirla como nueva | CAP-4 |
| Migración simulada y repetida | Simular no escribe; ejecución autorizada crea solo ausentes; segunda ejecución no duplica ni revierte decisiones recientes | CAP-5 |
| Cambio de estado entre snapshot y migración | Consulta origen vigente y preserva reanudación/pausa/bloqueo real; discrepancia material detiene solo escritura afectada | CAP-2, CAP-5 |
| BMAD pendiente | Visible como dependencia; registrar no instala, reintenta o levanta bloqueos | CAP-2, CAP-5 |
| Instalación sin activación | No crea ni migra registros; setup exige acuerdo local y verificación de fuente/permisos/generación | CAP-6 |
| Tracker existente o capacidad insuficiente | No duplica fuente; explica límite y traslado manual, sin declarar sincronización inexistente | CAP-6 |

El cierre de la futura entrega debe acreditar contrato/exportación/skills y setup
pertinentes, pruebas de datos y generación, demostración de vistas, revisión
independiente e integración a una versión exacta. La instalación o prueba real
solo se exige si forma parte de su alcance aprobado; no declarar completada esa
parte con evidencia de fuentes o simulaciones. Mantener pendientes explícitos.
