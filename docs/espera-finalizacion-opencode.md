# Espera por finalización en OpenCode: investigación de notificaciones y tiempos

## Mecanismos actuales distinguidos

**Chat antes de este estudio:** usaba `clock.sleep(300000)` fijo y luego comprobaba la salida. En este estudio se sustituyó esa espera por un aviso ligado a la finalización del proceso, aplicado ya en este chat.

**Núcleo delegado (`bound_execution._wait_result`):** sondea `result.json` cada 20 ms (`POLL_SECONDS=0.02`) y **retorna inmediatamente** cuando el archivo existe con estado terminal. No duerme 300 s fijos; el timeout es un deadline, no un sleep fijo.

## Evidencia empírica de espera acotada por finalización

- **Proceso propio de 35 s:** duró 35,001 s. La espera de herramienta se resolvió tras 20,23 s de espera efectiva, antes del máximo de 300 s.
- **Notificación asíncrona:** emitida a los 15,004 s del experimento, interrumpió un `clock.sleep(60s)` activo sin agotar su plazo.
- **Trabajo real:** notificación `client_exited` interrumpió `clock.sleep(300000)` a los 282,6 s; coordinador leyó estado del adaptador `ok` tras el wake. **Sólo durante turno de espera activo**; no hay canal push universal para chat idle/cerrado.

**No se demostró** ningún push universal a chat idle/cerrado. Los *background hooks* de OpenAI **no inician** nuevos turnos idle (docs oficiales).

## Recomendación: espera por proceso propio + validación semántica

En el cliente actual, preferir la **herramienta de espera del proceso propio**, con límite máximo y retorno anticipado al finalizar. Una notificación asíncrona disponible en este anfitrión puede despertar la espera activa. Después se debe comprobar el resultado del adaptador; una futura integración con el supervisor también deberá validar su estado persistido:

- Confirmar `delivery` ∈ {completed, failed, interrupted}
- Verificar `attempt_id`, `session_id`, `server_identity` coinciden
- `pending`/`uncertain` **nunca** autoriza reintento/duplicar inferencia; requiere reconciliación del estado
- Salida del cliente (exit code) es sólo **señal**, no finalización autoritativa: supervisor puede reportar pending tras pérdida de cliente

## OpenCode SSE: disponible pero volátil y global

Endpoint local `/api/event` (SSE) con filtro `types[]` expone `session.execution.succeeded/failed/interrupted`, `session.idle`, `session.created` (OpenAPI v2.2.0 verificado). **Contrato**: volátil — consumidor lento desborda y falla; eventos en desconexión se pierden. Requiere filtro por tipos y correlación de tarea/sesión en el cliente, reconexión, deduplicación y **reconciliación autoritativa tras caída**. No reemplaza validación de `result.json`. No es canal push probado para chat.

## Estadísticas: solo fallback, por intento comparable

- Recoger duraciones a **nivel de intento** (usuario→asistente terminal) particionadas por proveedor/modelo/esfuerzo/rol
- Separar éxitos de errores/censurados (right-censored)
- Usar mediana + dispersión (IQR/MAD); *conditional remaining time* dado tiempo transcurrido cuando datos suficientes
- **Dataset actual insuficiente**: 4 sesiones, 5–6 intentos medibles, 3 con frontera usuario→asistente clara (365 s, 73 s, 85 s), combinaciones proveedor/modelo/esfuerzo/rol distintas → **sin grupo homogéneo**. Reportar "insuficiente para predictores".

## Alcance y límites

- No se justifica reescritura de manejo de procesos en el núcleo solo por el sleep diferido del chat
- Mecanismo de chat probado; **integración skill/plugin permanente no implementada/instalada**
- Mantener multitarea y sin modelo/subagente de monitorización
- Investigación de solo lectura; sin cambios a código producto, config instalada, credenciales, servidor, programación, sondas ni delegación

## Fuentes

- OpenAPI local: `GET /api/event` (v2.2.0 observada, no restricción de versión); [protocolo oficial OpenCode](https://github.com/anomalyco/opencode/blob/dev/packages/protocol/src/groups/event.ts).
- [OpenAI Hooks](https://learn.chatgpt.com/docs/hooks): los hooks en segundo plano no inician un nuevo turno cuando el chat está inactivo.
- Evidencia empírica: `.aikit/opencode-wait-study/tool-wait-probes.json`
- Informe completo: `.aikit/opencode-wait-study/report.json` (y `report-round0.json`)