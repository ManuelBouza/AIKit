# Migración de pruebas a pytest y uv

Requisito de Manuel (2026-10-28): mejorar la suite que ha concentrado casi mil líneas en `test_delegate.py`, crear `.venv`, gestionar el entorno con `uv`, usar `pytest`, Ruff y Python tipado.

## Diseño de la mejora

- Configuración central en `pyproject.toml`, dependencias de desarrollo `pytest`, `ruff` y `mypy`; `uv.lock` versionado. `.venv` y cachés quedan fuera de Git. Sin dependencias nuevas en el adaptador distribuido.
- Fixtures pytest (`tmp_path`, `monkeypatch`, `capsys`) y parametrización para expresar variantes de un mismo comportamiento. Compartir solo constructores de datos y el transporte externo falso, con anotaciones y estructuras pequeñas.
- Módulos por comportamiento: selección de modelo/proveedor, metadatos del catálogo, ejecución y errores, interfaz CLI, procesos/Windows/timeouts. No trasladar el monolito a un helper de tamaño equivalente.
- Importación normal del adaptador mediante configuración de rutas de pytest/mypy, evitando cargadores dinámicos repetidos. Usar tipos concretos para fixtures, parámetros, retornos y registros de llamadas. Reservar tipos dinámicos para límites JSON reales.
- Preservar los escenarios que cubren las 52 pruebas actuales, incluidos sus subcasos: bloqueo exacto OpenAI, GPT por otras cuentas, variantes, tarifas por niveles/caché, privacidad, errores de eventos, salida ASCII, tiempo máximo, ejecutables Windows y argumentos literales.
- Ruff comprueba y formatea todo el Python mantenido. Mypy comprueba tipado del adaptador y las pruebas sin exclusiones generales para silenciar errores. Cambios productivos solo de formato/tipado necesarios; no cambiar la semántica de delegación.

## Criterios de aceptación

Entorno `.venv` creado con uv y dependencias reproducibles; `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .` y `uv run mypy` satisfactorios. Pruebas sin red ni inferencia real, módulos legibles y reducción de duplicación. README y AGENTS documentan los comandos vigentes. La versión anterior pasó 52 pruebas en la comprobación inicial guardada localmente.

La implementación se delega a OpenCode; Codex revisa equivalencia de escenarios y repite los controles. Si hay cambios de formato/tipado en el adaptador, se sincroniza la skill personal tras verificarlos.

## Retorno a Codex autorizado

Durante la migración OpenCode devolvió `provider.free-limit` al probar DeepSeek gratuito. Un segundo intento con GLM tampoco ejecutó la migración. Manuel autorizó entonces una regla permanente: si OpenCode agota el uso gratuito, informar y continuar normalmente con Codex y sus subagentes nativos, sin otra confirmación. La implementación se completó de esa forma.

El adaptador reconoce exclusivamente la señal estructurada y devuelve `free_limit_reached` con `fallback: codex`, incluso si el proceso termina con código distinto de cero. No lanza otra CLI ni habilita `openai/*` en OpenCode. Errores de permisos o autenticación y texto que simplemente mencione la señal no activan esta autorización.

## Resultado verificado

- `.venv` creada con uv y Python 3.14.9. Pytest 9.2.0, Ruff 0.17.3 y mypy 2.4.0 son dependencias de desarrollo; `uv.lock` se resuelve desde PyPI y `uv sync --locked` reproduce el entorno. No hay dependencias externas de ejecución para la skill.
- El monolito de 995 líneas se sustituyó por cinco módulos de comportamiento (selección, catálogo, ejecución, CLI y política/procesos), más un módulo específico del retorno a Codex. El archivo mayor tiene 241 líneas. Fixtures, constructores y transporte están tipados y compartidos; las tarifas reales de la API se integraron en la tabla de casos del catálogo.
- Se reconciliaron los escenarios de los 52 métodos originales, incluidos sus subcasos. La suite final contiene **87 casos pytest** tras parametrización y pruebas del nuevo retorno. El aumento del conteo no representa un porcentaje de cobertura; un revisor independiente confirmó que no se perdieron escenarios relevantes.
- Pasan `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .` y `uv run mypy`. Mypy también acepta el adaptador con `--platform linux`; esto es verificación estática, no una ejecución real en Unix.
- Los cambios de tipado productivo concretan valores JSON y condiciones de plataforma; se mantuvieron los contratos. El nuevo retorno pasó de tres regresiones fallidas a ocho casos positivos y negativos satisfactorios. También se reconoció la señal real capturada de OpenCode, sin repetir inferencia.
- La copia personal de la skill coincide por hash con la fuente actualizada. Se comprobó que una llamada directa a `openai/*` sigue siendo rechazada. `.venv`, temporales y cachés están ignorados por Git.

No se introduce inferencia ni acceso a red en los tests. La preparación del entorno sí descargó las herramientas de desarrollo solicitadas. Los históricos anteriores conservan los comandos y decisiones de su momento; README, AGENTS y `pyproject.toml` describen el flujo vigente.
