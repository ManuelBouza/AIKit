# Notificaciones proactivas del Coordinador

Fecha: 2026-11-16.
Estado inicial: Pendiente de debatir.
Estado actual: Implementada y verificada; actualización privada 0.1.4 instalada y descubierta.

## Petición y alcance

Manuel indica que avisar a los chats afectados por cambios relevantes forma
parte del rol del Coordinador y debe hacerse automáticamente, sin pedir su
aprobación para cada notificación. Solicita implementar esta mejora.
Surge tras publicar e instalar AIKit 0.1.3 y preguntar si debía informar a los
chats 028/040, que permanecen pausados.

Autorización verificable en el chat Coordinador
`01a1da03-23f1-7eb0-b0a0-5cb5184e6941`, turno
`01a1e5a2-043b-7221-a262-ecff24f20feb`, mensaje humano
`01a1e5a2-04bf-76d3-a0e9-2e3ca1da789f`.

## Criterios

- Ante cambios relevantes conocidos durante su trabajo, identificar chats
  asignados afectados y notificar por el cauce disponible y autorizado.
  No pedir autorización por aviso cuando ya existe autorización humana aplicable.
- Conservar cambio o versión, destinatarios, contenido y resultado real del envío.
  Distinguir envío y reconocimiento; reconciliar incertidumbres antes de repetir.
- No notificar cada comando ni emitir mensajes duplicados o a chats ajenos.
- Un aviso a una tarea pausada es informativo: no reanuda la tarea, amplía
  permisos ni autoriza actualizar su rama, investigar, probar o limpiar recursos.
- La herramienta puede activar un turno para recibir el mensaje; no confundir
  recepción con reanudación ni prometer una entrega silenciosa si el cliente no
  la proporciona. Sin mensajería, conservar pendiente y facilitar traslado manual.
- Conservar autoridad del usuario, revisión técnica delegada e integración
  centralizada. No activar comunicación directa entre tareas ni escribir sus ramas.
- La skill y setup describen el deber y el acuerdo de comunicación. Leerlos no
  concede autorización humana en proyectos nuevos ni crea vigilancia continua,
  tareas programadas, servicios o capacidades nativas inexistentes.

## Aplicación inmediata

El Coordinador envía los avisos `COORD-0.1.3-028-01` y
`COORD-0.1.3-040-01`, revisión 1, sobre 0.1.3 instalada y subida a origin/main.
Ambos explicitan que las tareas siguen Pausadas. Originales y reconocimiento
se conservan en el registro del proyecto y en los historiales nativos.
No se modifica ni reanuda el trabajo de 028/040.

## Relaciones

- [025 — Coordinación](025-coordinador-global-chats-autonomos.md).
- [032 — Coordinador escritor](032-coordinador-escritor-mensajes-tareas.md).
- [041 — Autonomía de tareas](041-autonomia-chat-tarea-tras-asignacion.md).
- [Registro de los dos chats](../coordinacion/paralelo-028-040/ENCARGOS.md).

Se ajustan las nueve fuentes de coordinación, setup y guías existentes; ambas
skills pasan el validador oficial y la prueba de exportación pertinente pasa.
Especificación: [042](../_bmad-output/implementation-artifacts/spec-042-notificaciones-coordinador.md).
Tres enfoques de revisión independiente completados y hallazgos pertinentes
corregidos. Evaluación independiente A–H y relectura del parche final correctas;
evalúa decisiones descritas, sin atribuir garantías de runtime. El empaquetado
y los ensayos de instalación, migración y recuperación a 0.1.3 pasan; aplicación
habitual de 0.1.4 y descubrimiento de las tres skills verificados, con respaldo
privado y configuración ajena conservada. [Entrega y recuperación](../docs/actualizacion-aikit-0.1.4.md).

Se informa también de 0.1.4 a ambos chats sin pedir aprobación por aviso;
originales conservados antes de enviar y reconocimiento consultado en el historial
nativo. Ambos mantienen Pausada. [Registro](../coordinacion/paralelo-028-040/ACUSES.md).
No se alteran los bytes de la distribución 0.1.3: se conserva como versión anterior.
