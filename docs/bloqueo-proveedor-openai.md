# Bloqueo de la cuenta directa OpenAI

Requisito vigente de Manuel (2026-10-28): la integración directa `openai` en OpenCode usa su misma cuenta de Codex y se excluye de la ejecución delegada. Codex conserva esa cuenta para orquestación y verificación.

El criterio es el identificador del proveedor de conexión, no el fabricante, nombre o familia del modelo. Por ejemplo, `openai/gpt-…` se bloquea; `opencode/gpt-…`, `opencode-go/gpt-…` y un GPT servido por otro proveedor habilitado siguen permitidos, gratuitos o de pago. No se bloquea por contener «GPT» u «OpenAI» en el nombre ni por metadatos de fabricante.

El adaptador debe rechazar el proveedor directo antes de iniciar procesos, incluso en directorios sin configuración local. Su catálogo de selección debe excluir esas entradas. La política de este proyecto añade además una denegación exacta `provider.use openai`; no se borran credenciales ni se cambian los modelos nativos de Codex.

Validación requerida: rechazo previo a subprocess para OpenAI directo, incluidas variantes; proveedores alternativos que ofrecen GPT aceptados por pruebas de transporte; catálogo mixto filtrado sin deshabilitar alternativas. Mantener selección de modelo/esfuerzo por tarea, preferencia gratuita, tarifas saneadas, roles de Superpowers y el resto de garantías del adaptador.

Este requisito sustituye únicamente la admisión de `openai/*` que se había permitido en la ampliación anterior del catálogo; conserva todos los demás proveedores conectados.

## Resultado verificado

- Código implementado por un worker gratuito de OpenCode con variante `low`; Codex revisó el diff y ejecutó la suite completa: **52 pruebas superadas**.
- Se verificó rechazo previo a subprocess para `openai/*`, variantes y diferencias de mayúsculas; catálogo mixto filtrado por proveedor; modelos GPT con `canonical: openai` y proveedores `opencode`, `opencode-go` y `openrouter` conservados en pruebas. No se hicieron llamadas a esos proveedores de pago.
- `opencode models --standalone` en el proyecto dejó visibles ocho modelos del proveedor `opencode` y ninguna entrada `openai/*` tras añadir la política exacta.
- El validador devuelve `Skill is valid!`. La copia personal actualizada coincide por hash con la fuente. Una llamada real al adaptador instalado con `openai/gpt-6.1-sol#high` devolvió `provider_not_allowed` sin necesitar inferencia.
- El primer worker aplicó código, tests, SKILL y README, pero terminó con error de OpenCode. Tras revisar los cambios parciales, un intento documental acotado también falló. Las últimas instrucciones de coordinación en AGENTS se completaron desde Codex; la implementación del adaptador procede del worker y fue verificada independientemente.

No se han borrado credenciales, desconectado cuentas ni modificado la configuración o modelos nativos de Codex. El bloqueo de la skill funciona en cualquier directorio; la política adicional de OpenCode se limita a este proyecto. El comportamiento de ejecución de otros proveedores se valida con pruebas simuladas, sin afirmar conexiones o llamadas de pago inexistentes.
