# Validación del complemento AIKit

29 de octubre de 2026. Coordinador: Codex. Windows, cliente Codex 0.153.4,
Python de desarrollo 3.14.9; uv eligió Python 3.13.14 para el runtime instalado,
SDK MCP 1.30.0 y dependencias resueltas con el lock incluido.

## Cobertura y decisiones

Se reutilizaron el núcleo CLI, MCP, política y skill existentes. Superpowers
cubre el proceso de desarrollo y revisión, `skill-installer` skills individuales
y `plugin-management` conexiones. Solo se añadió la exportación del paquete.
No se crearon hooks ni otra skill ni se modificó Superpowers.

Dos intentos de implementación por OpenCode no dieron resultado: MiniMax Go
`high` (de pago) fue detenido tras más de doce minutos sin cambios; GLM gratuito
`high` alcanzó 240 s y el adaptador terminó su árbol. No se demostró falta de
cuota ni se registró coste. Se continuó con Codex conforme al fallback del usuario.

## Esperado y observado

| Comprobación | Esperado | Observado |
| --- | --- | --- |
| Exportación | Solo lista permitida, salida nueva, sin enlaces | Pruebas de exclusión de `.env`, Git, `.aikit`, `.venv`, archivo privado en skill y enlaces de archivo/directorio correctas |
| Esquema MCP | Cliente reconoce servidor y límites | El formato portable rechazó timeouts; salida compatible sin manifiestos portables sí reconoce `aikit-opencode` |
| Perfil limpio | Instalar y arrancar sin `.venv` del checkout | Codex CLI instaló; uv creó entorno en caché; SDK inicializó, listó dos herramientas y bloqueó OpenAI directo sin inferencia |
| Con Superpowers | Ambos instalados, sin cambios a Superpowers | CLI listó ambos habilitados; retirada de AIKit dejó Superpowers instalado |
| Actualización | Renovar fuente e instalar copia nueva | Codex exigió retirar el registro anterior antes de añadir una ruta diferente; actualizado y reinstalado correctamente |
| Retirada | Eliminar solo AIKit y su caché temporal | `plugin remove` quitó la caché comprobada; Superpowers permaneció |
| Migración personal | Respaldo, reemplazo válido y ajustes ajenos intactos | SHA256 de paquete/caché coincidentes; MCP desde caché validado antes de retirar manuales; comparación estructural de configuración correcta |

Antes de implementar se observaron cuatro errores por ausencia del exportador;
tras implementarlo pasaron. La regresión de resolución de manifiesto falló con
`KeyError: mcpServers` y pasó con la salida compatible. Resultado final:
**212 pruebas**, Ruff lint/formato y mypy correctos. Revisión independiente
de lectura sin hallazgos bloqueantes; observaciones documentales y de cobertura
incorporadas.

La CLI de Codex omitió argumentos predeterminados de `node_repl` al escribir
configuración; se detectó y restauró esa pérdida antes de completar la migración.
La copia manual se apartó a `<CODEX_HOME>/backups/aikit/plugin-migration-*/manual-skill`.
El mismo respaldo conserva `config.toml` anterior y el estado previo a retirar
el MCP manual. Las cuentas y permisos de OpenCode no cambiaron.

## Límites de la evidencia

El backend nativo reconoce `aikit@aikit-local`, la skill
`aikit:delegating-to-opencode` y el MCP con `pluginId: aikit@aikit-local`.
No declara aplicaciones registradas ni hooks. El arranque y las dos herramientas
se probaron con el cliente del SDK usando la configuración del paquete instalado.
El inventario nativo aún mostró `tools: {}` para el MCP del plugin: no se afirma
que el chat activo lo haya cargado ni que ya aparezca en una pestaña concreta.
Se debe recargar el cliente y comprobar su catálogo.

La convivencia demostrada es de instalación y descubrimiento; no equivale a una
evaluación completa de todas las combinaciones de workflows de Superpowers.
No se repitió inferencia en el MCP al empaquetar: el núcleo ya tenía una prueba
real previa con Go. Cancelación activa y publicación pública siguen fuera del alcance.
