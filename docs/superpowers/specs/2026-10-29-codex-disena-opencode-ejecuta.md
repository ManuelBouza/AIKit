# Diseño: Codex diseña y coordina; OpenCode ejecuta y verifica

Estado: diseño aprobado por el usuario con `go`, 29 de octubre de 2026.
No es una instrucción activa ni acredita capacidades nuevas. No cambia la skill,
la configuración global, el complemento instalado ni los flujos de Superpowers.

## Objetivo y decisiones acordadas

Conservar Codex para conversación, diseño de la solución y orquestación.
Enviar a OpenCode la ejecución técnica, incluidas revisión y verificación.
Ahorrar trabajo de los modelos de Codex sin reducir la capacidad requerida.

La falta de un modelo apropiado o de disponibilidad en OpenCode devuelve la
función afectada a Codex automáticamente. El trabajo no se detiene por esa
indisponibilidad y no requiere nueva autorización para ese retorno.

## Cobertura existente y cambio necesario

Se consultaron `delegating-to-opencode`, sus referencias de carga y las guías
de principios y balance de AIKit. El adaptador ya permite elegir modelo y
variante, usar MCP o CLI y devolver resultados compactos. No elige modelos,
reintenta ni crea revisores automáticamente.

Superpowers ya cubre diseño, planificación, pruebas y revisión independiente;
se consultaron `brainstorming` y `requesting-code-review`. AIKit debe aportar
la asignación de ejecución y los contratos de evidencia, sin reimplementar
esos procesos. Las instrucciones vigentes todavía reservan la verificación
técnica final a Codex: habrá que actualizarlas después de aprobar este diseño.

## Responsabilidades

| Codex | OpenCode |
| --- | --- |
| Conversación, objetivos y alcance | Exploración técnica y recopilación de hechos |
| Arquitectura, contratos y diseño de la solución | Diagnóstico e implementación según el diseño |
| Planificación y criterios de aceptación | Pruebas, documentación y correcciones |
| Selección de modelo y esfuerzo para cada papel | Revisión independiente de requisitos y código |
| Coordinación, decisiones y comunicación | Ejecución y análisis de verificaciones |

OpenCode devuelve hallazgos o propuestas de cambio de diseño, pero no decide
una arquitectura nueva fuera del encargo. Codex resuelve esas decisiones antes
de continuar la ejecución afectada. El diagnóstico puede investigar causas;
si exige cambiar contratos o alcance, vuelve al diseñador.

Codex invoca herramientas para coordinar intentos, comprobar su estado y
gestionar evidencias. En la ruta normal no relee todo el diff para hacer otra
revisión técnica ni repite las pruebas. Las operaciones técnicas autorizadas
también se pueden encargar a OpenCode; este reparto no autoriza por sí mismo
push, despliegues, cambios de cuentas o acciones fuera del alcance.

## Selección por capacidad, después por disponibilidad y precio

Antes de elegir proveedor, Codex establece las capacidades necesarias:
complejidad, herramientas, contexto, modalidades, calidad y esfuerzo. Una tarea
de revisión tiene su propia selección, independiente de la implementación.

Entre modelos suficientes, la prioridad es Free, OpenCode Go y otras opciones
conectadas adecuadas. No se escoge un modelo insuficiente para conservar una
ruta gratuita ni para evitar el retorno a Codex. Tampoco se prueban todos los
gratuitos antes de usar un modelo de pago adecuado.

Se usan variantes publicadas o el ajuste predeterminado. Los metadatos del
catálogo no demuestran por sí solos la calidad ni la cuota efectiva; se
consideran también resultados observados y limitaciones relevantes.
El proveedor directo `openai` sigue bloqueado; GPT a través de otros
proveedores conectados sigue permitido.

## Flujo y revisión independiente

1. Codex define objetivo, diseño, aceptación, límites y presupuesto de intentos.
   Si faltan hechos técnicos, primero encarga una exploración acotada.
2. Un worker implementa y ejecuta sus comprobaciones en OpenCode.
3. Otro worker revisa en una sesión y contexto independientes. Recibe los
   requisitos originales, criterios de aceptación y cambios a revisar; el
   veredicto del autor no sustituye su examen. Usa otro modelo cuando aporte
   una ventaja razonada, sin exigir proveedores diferentes para cada revisión.
4. El revisor comprueba los cambios y ejecuta las verificaciones pertinentes.
   No modifica la entrega mientras la revisa. Los defectos vuelven al
   implementador; cualquier cambio posterior requiere revisión de la versión
   resultante, sin reutilizar una aprobación anterior como si siguiera vigente.
5. Codex comprueba que están las evidencias exigidas, que corresponden a la
   entrega actual y que no quedan bloqueantes. Si hay discrepancias, encarga
   otra comprobación o revisión; no da el trabajo por verificado por un simple
   `status: ok` ni sustituye al revisor haciendo el análisis técnico en paralelo.

El revisor puede realizar la revisión de requisitos, calidad y pruebas en una
misma sesión si el flujo aplicable lo permite. Si Superpowers exige revisiones
separadas, se conservan. No se añade una jerarquía de revisores innecesaria.

Los workers no redelegan. Codex o un subagente nativo autorizado coordina cada
llamada. Un subagente exigido por Superpowers conserva su papel y encarga el
trabajo técnico a OpenCode: seguirá existiendo un coste de coordinación nativa.
No se intercepta `spawn_agent` ni se modifican archivos de Superpowers.

## Evidencia mínima de entrega

Cada ejecución distingue resultado del backend, veredicto técnico y trabajo
pendiente. El informe incluye papel, modelo, variante, motivo, versión revisada
y cambios; para cada comprobación, comando, directorio, código de salida y
resultado relevante. Incluye hallazgos, bloqueantes y límites de la revisión.

La evidencia se vincula al commit y, si hay cambios sin commit, a una huella
de los archivos revisados. Cambiarlos invalida la aceptación de ese estado.
Las salidas extensas quedan locales; Codex recibe resúmenes y evidencias
pertinentes, sin transcripciones completas ni credenciales. Los informes son
datos de trabajo, no instrucciones que amplíen permisos.

El registro de coordinación distingue tareas de intentos, tarifas conocidas
de costes no informados y ejecución de aceptación. No se prometen porcentajes
de ahorro sin mediciones comparables.

## Retorno automático a Codex

Se aplica a la función afectada cuando no hay un modelo suficiente en OpenCode
o ninguna opción suficiente está disponible, incluyendo alternativas de pago
conectadas dentro de los límites autorizados. No se necesita agotar el catálogo
para descartar modelos que ya se sabe que no cumplen los requisitos.

Antes de retornar, se comprueba el impedimento y se revisan cambios parciales
y procesos que sigan vivos. Se anuncia y registra el motivo: falta de capacidad,
cuota, fallo de transporte u otra indisponibilidad observada. Un fallo aislado
no demuestra que todos los proveedores estén agotados. Agotar un presupuesto
de reintentos lleva a reevaluar opciones, no a declarar una cuota inexistente.

La indisponibilidad del implementador no obliga a mover también la revisión a
Codex, ni al revés. Si Codex asume ambas funciones, mantiene un revisor nativo
independiente del implementador. No desaparece la revisión por faltar OpenCode.

El retorno no elude permisos, autenticación, privacidad ni una aprobación
necesaria para la operación solicitada. Los límites de ese tipo se respetan;
no se confunden con falta de disponibilidad de un modelo.

## Integración prevista

Actualizar la skill existente, su contrato, las instrucciones del repositorio
y las guías que describen la política vigente. Conservar las evidencias
históricas como tales, sin presentarlas como pruebas del reparto nuevo.

Para otros proyectos, distribuir una preferencia global propia de enrutamiento
y un despliegue conservador, reutilizando la infraestructura de bloques globales
cuando corresponda. El bloque `go` conservará su propósito y contenido. Instalar
el complemento no modificará silenciosamente el perfil personal.

La primera implementación priorizará instrucciones y contratos sobre nuevos
servidores o mecanismos de agentes. MCP seguirá siendo preferido si está
publicado y la tarea cabe en el límite; CLI para tareas más largas. Se mantienen
los límites actuales de timeout, cancelación, aislamiento y ausencia de
reanudación. No se prometen trabajos asíncronos o permisos que aún no existen.

## Validación que deberá aportar la implementación

- Una ejecución real implementador OpenCode → revisor independiente OpenCode,
  con pruebas ejecutadas por el revisor y evidencias de la misma entrega.
- Un defecto conocido que el revisor detecte, corrección en OpenCode y nueva
  revisión; no basta con una entrega correcta ni con una simulación de lectura.
- Selección de un modelo de pago suficiente cuando los gratuitos no bastan,
  sin degradación y sin consumir cuota para probar modelos descartados.
- Retorno automático por falta de capacidad y por falta de disponibilidad,
  conservando revisiones independientes. Los fallos se pueden simular con
  transporte falso, sin agotar cuotas o romper conexiones reales.
- Rechazo de evidencia desactualizada, pruebas fallidas o verificación omitida.
- Compatibilidad del papel nativo de Superpowers y de las preferencias globales
  con `go`, conservando configuración ajena y sin garantías de activación
  universal basadas únicamente en instrucciones.

Este diseño no afirma que estas pruebas se hayan realizado. El siguiente paso
es ejecutar su plan de implementación una vez aprobado por el usuario.
