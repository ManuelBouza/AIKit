# Evaluación: MCP para delegar a OpenCode

Fecha: 28 de octubre de 2026. Base evaluada: `b110f47`. Alcance: investigación
documental y revisión estática; no se instaló ni ejecutó código comunitario,
no se hicieron inferencias y no se modificaron las configuraciones existentes.

## Conclusión

MCP encaja como interfaz de herramientas para Codex y para el futuro complemento
AIKit. Recomiendo evaluarlo mediante un prototipo sobre el núcleo actual, sin
retirar inicialmente la CLI ni duplicar sus controles. Sustituir también el
transporte hacia OpenCode por HTTP requiere otra validación.

La primera búsqueda en el catálogo conectado de plugins no devolvió resultados
para OpenCode. Eso no demuestra inexistencia: se encontraron varios servidores
comunitarios en GitHub. Las skills instaladas ya cubren creación, instalación,
planificación y revisión; ninguna de las consultadas aporta este puente local
con las políticas específicas de AIKit. No se propone crear otra skill general.

## Qué cambia realmente

Hoy: `Codex → shell/Python → CLI OpenCode → proveedor seleccionado`.

Con MCP conservando el backend: `Codex → herramienta MCP → núcleo AIKit → CLI
OpenCode → proveedor`. Desaparecería la necesidad de construir comandos desde
Codex, pero seguirían existiendo los procesos de CLI y sus límites.

Con una migración completa: `Codex → MCP → API HTTP local OpenCode → proveedor`.
Esto podría reutilizar un servidor persistente, a cambio de gestionar su arranque,
autenticación, sesiones, disponibilidad y cancelación. No se ha medido su mejora
de latencia ni de consumo en este entorno.

| Aspecto | CLI actual | MCP sobre núcleo actual | MCP sobre HTTP |
| --- | --- | --- | --- |
| Invocación desde Codex | Comando y archivo de tarea | Parámetros estructurados | Parámetros estructurados |
| Políticas AIKit | Implementadas y probadas | Reutilizables si se llama al mismo núcleo | Hay que conservarlas y verificar equivalencia |
| Procesos por consulta/tarea | Varias llamadas CLI | Inicialmente iguales | Potencialmente menos arranques con servidor persistente |
| Sesiones y progreso | Resumen al terminar | No mejoran automáticamente | API ofrece sesiones y eventos; el MCP debe gestionarlos |
| Dependencias | Runtime de biblioteca estándar | Añade servidor/SDK MCP | Añade además cliente y ciclo de vida HTTP |
| Convivencia con Superpowers | Conserva roles nativos | Puede conservarlos | Puede conservarlos; depende del puente |

MCP no cambia por sí mismo la cuenta facturada, la calidad del modelo ni la cuota
gratuita. El ahorro sigue dependiendo del proveedor y de la selección por tarea.

## Candidatos revisados

Las revisiones se identifican por commit. Se revisaron archivos pertinentes,
no todo el código ni sus dependencias; no equivalen a una auditoría de confianza.

| Candidato | Evidencia y ajuste a AIKit |
| --- | --- |
| [mryesiller/opencode-delegate-mcp](https://github.com/mryesiller/opencode-delegate-mcp/tree/52440fd2277858bf1c066daa4bdee02ea596f92e) | Su `src/backend.ts` construye `--dir` y `--variant`. La ayuda local de v2.2.0 usa directorio del proceso y `provider/model#variante`. No es sustitución directa. |
| [edulelis/opencode-mcp](https://github.com/edulelis/opencode-mcp/tree/bfb8114521219ddc7f7ab4f85af4c2dcfb5ba9e5) | Tiene trabajos consultables y cancelación. `src/index.mjs` envía a `/session/.../prompt_async` o `/session/.../message`, frente a las rutas `/api/session/...` documentadas para v2. Su resolución por nombres y herramientas dinámicas también exigiría acotar el contrato. |
| [AlaeddineMessadi/opencode-mcp](https://github.com/AlaeddineMessadi/opencode-mcp/tree/6f1f62fd6c151377e09f4fe95bed58eb48c6196b) | Ofrece una superficie amplia y trabajos asíncronos. `package.json` depende de `@opencode-ai/sdk ^1.18.31`; `src/client.ts` lo importa. No se acreditó equivalencia con la API v2.2 instalada ni con las restricciones AIKit. |
| [dmdboi/opencode-mcp](https://github.com/dmdboi/opencode-mcp/tree/942b9a1232bc124330b6aa914de0807becaf3545) | Tiene `fire/check/reply`, pero `src/api.ts` mezcla `/session`, `/session/.../message` y `/api/session/.../wait`. Usa modelo predeterminado y el contrato revisado no exige variante. Requiere adaptación y pruebas. |
| [MuhamadBarzani/forge-delegate](https://github.com/MuhamadBarzani/forge-delegate/tree/0161a7adf76c50e417e0bb179223defb9cea7dbb) | Es el más cercano a la CLI v2: usa `cwd` y modelo con `#variante`. Sigue lanzando la CLI; no elimina ese transporte. Sus valores e instrucciones actuales chocan con decisiones explícitas de AIKit. |

### Diferencias concretas de forge-delegate

En [lib.mjs](https://github.com/MuhamadBarzani/forge-delegate/blob/0161a7adf76c50e417e0bb179223defb9cea7dbb/lib.mjs):

- `autoApprove` vale `true` inicialmente y añade `--auto`.
- `pickVariant` elige una opción del catálogo sin analizar la tarea.
- `parseEvents` recoge texto y tokens, pero no clasifica eventos de error como
  AIKit. `opencodeRun` admite salida no vacía incluso con terminación no cero.
- Lanza `opencode` por nombre y mata el proceso con señales; no se acreditó la
  resolución de ejecutable nativo ni la cancelación del árbol en nuestro Windows.

En [server.mjs](https://github.com/MuhamadBarzani/forge-delegate/blob/0161a7adf76c50e417e0bb179223defb9cea7dbb/server.mjs), las instrucciones MCP recomiendan omitir
modelo y usar el predeterminado, delegar cualquier trabajo sobre archivos y
dividir la tarea antes de subir a un modelo más capaz. También expone llamadas
directas a proveedores. Adoptarlo sin cambios introduciría otra política de
coordinación y no conservaría por sí solo el bloqueo de OpenAI directo.

Puede servir de referencia, pero adaptarlo no es automáticamente más pequeño ni
más fiable que exponer el núcleo actual. Esa comparación necesita un prototipo.

## Integración que merece probarse

1. Una interfaz MCP local por STDIO, con catálogo y ejecución explícita. Mantener
   modelo, variante, motivo y directorio como parámetros; validar en el servidor,
   no confiar solo en la descripción de la herramienta.
2. Reutilizar las funciones actuales de catálogo, selección válida, bloqueo de
   proveedor, comprobación del destino y clasificación de errores. Conservar la
   CLI como herramienta de diagnóstico y alternativa operativa.
3. Acotar las instrucciones MCP al uso del puente. Mantener la skill existente
   para la selección por tarea y no incorporar otro planificador, revisor ni
   sistema de subagentes.
4. Para trabajos largos, comparar llamada síncrona con límite suficiente frente
   a un contrato explícito de iniciar/consultar/cancelar. Los trabajos asíncronos
   necesitan estado y pruebas propias; no vienen resueltos por añadir MCP.
5. Considerar después el backend HTTP, manteniendo la misma interfaz y las mismas
   pruebas de aceptación. Una respuesta perdida tras enviar un prompt no debe
   provocar reenvío ciego y ejecución duplicada.

Codex admite STDIO y Streamable HTTP, filtrado de herramientas y configuración
de tiempos. Su documentación indica un límite predeterminado de 60 segundos por
herramienta: no basta para nuestras tareas de varios minutos. Además, una
notificación MCP de cancelación no demuestra que el backend haya detenido la
ejecución: debe conectarse y comprobarse explícitamente.

## Criterios para aprobar una migración

- Descubrimiento e invocación desde Codex y un subagente autorizado, sin
  sustituir los roles de Superpowers.
- Igualdad de resultados y errores respecto al backend actual: OpenAI directo,
  GPT de Go, variantes inexistentes, cuota gratuita y configuración contradictoria.
- Windows: ruta y caracteres especiales, arranque, timeout, cancelación y ausencia
  de procesos huérfanos tras cierre del cliente.
- Tareas largas y fallos de conexión sin duplicar trabajo; cambios parciales
  visibles y conservados para revisión.
- Catálogo y resultados compactos, sin secretos ni transcripciones completas.
- Medición del tiempo, llamadas, contexto y cuota frente a la CLI; no asumir ahorro.

## Fuentes de plataforma

- [MCP en Codex: transportes, políticas y límites](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).
- [API OpenCode v2: modelos, sesiones, prompts e interrupción](https://dev.opencode.ai/v2/docs/api).
- [MCP en OpenCode](https://dev.opencode.ai/v2/docs/mcp-servers/): documenta que
  OpenCode consume servidores MCP; no prueba que publique un servidor oficial
  para delegarle tareas desde Codex.
- [Cancelación MCP](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/cancellation).

La recomendación es una conclusión de esta evaluación, no una migración aprobada
ni una compatibilidad de terceros ya verificada en ejecución.

Actualización del 29 de octubre de 2026: tras la aprobación se implementó el
[MCP local sobre la CLI](mcp-opencode.md), reutilizando el núcleo de AIKit y el
SDK oficial. Allí se documentan la validación observada y los límites actuales.
