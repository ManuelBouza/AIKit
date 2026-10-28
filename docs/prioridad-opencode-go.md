# Prioridad de ejecución con OpenCode Go

Nota de actualización: los escenarios de este documento conservan la validación
inicial. Después se verificaron ejecuciones de MiniMax Flash en Go con variantes
`high` y `medium`; véase [correcciones de revisión](correcciones-revision-funcional.md).
El rechazo regional de DeepSeek no demuestra indisponibilidad de todos los modelos Go.

## Alcance y cobertura

La skill existente `delegating-to-opencode` ya consulta modelos conectados,
valida variantes y devuelve errores al coordinador. Se amplía su preferencia de
selección; no se crea otra skill, MCP, instalador ni sistema de subagentes.
Superpowers conserva planificación, roles y revisiones.

Primero determina las capacidades y el esfuerzo que necesita la tarea. Entre
opciones suficientes, prioriza gratuitos de OpenCode, incluidos los gratuitos
servidos por Go; después OpenCode Go. Otros proveedores conectados siguen
permitidos como alternativas adecuadas. Si no queda una opción adecuada
disponible en OpenCode, continúa normalmente en Codex sin pedir confirmación.
El proveedor directo `openai` permanece bloqueado, no los GPT servidos por Go.

## Señal y responsabilidades

Un evento estructurado `provider.free-limit` devuelve `free_limit_reached` con
`fallback: reselect`. Sustituye la señal anterior `fallback: codex`, que omitía
Go. Los consumidores de esa salida deben actualizar su interpretación.

El coordinador decide el siguiente intento y registra modelo, variante y motivo;
el adaptador no reintenta ni cambia proveedor automáticamente. Revisa cambios
parciales antes de reintentar. Un catálogo habilitado no acredita cuota de
inferencia; un error aislado tampoco acredita agotamiento de todo OpenCode.
Las restricciones de privacidad, autenticación y permisos deben respetarse.

## Escenarios y evidencia — 28 de octubre de 2026

Entorno: Windows, repositorio AIKit, OpenCode v2 y entorno `.venv` gestionado con
uv. Las consultas y ejecuciones reales necesitaron acceso fuera del sandbox de
Codex; su primer rechazo local no se interpretó como indisponibilidad del servicio.

| Escenario | Esperado | Observado |
| --- | --- | --- |
| Catálogo real con Go conectado | Modelos Go y variantes visibles; excluir `openai` directo | `doctor` devolvió 74 modelos permitidos, incluidos Go y variantes. |
| Ejecución gratuita con DeepSeek Flash `high` | Ejecutar o informar cuota real | `free_limit_reached`; no se implementaron cambios. |
| Delegación a DeepSeek Flash Go `high` | Ejecutar tras el rechazo gratuito | OpenCode terminó con código 1, sin modificar archivos. |
| Prueba mínima Go sin variante ni herramientas | Identificar el rechazo | `provider.invalid-request`, estado 400: el modelo exige región Global en Privacy. No se cambió esa preferencia. |
| Transporte falso: evento de cuota con códigos 0, 1 y 7 | Pedir nueva selección, sin filtrar secretos ni reintentar | Las tres variantes pasan con `fallback: reselect`. |
| Transporte falso: mezcla de precios y proveedores | Gratuitos, después Go, después otros; conservar catálogo abierto | Prueba de orden pasa; `openai` directo sigue excluido. |

Se observaron cuatro fallos de pruebas antes del cambio de producción: tres por
la señal anterior y uno por el orden del catálogo. Después, la suite completa
pasó: 88 pruebas, Ruff lint y formato, y mypy sobre diez archivos.

La implementación de esta actualización se completó en Codex tras esos rechazos.
No se ha validado una inferencia Go exitosa ni se han probado todos sus modelos.
Los registros de diagnóstico permanecen en `.aikit/`, ignorado por Git.
