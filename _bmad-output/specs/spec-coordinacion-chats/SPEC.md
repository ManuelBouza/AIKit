---
id: SPEC-coordinacion-chats
companions:
  - protocolo.md
  - ../../planning-artifacts/architecture/architecture-coordinacion-almacenamiento/ARCHITECTURE-SPINE.md
  - ../../../notas/025-coordinador-global-chats-autonomos.md
  - ../../../notas/026-archivado-chats-coordinacion.md
  - ../../../notas/027-automatizacion-coordinacion.md
  - ../../../notas/029-estado-visible-nombre-chat.md
  - ../../../notas/031-aislamiento-sin-git.md
  - ../../../notas/032-coordinador-escritor-mensajes-tareas.md
sources: []
---

# Coordinación local de chats autónomos

## Por qué

Manuel necesita coordinar encargos independientes y seguir su estado sin perder
contexto ni abarrotar la lista de chats. Cada chat trabaja con el usuario y
conserva la responsabilidad de su entrega; un coordinador mantiene la visión del
proyecto y facilita su continuidad con documentación ligera.

## Capacidades

- **CAP-1 — Activación local**
  - **Intención:** El usuario activa y retira la coordinación en los proyectos que elija.
  - **Éxito:** Una prueba en proyecto vacío y otra con instrucciones existentes muestran activación local explícita, preservación de contenido ajeno y retirada controlada.
- **CAP-2 — Encargos y arranque**
  - **Intención:** El coordinador identifica encargos y sus chats responsables, y permite un arranque comprensible para el usuario.
  - **Éxito:** Un encargo elegido se vincula inequívocamente a un chat que explica su comprensión y espera al usuario; sin capacidad de creación se facilita un arranque manual.
- **CAP-3 — Estado y contexto**
  - **Intención:** Cada chat declara su estado y mantiene su título; el coordinador registra las novedades y sus acuses en una única fuente canónica.
  - **Éxito:** Un cambio significativo queda en el registro canónico y se refleja en el título o se comunica la discrepancia; una entrada relevante recibe tratamiento identificable.
- **CAP-4 — Cierre y continuidad**
  - **Intención:** El chat concluye o cancela su encargo con persistencia y limpieza autorizadas, y el coordinador organiza el archivado y la recuperación.
  - **Éxito:** Una demostración registra entrega o cancelación, limpieza y pendientes; el chat inactivo se archiva y puede recuperarse cuando el cliente lo permita.
- **CAP-5 — Seguimiento programado y relevo**
  - **Intención:** El proyecto configura seguimiento periódico asociado al coordinador y conserva su continuidad cuando se releva.
  - **Éxito:** Una ejecución de prueba consulta estados y actúa dentro de sus permisos; tras el relevo, solo el destino correcto queda configurado para ejecutar.
- **CAP-6 — Integridad y recuperación**
  - **Intención:** Las actualizaciones concurrentes o interrumpidas no destruyen silenciosamente registros de coordinación.
  - **Éxito:** Las pruebas de conflicto e interrupción detectan el problema, conservan información recuperable e informan sin simular éxito.
- **CAP-7 — Aislamiento e integración**
  - **Intención:** El usuario elige secuenciar escrituras o habilitar Git y worktrees para trabajo paralelo; el coordinador integra las entregas solicitadas.
  - **Éxito:** Una prueba muestra escrituras secuenciales sin Git y otra verifica solicitudes e integración coordinada de cambios aislados con Git, con conflictos y permisos tratados explícitamente.

## Restricciones

- Activación explícita por proyecto, con instrucciones locales y registros Markdown; funcionamiento manual sin depender de Git, BMAD ni una herramienta específica.
- Una única carpeta canónica `coordinacion/` reside en la raíz local del proyecto y solo el coordinador la escribe; las tareas aisladas comunican avisos y consultan acuses por los cauces autorizados disponibles.
- Una skill describe el procedimiento sin duplicar capacidades existentes; el cliente puede limitar la creación, consulta o modificación de chats.
- Cada tarea declara su estado y revisiones; el coordinador los registra, coordina y revisa la integración solicitada, sin sustituir sus verificaciones ni aprobar su cierre. La mensajería respeta permisos y disponibilidad del cliente, con alternativa manual.
- Los avisos conservan ID en reenvíos; acuses consultables distinguen recepción de incorporación. Se reconcilian envíos inciertos antes de reenviar y se conservan conflictos sin reemplazo automático, según `protocolo.md`.
- El almacenamiento sigue AD-1 a AD-5 de la arquitectura adoptada: estado y acuses se publican juntos por tarea bajo exclusión, con operaciones recuperables e índice derivado. La primera validación se limita a almacenamiento local de un equipo; no acredita garantías en red ni sincronización entre equipos.
- El usuario decide cambios materiales y cancelaciones; se respetan reglas de autorización de las herramientas y acciones sensibles.
- El coordinador es responsable de la integridad y salud de los datos finales y de prevenir su pérdida; con Git gestiona las ramas principales del proyecto y cada tarea su propia rama.
- No perder trabajo no persistido ni instrucciones ajenas. Los registros son breves, se consultan selectivamente y no requieren vigilancia continua.
- La frecuencia se elige por proyecto; la automatización queda vinculada al chat coordinador y se actualiza su destino al relevarlo.
- El protocolo, estados, límites y propuestas no aprobadas se detallan en `protocolo.md`; las notas adoptadas conservan decisiones, evidencia e historia. Las decisiones posteriores prevalecen sobre texto histórico incompatible.

## Fuera de alcance

- Exigir Git, BMAD, OpenCode o una aplicación de notas externa para coordinar.
- Sustituir las verificaciones de los chats de tarea, enviar mensajes directos entre chats por defecto o eliminar automáticamente recursos sin autorización aplicable.
- Garantizar disponibilidad de capacidades del cliente, supervisión continua o recuperación de una conversación inexistente en otra instalación.

## Señal de éxito

En un proyecto de prueba, un usuario activa la coordinación, sigue un encargo desde su preparación hasta su entrega y limpieza, observa el estado del chat y recupera su historial archivado. Las limitaciones y pruebas pendientes de la programación y de los conflictos quedan explícitas.

## Supuestos

- Cuando falte una herramienta del cliente se ofrece una vía manual para la parte posible, sin prometer una capacidad inexistente.

## Preguntas abiertas

- ¿Cómo se seleccionan encargos si faltan prioridades o compiten por recursos?
- ¿Qué mecanismos técnicos verifican la exclusión, recuperación e integración sin interferir con los chats activos ni exceder las autorizaciones?
- ¿Qué excepciones adicionales de archivado deben contemplarse?
- ¿Qué esquema concreto, runtime, primitivas de exclusión y publicación y permisos implementarán la arquitectura adoptada, y qué garantías verifican las pruebas en cada plataforma?
- ¿Cómo se identifica la raíz y se comprueba la carga de instrucciones en proyectos sin Git y subdirectorios?
- ¿Dispone una ejecución programada real de las herramientas y permisos necesarios, y despierta el nuevo coordinador tras el relevo sin solaparse?
