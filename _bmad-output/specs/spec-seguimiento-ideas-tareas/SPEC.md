---
id: SPEC-seguimiento-ideas-tareas
companions:
  - datos-y-flujo.md
  - migracion-y-aceptacion.md
sources:
  - ../../../docs/diseno-ideas-tareas-043.md
  - ../../../notas/043-separar-ideas-y-tareas-implementacion.md
---

> Contrato canónico derivado de la memoria de esta especificación. SPEC.md y
> sus dos compañeros definen el alcance completo para implementar y verificar.

# Seguimiento local de ideas y tareas

## Why

El usuario necesita distinguir ideas que madura de entregas que encarga y poder
seguir cada implementación antes de iniciarla. El tablero actual mezcla notas
con resúmenes operativos y los encargos activos usan registros heterogéneos.
Se adopta un registro local Markdown de tareas conectado a las ideas existentes,
con una fuente por tarea y dos vistas de consulta sobre datos canónicos.

## Capabilities

- **CAP-1**
  - **intent:** Relacionar ideas y entregas identificables sin fabricar ideas ni duplicar encargos.
  - **success:** Una idea enlaza varias tareas, una tarea admite varios orígenes y un encargo directo se registra sin idea; repetir su instrucción reutiliza el ticket.
- **CAP-2**
  - **intent:** Seguir ejecución, atención y autorización de cada entrega independientemente de su chat.
  - **success:** Bloqueos y pausas conservan la fase y el motivo; un chat atiende dos tareas sin cierre en cascada ni permisos derivados de su título.
- **CAP-3**
  - **intent:** Hacer visible cada encargo de implementación antes de ejecutarlo.
  - **success:** El Coordinador crea o actualiza el ticket y obtiene una generación correcta de la vista antes de iniciar una implementación nueva; las preguntas y operaciones auxiliares no crean tickets adicionales.
- **CAP-4**
  - **intent:** Consultar ideas y tareas en vistas conectadas, seguras y coherentes.
  - **success:** Ambas vistas e índices se derivan de sus fuentes, muestran responsable, fase, atención, dependencias y referencias; una entrada inválida falla sin sustituir la última salida válida ni abrirla como nueva.
- **CAP-5**
  - **intent:** Incorporar encargos vigentes y su dependencia sin perder contexto o decisiones humanas.
  - **success:** La simulación y la migración inicial de 028, 040 y preparación BMAD conservan estados contrastados al ejecutarse, recursos e historial; repetir la migración no duplica tareas ni ejecuta sus trabajos.
- **CAP-6**
  - **intent:** Configurar el seguimiento del proyecto usando sus capacidades existentes.
  - **success:** Setup ofrece la modalidad local, verifica fuente y operaciones disponibles y explica limitaciones; instalar el complemento no activa ni migra, y detectar un tracker existente no crea un backlog paralelo.

## Constraints

- El modelo adoptado aquí es Markdown local dentro de la raíz canónica existente; datos y reglas de validación en `datos-y-flujo.md`.
- Solo el Coordinador escribe el registro canónico; las tareas conservan avisos y solicitan actualizaciones por el cauce autorizado, sin escribir en el principal desde worktrees.
- Registrar, migrar, recibir mensajes o generar vistas no autoriza ejecución, instalaciones, publicaciones, integración o reintentos ni levanta pausas.
- Mantener la autonomía dentro del encargo autorizado; una espera afecta solo a la operación dependiente, sin segunda orden de arranque.
- Conservar notas y numeración histórica; IDs de implementación independientes de notas, chats y del auxiliar experimental, sin atribuir garantías transaccionales o de autenticación.
- Reutilizar el tablero y las herramientas existentes. BMAD conserva artefactos técnicos enlazados; no es requisito del runtime del producto ni se duplica su contrato.
- No exponer secretos o transcripciones privadas; datos y Markdown se representan sin ejecución ni cargas externas.
- Coordinar contrato y reparto con 028 antes de modificar su tablero; migración y comprobaciones según `migracion-y-aceptacion.md`.

## Non-goals

- Ejecutar implementación o migración por producir esta especificación; preparar BMAD, reanudar tareas, instalar en el perfil, crear chats o hacer push.
- Migrar todo el historial, convertir todas las ideas en tickets, crear un ticket por comando o un chat/worktree por ticket.
- Implementar conectores remotos, sincronización bidireccional, editor web, servidor continuo, scheduler, bloqueo distribuido o autenticación de avisos.
- Reemplazar trackers existentes de otros proyectos o imponer Git/BMAD/Markdown universalmente.

## Success signal

Un encargo directo queda visible antes de implementarse y puede seguirse hasta
su aceptación sin confundirse con una idea o un chat. La demostración incluye
una idea con varias tareas y la migración inicial idempotente con estados
humanos conservados, además del fallo seguro y la activación explícita en setup.

## Assumptions

- Python y el generador local actual permiten parsing/validación/HTML sin añadir
  dependencia de runtime; se propone JSON estricto dentro del Markdown.
- El escritor único manual basta para esta primera implantación. Los controles
  estructurales no detectan toda intención humana ni autentican autorizaciones.
