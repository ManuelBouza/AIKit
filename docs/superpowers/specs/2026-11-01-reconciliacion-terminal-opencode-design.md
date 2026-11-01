# Diseño: Reconciliación Terminal de OpenCode por Mensaje Persistido

Borrador de diseño pendiente de revisión del usuario. NO implementado ni instalado. El `go` previo eligió el enfoque, no aprobó este documento.

## 1. Objetivo, evidencia y limitaciones

Cuando la CLI de OpenCode v2.2.0 termina un turno sin emitir `step_finish`/`step-finish` (reason `stop`) en stdout, el supervisor conserva `delivery=pending` aunque el mensaje durable del servidor tenga `finish=stop` sin error. Este diseño propone reconciliar únicamente por lectura read-only del mensaje persistido cuando falte el marcador terminal, conservando el núcleo compartido CLI/MCP y el parser conservador. Evidencia: `.aikit/mcp-terminal-contract/report.json` y `.aikit/mcp-terminal-events/report.json` (artefactos ignorados por Git; referencias históricas, no dependencias para comprender el contrato). Fuentes oficiales tag v2.2.0: https://github.com/anomalyco/opencode/tree/v2.2.0 — `packages/cli/src/run/noninteractive.ts`, `packages/protocol/src/groups/session.ts`, `packages/schema/src/session-event.ts`, `packages/schema/src/llm.ts`, `packages/schema/src/session-status-event.ts`. Distinguir: código observado (reportes), garantías API (documentación oficial) y diseño propio (este documento). Limitaciones: un solo artefacto capturado; log SSE histórico no recuperable; correlación no garantizada si `parent_id=null`.

## 2. Alternativas y decisión aprobada

- **Enfoque 1 (elegido):** reconciliar mediante mensaje persistido solo cuando falta evento terminal, conservando CLI y núcleo compartido. Alcance acotado, sin infraestructura paralela.
- **Enfoque 2 (no elegido):** sustituir captura por eventos persistidos del servidor. Mayor alcance y mantenimiento; descartado.
- **No se acepta:** modificar el parser para inventar terminal, ni aceptar idle/exit 0/texto como éxito.

## 3. Alcance y no objetivos

En alcance: contrato de correlación, tabla de aceptación, persistencia de evidencia mínima, integración con `session_store`, `session_worker`, `session_stream`, `bound_execution`. Fuera de alcance: nueva skill o infraestructura, servicios, catálogo/cuota, cambios globales de estado, instalación, commit/push, inferencias adicionales. No se añaden SSE globales, hooks, monitor LLM ni servidor.

## 4. Flujo mínimo y contrato

1. El supervisor ejecuta la CLI y parsea stdout con `EventStream` (regla conservadora: `step_finish`/`step-finish` con `reason=stop` y actividad sin mismatch).
2. Si `terminal=false` al cerrar cliente y no hay error de sesión, realizar **una lectura puntual** read-only a `GET /api/session/:sessionID/message/:messageID` (API oficial) dentro del presupuesto restante compatible con MCP 45 s y timeout existente; sin polling nuevo ni catálogo.
3. Correlacionar inequívocamente propietario/servidor, sesión, intento y mensaje actual. Preferir IDs de admisión/prompt/asistente realmente soportados por la API; si no hay vínculo fiable, conservar `uncertain`. Nunca elegir el último mensaje por cercanía temporal.
4. Acreditar solo si `finish=stop` sin `message.error` ni interrupción. `idle`/inbox/permissions son apoyo, no éxito. `length` = parcial; `error`/`content-filter`/`interrupted`/`cancel` = no satisfactorio; `tool-calls`/`unknown` = nunca éxito final.
5. Si imposible o incierta la correlación, conservar IDs y mecanismos existentes para consulta explícita posterior; no reintentar ni inferir.
6. Persistir evidencia mínima sanitizada (procedencia, IDs, outcome, reason) de forma atómica con locks/`session_store` existentes; reusar evidencia verificada salvo cambio de identidad. Sin credenciales ni transcripciones. No inferir tarifa/coste.

## 5. Tabla de aceptación

| Caso | Condición | Resultado |
|------|-----------|-----------|
| Éxito real | `finish=stop`, sin `error`, IDs válidos | `completed` |
| Conflicto terminal | Evento de error en stdout | `failed` |
| IDs incorrectos / mensaje ajeno | assistant id ≠ intento actual | `uncertain`/`pending` |
| `parent_id=null` sin vínculo | Sin correlación fiable | `uncertain`, sin promesa de resolución |
| `finish=length` | Salida truncada | parcial, no éxito |
| `error`/`content-filter`/`interrupted`/`cancel` | Fallo o cancelación | no satisfactorio |
| `tool-calls`/`unknown` | Terminal no final | nunca éxito final |
| Mensaje incompleto | Sin `completed_at` | conservador |
| Solo idle | Sin mensaje válido | no éxito |
| API no disponible/timeout/propietario cambió | Lectura falla | conservar estado, `pending` |
| Persistencia/idempotencia | Reejecución con misma identidad | reusar evidencia verificada |
| Sin inferencia | Cualquier ambigüedad | no autoriza reintento |

## 6. Integración existente

Integrar en `session_worker.supervise` (tras `events.finish()`, cuando `terminal=false` y sin error) una llamada de reconciliación acotada, persistiendo en `record.delivery`/`record.execution` vía `save_task`/`lock_task`. `bound_execution._map_result` y `_recover` ya manejan `pending`/`result_mismatch`; reutilizarlos. `session_stream.EventStream` no se relaja: su regla conservadora permanece. `session_store` aporta locks atómicos y validación de identidad.

## 7. Pendientes y riesgos

- Riesgo principal: correlación no garantizada en el caso original (`parent_id=null`); requiere gate de implementación y pruebas con IDs ficticios antes de acreditar.
- Pendiente: revisión del usuario de este borrador; luego `writing-plans`, no implementación directa.
- Sin tests nuevos en esta fase documental; regresión sugerida en reportes de investigación.