# Correcciones de la revisión funcional

Este documento describe el comportamiento de la comprobación de restricciones
que `run` aplica antes de iniciar la inferencia en el destino (tarea 2 del plan
`docs/superpowers/plans/2026-10-28-correcciones-revision.md`).

También se retiró `require_selection_reason`: `policy.json` solo admite
`prefer_free` booleano y rechaza opciones desconocidas. El motivo es siempre
obligatorio. La prioridad de modelos sigue siendo una instrucción al coordinador,
sin un selector automático. Los ejemplos de respaldo usan una ruta fuera de las
carpetas habituales de descubrimiento, comprueban colisiones y detienen errores
de copia o movimiento. El empaquetado del complemento sigue pendiente.

## Qué comprueba

Antes de delegar, `run` ejecuta `opencode debug config --standalone` en el
directorio de destino, con el mismo ejecutable, directorio y timeout que usa
para la tarea. Lee la lista de fuentes de configuración que OpenCode devuelve y
exige un **certificado** con estos dos tripletes exactos:

| Acción | Recurso | Efecto |
| --- | --- | --- |
| `provider.use` | `openai` | `deny` |
| `tool.use` | `subagent:*` | `deny` |

Los dos bloqueos pueden estar repartidos entre documentos (por ejemplo, el
global y el del proyecto). No hace falta un archivo local: basta con que la
configuración efectiva del destino contenga ambos.

Se leen `policies` e `experimental.policies` de cada fuente, porque la clave
heredada sigue mezclándose con la actual. Las fuentes `document` con su objeto
`info` y `directory` sin `info` son las únicas conocidas; cualquier otro
formato, una lista vacía o una regla malformada impiden la certificación.

Se distingue la ausencia de una clave de un valor `null`: un `null` en
`policies`, `experimental` o `experimental.policies` invalida el certificado
aunque otra fuente contenga los dos bloqueos, porque la configuración efectiva
no es interpretable.

## Resultado

- `unsafe_configuration`: la configuración efectiva no acredita los dos
  bloqueos, o contiene un `allow` que puede contradecirlos.
- `config_check_failed`: el proceso de comprobación terminó con código distinto
  de cero o devolvió un JSON ilegible.

En ambos casos no se inicia la inferencia. Los mensajes son fijos: no incluyen
salida, errores, rutas ni contenido de la configuración.

`doctor` no cambia: solo consulta versión y catálogo y no exige certificado.

## Límites del certificado

- **Es conservador.** Cualquier `allow` que pueda solaparse con un bloqueo
  invalida el certificado, aunque exista un `deny` posterior o en otro archivo.
  No se reimplementa la precedencia de OpenCode, que depende del origen y del
  orden de lectura. Una configuración segura puede quedar rechazada por un
  `allow` anterior o demasiado amplio.
- **El solapamiento se evalúa con las reglas de OpenCode.** `*` casa cero o más
  caracteres y `?` casa uno sobre el valor entero, y un patrón terminado en
  ` *` también casa el valor sin argumentos, como documenta OpenCode para
  `shell:git push *`. Por eso un `allow` de proveedor con el recurso `openai *`
  invalida el certificado: cubre el proveedor `openai` sin argumentos. Los
  corchetes no son comodines.
- **La disjunción de herramientas es aproximada.** El bloqueo `subagent:*` usa
  un comodín, así que solo se acepta un `allow` de herramienta cuyo prefijo
  literal antes de `:` sea distinto (`shell:*` es disjunto, `subagent:general`
  no). Un patrón con comodines en el prefijo o sin `:` se considera ambiguo y
  se rechaza.
- **Es una fotografía.** La comprobación ocurre una vez, antes de la
  inferencia. No garantiza que la configuración siga igual después: una
  Console conectada, una política remota o una edición concurrente pueden
  cambiar las reglas después de la comprobación (ventana TOCTOU).
- **No es un aislamiento.** El bloqueo de `subagent:*` es una política de la
  herramienta `subagent` de OpenCode. No es un sandbox del sistema operativo:
  el agente conserva las herramientas que las reglas del agente y los permisos
  guardados le permitan, entre ellas `shell` y otros comandos arbitrarios. El
  aislamiento sigue siendo responsabilidad del entorno.

## Fuentes

- Políticas: https://dev.opencode.ai/v2/docs/policies/
- Configuración: https://dev.opencode.ai/v2/docs/config/

## Escenarios observados

El coordinador comprobó la evaluación del certificado con la CLI real
(`opencode debug config --standalone`) y el helper, en directorios temporales:
sin políticas locales el certificado es falso, con los dos `deny` explícitos es
verdadero y con un `allow` contradictorio es falso. Esa comprobación no ejecuta
una inferencia: solo lee la configuración efectiva y evalúa el certificado. La
integración de `run` (orden de las llamadas, rechazo antes de inferir y ausencia
de secretos en la salida) se probó con transporte falso, sin llamadas reales a
OpenCode.

| Entorno | Configuración | Resultado esperado | Resultado observado |
| --- | --- | --- | --- |
| Windows, directorios temporales, CLI real | sin políticas locales | certificado rechazado | certificado `false` |
| Windows, directorios temporales, CLI real | `opencode.json` del directorio con los dos `deny` | certificado válido | certificado `true` |
| Windows, directorios temporales, CLI real | los dos `deny` más un `allow` de `openai` | certificado rechazado | certificado `false` |
| Pruebas con transporte falso | fuentes malformadas, tipo de fuente no textual, `null` en políticas, JSON inválido o proceso con error | rechazo antes de ejecutar | `config_check_failed` o `unsafe_configuration`, sin llamadas `run` |

## Cierre de la revisión — 28 de octubre de 2026

- La implementación se delegó a `opencode-go/minimax-m3.1-flash`, usando `high`
  para la comprobación y `medium` para corregir los hallazgos concretos. Ambas
  llamadas devolvieron `status: ok`; la de `medium` atravesó el nuevo guard.
  OpenCode informó coste `0.0`, que no acredita una tarifa ni facturación futura.
- Se conservaron once fallos de regresión antes de las correcciones de comodines,
  tipos inesperados y valores nulos; después la verificación de Codex confirmó
  **161 pruebas**, Ruff lint/formato, mypy sobre doce archivos y validador de skill.
- La revisión independiente final no encontró hallazgos materiales pendientes.
- La copia personal se actualizó con respaldo fuera de las rutas habituales,
  cuatro hashes coincidentes y `doctor` correcto mostrando el modelo Go.
- El certificado puede rechazar configuraciones seguras por su conservadurismo.
  No aporta sandbox, rollback, presupuesto global de tiempo ni selección automática.
