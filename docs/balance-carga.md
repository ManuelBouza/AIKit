# Balance de carga AIKit/OpenCode

Evidencia sanitizada del cambio autorizado "OpenCode como ejecutor habitual".

## Cobertura

Superpowers ya cubre planificación, pruebas y revisiones; skill-creator cubre
edición de skills. La brecha es la activación de exploración técnica y el
reparto de trabajo externalizable: no se crea una nueva skill.

Superpowers using-superpowers, brainstorming, writing-plans, writing-skills y
test-driven-development; skill-creator; skill actual y docs/principios-aikit.md.

## Baseline

Evaluador independiente leyendo solo la SKILL anterior eligió, en escenario de
bug desconocido, exploración inicial con Codex hasta identificar objetivo y
alcance acotados, porque la skill solo hablaba de implementación/transformación.
En otros escenarios ya eligió OpenCode para corregir fallos, CLI para tareas
largas y Go tras cuota free. Es una decisión en seco, no ejecución real ni
ahorro de tokens.

## Diseño

OpenCode ejecuta por defecto trabajo externalizable autorizado: exploración
técnica/diagnóstico, propuesta técnica dentro del alcance acordado,
implementación + pruebas/lint/tipos + correcciones/documentación. Codex conserva
comprensión de la petición, exploración mínima para seguridad/skills/alcance,
decisiones del usuario y selección, roles nativos/Superpowers, revisión
independiente del diff y verificación final con comandos.

## Plan breve

1. Actualizar activación y contrato de ejecución.
2. Probar escenarios de selección.
3. Revisión y comandos de verificación.

## Límites

La instalación no garantiza activación global ni ejecución real. No se prometen
jobs, cancelación ni hooks.

## Verificación del 29 de octubre de 2026

Entorno: Windows, Python 3.14.9, OpenCode 2.2.0 y complemento 0.1.2.
Esperado: delegar también el diagnóstico inicial y las correcciones pequeñas,
conservar revisión independiente y no confundir timeout o cuota de un modelo
con indisponibilidad de todos los proveedores.

Observado: un evaluador independiente tomó las cinco decisiones esperadas
con la skill modificada: diagnóstico en Free, correcciones en OpenCode,
CLI para cinco minutos, Go tras cuota Free y Codex sin opciones adecuadas.
Una revisión posterior mantuvo la delegación bajo presión de tiempo y tres
rondas previas. Son simulaciones limitadas; no garantizan activación global
ni permiten calcular ahorro de tokens.

Implementación real: dos llamadas CLI a `opencode/beam-free#medium`, ambas
con resultado `ok` y coste informado 0.0. La primera entrega necesitó
correcciones, que también hizo OpenCode. Codex coordinó, revisó y verificó;
no hubo retorno nativo para implementar. Se cuenta una tarea con dos intentos.

Verificación final independiente: `scripts/verificar.ps1` pasó sincronización
con lock, 215 pruebas, Ruff, formato y mypy; el validador de la skill y
`git diff --check` también pasaron. Las pruebas de exportación comprueban que
el contrato de carga se distribuye dentro del complemento.

En el registro de coordinación se distingue result/backend_status (ok/error) de
review (accepted/needs_corrections); el éxito de ejecución no equivale a calidad.

## Prueba real desde un subagente nativo

El 29 de octubre de 2026 se comprobó el recorrido coordinador Codex →
subagente nativo `opencode_e2e_worker` → OpenCode → revisión del subagente →
verificación independiente del coordinador. Se usó la skill instalada de AIKit
0.1.2, Windows y OpenCode 2.2.0, en un directorio ignorado y con datos ficticios.

El subagente consultó el catálogo y eligió
`opencode/deepseek-v4.1-flash-free#low`, gratuito según tarifas publicadas,
para agregar un CSV a JSON. No encontró MCP tras una espera de seis segundos
y ejecutó él mismo la CLI instalada, con un intento y timeout de 120 s por
proceso. El coordinador anunció la selección antes de autorizar la inferencia.

Esperado: que OpenCode creara el archivo, sin implementación nativa, y que
ambos niveles de revisión comprobaran sus valores y la integridad de entradas.
Observado: backend `ok`, código 0, coste informado 0.0 y sesión
`ses_e7691deb2ffegL2bBT2q3ub72T`. El JSON inexistente al inicio quedó creado
con seis filas agregadas, nueve unidades y 1130 céntimos. Subagente y
coordinador recalcularon y verificaron el resultado; los hashes de entradas y
configuración permanecieron intactos, sin cambios inesperados en Git ni en
el inventario local comprobado. No se necesitó reintentar ni corregir el JSON.

Las evidencias locales están en
`.aikit/subagent-e2e-8ae6895ee2f3416d922a15f98b027307/`:
`delegate-result.json`, `summary.json` y `verification.json`. La comprobación
del coordinador está en `.aikit/subagent-e2e-coordinator-verification.json`.
Son archivos ignorados; este apartado conserva la evidencia sanitizada.

Esta prueba acredita una delegación real por CLI desde un subagente con la
skill indicada explícitamente. No acredita descubrimiento implícito en todos
los subagentes, MCP desde subagentes, funcionamiento de todos los roles de
Superpowers ni aislamiento del sistema operativo.
