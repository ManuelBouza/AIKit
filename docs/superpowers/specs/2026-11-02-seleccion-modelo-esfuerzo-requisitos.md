# Requisitos: selección de modelo y esfuerzo por encargo

**Borrador pendiente de revisión del usuario.** Describe requisitos para una etapa posterior; no implementa ni habilita cambios de política.

## Objetivo y alcance

Definir una selección proporcionada del modelo y esfuerzo según las necesidades de cada encargo, conservando calidad suficiente y uso responsable de recursos. El documento concreta la fase de requisitos relacionada con las notas *Método del Director de Ideas* (009) y *Criterios modelo y esfuerzo* (010), ubicadas en otro checkout y no copiadas aquí. No activa el método 009 para todas las tareas.

## Acuerdos explícitos

La adecuación al encargo prevalece sobre precio, cuenta o plataforma: “suficiente” significa cumplir sus requisitos, no usar siempre el modelo más potente. No se forzarán modelos pequeños ni esfuerzo insuficiente para evitar Codex, ni `high`/`max` por costumbre. Primero se determina adecuación; entre alternativas adecuadas se consideran coste, tiempo y recuperaciones con criterio, sin fórmula inventada.

Si OpenCode y Codex ofrecen vías disponibles y suficientemente adecuadas, se prefiere OpenCode para preservar la cuenta Codex. Dentro de OpenCode no habrá orden fijo por gratuidad, precio o proveedor, asignaciones rígidas tarea-modelo, obligación de agotar candidatos ni degradación para evitar Codex.

Si un intento OpenCode queda incompleto por agotamiento verificado de tokens/cuota y no queda alternativa adecuada disponible, se permitirá evaluar OpenAI de pago en esa misma sesión para continuar ese intento. No habilita tareas nuevas ni una ruta ordinaria a Codex mediante OpenCode. GPT servido por Go u otro proveedor ya permitido no necesita esta excepción. Si tampoco hay vía adecuada, se continúa en Codex con el contexto y evidencia recuperables, sin detener el trabajo ni prometer transferencia íntegra entre plataformas.

## Requisitos

Las siguientes concreciones operativas son **propuestas para aprobación**, no acuerdos adicionales:

- **R01 — Perfilar la tarea.** Antes de elegir, registrar brevemente complejidad, ambigüedad, contexto real, herramientas, impacto de error y calidad requerida. Contrastar ese perfil con capacidades acreditadas por documentación, evidencia o experiencia; nombre, precio, catálogo o cuota por sí solos no acreditan calidad.
- **R02 — Consultar proporcionalmente.** Empezar por la tabla local disponible (modelos, esfuerzos, capacidades, cuota y tiempos solo si fueron medidos). No consultar catálogo, web ni cuota, ni lanzar comparación con modelos, por rutina en cada tarea. Usar el flujo existente ante cambios, rechazos o recuperación; no crear TTL, horarios ni automatizaciones. Estado desconocido no significa disponible ni agotado; una tarea autorizada cuenta como intento, no como sondeo.
- **R03 — Elegir sin equivalencias rígidas.** Comparar solo combinaciones publicadas de modelo y variante; si no hay variante publicada, usar y declarar el valor predeterminado. No asumir equivalencia de esfuerzos entre proveedores ni elevar automáticamente al máximo para compensar limitaciones. Si ninguna opción OpenCode es adecuada y disponible, elegir Codex cuando sí lo sea.
- **R04 — Avisar y dejar rastro.** Antes de cada inferencia, comunicar objetivo, modelo, proveedor, variante o predeterminado, tarifa acreditada o desconocida y motivo breve de adecuación/selección. Registrar decisión y resultado mínimos, sin secretos, transcripción ni coste inventado.
- **R05 — Recuperar sin duplicar.** Antes de reenviar, confirmar estado y proceso reales; conservar IDs, sesión, cambios parciales y presupuesto. Intento activo, terminado, `pending` o `uncertain` no autoriza duplicación. Lentitud, error de red o falta de `step_finish` no prueban agotamiento; exigir señal verificable de cuota.
- **R06 — Acotar la excepción OpenAI.** Para continuar con proveedor directo OpenAI exigir intento existente incompleto por cuota, ausencia verificada de alternativas adecuadas disponibles, modelo/cuenta conectados adecuados y permisos válidos. Diseñar después un mecanismo limitado a esa sesión; no desactivar el bloqueo general ni afirmar que hoy está soportado.
- **R07 — Preservar roles.** Mantener subagentes nativos, Superpowers y revisión independiente. La revisión es una tarea propia que requiere modelo adecuado: checks deterministas no sustituyen análisis técnico y etiquetar un modelo o esfuerzo como `high` no acredita calidad de revisor. No rediseñar aquí el reparto general Codex/OpenCode.
- **R08 — Alinear cambios futuros.** Tras aprobación, armonizar texto global, de proyecto, skill y transporte existentes e identificar prioridades previas que deban sustituirse. Este borrador no modifica reglas activas ni permisos: el bloqueo OpenAI actual, si está configurado, permanece vigente.

## Ejemplos de aceptación

Son criterios para implementar y probar posteriormente; **no se ejecutan en esta fase**.

| Situación | Resultado requerido |
|---|---|
| Free y pago son adecuados | Sin preferencia fija por tarifa; elegir con criterio. |
| OpenCode inadecuado; Codex adecuado | Continuar en Codex. |
| Ambos suficientemente adecuados | Preferir OpenCode. |
| Sin variante publicada | Usar y declarar el predeterminado. |
| Modelo limitado | No elevar automáticamente a `max`. |
| Cuota agotada, sin alternativa adecuada | OpenAI de pago solo en la misma sesión existente. |
| Nueva tarea directa OpenAI | Rechazar por la regla ordinaria. |
| Intento activo | No reenviar ni duplicar inferencia. |
| Ninguna vía adecuada disponible en OpenCode | Continuar con una opción adecuada de Codex y evidencia/contexto recuperables, sin promesa de transferencia íntegra. |

## Fuera de alcance y pendientes

Quedan pendientes la aprobación del usuario, el diseño concreto de la habilitación excepcional, la identificación de prioridades que se reemplazarían y la implementación con pruebas de aceptación. No se modifica routing, instrucciones globales o de proyecto, skills, políticas, `opencode.json`, checkout principal, notas, caché, configuración, estado ni cuentas. Esta fase no autoriza ejecutar los casos de aceptación, instalar el complemento ni publicarlo. Versionar el borrador no activa la política. La propuesta no acredita disponibilidad, calidad de modelos concretos ni permisos nuevos.
