# Investigación: delegación de Codex a OpenCode

Fecha: 2026-10-28. Estado: investigación terminada; integración pendiente de elegir e implementar.

## Objetivo

Reservar la cuota de OpenAI utilizada por Codex para coordinación, decisiones y verificación. Delegar las tareas de ejecución a OpenCode, priorizando sus modelos gratuitos. Usar OpenCode no implica por sí solo consumir una cuenta diferente: el proveedor seleccionado determina dónde se procesa el trabajo.

## Evidencia local

- OpenCode instalado mediante npm y accesible desde PowerShell; versión `v2.2.0`.
- `opencode auth list` muestra únicamente una integración guardada: OpenAI. No se han leído ni exportado secretos. No se ha comprobado si corresponde a la misma cuenta usada en Codex.
- `opencode models` muestra modelos OpenAI y modelos del proveedor `opencode`, incluidos `deepseek-v4.1-flash-free`, `glm-5.3-flash-free`, `mimo-v2.6-flash-free`, `nemotron-3-ultra-free`, `nemotron-3.5-lightning-free`, `nemotron-3.5-super-vl-free`, `flint-40b-free` y `beam-free`.
- Estar en el catálogo no demuestra que un modelo responda, su rendimiento ni su cuota disponible. No se han enviado prompts ni realizado pruebas de inferencia.
- La ayuda local de `run` admite `--model proveedor/modelo#variante`, `--agent`, `--format json`, `--file`, `--session` y `--standalone`. No anuncia `--dir` ni `--variant`.
- El catálogo de plugins consultado no devolvió resultados para OpenCode; la búsqueda no demuestra que no existan otras integraciones.

## Integraciones encontradas

### opencode-delegate-mcp

Repositorio comunitario: <https://github.com/mryesiller/opencode-delegate-mcp>.

Expone herramientas de delegación y usa `opencode run`. El backend revisado construye argumentos con `--dir` y `--variant`. Esto no coincide con la ayuda local de v2.2.0; requiere adaptación o pruebas antes de adoptarlo. La revisión fue estática y parcial; no constituye una auditoría de seguridad ni de sus dependencias.

Código revisado: <https://github.com/mryesiller/opencode-delegate-mcp/blob/main/src/backend.ts>.

### mcp-opencode / mcp-orchestrate

Repositorio comunitario: <https://github.com/shreeraman96/mcp-coding-agents>.

Ofrece modelo explícito, límites, colas por directorio y tratamiento de errores. El backend consultado también construye argumentos con `--dir` y `--variant`. El router añade varios ejecutores y rutas alternativas que deben limitarse para evitar recurrir a Codex u OpenAI. No se ha validado su funcionamiento en Windows ni con v2.2.0.

Código revisado: <https://github.com/shreeraman96/mcp-coding-agents/blob/main/packages/core/src/backends/opencode.ts>.

## Conclusión y alternativas

Existen MCP comunitarios para este objetivo. La investigación no permite calificarlos como integraciones oficiales, auditadas o verificadas en este entorno. No se han instalado.

1. **Skill propia con un adaptador pequeño a la CLI oficial (recomendada):** menos dependencias y adaptación directa a Windows/v2.2.0. La política de delegación se conserva en este repositorio y se instala en otros equipos.
2. **Adaptar y fijar una revisión de un MCP comunitario:** ofrece herramientas MCP, pero exige revisar sus dependencias, corregir la compatibilidad y probar instalación y cancelación en Windows.
3. **MCP propio:** interfaz estructurada y reutilizable entre clientes; mayor implementación y mantenimiento para el mismo ejecutor.

## Criterios propuestos para implementar

- Codex coordina y verifica los resultados; OpenCode realiza el trabajo delegado.
- Selección explícita de proveedor y modelo en cada ejecución; no depender del modelo predeterminado.
- Empezar con una lista permitida de modelos gratuitos comprobados. No deducir gratuidad únicamente por el nombre ni prometer disponibilidad permanente.
- No usar `openai/*` para la ejecución delegada ni recurrir automáticamente a modelos de pago. Las cuentas adicionales y sus presupuestos deben configurarse expresamente.
- No equiparar los esfuerzos de Codex con variantes de otros modelos: comprobar las variantes disponibles antes de seleccionarlas.
- Tareas acotadas, salida resumida, tiempos máximos y reintentos limitados. No volver a ejecutar a ciegas una tarea que ya haya modificado archivos.
- Revisar cambios y ejecutar comprobaciones locales desde Codex antes de aceptar el resultado.
- Mantener las credenciales en OpenCode. No incorporarlas a Git, archivos de tareas o informes.
- Una carpeta de trabajo o worktree no constituye por sí sola un aislamiento de seguridad. Los permisos del ejecutor deben revisarse y probarse.
- Una integración vía CLI/MCP no convierte automáticamente las llamadas nativas de subagentes de Superpowers en llamadas a OpenCode: hace falta una instrucción explícita de enrutamiento.

## Fuentes oficiales

- CLI v2, ejecución no interactiva y salida JSON: <https://opencode.ai/v2/docs/cli/commands/>.
- Selección explícita de modelos, variantes y catálogo: <https://opencode.ai/v2/docs/models/>.
- Modelos de Console y condiciones de acceso desde otros clientes: <https://opencode.ai/v2/docs/console/models/>.
- Arquitectura HTTP de OpenCode (documentación v1; no asumir compatibilidad v2): <https://opencode.ai/docs/server/>.
- MCP en OpenCode añade herramientas a OpenCode; no demuestra que exponga un servidor MCP oficial de delegación: <https://opencode.ai/docs/mcp-servers/>.

Las páginas y ramas `main` pueden cambiar. Antes de instalar código de terceros, fijar una revisión y revisar de nuevo su contenido.
