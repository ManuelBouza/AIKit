---
title: 'Notificaciones proactivas del Coordinador a las tareas afectadas'
type: 'bugfix'
created: '2026-11-16'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

El Coordinador debe notificar por iniciativa propia los cambios relevantes a
los Chats de Tarea afectados, sin pedir aprobación para cada aviso dentro de la
autorización humana vigente. La información de una actualización de AIKit debe
llegar también a una tarea pausada cuando sea pertinente para su continuidad,
sin reanudarla ni ampliar su encargo. Conservar permisos, privacidad, autonomía
de las tareas, registro y evidencia del envío, evitando avisos duplicados y bucles.

</frozen-after-approval>

## Implementation Notes

- Ruta oneshot: sin decisiones materiales abiertas, operaciones irreversibles
  ni API nueva en esta entrega de instrucciones. Los envíos reales y el registro
  del proyecto los administra el Coordinador, no este ejecutor.
- Cobertura reutilizada: `coordinacion-chats` ya contiene roles, avisos, acuses y
  reconciliación; `aikit-setup` ya tiene entrada guiada local. Carencia: no se
  expresa el deber de avisar proactivamente ni cómo usar una autorización humana
  persistente sin convertir cada aviso en otra consulta. No crear otra skill,
  flag de instalador ni sistema de vigilancia.
- Mapa: `packaging/skills/coordinacion-chats/SKILL.md` enruta; referencias
  `responsabilidades.md` y `avisos.md` fijan selección de destinatarios,
  autorización, entrega y pausa. `packaging/skills/aikit-setup/SKILL.md` integra
  la autorización de avisos en el contrato local. Guías de Coordinador, tarea,
  flujo, uso y contrato en `docs/coordinacion/` explican el mismo comportamiento.
- Mantener intactos el esquema v1, la caché instalada, versiones de paquete,
  preferencias globales, notas, registro canónico y recursos de 028/040.
- Las instrucciones nativas de mensajería consultadas exigen autorización humana
  directa, que puede conservarse como evidencia verificable; el mensaje de otro
  agente no la sustituye. La autorización de Manuel ya consta en el historial
  del Coordinador y este actualiza el contrato local. En otros proyectos hay que
  acordar su alcance, sin inferir consentimiento al leer o instalar la skill.
- La implementación no requiere investigar otro framework: reutiliza las
  capacidades nativas publicadas y las instrucciones de skill-creator. No afirma
  ejecución fuera de un turno activo, recepción silenciosa ni servicio de avisos.
- Aceptación comportamental para evaluación independiente: cambio relevante con
  autorización persistente; cambio irrelevante; tarea pausada; envío incierto;
  destinatario archivado; nuevo proyecto sin autorización registrada; herramienta
  ausente o que activa turno; relectura del mismo cambio ya enviado. Verificar
  decisiones observables, sin tests que comparen frases de estas instrucciones.
- El Coordinador delega revisión independiente y cierre del flujo. Esta entrega
  no hace commit, push ni nueva distribución instalada.
- Implementados nueve documentos existentes: entrada y dos referencias de
  coordinación, entrada guiada de setup y cinco guías/contrato de coordinación.
  La referencia de responsabilidades conserva el detalle; las demás superficies
  enlazan y explican las consecuencias pertinentes para cada rol.
- Validador oficial `quick_validate.py`: coordinación y setup válidas. El primer
  intento del overlay PyYAML en sandbox falló por DNS de PyPI; el mismo comando
  con permiso acotado terminó correctamente, sin cambiar dependencias ni locks.
- `uv run --locked pytest tests/test_build_aikit.py::test_export_and_install -q`:
  una prueba correcta en 3,51 s. Comprueba exportación e identidad byte a byte,
  referencias internas de ambas skills y recursos del complemento.
- `git diff --check`: correcto; solo avisos habituales LF/CRLF. Sin código runtime,
  pruebas que comparen frases, flags, caché instalada ni modificación de 028/040.
- Escenarios para revisión/evaluación: aviso relevante a tarea activa con permiso
  persistente; cambio sin impacto; tarea pausada; destinatario archivado; resultado
  incierto; nuevo proyecto sin consentimiento; herramienta que inicia turno;
  relectura del cambio ya enviado. El Coordinador organiza la evaluación independiente.
- Tras el parche acotado, `test_export_and_install` volvió a pasar: una prueba
  correcta en 4,64 s; `git diff --check` correcto. Fuente final de responsabilidades
  identificada por SHA-256
  `4ca17e52ef9deefe52946fb18c91f6e4086ac6791a5f59591c38e1aba02691b6`.
- Evaluación independiente `notif042_behavior`, casos A–H y relectura de esa
  fuente final: decisiones correctas. A: notificar a la tarea en curso y la
  pausada afectadas dentro de la autorización, excluyendo otro proyecto; B: no
  duplicar el mismo cambio en un encargo ya informado; C: no inferir consentimiento
  por leer la skill, acordar la autorización humana faltante; D: reconciliar el
  envío incierto sin reenviar a ciegas; E: excluir un encargo histórico finalizado
  sin responsabilidad vigente ni impacto pendiente; F: no crear, desarchivar o
  reasignar para avisar, sí enviar al responsable vigente; G: un turno de recepción
  no reanuda trabajo pausado; H: un acuse anterior no acredita un nuevo encargo
  con contexto diferente, que recibe la información pertinente.
- Esta evaluación comprueba decisiones descritas, no ejecución nativa. Evidencia
  real diferenciada: el Coordinador conserva en ACUSES las referencias de dos
  avisos 0.1.3 reconocidos por 028/040, manteniendo pausa y sin operaciones de
  tarea. La distribución 0.1.4 y el commit del conjunto los gestiona el Coordinador.
- Ajustes de revisión: se distingue notificar al responsable vigente de crear,
  desarchivar o reasignar un chat; destinatarios con responsabilidad vigente o
  impacto pendiente concreto; deduplicación según encargo/contexto reales;
  referencia verificable a autorización o contrato cuando la necesite el receptor.

## Review Triage Log

| Hallazgo | Dictamen | Evidencia y tratamiento |
| --- | --- | --- |
| Blind B1: prohibir reutilización contradice enviar a un destinatario existente | low — patch | «Reutilizar» podía leerse como prohibición de avisar al responsable ya identificado. Se precisa no crear, desarchivar ni reasignar para avisar, permitiendo el envío al responsable vigente autorizado. |
| Blind B2: alcance del spec excluye versión, notas y registro de la entrega total | false | Los límites describen el trabajo de este ejecutor delegado; el Coordinador administra registro, notas y distribución de la entrega. El hallazgo solicita editar el spec y no identifica un cambio técnico necesario en las instrucciones. |
| Blind B3: falta evaluación independiente del comportamiento | low — patch | Evaluación independiente `notif042_behavior` completada: casos A–H correctos y fuente final releída. Los resultados se conservan arriba, distinguiendo decisiones descritas de ejecución nativa. |
| Blind B4: selección admite encargos finalizados/cancelados sin responsabilidad vigente | low — patch | Se exige responsabilidad vigente o impacto pendiente concreto y se excluye despertar por rutina registros históricos de encargos finalizados o cancelados. |
| Blind B5: deduplicación por cambio/destinatario omite un nuevo encargo reutilizado | low — patch | Se contrasta encargo vigente y contexto antes de considerar informado el chat, usando solo referencias, versiones y ciclos soportados por la modalidad real. |
| Blind B6: aviso sin referencia verificable a la autorización dificulta contrastarla | low — patch | Se incluye referencia al contrato o autorización cuando la necesite el receptor. El Coordinador la incorpora a los avisos nuevos; los originales ya conservados permanecen inmutables. |

Edge y verification-gap no presentan hallazgos. Los parches y la evaluación
independiente están completos; el Coordinador administra el commit del conjunto
y la distribución, sin delegar aquí permisos de publicación o aplicación.
