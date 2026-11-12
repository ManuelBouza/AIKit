# Método del Director de Ideas

Fecha: 2026-10-31.
Estado: implementada e instalada en el perfil de prueba; activación observada
sin BMAD y convivencia con BMAD observada en un escenario simulado.

## Intención

Definir un método para que el usuario comprenda todo el proceso: qué tarea se
realizará, por qué y cómo se hará. El usuario debe poder participar con intención,
criterio y dirección, manteniendo la comprensión del proyecto o tarea.

## Fases propuestas

### 1. Visión

Partir de la intención del usuario, sin exigir instrucciones específicas. En esta
fase el usuario está pidiendo una opinión sobre el problema planteado.

Organizar el caos inicial, explorar opciones y presentar sus pros y contras para
que el usuario pueda formar su criterio y decidir una dirección.

### 2. Estructura

Una vez que el usuario escoja una opción o una combinación de opciones,
estructurar la petición de forma que pueda revisarla y aprender qué se va a hacer.

Hacer comprensible la estructura del proyecto o de la tarea que se ejecutará,
evitando que el usuario quede ajeno a su organización y desarrollo.

### 3. Requisitos

Plantear todos los requisitos de la tarea. El usuario los revisará y decidirá
cuáles aprobar, cuáles rechazar y cuáles requieren modificaciones.

## Aplicación propuesta

Aplicar el método a cada solicitud que presente el usuario, garantizando en todo
momento su comprensión de la tarea que se realizará y de cómo se hará.

## Ingeniería de contexto

Principios aportados por el usuario para desarrollar este método:

- Lo importante no es solo lo que se le dice al modelo de IA, sino qué sabe el
  modelo cuando se le dice.
- Un contexto rico gana a un prompt perfecto en un contexto pobre.
- Una sesión larga de exploración y divagación puede ayudar a que una idea quede
  bien estructurada y con los requisitos correctos antes de implementarla.

El valor del usuario está en la intención, en el criterio y en la dirección.

## Para debatir después

- Cómo comprobar que el usuario comprende cada fase y cómo recoger sus decisiones.
- Cómo adaptar la profundidad del método a cada solicitud sin perder su intención.
- Cómo encajar el método con los flujos existentes de Superpowers y distribuir sus
  instrucciones entre `AGENTS.md` y skills, como plantea la nota
  [007](007-separar-delegacion-de-aikit.md).
- Cómo conservar el contexto útil y las decisiones durante conversaciones largas,
  y trasladar solo lo necesario a las tareas delegadas de la nota
  [005](005-prompts-concisos-opencode.md).

Guardar esta nota no activa el método ni cambia las reglas actuales. Su diseño e
implementación quedan pendientes de debate y autorización.

## Referencias preliminares — 2026-11-09 (histórico)

La exploración encontró enfoques relacionados; no establece que alguno cubra por
completo esta idea ni que se haya probado su eficacia en AIKit:

- [OpenSpec Explore](https://github.com/Fission-AI/OpenSpec/blob/main/docs/explore.md)
  propone conversar sobre el problema, investigar el proyecto y comparar opciones
  antes de proponer cambios; permite pasar a una propuesta cuando hay claridad.
- [GitHub Spec Kit](https://github.com/github/spec-kit/blob/main/extensions/assess/README.md)
  documenta una extensión para evaluar ideas antes de especificar, planificar e
  implementar. Su proceso se centra en desarrollo de software.
- En este proyecto, las descripciones instaladas de `bmad-forge-idea`,
  `bmad-brainstorming` y `bmad-spec` ya cubren respectivamente el examen de una
  idea, la generación de alternativas y la elaboración de una especificación.
- Un [estudio sobre expresión de requisitos con LLM](https://arxiv.org/abs/2601.16699)
  explora ayudar a las personas a expresar y validar sus necesidades; sus
  resultados no demuestran que un flujo concreto funcione para todas las tareas.

Como hipótesis para debatir: un coordinador ligero podría adaptar la profundidad
al encargo, distinguir decisiones del usuario de supuestos y reutilizar las
capacidades disponibles. No se ha decidido instalar otro sistema, activar BMAD
globalmente ni implementar una nueva skill.

## Propuesta para debate — 2026-11-09 (histórico)

AIKit podría incorporar una preferencia breve para dirigir ideas: entender la
intención, adaptar la profundidad a la solicitud, explicar las decisiones que
importan y conservar el contexto útil. Usaría las capacidades disponibles del
entorno sin exigir BMAD ni instalar otro sistema. La forma concreta de distribuir
esa preferencia queda por diseñar y verificar.

- **Solicitud clara y acotada:** actuar dentro de lo autorizado y comunicar el
  resultado; no imponer fases, documentos ni preguntas innecesarias.
- **Idea abierta o decisión material:** explorar el problema y el contexto,
  señalar supuestos, comparar opciones con sus consecuencias y recomendar una
  cuando exista una opción razonable. Pedir decisiones solo cuando hagan falta.
- **Trabajo complejo:** organizar visión, alcance, requisitos, restricciones,
  criterios de éxito y decisiones pendientes con la profundidad necesaria.
  Utilizar el mecanismo de notas o documentación del proyecto cuando exista y
  sea apropiado, sin crear artefactos duplicados por rutina.
- **Continuidad:** distinguir decisiones del usuario, propuestas y dudas;
  registrar lo necesario para continuar y actualizarlo si cambian las decisiones.
  Seguir las reglas del proyecto y evitar incluir información sensible.
- **Capacidades existentes:** cuando correspondan y estén disponibles, recurrir
  a herramientas de exploración, especificación o desarrollo como las de BMAD;
  no asumir que estén presentes en otros equipos ni activarlas globalmente.
- **Autorización:** respetar las instrucciones vigentes, incluidas las reglas
  de `go` y las autorizaciones específicas para acciones sensibles. Una propuesta
  o un registro no autoriza por sí solo la implementación.

Ejemplos: «corrige esta errata» se ejecuta directamente; «quiero organizar mis
ideas» inicia una exploración proporcional; «construyamos un producto» requiere
definir el problema y las decisiones relevantes antes de comprometer un diseño.
Son orientaciones, no categorías rígidas ni una garantía de comprensión.

Esta propuesta no modifica las preferencias instaladas y está pendiente de debate.

## Aclaración del objetivo — 2026-11-09 (histórico)

Manuel precisa que el objetivo es madurar una idea antes de implementarla:
identificar y resolver las ambigüedades relevantes tanto en lo que expresa el
usuario como en lo que entiende o supone la IA. Una vez aclarada y suficientemente
madura, se presenta para dar luz verde a su materialización. La ausencia absoluta
de incertidumbre no puede garantizarse; deben explicitarse las dudas restantes y
su impacto antes de decidir si se puede avanzar.

También decide que el Director de Ideas debe ser una skill de AIKit que se cargue
cuando corresponda. Hay que definir qué instrucciones generales pertenecen a
`AGENTS.md` y qué procedimiento pertenece a la skill. La skill debe poder operar
sin BMAD y reutilizar capacidades disponibles cuando proceda. Los criterios de
activación, madurez, luz verde y conservación de contexto requieren concretarse;
esta decisión no completa por sí sola el diseño ni activa la skill.

## Diseño propuesto para decidir — 2026-11-09 (histórico; autorizado después)

### Activación

La skill se invoca explícitamente si el usuario lo solicita. También puede
descubrirse por su descripción cuando se pide explorar o madurar una idea, o
cuando una solicitud de materialización deja sin resolver decisiones esenciales
que cambiarían el resultado. No interviene por el solo hecho de que exista una
pequeña incertidumbre: en tareas concretas y autorizadas el agente investiga,
decide lo rutinario y continúa. Una solicitud explícita de ejecución no permite
inventar requisitos; si hay una ambigüedad material, se aclara antes de afectar
la parte dependiente y se continúa con lo independiente cuando sea posible.

### Conversación y comprobación

1. Identificar la intención, el problema y el resultado buscado. Consultar el
   contexto y las fuentes pertinentes antes de preguntar lo que pueda descubrirse.
2. Diferenciar decisiones del usuario, hechos comprobados, hipótesis, propuestas
   de la IA y preguntas abiertas. Señalar contradicciones y explicar su impacto.
3. Explorar alternativas cuando haya una decisión significativa; presentar sus
   consecuencias y una recomendación razonada. Preguntar de forma concreta solo
   aquello que el usuario deba decidir, sin transformar cada paso en un trámite.
4. Ajustar profundidad y evidencia al alcance, la complejidad y el impacto.
   Si ya existe una skill apropiada, aprovecharla sin asumir que esté instalada.
   El usuario puede aclarar, cambiar de dirección o abandonar la idea.
5. Contrastar la comprensión con ejemplos o una síntesis cuando sea útil. No
   declarar que el usuario comprende algo por su silencio o mera cortesía.

### Criterios de madurez

Una idea está lista para proponer su materialización cuando, para el alcance
convenido, se pueden expresar con suficiente claridad:

- **Intención y resultado:** qué problema se aborda, para quién y qué se espera.
- **Alcance y límites:** qué se incluye y qué queda fuera cuando importe.
- **Decisiones y restricciones:** alternativas relevantes resueltas, condiciones
  del usuario y dependencias necesarias identificadas.
- **Comprensión compartida:** el resumen refleja las decisiones conocidas; no hay
  contradicciones o ambigüedades pendientes que cambien materialmente el resultado.
- **Comprobación:** se sabe cómo reconocer un resultado aceptable y qué evidencia
  se necesita, con detalle proporcional a la tarea.
- **Incertidumbres:** se explicitan los supuestos y riesgos relevantes; una
  incógnita no impide avanzar si se entiende su impacto y puede tratarse sin
  inventar una decisión que corresponda al usuario.

Si falta una condición material, indicar qué falta y continuar su exploración. No
exigir requisitos técnicos irrelevantes ni convertir una hipótesis en decisión.
La madurez se refiere al siguiente alcance concreto, no a todo el proyecto.

### Luz verde y continuidad

Presentar una síntesis comprensible con resultado, alcance, decisiones,
supuestos o dudas relevantes y la próxima acción concreta. Aplicar las reglas
de autorización vigentes: una solicitud explícita ya autorizada puede bastar para
trabajo ordinario dentro de su alcance; `go` autoriza la próxima tarea formulada;
las acciones sensibles requieren su autorización específica. La mera madurez,
el silencio o la aprobación de una decisión parcial no autorizan por sí solos
materializar una idea no autorizada. No pedir otra aprobación entre pasos de una
tarea ya autorizada.

Conservar decisiones y dudas en el mecanismo existente del proyecto cuando sea
adecuado; no imponer una plantilla o crear archivos en cada conversación. Si se
retoma una sesión larga, recuperar el contexto relevante y señalar discrepancias.
La autorización de un paso no equivale a aprobar pasos posteriores fuera de él.

### Reparto propuesto

**`AGENTS.md`, instrucción breve candidata:** «Cuando una idea necesite madurar
antes de materializarse o existan ambigüedades que cambien el resultado, usa la
skill Director de Ideas si está disponible. Aclara las decisiones esenciales y
respeta las autorizaciones vigentes; continúa directamente con tareas claras y
autorizadas». El texto definitivo debe ajustarse al mecanismo real de activación
y probarse antes de instalarlo globalmente.

**Skill:** descripción de descubrimiento precisa y procedimiento anterior, con
independencia de BMAD. El formato de salida debe adaptarse al encargo; conservar
el contexto existente y derivar a herramientas pertinentes cuando corresponda.
`bmad-forge-idea` cubre el cuestionamiento profundo y `bmad-spec` la redacción
de especificaciones; la aportación propuesta de AIKit es la coordinación de
madurez, comprensión compartida y luz verde también en entornos sin BMAD. Falta
validar la convivencia real y la selección automática, no solo la presencia de
archivos. No se ha creado ni instalado la skill.

### Casos para validar al implementar

- Una corrección evidente y autorizada se realiza sin iniciar una entrevista.
- Una idea abierta se explora sin construirla; se identifican decisiones y dudas.
- Un pedido de implementación con una ambigüedad material se aclara antes de
  comprometer el resultado, avanzando con trabajo independiente autorizado.
- Una idea suficientemente aclarada produce una síntesis y una acción concreta;
  el agente no confunde la madurez con una autorización aún ausente.
- Una ejecución ya autorizada continúa sin solicitar aprobaciones redundantes;
  una acción sensible mantiene la autorización específica que corresponda.
- Con y sin BMAD, la skill descubre su alcance sin sustituir ni exigir terceros;
  selección y comportamiento se comprueban en ejecución, no solo por metadatos.

Este diseño es una propuesta para revisión del usuario; no aprueba ni implementa
la skill ni altera `AGENTS.md`.

## Implementación — 2026-11-09

El usuario autorizó implementar el diseño. La skill está en
`packaging/skills/director-de-ideas/SKILL.md`, se incorpora al exportador de
AIKit y la instrucción de activación se añadió a `AGENTS.md` del proyecto. La
instalación global y la selección automática aún no están verificadas.
La especificación de implementación está en
[`spec-director-de-ideas.md`](../_bmad-output/implementation-artifacts/spec-director-de-ideas.md).

Una [prueba en sesiones temporales](../docs/evidencias/director-de-ideas-descubrimiento.md)
observó selección de la skill con y sin un candidato de BMAD, pero las políticas
del entorno impidieron leerla. Inyectando su contenido se observó una respuesta
apropiada para una idea abierta. Siguen pendientes la carga real y la convivencia
con una instalación funcional de BMAD.

## Complementariedad con BMAD — 2026-11-09

Manuel decide que en proyectos con BMAD el Director de Ideas y las skills de
BMAD se complementan: el Director mantiene la comprensión, la madurez y la luz
verde, y BMAD puede aportar exploración o cuestionamiento cuando sea pertinente.
En proyectos sin BMAD, el Director realiza por sí mismo la tarea de aclaración.
La skill de fuentes recoge esta decisión; la convivencia real sigue pendiente de
prueba. El protocolo está en [prueba en Desktop](../docs/prueba-director-ideas-desktop.md).

El 2026-11-10 se actualizó el complemento personal de prueba y se comprobó que
la skill instalada coincide con la fuente. En chats nuevos se observó selección
y lectura automáticas sin BMAD y lectura de ambas skills con BMAD. En este último
caso no se ejecutó el flujo completo de Forge; la convivencia completa sigue
pendiente. Detalles y límites en el protocolo de prueba enlazado arriba.

Se ejecutó además una prueba ficticia aislada de los comandos de registro de
Forge con informe y criterios de Director. La conversación no fue interactiva
con una persona real; no demuestra el flujo completo de extremo a extremo.

Posteriormente se retomó el chat de Desktop y se activó Forge junto con Director:
se creó y cerró un registro y un informe en una carpeta aislada. La respuesta del
escenario fue simulada y el resultado quedó como idea aclarada, no validada. El
protocolo describe la evidencia y sus límites.

## Reconciliación de cierre — 2026-11-12

La prueba autorizada de Desktop terminó. Se contrastó el cierre del chat de
coordinación con el protocolo: hubo descubrimiento y lectura sin BMAD, lectura
explícita de ambas skills con BMAD y ejecución de Forge con respuesta ficticia.
No se acredita selección automática de Forge, validación con usuarios reales
ni revisión visual del informe. Estas limitaciones no convierten la prueba
acotada terminada en una ejecución todavía activa.

Este cierre reúne la actualización de complementariedad de la skill y sus
evidencias para su registro en Git. La mejora posterior de `go` pertenece
a la nota 020; la política futura de chats y relevo pertenece a la nota 021.
No se reanudan por este cierre la integración OpenCode ni otros trabajos pausados.

Validación del cierre: `tests/test_build_aikit.py`, 13 pruebas aprobadas;
`git diff --check`, sin errores. El empaquetado no demuestra comportamiento
conversacional adicional al observado en las pruebas descritas.
