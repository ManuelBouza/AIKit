# 029 — Estado visible en el nombre de cada chat

- Fecha: 2026-11-14.
- Estado inicial: Pendiente de debatir.
- Estado actual: En debate; responsabilidad del chat acordada.

Manuel solicita ver el estado de los distintos chats de trabajo directamente en
sus nombres. Cada chat de tarea es responsable de mantener actualizado su nombre
y su registro al cambiar de estado. Complementa la
[nota 025](025-coordinador-global-chats-autonomos.md): el estado canónico sigue
en `TAREA.md`; el nombre es una representación visible, no una segunda autoridad.

## Aspectos para concretar

- Definir un formato breve y legible que identifique tanto el estado como la tarea,
  sin confundir chats reales y de prueba ni depender solo del nombre para la
  identidad. Conservar los estados ya acordados en la nota 025.
- Determinar cómo actuar si el registro se actualiza y el cambio de título falla,
  si el cliente no ofrece renombrar o si ocurre un cambio concurrente. Mostrar la
  discrepancia y no afirmar que el nombre está actualizado sin comprobarlo.
- Verificar si la herramienta de cambio de título está disponible en el chat de
  tarea y en ejecuciones pertinentes; el diseño debe contemplar una vía manual.
- Precisar cuándo sincronizar el nombre con el registro, sin convertir cada turno
  en una actualización ni presumir observación continua en segundo plano.

La decisión de responsabilidad no implementa el mecanismo ni autoriza modificar
los nombres de chats existentes. Relacionada con
[026 — Archivado](026-archivado-chats-coordinacion.md) y
[027 — Automatización](027-automatizacion-coordinacion.md).

## Formato y sincronización propuestos — 2026-11-14

Formato recomendado: `[Estado] T-001 · Nombre breve de la tarea`. El estado va
al principio para que se vea antes de una posible truncación; el identificador
estable ayuda a localizar el registro, y el nombre describe el trabajo. Por
ejemplo: `[En curso] T-001 · Configurar integración`. Los títulos de prueba
conservan además la marca `PRUEBA`. El nombre no sustituye el ID real del chat.

Usar literalmente los estados acordados: `Preparada`, `Esperando al usuario`,
`En curso`, `Bloqueada`, `Pausada`, `Finalizada` y `Cancelada`. `Preparada` puede
existir antes de que haya chat; no obliga a crearlo. Un título puede abreviarse
para ajustarse al cliente, siempre que siga identificando tarea y estado.

1. Ante un cambio significativo, el chat responsable actualiza `TAREA.md` con
   estado, fecha y motivo o siguiente intervención cuando corresponda, siguiendo
   las reglas de escritura acordadas. No actualiza por cada turno ordinario.
2. Intenta cambiar su propio título a la representación del estado registrado.
   El contrato de `set_thread_title` disponible en este chat permite omitir el ID
   para seleccionar el chat que llama. No se ha comprobado su disponibilidad en
   todos los clientes ni el comportamiento en una sesión de tarea real.
3. Verifica el resultado cuando el cliente permita consultar el título. Si falla
   o no puede verificarlo, conserva el estado canónico, informa de la discrepancia
   y deja pendiente la sincronización; no crea una segunda versión del estado.
   Si no existe capacidad de renombrar, indica el título exacto para cambio manual.
4. Al retomar, el chat compara el título con `TAREA.md` cuando pueda y corrige
   discrepancias conforme al estado canónico. Evita sobrescribir un título cambiado
   por el usuario sin considerar su intención. Si la tarea está en ejecución, la
   automatización no debe inferir un estado distinto solo por el nombre.

El cambio del registro y el título son operaciones separadas: puede haber un
intervalo de discrepancia. No se promete sincronización instantánea, vigilancia
continua ni exclusión frente a renombrados externos. El procedimiento y el formato
son candidatos para revisión, no se ha renombrado ningún chat ni verificado la
activación automática del chat responsable.

## Prueba de cambio de título — 2026-11-14

Se creó el chat de prueba `PRUEBA · AIKit · Estado` en AIKit, host local, ID
`01a1dab6-5ddd-7761-80d1-0700761b9f68`. En su instrucción inicial se le pidió
renombrarse sin modificar archivos ni otros chats. Informó que la herramienta nativa
aceptó el cambio y que el listado confirmó el título efectivo
`[En curso] PRUEBA · AIKit · Estado`. Su turno terminó; el título es parte de la
prueba y no representa una tarea activa. No se probó sincronización con `TAREA.md`,
otros estados, errores, clientes o automatizaciones. El chat se conserva.

## Nombre del coordinador — 2026-11-14

Manuel solicita una nomenclatura también para el chat coordinador. Propuesta:
`<Proyecto> · Coordinador principal`, por ejemplo `AIKit · Coordinador principal`.
El nombre identifica proyecto y función, sin asignar al coordinador el estado de
una tarea individual. Si hace falta un coordinador de prueba, añadir `PRUEBA ·`
al principio. El título no sustituye el ID del chat ni su registro de identidad.

Si se releva al coordinador, distinguir el anterior y el nuevo sin borrar su
historia; concretar la convención al diseñar el relevo. No se ha renombrado ningún
chat ni decidido un estado propio del coordinador.
