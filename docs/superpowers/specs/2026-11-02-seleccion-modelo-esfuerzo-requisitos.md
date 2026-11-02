# Requisitos: selección de modelo y esfuerzo por encargo

**Borrador pendiente de revisión del usuario.** Describe requisitos para una etapa posterior; no implementa ni habilita cambios de política.

## Objetivo y alcance

Definir una selección proporcionada del modelo y esfuerzo según las necesidades de cada encargo, conservando calidad suficiente y uso responsable de recursos. El documento concreta la fase de requisitos relacionada con las notas *Método del Director de Ideas* (009) y *Criterios modelo y esfuerzo* (010), ubicadas en otro checkout y no copiadas aquí. No activa el método 009 para todas las tareas.

## Acuerdos explícitos

La adecuación al encargo prevalece sobre precio, cuenta o plataforma: “suficiente” significa cumplir sus requisitos, no usar siempre el modelo más potente. Todas las alternativas deben ser adecuadas antes de comparar recursos. No se forzarán modelos pequeños ni esfuerzo insuficiente para evitar Codex, ni `high`/`max` por costumbre. Se respetan presupuesto, urgencia y dependencias; se estima el coste total hasta un resultado aceptado, incluidos reintentos y correcciones, usando evidencia de trabajos comparables. Si faltan datos, se declara incertidumbre; gratuito no significa automáticamente conveniente.

Si OpenCode y Codex ofrecen vías disponibles y suficientemente adecuadas, se prefiere OpenCode para preservar la cuenta Codex. Dentro de OpenCode no habrá orden fijo por gratuidad, precio o proveedor, asignaciones rígidas tarea-modelo, obligación de agotar candidatos ni degradación para evitar Codex.

Si un intento OpenCode queda incompleto por agotamiento verificado de tokens/cuota y no queda alternativa adecuada disponible, se permitirá evaluar OpenAI de pago en esa misma sesión para continuar ese intento. No habilita tareas nuevas ni una ruta ordinaria a Codex mediante OpenCode. GPT servido por Go u otro proveedor ya permitido no necesita esta excepción. Si tampoco hay vía adecuada, se continúa en Codex con el contexto y evidencia recuperables, sin detener el trabajo ni prometer transferencia íntegra entre plataformas.

Cuando dos opciones OpenCode adecuadas sirven a la tarea, se acuerda preservar la cuota de una bolsa compartida que también habilite capacidades útiles para encargos más exigentes, favoreciendo otra bolsa solo si es compatible con las condiciones concretas de la tarea. Perjuicio significativo significa comprometer esas condiciones: se respetan presupuesto, urgencia y dependencias, y se compara el coste total hasta resultado aceptado, incluidos reintentos y correcciones. Se usan estimaciones acreditadas de trabajos comparables; si faltan datos, se declara incertidumbre. No hay porcentajes ni segundos universales, ni se presume que una opción gratuita convenga más. La reserva es flexible, no absoluta: no justifica degradar calidad ni impone orden por gratuidad o pago. Se considera el reinicio o caducidad para evitar desperdiciar cuota. Se reserva una bolsa concreta, no un proveedor entero; un proveedor puede tener bolsas independientes. Si reservar implica gasto o demora material que las instrucciones no resuelven, se presenta la decisión al usuario; las elecciones rutinarias corresponden al coordinador.

Solo se atribuye este coste de oportunidad cuando la relación entre cuota y capacidades está acreditada. Que varios modelos aparezcan bajo un mismo proveedor no demuestra que compartan cuota. Si esa relación es desconocida, no se presume beneficio de reserva ni se lanzan inferencias para averiguarlo.

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
- **R09 — Representar reservas acreditadas.** Propuesta: basar la reserva solo en evidencia local de grupos de cuota, sus miembros y alcance, fuente y fecha de observación; conservar caducidad o reinicio únicamente si se conoce. No inferir cuota compartida por proveedor, nombre o listado de modelos, inventar relaciones entre bolsas ni añadir consultas rutinarias, TTL o ranking universal. Relacionar la reserva con capacidades acreditadas útiles para tareas más exigentes, no con etiquetas comerciales o coste por sí solos; no prometer beneficio futuro.
- **R10 — Aplicar preferencia flexible.** Conforme al acuerdo explícito, comparar recursos solo entre opciones adecuadas y preservar la bolsa compartida cuando la alternativa sea compatible con las condiciones concretas del encargo. Evaluar presupuesto, urgencia, dependencias y coste total hasta resultado aceptado, incluidos reintentos y correcciones, con evidencia comparable; si faltan datos, declarar incertidumbre. Considerar la caducidad conocida. Si la reserva supone gasto o demora material que las instrucciones no resuelven, presentar la decisión al usuario; las elecciones rutinarias corresponden al coordinador. No hay prioridad absoluta ni se presume conveniente lo gratuito. Esta preferencia nunca amplía la excepción OpenAI, que sigue requiriendo un intento incompleto por cuota y ninguna alternativa adecuada disponible.

## Ejemplos de aceptación

Son criterios para implementar y probar posteriormente; **no se ejecutan en esta fase**.

| Situación | Resultado requerido |
|---|---|
| Free y pago son adecuados | Sin preferencia fija por tarifa; elegir con criterio. |
| Alternativas de recursos aún no evaluadas | Confirmar adecuación de todas antes de compararlas; no presumir que la gratuita conviene. |
| OpenCode inadecuado; Codex adecuado | Continuar en Codex. |
| Ambos suficientemente adecuados | Preferir OpenCode. |
| Sin variante publicada | Usar y declarar el predeterminado. |
| Modelo limitado | No elevar automáticamente a `max`. |
| Cuota agotada, sin alternativa adecuada | OpenAI de pago solo en la misma sesión existente. |
| Nueva tarea directa OpenAI | Rechazar por la regla ordinaria. |
| Intento activo | No reenviar ni duplicar inferencia. |
| Ninguna vía adecuada disponible en OpenCode | Continuar con una opción adecuada de Codex y evidencia/contexto recuperables, sin promesa de transferencia íntegra. |
| A adecuada en bolsa independiente; B adecuada en bolsa compartida acreditada, útil para tareas exigentes | Favorecer A si no perjudica significativamente coste/plazo de la tarea actual. |
| Relación entre bolsas desconocida | No atribuir beneficio de reserva ni averiguarlo mediante inferencias. |
| Reservar compromete presupuesto, urgencia o dependencias y las instrucciones no lo resuelven | Presentar el intercambio al usuario; no aplicar primacía automática de la reserva. |
| Cuota compartida caduca antes del uso previsto | Considerar la pérdida evitable; no reservar incondicionalmente. |

## Fuera de alcance y pendientes

Quedan pendientes la aprobación del conjunto de requisitos y el diseño concreto de la habilitación excepcional OpenAI. También falta concretar qué evidencia identifica capacidades reservables, modelos de frontera y coste de oportunidad —sin ranking universal ni beneficio futuro asegurado—, así como el diseño y la implementación con pruebas de aceptación. La elección entre inferencia y código determinista para seleccionar recursos sigue en deliberación y no se considera aprobada. No se modifica routing, instrucciones globales o de proyecto, skills, políticas, `opencode.json`, checkout principal, notas, caché, configuración, estado ni cuentas. Esta fase no autoriza ejecutar los casos de aceptación, instalar el complemento ni publicarlo. Versionar el borrador no activa la política. La propuesta no acredita disponibilidad, calidad de modelos concretos ni permisos nuevos.
