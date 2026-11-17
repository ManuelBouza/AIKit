# Verificación del seguimiento local 043

Fecha: 2026-11-17. Entorno: Windows, Python 3.14.9, pytest 9.2.0,
Mistune del lockfile; Edge instalado con Playwright aislado ya disponible.
No se añadieron dependencias de runtime ni se instaló el complemento en el perfil.

## Cobertura y reutilización

Se consultaron las skills existentes `coordinacion-chats`, `aikit-setup` y
`skill-creator`, además de los principios de reutilización del repositorio.
Coordinación y setup ya cubrían roles, avisos y activación manual; faltaba el
contrato de registro previo y seguimiento de entregas. Se amplían mediante una
referencia compartida `references/seguimiento.md`, sin nueva skill, flags ni
cambios en Superpowers. El exportador incluye esta referencia por allowlist,
sin runtime del tablero ni datos locales. El generador reutiliza Mistune,
renderizado seguro y publicación atómica existentes; JSON y validación usan
la biblioteca estándar. La migración real es responsabilidad del Coordinador.

## Resultados

- `uv run --locked pytest tests/test_seguimiento_tareas.py tests/test_tablero_notas.py tests/test_build_aikit.py`: 55 aprobadas. Se cubren alta sin idea, varias entregas independientes, repetición sin mutación, metadata estricta, relaciones, secciones, autorización, referencias y preservación de HTML ante errores. La exportación aislada compila npm y comprueba recursos distribuidos.
- `uv run --locked ruff check .`: correcto; formato aplicado únicamente a archivos modificados.
- `uv run --locked mypy`: correcto, 73 archivos; control explícito adicional de `scripts/seguimiento_tareas.py` y `scripts/tablero_notas.py`: correcto.
- `quick_validate.py` de skill-creator para ambas skills: `Skill is valid!`. Se usó Python del sistema con PyYAML 6.0.3 ya disponible; el entorno uv no incorpora PyYAML.
- Playwright con Edge instalado: 43 ideas y cuatro tareas reales visibles; activación con Enter, filtros de fase/atención/idea y navegación de tarea a dependencia y de tarea a idea con relación inversa. Cero errores JavaScript y cero peticiones externas. Captura y script de evidencia privados en `.aikit/043-migracion/`.

Para uv se configuraron TEMP, TMP y UV_CACHE_DIR a la ruta absoluta
`.aikit/uv-temp` únicamente en cada proceso, tras el error conocido de caché
Windows. El lanzamiento de navegador no devolvía salida dentro del sandbox;
se canceló y la misma comprobación local se completó fuera de él mediante
la aprobación de herramienta aplicable, sin descargar navegadores o paquetes.

## Revisión independiente y correcciones

Tres capas revisaron el diff: defectos generales, casos límite y lagunas de
verificación. El contraste técnico independiente verificó cada hallazgo antes
de agrupar duplicados. Se corrigieron raíz canónica, fuente activa ausente,
offsets RFC3339, secciones dentro de código, recorrido de dependencias y selección
tras filtrar; se añadieron regresiones DOM ficticias y de enlace externo.
No se endureció el campo motivo de cancelación sin un requisito que lo exigiera
ahí, ni se borran filtros al navegar explícitamente por relaciones.

El revisor seguimiento043_edge aceptó el candidato corregido por lectura y
trazado independiente. Sus resultados no se presentan como ejecución de pruebas.
Diff revisado: SHA-256
`2bd41918075e3fccefaaf1abad019df25dbe14405bd26c2ee1cc198ee224909e`.
Archivos adicionales inspeccionados:

- tests/test_tablero_notas_dom.py: `7eb9a2ce0416e7944c84dc2958f0fe8b8275e13f15cfbc0ff632d0d3855f421c`.
- tests/test_seguimiento_tareas.py: `3e21dfe23a3be97efba02afe012ba885dfcb619302aa05944d3205692ef05ba4`.
- coordinacion/MIGRACION-043.md: `df81b3371e1c016a5a50ecb89ca0008c7d4e099a7a04581fc0591e7078383d5f`.

Tras los parches: 52 pruebas focales y dos de DOM/enlace externo aprobadas sin
omisiones en entorno permitido. La ejecución DOM usa fuentes ficticias y está
documentada como comprobación opcional de desarrollo; no requiere datos reales
ni añade requisitos al usuario del complemento. La migración real y su repetición
manual se describen en coordinacion/MIGRACION-043.md.

## Límites

Verificación conjunta final del Coordinador: `uv run --locked pytest` con las
variables documentadas de Playwright/Edge y permisos de ejecución aplicables:
**988 passed in 202.17s**, sin omisiones. Ruff lint y formato global correctos
(321 archivos ya formateados); mypy global correcto en 74 archivos y control
explícito de los dos módulos del generador/registro correcto. No hubo cambios de
código después del candidato revisado; el cierre solo actualiza evidencias y
estados del registro.

La validación comprueba estructura y relaciones; no autentica referencias
humanas ni detecta todos los duplicados semánticos. El generador no muta tickets
ni concede permisos. La publicación protege el HTML único, sin prometer una
transacción multiarchivo. La vista es una instantánea que requiere regeneración
y recarga. La migración, revisión independiente e integración final se registran
por el Coordinador con su evidencia propia; estos controles no las sustituyen.

## Correcciones tras revisión independiente

Regresiones focales de parser y tablero: 52 aprobadas. Se incorporan contraste
de raíz canónica con copia obsoleta en worktree, fallo conservador ante fuente
activa ausente, límites RFC3339 de offsets, secciones reales separadas de fences
Markdown indentados o no cerrados y cadena acíclica de 1011 tickets con recorrido
iterativo. Ruff y tipos se controlan sobre los archivos de esta corrección.

Prueba DOM compartida ficticia `tests/test_tablero_notas_dom.py` y prueba de
referencia simbólica externa: 2 aprobadas, sin omisiones, con Edge/Playwright
existentes fuera del sandbox. El enlace solo apunta a otro archivo ficticio del
mismo directorio temporal de pruebas, fuera de la raíz canónica simulada; el HTML
previo y los bytes externos se conservan. La ruta de ejecución reproducible se
documenta en `docs/tablero-notas.md`; sustituye como regresión mantenida a la
comprobación privada sobre datos reales descrita anteriormente.
