# Diseño de seguimiento de ideas y tareas

Fecha: 2026-11-17.
Estado: borrador técnico para decidir el siguiente alcance; no implementado.
Origen: [nota 043](../notas/043-separar-ideas-y-tareas-implementacion.md).

Actualización — 2026-11-17: Manuel adopta «la opción 1», registro local
Markdown, y autoriza formalizar el contrato con bmad-spec. La especificación
derivada está en `_bmad-output/specs/spec-seguimiento-ideas-tareas/`.
No autoriza aún implementar o ejecutar la migración. El resto del documento
conserva el borrador que dio origen a esa decisión.

Conciliación de estado — 2026-11-17: 028 ya fue reanudada directamente por
Manuel en el turno `01a1e822-ed79-7e02-94fd-dd2505eedaba`, mensaje
`01a1e822-ee3a-7091-b6d8-89e892af1841`. Está Esperando al usuario por la
propuesta visual, con BMAD pendiente antes de implementar. Las menciones a
Pausada debajo describen el snapshot anterior, no una orden vigente. Al migrar
deben consultarse los estados y decisiones humanos vigentes, sin congelar estos
ejemplos históricos. 040 sigue Bloqueada por entorno tras su reanudación.

## Decisiones del usuario y límites

El usuario distingue ideas y tareas de implementación, exige registrar cada
encargo antes de implementarlo y confirma que una idea puede generar varias
tareas, mientras que un encargo directo puede originar una tarea sin idea previa.
Ambos sistemas deben estar conectados y permitir seguimiento visual.

Registrar una tarea no autoriza ejecutarla. Se conservan go, permisos sensibles,
pausas y decisiones directas del usuario. Este documento propone cómo cumplirlo;
no crea el nuevo registro, migra tareas, amplía 028 ni instala preferencias.

## Contraste y cobertura existente

GitHub Projects ofrece vistas de tabla, tablero y planificación sobre los mismos
issues y PR, con referencias y campos compartidos. Apoya separar el registro de
trabajo de sus vistas, en vez de mantener copias editables del mismo estado.
[Documentación oficial](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects).

GitHub Issues permite descomponer entregas y expresar dependencias entre issues.
Es un precedente para registrar entregas identificables y bloqueos, sin exigir
un chat por cada ticket ni confundir una conversación con una unidad de trabajo.
[Documentación oficial](https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues).

La Kanban Guide de mayo de 2025 pide explicitar unidades de trabajo, puntos de
inicio y fin, estados y políticas de flujo. Se toma como referencia especializada
primaria para definir qué cuenta como empezado y terminado. No se adopta una
implantación Kanban completa ni métricas sin necesidad.
[Guía](https://kanbanguides.org/the-kanban-guide/2025.5/).

Estas fuentes respaldan los principios; las rutas, identificadores y estados
siguientes son propuestas propias para AIKit, no requisitos de esas herramientas.

En este proyecto ya existen notas Markdown y un tablero local de lectura,
un registro manual único de coordinación, avisos y artefactos BMAD. La carencia
es un registro uniforme de tareas separado de las ideas, con una vista propia.
No se ha comprobado ni configurado un GitHub Project para este propósito.

## Recomendación para este proyecto

1. Conservar las notas y su numeración histórica en `notas/`.
2. Usar el registro canónico existente `coordinacion/` para los tickets locales:
   `coordinacion/tareas/IMP-0001/TAREA.md`, uno por entrega delimitada.
3. Generar dos vistas de consulta, «Ideas» y «Tareas», desde sus fuentes respectivas.
   Reutilizar el generador y la presentación existentes cuando resulte adecuado.
4. Mantener el índice de tareas y el HTML como derivados; no editar estados allí.

Es la opción recomendada porque aprovecha el seguimiento local existente sin
introducir un servicio, otra base de datos ni sincronización bidireccional.
La alternativa es usar Issues y Projects u otro tracker existente como fuente
canónica. AIKit debe admitir esa modalidad por proyecto, pero aquí supondría
configuración y escrituras externas que este diseño no ejecuta ni autoriza.

El almacenamiento no es una preferencia universal: en otro proyecto setup debe
identificar primero el tracker que ya se utiliza. No crear un segundo backlog
Markdown editable si el estado canónico está en Jira, GitHub u otra herramienta.

## Entidades y enlaces

| Entidad | Responsabilidad | Identidad propuesta |
| --- | --- | --- |
| Idea | Contexto, intención, dudas y decisiones de maduración | Número histórico de nota, mostrado como «Idea 043» |
| Tarea | Una entrega con alcance y aceptación propios | `IMP-0001`, secuencia independiente por proyecto |
| Chat | Conversación y responsable de uno o varios encargos | Identidad nativa ya registrada |
| Evidencia | Especificación, revisión, prueba, entrega o aviso | Referencia existente, sin inventar otro identificador |

El Coordinador asigna números de tarea sin reutilizarlos tras cancelar. `IMP-`
no reutiliza los IDs `T-` ni los ciclos del auxiliar experimental: esta modalidad
manual no dispone de sus garantías. La identidad completa incluye el proyecto.

Cada tarea contiene una lista de ideas de origen, que puede estar vacía. Si nace
de un encargo directo, conserva la referencia humana de origen. También puede
contribuir a varias ideas. Los enlaces inversos de idea a tareas se obtienen
del registro de tareas; no mantener manualmente otra lista de estados.

Un chat puede atender varias tareas y una tarea puede cambiar de chat conservando
su identidad y el historial de asignación. No crear automáticamente un chat,
una rama o un worktree por registrar un ticket. El Coordinador elige el medio
según continuidad, aislamiento y alcance, respetando las autorizaciones vigentes.

## Contenido mínimo del ticket

El archivo canónico conserva estos campos con formato documentado y validable:

- ID, título, fecha de alta y última actualización.
- Origen: ideas relacionadas y referencia del encargo directo cuando corresponda.
- Resultado, alcance, exclusiones y criterios de aceptación proporcionales.
- Estado de ejecución y condición de atención definidos debajo.
- Responsable y chat asignado, si existe; destino de integración cuando proceda.
- Autorización: referencia y alcance aprobado, o indicación de que sigue pendiente.
- Dependencias explícitas, motivo de espera y siguiente acción que lo resuelve.
- Enlaces a especificación, revisiones, comprobaciones y versión entregada.
- Historial breve de decisiones y cambios relevantes, sin repetir transcripciones.

No exige completar criterios técnicos detallados para capturar un encargo nuevo:
se registra Pendiente y se concreta antes de empezar. No almacenar credenciales
ni transcripciones privadas en un registro que pueda versionarse o publicarse.

## Estados: distinguir ejecución, atención y chat

| Estado de ejecución | Significado |
| --- | --- |
| Pendiente | Capturada; puede faltar definición, autorización o prioridad |
| En curso | Se está realizando la entrega autorizada |
| En revisión | Entrega preparada; controles o revisión independiente pendientes |
| Pendiente de integración | Entrega revisada; integración final pendiente |
| Finalizada | Aceptación y destino acordados acreditados, con pendientes explícitos |
| Cancelada | Cancelación autorizada y motivo conservado |

La condición de atención es Normal, Esperando al usuario, Bloqueada o Pausada.
Se conserva junto al estado de ejecución y su motivo: así, una tarea puede
estar «En revisión · Bloqueada» sin perder el punto del flujo al que debe volver.
Una tarea terminal no mantiene una condición activa de espera. Si falta limpieza
o persistencia exigida para cerrar, permanece abierta con el pendiente visible.

No se cambia a En curso por crear el ticket, abrir un chat o recibir un acuse.
No se declara Finalizada solo porque existe un commit, una revisión favorable
o un chat archivado. Cuando el alcance requiere instalación o validación real,
debe acreditarse antes del cierre o dividirse explícitamente en otra tarea.

El estado del chat conserva la nomenclatura ya acordada. Resume su situación
operativa, no sustituye los estados de sus tickets: si atiende una tarea bloqueada
y otra que avanza, puede seguir En curso. El Coordinador no archiva un chat por
cerrar un ticket mientras conserve otros encargos o responsabilidades activas.

Las ideas conservan contexto y maduración. La ejecución se consulta por sus tareas
enlazadas; no convertir «una tarea terminada» en «toda la idea implementada».
Los estados históricos actuales se preservan durante la migración como historial.

## Regla operativa antes de implementar

1. Detectar un encargo nuevo de cambio o entrega, frente a una pregunta o comentario.
   Una duda, un comando auxiliar o una corrección dentro del alcance de un ticket
   no crea por sí solos otro ticket.
2. Buscar el encargo existente por origen, objetivo y alcance. Actualizarlo si
   sigue siendo la misma entrega; separar solo resultados con aceptación propia.
3. Si no existe, el Coordinador lo registra con los mínimos anteriores antes
   de delegar o iniciar implementación. Puede permanecer Pendiente sin permiso
   de ejecución. El registro debe aparecer en la vista de tareas regenerada.
4. Comprobar alcance, autorización y dependencias. Un ticket válido no levanta
   pausas ni concede publicación, instalaciones o permisos de escritura.
5. Al implementar, conservar la referencia del ticket; actualizarlo ante cambios
   relevantes de estado, bloqueos, revisión, integración y cierre.

En el chat de tarea, una decisión directa del usuario dentro del encargo continúa
con autonomía. Se reporta su impacto relevante sin pedir otro arranque. Si aparece
una entrega de implementación nueva sin ticket, la tarea conserva el encargo y
solicita su registro al Coordinador antes de comenzar esa nueva implementación;
puede continuar trabajo independiente ya registrado y autorizado. No escribe
el registro principal desde su worktree ni crea una raíz canónica alternativa.

El validador podrá detectar un ticket ausente, ID duplicado, enlace roto o campos
obligatorios inválidos. No puede garantizar que toda petición humana haya sido
detectada ni deducir por sí solo autorizaciones a partir del texto de una nota.
Sin registro o vista actualizables, se conserva el encargo pendiente y se informa
de la limitación; no se declara cumplida la visibilidad previa a implementación.

## BMAD y coordinación sin duplicar fuentes

BMAD mantiene especificaciones, historias, planes, dictámenes y pruebas cuando
se utiliza. El ticket enlaza esos artefactos; no vuelve a copiar criterios ni
checklists completos. Si un proyecto usa el seguimiento de BMAD como canónico,
se adapta la vista a ese registro en vez de exigir otra fuente editable.

En la modalidad local recomendada, el ticket es la fuente del estado operativo
de entrega. Los estados internos de una historia BMAD representan su flujo
técnico; se explicita su relación al ticket y no se presentan como otra decisión
independiente sobre la aceptación o el cierre final del proyecto.

El registro de chats conserva identidad, responsabilidades, asignaciones y
comunicaciones; sus índices enlazan tickets sin repetir sus estados manualmente.
Los avisos se conservan íntegros y sus acuses prueban la incorporación disponible,
sin prometer transacciones o autenticación inexistentes en el modo manual.

## Vistas y actualización

Una misma página puede ofrecer pestañas Ideas y Tareas. Son dos entidades y
flujos distintos, no dos aplicaciones obligatorias. Ideas muestra las notas y
sus tareas enlazadas; Tareas muestra el backlog, responsable, ejecución, atención,
dependencias y entregas. Los elementos bloqueados o pausados siguen visibles.

Regenerar ambas vistas después de modificar sus fuentes, mostrar fecha de
generación y conservar la última instantánea si falla la validación. Explicar
que esa salida quedó desactualizada, sin abrirla como una generación correcta.
Reutilizar el modelo de consulta local existente; edición interactiva, servidor
continuo, sincronización remota y avisos en tiempo real quedan fuera del primer
alcance. La regla exige generación correcta, no que un navegador abierto se
recargue automáticamente sin soporte implementado.

## Migración propuesta, sin cambios ejecutados

| Registro actual | Tratamiento al implantar |
| --- | --- |
| Encargo 028 | Crear un ticket enlazado a Idea 028 y al chat existente; conservar Pausada y decisión visual pendiente |
| Encargo 040 | Crear un ticket enlazado a Idea 040; conservar la reanudación humana y el bloqueo por entorno |
| Preparación BMAD | Registrar una tarea de dependencia delimitada; no ejecutar instalaciones ni reintentos por registrarla |
| Diseño de seguimiento 043 | Conservar el registro documental actual y enlazarlo; no dar por implementado el sistema |

No se propone una migración retrospectiva completa del historial del proyecto.
Asignar IDs solo al realizar la migración aprobada, después de contrastar estados
y orígenes. Conservar documentos y avisos anteriores como historial; los antiguos
índices pasan a enlazar los nuevos registros. No importar todas las ideas como
tareas: una nota pendiente de debatir no es un compromiso de implementación.

El cambio afecta al tablero de 028: acordar un contrato de datos y reparto de
archivos antes de tocar su implementación. No ampliar ese encargo mediante una
notificación informativa ni incorporar a ciegas cambios entre ramas.

## Integración en AIKit y setup

Setup debe presentar seguimiento de ideas/tareas como capacidad del proyecto:
detectar herramienta existente, acordar fuente canónica y rutas, comprobar
lectura/escritura autorizadas y definir cómo actualizar la vista. Si faltan
conectores o permisos, ofrecer traslado manual explícito; no fingir sincronización.

La preferencia general puede expresar la regla de registro previo, pero IDs,
estados adaptados, rutas, chats y credenciales de conexión pertenecen al proyecto.
La instalación del complemento no activa ni migra registros. Aplicar controles
de cobertura de setup de la nota 039 cuando se implemente esa mejora; no asumir
que ya existe un detector automático de omisiones.

## Aceptación de una futura implementación

1. Un encargo directo nuevo queda visible como tarea antes de implementar, sin
   crear una idea artificial ni ejecutar trabajo no autorizado.
2. Una idea enlaza varias tareas, y su consulta distingue las finalizadas de las
   pendientes. Repetir el mismo encargo no duplica tickets.
3. Bloquear o pausar una tarea conserva su fase, motivo y siguiente acción;
   cambiar el título del chat no altera por sí solo sus tickets.
4. Las vistas se generan desde sus fuentes únicas, rechazan IDs o referencias
   inválidas y muestran las limitaciones de una instantánea desactualizada.
5. 028 conserva su pausa; 040 conserva su bloqueo; registrar la dependencia BMAD
   no se interpreta como autorización para instalar o reintentar.
6. Un chat puede atender dos tickets y cerrar uno sin cerrar el otro ni archivarse.
7. Con BMAD o con un tracker externo, se enlazan los artefactos existentes sin
   mantener dos estados canónicos editables del mismo ticket.
8. Setup permite elegir la modalidad y verificarla; una capacidad indisponible
   produce una limitación explícita, no una activación declarada sin evidencia.

## Siguiente alcance recomendado

Revisar este borrador con el usuario y aprobar el modelo mínimo. Después,
formalizar el contrato de datos, la migración y las comprobaciones con `bmad-spec`
y asignar su implementación mediante `bmad-build`, incluyendo integración en
setup y coordinación previa con 028. La aprobación de este diseño no sustituye
la autorización de ese encargo de implementación ni resuelve el entorno de 040.
