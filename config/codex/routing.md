<!-- AIKIT:ROUTING:BEGIN -->
# Orquestación Codex/OpenCode (AIKit)

Codex conserva conversación, diseño, arquitectura, contratos, plan y selección de
modelo. OpenCode ejecuta exploración factual, diagnóstico, implementación,
pruebas, correcciones, documentación, revisión independiente y verificación.

Capacidad primero: Free adecuado -> Go -> otras alternativas adecuadas -> Codex
nativo si no hay opción adecuada o disponible. No degradar para evitar Codex ni
agotar Free inadecuados. Si falta modelo adecuado o disponibilidad adecuada,
retornar automáticamente por función, anunciando y registrando motivo, sin nueva
aprobación; mantener revisión independiente. Solo bloquea el proveedor directo
`openai`; GPT de otros proveedores sigue permitido. Usa variantes publicadas o
el predeterminado.

Antes de cada inferencia en OpenCode anuncia objetivo, modelo, esfuerzo y tarifa
(acreditada o desconocida). Revisa cambios parciales y procesos vivos antes de
reintentar. No eludas permisos, autenticación ni privacidad. Workers no
redelegan; no interceptar subagentes ni modificar Superpowers.

Si un subagente nativo usa la CLI, devuelve el JSON de stdout directamente al
coordinador; solo este persiste en una ruta permitida. Si falla el guardado,
recupera la salida y registra el problema: no repitas una inferencia terminada.
Reutiliza permisos conocidos solo para el mismo entorno y alcance; si se sabe que
el sandbox bloquea la CLI, solicita `exec_command` con `require_escalated` desde
el primer intento y justificación acotada. Si el entorno cambió o se desconoce,
haz primero un preflight sin inferencia. No escales globalmente ni para eludir
controles; ante denegación informa código y motivo, sin reintento a ciegas. No
pruebes permisos con modelos ni elijas otra vía CLI por un caso antiguo si MCP
está disponible.

Si la skill `$delegating-to-opencode` o su transporte no están disponibles,
informar y continuar nativamente según el diseño; no asumir rutas personales ni
autoinstalar. Referenciar la skill por nombre, no por ruta local.

Revisor en sesión nueva, sin redelegar ni modificar la entrega; devuelve
decisiones de diseño al coordinador. Codex valida la metadata de aceptación, no
repite la revisión técnica. MCP preferido si está publicado y cabe en 60 s; CLI
para tareas largas; no reintentar si hay intento vivo.
<!-- AIKIT:ROUTING:END -->
