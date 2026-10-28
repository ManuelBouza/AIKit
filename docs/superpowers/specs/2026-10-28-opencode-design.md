# Diseño: delegación a OpenCode

Se elige una skill propia sobre la CLI oficial, conforme al «Go» de Manuel tras la investigación. Codex conserva coordinación y verificación; OpenCode ejecuta trabajo acotado. No se instala un MCP comunitario.

Alternativas: adaptar un MCP existente exige corregir compatibilidad y revisar dependencias; un MCP propio añade transporte y mantenimiento innecesarios para este primer uso local.

La fuente versionada será `skills/delegating-to-opencode/`, instalable en el directorio personal de skills. Un adaptador Python 3.10+ sin dependencias descubrirá OpenCode, comprobará versión v2 y catálogo, y ejecutará una sola tarea con modelo explícito. Política JSON con lista permitida de modelos gratuitos, predeterminado Mimo; variantes opcionales explícitas, nunca esfuerzos inventados. Sin alternativa de pago ni reintentos automáticos.

El adaptador usará `cwd` y `--model proveedor/modelo#variante`; nunca `--dir`, `--variant` o `--effort`. Argumentos sin shell. Modo standalone para evitar reutilizar un servidor con configuración antigua. Salida JSON compacta, tiempo máximo, errores detectados incluso con código de salida cero y coste desconocido expresado como null. Nada de credenciales en informes.

La configuración del proyecto permite solo el proveedor `opencode` y bloquea subdelegaciones internas. La lista del adaptador restringe los modelos concretos; esto no constituye un sandbox del sistema operativo ni garantiza precios futuros. Para otros repositorios se debe configurar y comprobar la misma política antes de delegar. No se modifica la cuenta OpenAI guardada en OpenCode.

Pruebas: rechazo de OpenAI, modelo fuera de lista o ausente del catálogo; argumentos Windows y variantes; errores JSON, salida vacía, timeout y datos de coste ausentes; escenario real de delegación y validación de skill. Instalación sin sobrescribir silenciosamente una skill existente y posibilidad de desinstalar eliminando solo su carpeta.

Límite inicial: sin cuotas de cuentas adicionales, sin clasificación automática de calidad de modelos y sin promesa de ahorro porcentual. Se registran resultados observados.
