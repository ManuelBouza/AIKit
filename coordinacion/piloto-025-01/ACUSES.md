# Avisos y acuses de PILOTO-025-01

Registro manual escrito exclusivamente por el coordinador.
## PILOTO-025-01/AV-001 — incorporado

- Fecha: 2026-11-16. Versión del aviso: 1.
- Original íntegro: [avisos/AV-001.md](avisos/AV-001.md).
- SHA256: `3974201c2b42bb8cf05f5a164b5ca980c0934ba853caed380b7a4fa9b819baec`.
- Emisor: chat asignado `01a1dff8-061d-7170-b111-2f5577f1f570`.
- Origen: mensaje nativo recibido y send_message_to_thread completado en su turno
  `01a1e2f7-225d-7c63-a87f-d31890239aaa`, comprobado por read_thread;
  herramienta `exec-8b16ea1b-3b00-4f4c-958d-8f8498d87d4a`.
- Decisión: incorporado. Estado declarado En curso; redacción iniciada según aviso.
- Título observado por el coordinador: [En curso] PRUEBA · AIKit · Guía de coordinación.
- Este acuse acredita incorporación manual de ese original, no aprobación de
  entrega, integración, limpieza o archivado. No tiene garantías transaccionales v1.

## PILOTO-025-01/AV-002 — incorporado

- Fecha: 2026-11-16. Versión del aviso: 2.
- Original íntegro: [avisos/AV-002.md](avisos/AV-002.md).
- SHA256: `498f9e9d979f344576cddb3f027b75d9378308beff8a799403f8dc31fe96bfc1`.
- Emisor: mismo chat asignado; origen contrastado por mensaje nativo recibido,
  identidad de cliente e historial del turno `01a1e2f7-225d-7c63-a87f-d31890239aaa`.
- Decisión: incorporado. Solicitud de revisión e integración recibida, estado En curso.
- Entrega indicada: `.aikit/piloto-025-01/entrega/guia-uso.md`, hash
  `a53b345620e5882884548f3ae7ab93d6f185b7f8d7aa3748a1a47f964182ed7b`, comprobado.
- La referencia a acuse AV-001 pendiente describe el momento de su consulta:
  el acuse posterior existe y la tarea dejó constancia de contrastarlo; no se
  reescribe el aviso original para ocultar esa secuencia.
- Revisión independiente encargada; integración y cierre pendientes. El acuse
  no los acredita ni aprueba el contenido de la guía.

## PILOTO-025-01/AV-003 — incorporado

- Fecha: 2026-11-16. Versión del aviso: 3.
- Original íntegro: [avisos/AV-003.md](avisos/AV-003.md).
- SHA256: `4223264e07107af89f741e8fcd5107a759fed28f74e064e1b9d1b24a069f1fde`.
- Emisor: chat asignado; mensaje nativo y herramienta de envío completada
  `exec-4c966d1d-1b82-43ea-ad4f-1628c6cbb540`, turno
  `01a1e2fb-20e0-74e2-9f03-453c82c08cf3` consultado por wait_threads.
- Decisión: incorporado. Estado declarado Finalizada, integración contrastada por
  la tarea, AV-001/AV-002 reconciliados y evidencias conservadas.
- Persistencia Git de la guía contrastada por la tarea mediante el registro y
  salida del coordinador, no lectura propia del blob. El coordinador sí comprobó
  el blob y su equivalencia tras normalización CRLF/LF, descrita en INTEGRACION.md.
- Limpieza: la tarea no creó recursos que necesiten retirada; conservó avisos,
  entrega y verificaciones bajo su raíz permitida. No se borraron evidencias.
- Pendientes del coordinador: persistir este cierre, recibir contraste del acuse
  final y archivar el chat inactivo. Este acuse aún no acredita archivado.

## Seguimiento posterior al acuse final

El cierre se persistió en `a86c04411e7ece3e6f2177665758ae88ee3bc36c`.
La tarea contrastó AV-003 en su turno `01a1e2fd-1293-7430-bceb-3143117276ee`,
mensaje final `msg_0ebe63487f15bda7016afa9f13eab087d189bd4f0832badb42`,
comprobado por wait_threads. Conservó evidencia en VERIFICACION-TAREA.md.
Después de observar inactividad y título Finalizada, el coordinador archivó el
chat; resultado archived:true confirmado por listado de archivados. No se envían
más mensajes ni se generan nuevos avisos por el solo contraste de este acuse.

Persistencia exacta: los originales de avisos tienen atributos locales -text;
se verificó igualdad de sus bytes almacenados en Git con los hashes anteriores.
Las copias legibles, los originales y el registro se conservan; no hay cambios
de contenido para ocultar normalizaciones o reenvíos.
