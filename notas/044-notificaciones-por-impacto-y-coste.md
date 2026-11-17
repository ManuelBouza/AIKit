# Notificaciones por impacto y coste de activación

Fecha: 2026-11-17.
Estado inicial: Pendiente de debatir.
Estado actual: Implementada; actualización privada0.1.6 instalada y descubierta.

## Actualización privada autorizada — 2026-11-17

El usuario autoriza con «go» preparar e instalar el filtro en el perfil habitual.
[IMP-0007](../coordinacion/tareas/IMP-0007/TAREA.md) registra esta entrega separada:
candidata0.1.6, ensayos y recuperación aislados, respaldo privado y revisión previa
a la aplicación. Esta entrada no declara todavía instalado el paquete nuevo.

Resultado posterior: [AIKit0.1.6](../docs/actualizacion-aikit-0.1.6.md) instalado
en el perfil habitual, con respaldo privado y dictámenes independientes antes y
después. Tres skills habilitadas y contenido exacto comprobados; configuración e
instrucciones ajenas conservadas. IMP-0007 finalizada. No equivale a verificar
lectura de las instrucciones por todos los chats abiertos.

## Resultado — 2026-11-17

[IMP-0006](../coordinacion/tareas/IMP-0006/TAREA.md) finalizada en fuentes:
filtro compartido en coordinación, avisos, seguimiento, setup y guías. Revisión
independiente aceptada tras ajustes de localización, conservación, procedencia
y contexto al reanudar. Dos skills válidas, exportación/instalación aislada
correcta y 18 casos de decisiones simuladas consistentes. No prueba ahorro
cuantificado ni transporte real; no hubo mensajes a los chats activos.

Evidencia: [validación](../docs/validacion-avisos-044.md) y
[Build con triage y snapshot](../_bmad-output/implementation-artifacts/spec-044-avisos-por-impacto.md).
La instalación posterior se completó mediante IMP-0007 con versión0.1.6.
El Coordinador aplica el criterio en su contrato local.

## Implementación autorizada — 2026-11-17

El usuario responde «go» a implementar el filtro en ambos roles y verificar sus
decisiones con casos concretos. Encargo registrado antes de implementar en
[IMP-0006](../coordinacion/tareas/IMP-0006/TAREA.md). Se reutilizan coordinación,
avisos y seguimiento; sin nuevos canales, instalación ni avisos de prueba a chats
reales. BMAD Help selecciona Build proporcional y Skill Creator guía el ajuste.

## Decisión del usuario — 2026-11-17

Manuel elige explícitamente «go, opción 1»: reducir activaciones y recoger
avances ordinarios en la siguiente revisión del Coordinador. Acepta que el
tablero pueda reflejar temporalmente el último estado incorporado, no todo lo
ocurrido en los chats. La autorización de avisos útiles sigue vigente.

El Coordinador aplica este criterio de selección en su trabajo actual; las
instrucciones actualizadas de ambos roles están instaladas en el perfil habitual.

## Política concretada para implementar

Enviar ahora exige identificar una acción o decisión operativa del destinatario,
o un riesgo que empeore al esperar. Informar por informar o actualizar el registro
por sí solo no justifica activar otro agente. Agrupar novedades que puedan esperar;
conservar evidencia recuperable y reconciliar envíos inciertos sin repetirlos.

| Situación | Tratamiento |
| --- | --- |
| Push, commit, pruebas o actualización general sin efecto en el encargo receptor | Conservar; no enviar |
| Progreso propio o espera de una decisión del usuario dentro del mismo encargo | Evidencia local y título del chat actualizados; recoger en siguiente revisión |
| Bloqueo que la tarea puede resolver dentro de su alcance | Resolverlo o consultarlo con su usuario; no escalar por rutina |
| Bloqueo que necesita recurso, decisión o permiso del Coordinador | Una solicitud concreta al Coordinador, con impacto y parte afectada |
| Dependencia resuelta que permite continuar | Coordinador avisa a la tarea afectada para que pueda actuar |
| Nueva entrega sin ticket solicitada a una tarea | Solicitar registro al Coordinador antes de implementar esa entrega; trabajo independiente continúa |
| Cambio humano transversal, incompatibilidad, recurso compartido o riesgo de pérdida | Avisar a quien debe coordinar antes de la operación afectada |
| Entrega lista para revisión o integración | Solicitud al Coordinador con versión/evidencias y acción requerida |
| Resultado de integración que permite corrección, verificación o limpieza | Coordinador comunica el resultado operativo al responsable |
| Cierre y limpieza verificados que permiten al Coordinador archivar/liberar recursos | Un aviso de cierre accionable; sin cadena de confirmaciones |
| Pausa o cancelación humana | Detener lo afectado y conservar origen; avisar ahora si hay integración, reserva o trabajo compartido que detener/corregir; en otro caso recoger después |
| Recepción de información o acuse sin operación pendiente | No enviar otra confirmación |

Solo el Coordinador incorpora datos al registro canónico. Las tareas conservan
sus novedades ordinarias en su entorno autorizado; esto no permite escribir el
principal desde un worktree. En una revisión de coordinación pertinente, el
Coordinador consulta los datos pendientes o el historial accesible sin enviar
mensajes para pedir una mera repetición. Consulta solo los encargos necesarios,
no todos los historiales por cada comando o mensaje del usuario.

La revisión se hace cuando el usuario la solicita o cuando la coordinación activa
necesita datos para asignar, integrar o cerrar; una automatización solo participa
si existe y está autorizada. Esta decisión no crea tarea programada, buzón,
servicio ni entrega silenciosa. No promete ejecución fuera de un turno activo.

La fecha de generación del tablero no acredita consulta reciente de cada chat.
Mostrar o explicar que se trata del estado incorporado y que puede haber avances
pendientes de conciliación; no exigir un mensaje por cada transición para
simular frescura continua.

## Contraste con fuentes

Se consultaron las fuentes primarias de Anthropic sobre
[agentes efectivos](https://www.anthropic.com/research/building-effective-agents)
y su [sistema multiagente de investigación](https://www.anthropic.com/research/multi-agent-research-system).
Respaldan evaluar coste/latencia y complejidad de coordinación frente al beneficio,
y conservar resultados en artefactos en lugar de retransmitir contexto completo.
La política concreta anterior es una decisión de AIKit, no una regla del proveedor;
las cifras de coste de esos sistemas no se extrapolan a estos chats.

## Solicitud del usuario

Revisar qué y cuándo comunica el Coordinador a los Chats de Tarea y qué y cuándo
comunican estos al Coordinador. Evitar mensajes que consumen inferencia y tiempo
sin aportar valor operativo al destinatario.

Ejemplo aportado: COORD-PUSH-231e850-040-01 comunicó un push que no cambiaba el
trabajo, bloqueo ni siguiente acción de 040. Escribir «No necesitas responder»
no evita que la entrega del mensaje active un turno en el cliente actual.
La autorización de avisos proactivos no obliga a comunicar cada cambio del proyecto.

## Criterio propuesto para debatir

Antes de enviar, identificar destinatario afectado y qué decisión, acción o
riesgo cambia al recibir el mensaje ahora. Si no existe ese efecto, conservar
la información sin despertar al otro chat. Ser breve no sustituye este filtro.

- Coordinador hacia tarea: decisiones aplicables que cambian su trabajo,
  dependencia resuelta, conflicto o recurso compartido que exige coordinación,
  resultado de integración que necesita conocer para continuar o cerrar.
- Tarea hacia Coordinador: solicitud de integración, nueva entrega que requiere
  registro, bloqueo que necesita intervención fuera de su ámbito, decisión humana
  de impacto transversal, riesgo de pérdida de datos o incompatibilidad real.
- Progreso ordinario, pruebas repetidas, comandos, commits/push sin impacto en
  ese destinatario y confirmaciones sin acción: conservar como datos consultables,
  no enviar por rutina. Agrupar novedades cuando esperar no agrave el problema.
- No generar acuses de acuse ni mensajes solo para confirmar que se recibió
  información. Mantener trazabilidad de envío incierto sin duplicarlo a ciegas.

## Alternativas debatidas — historial previo a la elección

Solo el Coordinador escribe el registro canónico. Suprimir mensajes ordinarios
implica que los cambios de seguimiento no incorporados pueden quedar pendientes
hasta su próxima consulta. Diferenciar actualización de datos de activación de
un agente; no afirmar que existe un canal silencioso sin disponer de él.

Alternativa recomendada para debatir: avisos inmediatos por necesidad de acción
o riesgo; avances ordinarios conservados en evidencias de la tarea y recogidos
en la siguiente revisión autorizada del Coordinador. Explicar antigüedad y
pendientes de incorporación en el seguimiento cuando proceda.

Alternativa de mayor frescura: avisar también por cada cambio relevante de estado
para actualizar enseguida el canónico, aceptando activaciones adicionales.

Los casos de pausa, espera, integración y cierre se concretaron arriba tras la
elección. Antes de implementar se debe registrar un encargo identificable,
seleccionar el flujo BMAD proporcional y comprobar el comportamiento de ambos
roles, manteniendo la autonomía y sin notificaciones a tareas no afectadas.

## Relaciones

- [042 — Avisos proactivos](042-notificaciones-proactivas-coordinador.md).
- [043 — Ideas y tickets](043-separar-ideas-y-tareas-implementacion.md).
- [027 — Automatización de coordinación](027-automatizacion-coordinacion.md).
- [032 — Coordinador escritor](032-coordinador-escritor-mensajes-tareas.md).

El debate no reanuda tareas ni modifica sus permisos. No se notificará a los
Chats de Tarea este registro de idea: no les exige ninguna acción.
