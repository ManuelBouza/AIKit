# Selección por tarea en OpenCode

## Requisito vigente (2026-10-28)

El coordinador y los subagentes nativos de Codex conservan los roles y revisiones de Superpowers. Antes de implementar o transformar archivos en su espacio de trabajo, delegan la ejecución a OpenCode. Codex/OpenAI se reservan para orquestación y verificación. Preparar instrucciones de trabajo y ejecutar verificaciones pertenece al rol de coordinación, no a la implementación delegada.

La herramienta permite cualquier modelo conectado y habilitado en el catálogo efectivo de OpenCode, gratuito o de pago. Los gratuitos tienen preferencia cuando sus capacidades bastan. La elección de modelo y esfuerzo debe justificarse según la tarea: complejidad, herramientas, modalidades, contexto y resultados previos. No hay lista fija ni escalado opaco. El usuario ha autorizado considerar modelos de pago; no se añade una confirmación repetida a cada elección.

La variante debe existir en los metadatos del modelo. Si no hay variantes o conviene el ajuste predeterminado, se registra esa decisión; no se inventa una equivalencia con esfuerzos de Codex. Cada ejecución requiere modelo explícito y motivo de selección, y devuelve modelo, variante, motivo y coste conocido o desconocido.

## Implementación y validación

- Consultar `opencode api --standalone GET /api/model`: respuesta `{location, data}` con `providerID`, `id`, `enabled`, `capabilities`, `variants`, `cost` (array de tarifas) y `limit`.
- Exponer únicamente metadatos de selección; nunca `headers`, `body`, credenciales o ajustes completos del proveedor.
- Retirar bloqueos de proveedor, listas cerradas y obligación de crear una configuración de proyecto especial. Respetar las restricciones propias de OpenCode y del usuario.
- Mantener las protecciones existentes: argumentos sin shell, ejecutable nativo Windows, tarea literal, timeout, detección de errores y JSON seguro.
- Actualizar pruebas con modelos gratuitos, de pago, OpenAI, variantes reales, ausencia de variantes, proveedores múltiples, configuración inexistente y ausencia de modelo/motivo explícitos.
- Mantener una sola ejecución por llamada. Ante fallos, el rol que invocó revisa cambios parciales antes de escoger otro modelo y presupuesto.
- Actualizar skill, README, AGENTS y copia personal; verificar tests, catálogo real, ejecución gratuita con variante y Git.

## Cuotas

Todos los proveedores del catálogo están permitidos. Una integración OpenAI autenticada con la misma cuenta ChatGPT puede consumir la cuota que se pretende reservar; no se clasifica como gratuita solo porque reporte coste monetario cero. Se prefieren cuentas externas para ejecución y se deja ese dato visible al coordinador.

Fuentes comprobadas: [modelos y variantes](https://opencode.ai/v2/docs/models/), [API local](https://opencode.ai/v2/docs/api/). API consultada en OpenCode v2.2.0. Los modelos y sus tarifas pueden cambiar; el catálogo es evidencia de disponibilidad actual, no de calidad garantizada.

## Resultado de la implementación

Validado el 2026-10-28 con OpenCode v2.2.0 en Windows:

- Lista cerrada y bloqueos de proveedores retirados. El catálogo real presenta 26 modelos habilitados (`opencode` y `openai` en este equipo). No se exige configuración local en el directorio de ejecución.
- `doctor` expone capacidades, modalidades, límites, variantes y precios sin ajustes privados. `pricing` conserva la tarifa inicial; `pricing_tiers` incluye todos los niveles y sus umbrales de contexto. Las tarifas son USD por millón de tokens, no el coste total de una llamada.
- Suite final ejecutada por Codex: **50 pruebas superadas**. Incluye proveedores múltiples, pago/OpenAI, modelos deshabilitados, variantes reales e inexistentes, motivo obligatorio, niveles de tarifa y privacidad. Se sustituyeron las pruebas que imponían el contrato antiguo.
- Revisor independiente de Codex detectó pérdida de tarifas posteriores; corregida con regresión antes de instalar. Las pruebas de caché positiva y formato real de precios también verifican que no se clasifique como gratuito un modelo con cargos conocidos.
- Implementación delegada: `opencode/deepseek-v4.1-flash-free#high`, por complejidad de integración entre código, pruebas y documentación. Sesión `ses_e7ca5deb8ffeTC4o76nHlNVSoK`.
- Prueba real de tarea mecánica: `opencode/beam-free#low` creó `.aikit/seleccion-tarea-smoke/resultado.txt` con `SELECCION_POR_TAREA_OK`, sin configuración local en esa carpeta. La respuesta registró modelo, variante, esfuerzo, motivo y coste informado `0`. Sesión `ses_e7c9f2c3dffezrPCEuPkHSESpL`.
- La copia instalada en `C:/Users/Manuel/.codex/skills/delegating-to-opencode/` coincide por hash con la fuente. Su `doctor` reconoce el catálogo abierto y las variantes reales de Beam. El validador de skill devuelve `Skill is valid!`.
- Evaluador nativo independiente: ante dos casos hipotéticos eligió gratuito/low para una transformación pequeña y pago/deep cuando el contexto requerido excedía al gratuito; mantuvo a Codex para verificar y rechazó implementar localmente en silencio ante un fallo externo.

No se realizaron llamadas de pago para validar esta ampliación: su admisión se comprobó con transporte simulado y metadatos reales. No se afirma que todos los modelos hayan sido evaluados en calidad ni que se haya probado Unix. Las tarifas o capacidades desconocidas permanecen desconocidas; la decisión del coordinador usa evidencia disponible y el historial de resultados, no una clasificación automática garantizada.
