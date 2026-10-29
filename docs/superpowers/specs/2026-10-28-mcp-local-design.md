# MCP local sobre el adaptador de OpenCode

El usuario aprobó implementar MCP como puerta de entrada a la CLI existente.
La comparación previa está en `docs/evaluacion-mcp-opencode.md`: los puentes
comunitarios revisados no conservan directamente las políticas de AIKit.
Se reutiliza la skill actual y el SDK oficial Python; no se crea otro protocolo,
planificador, instalador ni sistema de subagentes.

## Alcance aprobado y decisiones de implementación

- STDIO local y dos herramientas: `opencode_catalog` y `opencode_delegate`.
- Catálogo: `cwd` absoluto, filtro `model` opcional, timeout por proceso.
- Delegación: `cwd` absoluto, `task`, `model` y `reason` obligatorios; `variant`
  opcional, `agent` build/plan y timeout finito de hasta 3600 segundos por proceso.
- La tarea llega como texto en memoria. Extraer una entrada de texto al núcleo
  compartido; conservar `run --task-file` y sus errores/prevalidaciones.
- Reutilizar catálogo, bloqueos, variante, comprobación de destino, errores y
  `fallback: reselect`. El servidor no interpreta qué modelo basta ni reintenta.
- Devolver JSON compacto en contenido y `structuredContent`; `isError=true`
  cuando el núcleo devuelve error. Los fallos inesperados usan mensaje fijo.
- Anotar catálogo como consulta y delegación como posible modificación no
  idempotente. Solo instrucciones de uso del puente, sin competir con Superpowers.
- No bloquear el bucle MCP mientras corre el backend; serializar delegaciones
  del mismo servidor. Mantener stdout exclusivamente para MCP.
- Usar la línea estable 1.x del SDK oficial (`mcp>=1.26,<2`), fijada en uv.lock.
  El runtime de CLI sigue sin dependencias externas; desarrollo instala el SDK
  para ejecutar todas las pruebas MCP, sin omitirlas silenciosamente.

## Límites explícitos

No hay trabajos persistentes, progreso, cancelación activa de inferencia ni API
HTTP en esta versión. Cerrar/cancelar una llamada MCP no garantiza detener el
backend. Los timeouts por proceso solo protegen mientras el servidor siga vivo;
si termina forzosamente, no se garantiza detener los hijos. No reintentar a ciegas.
No hay sandbox, rollback ni modificación de políticas/credenciales de OpenCode.
La suma de procesos puede exceder el timeout individual; el límite del cliente
debe contemplarlo (hasta cuatro procesos más limpieza).

## Validación y conexión

Pruebas de contrato mediante SDK, argumentos inválidos antes de inferencia,
errores estructurados y regresiones CLI. Prueba real STDIO con initialize,
tools/list, catálogo filtrado y rechazo de OpenAI directo, sin inferencia.
Verificar CLI sin importar MCP. Revisión independiente antes de instalación.

Después de las pruebas, actualizar la skill personal con respaldo y hashes y
registrar solo `aikit-opencode` en Codex si no existe. Conservar otros servidores
y ajustes; limitar herramientas y configurar un timeout de cliente suficiente.
No afirmar disponibilidad en este chat hasta que el cliente renueve su catálogo.
