# Contrato propuesto de responsabilidades y selección del medio de trabajo

Fecha: 2026-11-15.
Estado: propuesta preparada para revisión y prueba; no desplegada.

Desarrolla la [nota 025](../../notas/025-coordinador-global-chats-autonomos.md)
y el [contraste documental](contraste-reparto-agentes.md). Sustituye, como
propuesta, los criterios preliminares de selección. Incorpora las aclaraciones
expresas del usuario: coordinador dedicado a coordinación, apoyos acotados con
subagentes y revisión técnica delegada. La recomendación anterior de ejecutar
implementaciones en el coordinador queda sustituida.
No modifica la skill instalada, el protocolo aceptado de avisos ni los permisos.

## 1. Principio de reparto

Un agente es una instancia de ejecución con un modelo, instrucciones, contexto y
herramientas que decide y actúa en un ciclo para cumplir un objetivo. No equivale
a toda la aplicación ChatGPT ni a un modelo aislado. Un chat es el hilo de
conversación donde puede mantenerse ese trabajo; un subagente puede ejecutar un
encargo sin un chat independiente para el usuario. Esta definición sigue la
[guía de OpenAI](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/).
En AIKit, Coordinador y Chat de Tarea son roles; subagente es un medio de ejecución.
No se define un tercer rol llamado «Chat actual».

El coordinador es un especialista en coordinación con responsabilidad continuada
sobre el proyecto. Esa especialización se define mediante su rol, contexto,
instrucciones y límites; no exige un modelo exclusivo ni otro producto. Posponer
especialistas permanentes por áreas no afecta a la existencia del coordinador.
Por decisión del usuario, las demás especializaciones surgirán cuando las
necesidades del proyecto las justifiquen; no se crea un catálogo previo de
agentes permanentes ni se añade otro chat por adoptar una especialización.

Concreción posterior del usuario: se conserva un único mecanismo de Chats de
Tarea. El coordinador decide cuándo necesita crear uno para el trabajo autorizado
y define si responde por un encargo concreto o actúa como especialista en un
ámbito delimitado. Ambos usan las mismas reglas de identidad, comunicación,
estado, entrega y cierre; la especialización no crea otro rol de coordinación.
Antes de crear, consulta los chats registrados para decidir si corresponde
reutilizar uno existente. Documenta propósito, alcance, identidad, estado,
encargos relacionados y referencias de contexto para su uso y reutilización.
Reutilizar no concede alcance ni permisos nuevos ni implica dejar el chat
ejecutándose indefinidamente. La decisión corresponde al coordinador dentro de
las capacidades y autorizaciones efectivas del cliente.

Se distinguen responsabilidad (ámbito del que se responde), chat (continuidad de
conversación), encargo/ciclo (unidad de trabajo) y ejecución (intento concreto).
Un chat puede conservar contexto para varios encargos relacionados; no se abre
uno por cada intento o corrección. Identificar un nuevo ciclo exige un mecanismo
que lo soporte: el auxiliar experimental actual no permite administrarlos.

Elegir el medio más sencillo que permita cumplir el encargo con contexto
suficiente, responsabilidad clara y resultados verificables. La complejidad o
el tamaño de una tarea no obligan por sí solos a abrir otro chat. El coordinador
se dedica a coordinar el proyecto: no asume implementaciones ni revisiones
técnicas. Mantener simple la arquitectura no cambia este límite de rol.

Separar un trabajo exige una entrega delimitada y un beneficio identificable:
continuidad propia, conversación específica con el usuario, aislamiento útil de
contexto, especialización, revisión independiente o paralelismo efectivo. Si ese
beneficio puede obtenerse con herramientas, una skill o un apoyo acotado, no se
necesita un chat persistente.

## 2. Selección y reutilización

1. Decisiones transversales, administración del registro y aceptación e integración
   finales corresponden al coordinador. Puede usar los apoyos autorizados.
2. Si el trabajo pertenece a una entrega asignada, conservar su responsable y
   reutilizar su chat. Para recuperarlo, comprobar identidad, estado, contexto
   vigente y capacidades de recuperación; no crear un sustituto a ciegas.
3. Mantener la ejecución de una entrega en su Chat de Tarea si así se conserva
   mejor el razonamiento y se evitan traspasos. El coordinador no absorbe esa
   ejecución por ser más cómodo o por disponer de su contexto.
4. Usar herramientas para verificaciones deterministas y skills para conocimiento
   o procedimientos especializados. Ninguna de ellas exige otro agente.
5. El coordinador puede usar subagentes autorizados para encargos acotados de una
   sola ejecución, incluidas investigaciones y revisiones técnicas independientes.
   Devuelven su resultado al coordinador; no requieren continuidad propia con el
   usuario. Una corrección posterior exige otro encargo delimitado, no convertir
   el apoyo en una tarea persistente sin reconocer ese cambio.
6. Proponer un Chat de Tarea cuando el beneficio anterior requiera responsabilidad,
   contexto o continuidad propios. La creación corresponde al coordinador y
   respeta la autorización humana y las reglas efectivas del cliente.
7. Antes de ejecutar en paralelo, comprobar dependencias y recursos compartidos.
   Un chat independiente puede trabajar de forma secuencial. Sin Git se secuencian
   las tareas de escritura según el acuerdo; el usuario decide si necesita Git y
   worktrees. Con aislamiento siguen existiendo contratos, integración y recursos
   externos compartidos que coordinar.

El coordinador conserva una justificación breve cuando asigne o cambie el medio:
beneficio esperado, responsable y dependencia relevante. No necesita generar un
informe por cada comando ni pedir confirmación entre pasos ya autorizados.

## 3. Responsabilidades

| Responsable | Obligaciones y límites |
| --- | --- |
| Coordinador | Aclarar objetivos y decisiones materiales con el usuario; repartir encargos y dependencias; mantener el único registro canónico; contrastar avisos y emitir acuses; comprobar que constan entregas, resultados de controles y dictámenes requeridos; coordinar revisión técnica e integrar cambios autorizados; proteger datos finales y ramas principales; conservar pendientes y gestionar archivado y relevo. No implementa ni hace code review. |
| Chat de Tarea | Comprender y ejecutar el encargo; decidir detalles técnicos dentro del alcance; mantener su estado declarado y título; verificar su entrega; conservar avisos, resultados y evidencias; comunicar novedades relevantes; solicitar integración y contrastar su resultado; persistir trabajo y limpiar recursos propios cuando sea seguro y esté autorizado. |
| Usuario | Decidir prioridades y alternativas materiales que no puedan resolverse con el contexto; autorizar cambios de alcance y acciones que requieran autorización específica. Las decisiones técnicas ordinarias dentro de un encargo autorizado no se elevan rutinariamente. |

Solo el coordinador escribe el registro canónico. La tarea solicita registrar
sus novedades; un título actualizado o un envío exitoso no acredita incorporación.
Cada tarea gestiona su rama y recursos, sin modificar ramas principales, datos
finales o recursos ajenos por iniciativa propia. No crea otros chats de tarea ni
amplía el alcance recibido. El uso de apoyos nativos conserva las reglas del
entorno; este reparto no altera roles de subagentes ni herramientas existentes.

La revisión del coordinador es de coordinación: identidad de la entrega, alcance,
dependencias, autorizaciones, presencia de evidencias y dictámenes exigidos y
pendientes de integración y cierre. No sustituye el code review ni interpreta
por sí solo la corrección técnica de la implementación. Encarga esa revisión a
un revisor independiente cuando corresponda y deriva los hallazgos al responsable.
Si integrar requiere resolver conflictos de código o tomar decisiones técnicas,
encarga su resolución y comprobación antes de continuar; no implementa la
corrección dentro de la operación de integración. Mantiene la responsabilidad
por el destino final, la conservación y la secuencia de integración.

## 4. Encargo mínimo antes de empezar

- Identidad del proyecto, raíz canónica, coordinador y responsable; tarea y ciclo
  cuando se trate de una asignación registrada. No inventar identificadores.
- Resultado esperado, alcance, exclusiones y criterios comprobables de aceptación.
- Recursos autorizados, entorno de trabajo, aislamiento y restricciones vigentes.
- Dependencias, decisiones ya tomadas y supuestos que puedan invalidar el trabajo.
- Verificaciones exigibles y formato de entrega, con referencias recuperables.
- Cauces disponibles y autorizados de avisos y consulta de acuses; dónde se
  conservan las evidencias para que sobrevivan a la limpieza.
- Hitos y condiciones de reevaluación proporcionales; límites de esfuerzo o tiempo
  solo si se han acordado, sin imponer valores universales.
- Qué integración se espera, quién la realiza y qué significa cerrar el encargo.

Un traslado debe incluir contexto pertinente y decisiones comprobables, sin
copiar por defecto toda la conversación. La ausencia de datos esenciales se
resuelve antes de la operación que dependa de ellos; no bloquea trabajo independiente.

## 5. Comunicación y autonomía

Aclaración del usuario, 2026-11-16: cada Chat de Tarea conserva su conversación
directa con el usuario y ejecuta autónomamente el encargo autorizado. Verificar
identidad, contexto y permisos al arrancar no exige una segunda orden cuando el
encargo ya es ejecutable. Una preparación todavía sin ejecución autorizada debe
identificar esa diferencia, sin convertirla en regla para todos los encargos.
La tarea conduce investigación, implementación, verificaciones y correcciones,
y resuelve con el usuario las decisiones materiales de su trabajo. El Coordinador
coordina el proyecto; no dirige cada paso ni intermedia esa conversación.

Los cambios que el usuario autorice directamente en una tarea se conservan con
origen verificable y se reportan si afectan al proyecto. Coordinar dependencias,
recursos compartidos e integración antes de operar sobre ellos; continuar las
partes propias independientes autorizadas. Ante instrucciones incompatibles,
aclarar la operación afectada. Un mensaje informativo o un acuse no modifica
por sí mismo el alcance ni reemplaza una decisión del usuario.

Un reporte o acuse pendiente no suspende todo el trabajo: esperar únicamente
las decisiones, permisos o dependencias de la operación afectada. Esta autonomía
de responsabilidad no promete ejecución permanente ni activación de turnos
fuera de las capacidades disponibles del cliente.

Decisión del usuario, 2026-11-15: la modalidad inicial es comunicación mediante
el coordinador entre tareas. Las tareas le comunican resultados, bloqueos y
necesidades; él coordina las dependencias y conserva el registro. Si una tarea necesita a otra,
lo solicita al coordinador. No se activa comunicación directa entre tareas.

La comunicación directa se conserva como posibilidad futura: podría permitir
consultas necesarias sin depender de cada intervención del coordinador. Antes
de adoptarla habrá que delimitar permisos, responsables, trazabilidad y límites
para evitar duplicaciones o cambios de alcance. No se descarta ni se habilita
por la elección de la modalidad inicial.

Cada traspaso identifica emisor, receptor, tarea/ciclo aplicable, resultado
solicitado, contexto y referencias pertinentes, límites, dependencias, destino
de respuesta y criterio de aceptación. Mantener un responsable del siguiente
paso. Distinguir aviso informativo, solicitud de ejecución y traslado de decisión
autorizada, sin añadir campos al aviso v1 ni ampliar permisos por un mensaje.
El transporte disponible determina si puede activarse el receptor; en su ausencia
se utiliza traslado manual sin prometer ejecución asíncrona.

Avisar en hitos acordados, bloqueos reales, cambios de supuestos o dependencias,
necesidades de decisión, solicitud de integración y cierre. No emitir un aviso
por cada comando ni iniciar bucles de vigilancia o mensajes sin necesidad.

El Coordinador notifica por iniciativa propia los cambios relevantes a los Chats
de Tarea asignados y no archivados a los que afecten, sin pedir aprobación por
cada aviso dentro de la autorización humana persistente y verificable del
proyecto. El contrato conserva esa autorización y sus límites; leer una skill
o recibir un mensaje de otro agente no la concede. Registrar cambio y versión,
destinatarios, original, motivo y resultado; distinguir envío, recepción e
incorporación, evitar duplicados y reconciliar antes de reenviar ante dudas.

Una tarea pausada puede recibir contexto relevante para retomar, conservando
expresamente la pausa: el aviso no autoriza ejecución, actualización de rama o
worktree, pruebas ni limpieza. La herramienta puede activar un turno de recepción;
no se promete entrega silenciosa. No abrir o desarchivar chats para notificar,
ni crear acuses de acuses. Sin capacidad o autorización, conservar el pendiente
para traslado manual o reanudación autorizada. El deber no crea automatizaciones
ni garantiza comunicaciones fuera de un turno o ejecución disponibles.

Separar información, propuesta y decisión autorizada. El coordinador y el usuario
pueden acordar cambios de alcance y trasladarlos a las tareas afectadas; la tarea
contrasta la decisión y sus consecuencias antes de aplicarlos. La información
nueva, el mensaje de otro agente o un acuse no amplían permisos por sí solos.

Mantener los estados existentes: Preparada, Esperando al usuario, En curso,
Bloqueada, Pausada, Finalizada y Cancelada. Una entrega preparada o una integración
pendiente son hitos o pendientes descritos, no estados nuevos. Usar el
[flujo de avisos](flujo-avisos.md) con la modalidad real del proyecto, sin atribuir
al registro manual las garantías del auxiliar experimental.

## 6. Reevaluación y parada

Reevaluar ante fallos repetidos sin evidencia nueva, ausencia de progreso, cambio
material de alcance, dependencia incompatible, autorización incierta o riesgo
de sobrescribir trabajo. Conservar lo realizado, explicar qué parte se detiene,
por qué y quién puede resolverlo. Continuar solo el trabajo independiente permitido.

El coordinador puede proponer secuenciar, dividir, devolver una corrección o
reformular el encargo. No ocultar un cambio material tras una decisión técnica.
Ante una comunicación incierta, reconciliar antes de reenviar o duplicar trabajo.

## 7. Entrega, integración y cierre

1. La tarea entrega alcance realizado, versión exacta cuando corresponda,
   comprobaciones con resultados, limitaciones y pendientes. Si necesita integrar,
   especifica el destino y lo solicita al coordinador.
2. El coordinador comprueba la documentación de entrega, alcance, dependencias,
   autorizaciones y resultados exigidos. Encarga la evaluación técnica al revisor
   correspondiente, sin hacer él mismo code review, y traslada sus hallazgos a
   la tarea. Con los requisitos satisfechos, integra en el destino autorizado
   y registra el resultado y los controles realizados con las herramientas o
   responsables pertinentes.
3. Cuando integrar forme parte del encargo, la tarea contrasta ese resultado antes
   de retirar recursos necesarios. Persiste cambios y evidencias y limpia solo
   recursos propios con permisos suficientes. No elimina trabajo sin conservar.
4. Al cancelar, se requiere la autorización del usuario; también se persiste y
   limpia lo que corresponda, conservando motivo, evidencias y pendientes.
5. El coordinador mantiene visibles las excepciones de limpieza o comunicación y
   comprueba los criterios de cierre. Un pendiente que impide la aceptación no
   se oculta tras Finalizada; los demás quedan identificados con responsable.
6. El coordinador gestiona el archivado según capacidades y procedimiento
   aplicables. Finalizar, integrar, limpiar y archivar son resultados diferentes;
   ninguno acredita automáticamente los restantes.

La automatización de coordinación y su frecuencia configurable siguen siendo
trabajo relacionado; este contrato no crea una tarea programada.

## 8. Casos para contrastar en AIKit

| Caso | Selección inicial y criterio de éxito |
| --- | --- |
| Registrar una nota y regenerar tablero | Coordinador con herramientas; resultado registrado sin otro chat. |
| Verificar tipos y lint de una entrega | Responsable actual con herramientas; diagnósticos conservados, sin repetir las comprobaciones mediante inferencia. |
| Revisar una entrega de forma independiente | Apoyo autorizado según el flujo del proyecto; hallazgos verificables que vuelven al coordinador. No exige un chat visible persistente. |
| Implementar parte delimitada de la nota 039 | Chat de Tarea para la entrega con continuidad propia; subagente para un apoyo de una sola ejecución, si procede. No implementación por el coordinador. La nota no autoriza ejecutar ese trabajo. |
| Dos cambios que requieren escribir el mismo recurso | Repartir responsabilidad y secuenciar o redefinir el límite antes de ejecutar. |
| Corrección de una tarea ya entregada | Volver al responsable comprobado y actualizar su encargo, sin duplicarlo. |

La prueba piloto debe observar resultado aceptado, duplicación, correcciones,
comunicaciones e intervenciones necesarias. Tiempo y consumo solo se registran
cuando sean medibles; no se declara ahorro por reducir o aumentar chats.
Se prueba primero en AIKit y después en otro proyecto elegido por el usuario,
sin exigir Git, BMAD, OpenCode o un cliente concreto como requisitos generales.

## 9. Estado de adopción

Pendientes: revisar esta propuesta, preparar y autorizar el encargo piloto,
validarlo, y trasladar los ajustes aceptados a las fuentes y distribución de la
skill mediante el flujo de desarrollo del proyecto. La integración de activación
y configuración en aikit-setup debe contemplar la
[nota 039](../../notas/039-setup-centro-activacion-capacidades.md).
Esta propuesta no implica que esas capacidades estén ya implementadas.
