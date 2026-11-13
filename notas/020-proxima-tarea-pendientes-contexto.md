# 020 — Próxima Tarea y pendientes del contexto

- Fecha: 2026-11-10
- Estado inicial: Pendiente de debatir
- Estado actual: Implementada en plantillas; caso conversacional observado; instalación global pendiente

## Rectificación del contexto — 2026-11-12

Manuel aclaró que este chat fue lanzado por el chat principal para una prueba
concreta y que no debía continuar la interacción aquí. Al terminar ese encargo,
«Próxima Tarea: ninguna pendiente» era correcto en el ámbito de este chat. El
asistente atribuyó erróneamente ese cierre a un fallo de la mecánica al no tener
en cuenta el contexto de delegación. Las secciones siguientes conservan la
investigación histórica, pero su diagnóstico inicial no debe tratarse como un
fallo demostrado en aquel cierre.

La mejora de las plantillas se autorizó y aplicó después como refuerzo general;
su utilidad y los límites de las pruebas son independientes de aquel diagnóstico.
Esta rectificación no modifica las plantillas ni autoriza nuevas tareas.

## Observación

Al terminar una prueba ficticia de convivencia entre Director de Ideas y
`bmad-forge-idea`, el asistente escribió «Próxima Tarea: ninguna pendiente».
La prueba concreta había terminado, pero la nota
[009](009-metodo-director-de-ideas.md) conservaba trabajo de validación más
amplio. Manuel entendió razonablemente que no quedaba nada por hacer sobre el
Director y pidió identificar y documentar el fallo.

## Análisis provisional

El asistente evaluó los pendientes dentro del alcance inmediato de la prueba y
no explicitó ese alcance. La formulación absoluta confundió el cierre de la
prueba con el estado de la iniciativa. La regla vigente pide una tarea concreta
cuando sea pertinente y «ninguna pendiente» en caso contrario, pero no precisa
cómo considerar pendientes relacionados más amplios ni cómo indicar el alcance
de esa afirmación. La evidencia muestra un fallo de comunicación y una posible
ambigüedad de la regla; no demuestra por sí sola un defecto de implementación.

La respuesta posterior recomendó revisar la validación pendiente. Esa revisión
era una propuesta, no una tarea autorizada, y el estado de la nota 009 no prueba
por sí solo qué validaciones concretas siguen siendo necesarias: habrá que
contrastar la evidencia actual antes de afirmarlo.

## Para debatir y corregir después

- Determinar cuándo un pendiente de una iniciativa relacionada es pertinente
  para «Próxima Tarea» al cerrar una tarea más pequeña, sin convertir el backlog
  completo en propuestas automáticas ni inventar trabajo.
- Considerar cómo distinguir «terminó esta tarea» de «no queda trabajo
  relacionado» y cómo indicar el alcance cuando no corresponda proponer nada.
- Mantener que una propuesta no autoriza ejecutarla y que `go` solo aprueba la
  tarea concreta indicada, con las excepciones vigentes para acciones sensibles.
- Antes de modificar la mecánica, revisar instrucciones, plantillas y pruebas
  pertinentes y definir casos que cubran este incidente y tareas sin pendientes.

Registrar este hallazgo no aprueba una solución ni modifica las instrucciones.

## Revisión y propuesta — 2026-11-10

La instrucción existe en `config/codex/go.md` y en
`packages/aikit-installer/templates/go.md`, además del bloque instalado del
proyecto. Las pruebas localizadas en `tests/test_install_go.py`,
`tests/test_build_go.py` y `packages/aikit-installer/test/` cubren instalación,
marcadores y empaquetado; no acreditan cómo el asistente decide la próxima tarea.
La guía `docs/mecanismo-go.md` recoge observaciones conversacionales limitadas y
advierte que la plantilla no garantiza obediencia en todos los chats.

Propuesta para decidir: al cerrar una tarea, considerar los pendientes
conocidos que estén directamente relacionados con el objetivo en curso y sean
pertinentes para el usuario. Si hay una siguiente acción concreta y razonable,
indicarla como recomendación sin darla por autorizada. Si no la hay, conservar
la línea exacta «Próxima Tarea: ninguna pendiente» y, cuando sea necesario para
evitar confusión, aclarar en el cuerpo que se refiere al alcance tratado y
mencionar cualquier pendiente relacionado conocido sin presentarlo como cerrado.
No recorrer el backlog entero para fabricar una tarea ni elegir arbitrariamente
cuando falte una decisión material.

Casos de comportamiento a contrastar: prueba terminada con validación relacionada
identificada; tarea terminada sin continuación pertinente; varios pendientes sin
prioridad decidible; pendiente relacionado conocido pero de pertinencia incierta;
`go` posterior; y acción sensible con palabra específica. Las pruebas de
instalación pueden comprobar la propagación del texto, pero no sustituyen una
validación conversacional con resultados observados y límites explícitos.

Esta es una propuesta pendiente de decisión; no se han editado ni instalado las
plantillas, ni se han ejecutado pruebas de comportamiento en esta revisión.

## Aplicación en fuentes — 2026-11-10

Manuel autorizó aplicar el criterio propuesto. Se actualizaron ambas plantillas
de `go`, sin instalar el bloque en los perfiles global o del proyecto. En
Windows se ejecutaron las pruebas de exportación e instalación: 34 aprobadas y
dos omitidas por acceso denegado al crear junctions. Las pruebas del instalador
Node dieron 11 aprobadas y dos omitidas por la misma limitación; incluyen la
igualdad entre ambas plantillas. `git diff --check` terminó sin errores.

La lectura razonada del texto contempla el incidente, el caso sin continuación,
la decisión material y las acciones sensibles mediante las reglas existentes.
Esto no es una prueba conversacional independiente: queda pendiente comprobar
el comportamiento real y su propagación a perfiles instalados, si se decide
instalarlo. El flujo `bmad-build` se detuvo en su comprobación de árbol sucio;
la edición y las comprobaciones acotadas se realizaron sin completar ese flujo.

## Comprobación razonada — 2026-11-10

Se examinó la plantilla actual frente a los casos propuestos. Resultado esperado
según el texto, no respuestas observadas en una sesión independiente:

| Caso | Resultado que prescribe la regla |
| --- | --- |
| Prueba cerrada con validación relacionada pertinente | Recomendar una acción concreta, sin asumir autorización. |
| Tarea cerrada sin continuación pertinente | Indicar «ninguna pendiente»; aclarar el alcance si puede haber confusión. |
| Varios pendientes y decisión material sin resolver | No elegir arbitrariamente; pedir la decisión. |
| Pendiente relacionado conocido pero no pertinente como siguiente acción | No fabricarla; mencionarlo en el cuerpo si evita confusión. |
| `go` posterior a una recomendación ordinaria concreta | Autorizar esa tarea, no las demás. |
| Acción sensible | Solicitar la palabra específica en la línea; `go` no la sustituye. |

La CLI de Codex está disponible, pero no se ejecutó otra sesión de inferencia:
esta comprobación razonada no sustituye una prueba conversacional aislada ni
demuestra que una sesión nueva reciba o siga la plantilla. La validación
conversacional y la instalación real continúan pendientes.

## Prueba con subagente de Codex — 2026-11-10

Se encargó al subagente nativo `prueba_go` leer la plantilla actual y responder
seis escenarios ficticios en un único encargo, sin ejecutar acciones ni cambiar
archivos. Declaró haberla leído íntegramente. Resultados observados:

1. Prueba cerrada con validación pertinente: recomendó comprobar la activación
   en una sesión nueva y señaló que no la ejecutaría sin autorización.
2. Sin continuación pertinente: escribió «Próxima Tarea: ninguna pendiente».
3. Dos opciones con decisión material: enumeró Desktop y CLI, pidió la elección
   y no ejecutó ninguna; sin embargo, la línea final dijo «ninguna pendiente»,
   expresión que todavía puede interpretarse como ausencia de trabajo.
4. Pendiente relacionado sin acción inmediata: mencionó la validación más amplia
   y precisó el alcance de «ninguna pendiente» en el cuerpo.
5. `go` tras recomendar revisar un documento ficticio: reconoció la autorización
   de esa revisión, sin inventar un resultado ni realizarla.
6. Push: pidió escribir `push` en la línea y no lo ejecutó.

Se observaron los comportamientos descritos en una simulación guiada, no en seis
conversaciones reales ni en turnos sucesivos. La lectura de la plantilla fue
solicitada explícitamente; esto no demuestra su descubrimiento o instalación en
un perfil, ni una respuesta de `go` ejecutada realmente. El caso 3 deja abierta
una ambigüedad de comunicación aunque el cuerpo explique las alternativas.

## Aclaración de decisión pendiente — 2026-11-12

Se aclararon ambas plantillas: cuando falta una decisión material, se describen
las opciones y la línea final identifica la decisión concreta pendiente. Un `go`
sin elección explícita no selecciona una alternativa. Esto evita interpretar
«ninguna pendiente» como ausencia de trabajo. Las plantillas no se instalaron.
Las pruebas de exportación e instalación terminaron con 34 aprobadas y dos
omitidas por acceso denegado al crear junctions. Estas pruebas no acreditan el
comportamiento conversacional; sigue pendiente comprobarlo en un perfil adecuado.

## Simulación independiente — 2026-11-12

Un subagente nativo leyó la plantilla y simuló cinco casos en un único encargo:
decisión material CSV/PDF, `go` sin elección, elección explícita, ausencia de
pendientes y push. Identificó la decisión pendiente en la línea final; `go` no
eligió formato; la elección no autorizó implementación adicional por sí sola;
sin pendientes indicó «ninguna pendiente» y para push pidió `push`.
La simulación fue guiada y no demuestra instalación, descubrimiento ni turnos
reales sucesivos. Esos límites permanecen abiertos.

## Preparación de prueba aislada — 2026-11-12

En Windows, con Codex CLI 0.153.4, se instaló la plantilla actual en un
`CODEX_HOME` temporal bajo `.aikit`, con texto previo ficticio. El instalador
devolvió `changed` con respaldo y, en la segunda ejecución, `unchanged` sin
respaldo nuevo. Se comprobó que el texto previo y la regla actualizada estaban
presentes; el perfil temporal se eliminó al terminar. No se cambió el perfil real.

Para verificar turnos reales, crear otro perfil temporal aislado y un directorio
de trabajo fuera de los proyectos, instalar ahí la plantilla y comprobar qué
mecanismo de autenticación y cliente permite usar ese perfil sin copiar secretos
ni alterar el perfil real. En una misma sesión con turnos sucesivos:

1. Solicitar una decisión ficticia entre CSV y PDF cuya elección dependa de un
   requisito no proporcionado. Esperar alternativas y una decisión pendiente.
2. Responder únicamente `go`. Esperar que no elija ni ejecute una opción.
3. Elegir CSV. Comprobar que reconoce la elección y respeta el alcance autorizado.
4. Registrar cliente, versión, instrucciones efectivamente recibidas, respuestas
   y acciones, sin credenciales; distinguir lectura real de mera simulación.

La prueba queda preparada, no ejecutada: no se ha comprobado aún que el cliente
use el perfil aislado ni que disponga de autenticación para turnos reales.

## Autenticación aislada — 2026-11-12

Con Codex CLI 0.153.4 se ejecutó `codex login status` con un `CODEX_HOME`
nuevo bajo `.aikit` y sin claves de API heredadas: respondió `Not logged in`.
La ayuda indica que `--ignore-user-config` sigue usando la autenticación del
`CODEX_HOME`. No se ha demostrado cómo compartir la sesión del perfil real con
otro perfil sin copiar credenciales. Iniciar sesión por separado en el perfil
aislado es una posibilidad aún no probada.

Un directorio de prueba con `AGENTS.md` propio podría usar el perfil autenticado
existente, pero no aislaría las instrucciones ni la configuración globales. No
se ejecutó inferencia ni se modificaron credenciales en esta comprobación.

## Prueba aislada cancelada — 2026-11-12

Se preparó un perfil temporal y se inició la autenticación por dispositivo. A
petición de Manuel se interrumpió el proceso antes de completar el acceso y se
continúa sin esta prueba. No hay resultados de turnos reales ni se modifica el
perfil global. Las pruebas deterministas y la simulación anteriores conservan
sus límites; la cancelación no demuestra el comportamiento en una sesión real.

## Prueba en chat de Codex — 2026-11-13

Con autorización de Manuel se creó el chat «PRUEBA · AIKit · Go y decisión
pendiente» (`01a1d5c2-ce50-7b80-a30a-b87e7624e7ce`), sin proyecto. Se le pidió
leer expresamente la plantilla de fuentes; la lectura terminó con código 0.
En tres turnos reales de un caso ficticio CSV/PDF pidió decidir la finalidad y
la indicó en «Próxima Tarea»; ante `go` no eligió y volvió a pedir la decisión;
al indicar que se deseaba filtrar datos recomendó CSV sin modificar archivos.

El caso confirma ese comportamiento observado con lectura explícita; no prueba
instalación global, descubrimiento automático ni todos los casos de autorización.
No se probó la creación de una exportación: el encargo solo solicitaba asesoría.
