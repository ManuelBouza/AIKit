# Validación de la delegación a OpenCode

Fecha: 2026-10-28. Entorno real: Windows, Python 3.14.9 y OpenCode v2.2.0. Codex Desktop coordinó y verificó; la implementación y sus correcciones se delegaron a modelos gratuitos de OpenCode.

## Control sin skill

Modelo: `opencode/mimo-v2.6-flash-free`; agente `plan`; modo standalone. Sesión: `ses_e7d954a1effeOFVEu1wZRebnHS`.

Ante un caso de delegación conservando la cuota OpenAI, propuso `opencode run -m anthropic/claude-sonnet-4-5 --effort high` y una alternativa de pago ante fallos. Resultado: escenario fallido por argumento inexistente y selección fuera del catálogo gratuito permitido.

## Implementación externa

El primer intento con Mimo, sesión `ses_e7d92ffd8ffefI3f1k6koIgTRI`, perdió la conexión antes de crear archivos. Se canceló su proceso concreto y su servidor privado. Después de comprobar la ausencia de cambios de implementación, el coordinador eligió DeepSeek gratuito explícitamente.

DeepSeek implementó adaptador, pruebas y documentación en la sesión `ses_e7d8f188cffeiKI53f0URdMIDP`. Los eventos de esa ejecución informaron coste total `0` y 14.431 tokens de salida. Son cifras informadas por OpenCode; no miden ahorro de cuota de Codex ni garantizan precios futuros. Las correcciones se ejecutaron también con `opencode/deepseek-v4.1-flash-free`.

## Comprobaciones de Codex

- Suite final: **53 pruebas superadas**, ejecutadas por Codex con `python -m unittest discover -s tests -v` y `TEMP`/`TMP` locales en `.aikit/tmp`. El primer intento en el sandbox falló por permisos sobre su carpeta temporal; usar la carpeta local permitió ejecutar toda la suite.
- Pruebas escritas antes de implementar. La ejecución inicial falló por ausencia del módulo; las rondas de corrección registraron fallos de regresión antes de los cambios. Se retiraron las pruebas que solo buscaban texto en documentos.
- Revisor independiente de Codex: detectó la regla incompleta `subagent` y la posible ejecución de shims Windows sin ejecutable nativo. Ambos hallazgos se corrigieron con regresiones.
- La CLI v2 puede interpretar `--auto` como opción incluso tras `--`. Se añadió un prefijo fijo al argumento de tarea, conservando íntegro su contenido literal; comprobado con modelo inexistente, sin inferencia.
- JSON ASCII seguro: prueba de subprocess con `PYTHONIOENCODING=cp1252`, conservando acentos al decodificar el JSON.
- `quick_validate.py`: **Skill is valid!**
- Timeout real: un proceso Python y su hijo se iniciaron en `.aikit/timeout-real`; el adaptador los terminó y el hijo no alcanzó a escribir su archivo posterior.

## Comportamiento con skill

Mismo modelo gratuito que el control, sesión `ses_e7d84427fffex9hRwJ5Ox24D4t`. Con la skill como referencia, propuso el adaptador instalado y un modelo permitido, omitió esfuerzos inventados y rechazó la alternativa automática de pago. También indicó revisar cambios parciales antes de repetir. Resultado: escenario superado. Es una evaluación individual, no estadística. En esa respuesta no se informó coste: el adaptador devolvió `null`.

## Instalación y prueba final

Instalada en `C:/Users/Manuel/.codex/skills/delegating-to-opencode/`, sin sobrescribir otra instalación. Fuente versionada: `skills/delegating-to-opencode/`. Se compararon los SHA-256 de los archivos de código, política e instrucciones.

`doctor` de la copia instalada reconoció v2.2.0, nueve modelos del proveedor `opencode`, los tres modelos permitidos y una política de proyecto válida. Ningún modelo `openai/*` apareció en el catálogo. Un intento explícito de usar OpenAI fue rechazado antes de iniciar inferencia.

La copia instalada ejecutó una tarea real con `opencode/deepseek-v4.1-flash-free`: creó `.aikit/smoke-final/verificado.txt` con `VALIDACION_OK`. Codex comprobó el archivo. Sesión: `ses_e7d7fa142ffefqQt4p5qVh3O15`; coste informado `0`; resumen en español con acentos conservados.

## Límites

No se ha probado OpenCode en Unix ni se han verificado variantes de razonamiento mediante inferencia. Los modelos gratuitos pueden cambiar o agotar capacidad. El adaptador hace un solo lanzamiento; la CLI puede reintentar internamente dentro del timeout. La configuración protege este proyecto y debe replicarse en otro destino; no sustituye un sandbox ni modifica las credenciales guardadas. La activación automática de la skill en una nueva conversación depende de su descubrimiento por Codex; aquí se verificaron los archivos instalados y su ejecución directa.
