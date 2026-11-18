# Modernizar la experiencia del tablero de notas

Fecha: 2026-11-14.
Estado inicial: Pendiente de debatir.

Estado actual: Implementada y verificada localmente; cierre completado y chat archivado.

## Entrega — 2026-11-18

Resultado final de integración: corrección `5d712f73` incorporada mediante
`4daca7849743cf2481107790e7af2967718f31b6`, sin cambio al HTML. El control
DOM obligatorio posterior pasa en escritorio y móvil. Era una carrera de la
aserción con el evento close; un control negativo confirma que la espera
mantiene la exigencia de foco. [Evidencia final](../docs/integracion-tablero-028.md).
La implementación está terminada en fuentes; IMP-0002 conserva pendiente el
cierre de recursos del chat.

Cierre posterior completado: todo el contenido local se conserva en ZIP privado
verificado y la historia en bundle. La tarea retiró33enlaces sin borrar sus
destinos; después de comprobar9571archivos intactos se archivó el chat. El
cliente retiró el checkout y el Coordinador retiró la rama con respaldos intactos.
IMP-0002 finalizada. El tablero generado refleja la implementación al recargarlo.

Aplicación posterior: `26847986aac76fce7ee9971d0e1938f57f58fa98` conserva
la entrega en main. El control DOM posterior falla en escritorio y móvil al
comprobar retorno de foco tras relaciones/cierre; se ha pedido corrección dentro
del mismo IMP-0002. La mejora no se considera finalizada hasta aclarar y verificar
ese resultado. Aviso [028-correccion-foco-01](../coordinacion/paralelo-028-040/avisos/028-correccion-foco-01.md).

El Chat028 presenta `21f1a6977183db8c2af8f1220186ba7b0a5fe47e`, base36cb,
con HTML, documentación, prueba DOM y especificación. La verificación independiente
acepta el commit completo y acredita54pruebas sin omisiones y correcciones
revisadas. Integración y cierre se siguen en IMP-0002. Original en
[028-entrega-revision-01](../coordinacion/paralelo-028-040/avisos/028-entrega-revision-01.md).

## Aprobación visual — 2026-11-18

Manuel aprueba directamente la propuesta en chat028, turno
`01a1ed3a-39d9-7ac2-b5f6-cf3eca31a2b0`, mensaje
`01a1ed3a-3bf8-79e1-81cb-2036f9801ce4`. El Coordinador contrasta esa aprobación
y registra la implementación en IMP-0002. La preparación local y la coordinación
de base con las vistas Ideas/Tareas043 se resuelven antes de modificar el tablero.
La aprobación no incluye Sites, herramientas globales ni publicación.

El chat028 incorpora la base36cbde57eff20dde73a968e44665957178e4aaa0 por avance
directo comprobado, conservando el árbol limpio. Se mantienen las vistas y el
contrato de Ideas/Tareas043. La preparaciónBMAD de IMP-0004 está finalizada y
verificada; puede continuar su implementación aprobada con autonomía.
Véase [entorno y evidencia](../docs/preparacion-bmad-worktree-028.md).

## Reanudación de propuesta visual — 2026-11-17

Manuel retoma directamente el diseño en el chat 028 y pide proponer la mejor
opción tras revisar tableros modernos. Origen humano contrastado: turno
`01a1e822-ed79-7e02-94fd-dd2505eedaba`, mensaje
`01a1e822-ee3a-7091-b6d8-89e892af1841`. La propuesta se presenta y queda pendiente
de aprobación; no se interpreta como permiso de implementación ni instalación.
El estado sustituye la pausa histórica de abajo. BMAD sigue pendiente antes de
implementar; véase la conciliación en el registro canónico de ACUSES.md.

## Pausa — 2026-11-16

Manuel pide mantener en espera los chats 028 y 040 y continuar la corrección
en el Coordinador. No reanudar investigación, implementación ni preparación
del entorno hasta nueva indicación. Se conservan rama, worktree y evidencias.
La decisión visual previa sigue pendiente, sin solicitarla durante la pausa.

## Continuidad autónoma — 2026-11-16

El chat reconoce la corrección de autonomía de la [nota 041](041-autonomia-chat-tarea-tras-asignacion.md)
y presenta al usuario una propuesta visual. No espera otra orden del Coordinador.
La preparación aislada de BMAD queda pendiente antes de implementar, sin detener
esa conversación visual. Véanse [aviso y acuse](../coordinacion/paralelo-028-040/ACUSES.md).

## Preparación — 2026-11-16

Manuel aprueba preparar un Chat de Tarea y worktree propio para esta nota en
paralelo con la 040. [Encargo y límites](../coordinacion/paralelo-028-040/ENCARGOS.md).
Se mantiene pendiente concretar el diseño antes de implementar; la prueba con
Sites queda fuera de este encargo.

## Idea

El tablero de notas actual se siente frío. Modernizar su apariencia y su
interacción tomando como referencia tableros Kanban profesionales para conseguir
una experiencia más agradable, clara y cuidada.

Al pulsar una tarjeta o elemento del tablero, abrir su detalle en una ventana
emergente centrada, en lugar de mostrarlo debajo del tablero.

## Pendiente de concretar

- Investigar referencias de tableros profesionales y sus patrones de experiencia
  antes de proponer el diseño; los productos de referencia están por elegir.
- Definir el estilo visual y el comportamiento del detalle centrado, incluido
  su cierre, navegación por teclado y adaptación a pantallas pequeñas.

## Ampliación — 2026-11-15

- Hacer una prueba con [Sites](plugin://sites@openai-curated-remote) para explorar
  una propuesta de mejora del tablero de notas y valorar su experiencia visual
  e interacción, incluida la apertura del detalle en una ventana centrada.
- La prueba queda anotada para más adelante; no se ejecuta ni se publica nada
  al registrar esta ampliación.

## Relación y alcance

Mejora del tablero local existente descrito en la
[nota 023](023-visualizacion-backlog.md). Mantener la trazabilidad con las notas
Markdown y el backlog canónico [IDEAS.md](IDEAS.md).

Esta nota registra la intención del usuario; no inicia investigación, diseño
detallado ni implementación.
