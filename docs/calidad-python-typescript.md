# Controles de calidad por lenguaje

Fecha: 2026-11-14. Estado: configuración aplicada; resultados de validación al final.
Origen: [nota 033](../notas/033-responsabilidades-lenguajes-calidad.md).

## Responsabilidades y criterio común

Manuel establece un criterio de coste y ejecución: las herramientas instaladas
son la primera vía para detectar errores que puedan comprobar automáticamente.
No sustituir compilador, linter, formateador, comprobador de tipos o pruebas por
una inspección del modelo que intente reproducir sus comprobaciones. Configurarlas
una vez y ejecutar los controles pertinentes permite obtener diagnósticos
reproducibles con menos inferencia.

El agente selecciona los controles aplicables, los ejecuta y utiliza sus códigos
de salida y diagnósticos como evidencia. Usa inferencia para interpretar resultados,
corregir causas, decidir pruebas necesarias y revisar aspectos no cubiertos por
las herramientas. No envía salidas completas a revisores para repetir controles
que ya pasaron: comunica resultados y limita la revisión a riesgos pendientes.
Después de corregir, repite los controles afectados; amplía la ejecución solo
si el cambio, un fallo o una duda pendiente lo justifica. No declara una propiedad
verificada cuando la herramienta no la comprueba.

Python conserva herramientas internas de empaquetado, tablero, comprobaciones y
la integración histórica independiente. TypeScript conserva el instalador y es
el candidato del nuevo auxiliar de coordinación. JavaScript compilado se ejecuta
con Node. Esta propuesta no migra componentes ni duplica reglas entre lenguajes.
PowerShell mantiene el lanzador Windows y los adaptadores específicos del sistema.

Ambos lenguajes deben tener dependencias reproducibles, comprobación de tipos,
lint, formato y pruebas. Equivalencia de controles no exige herramientas idénticas.
Las dependencias de desarrollo no se convierten en requisitos del proyecto que
utiliza AIKit ni se incluyen como dependencias de ejecución del auxiliar.

## Herramientas elegidas como recomendación

1. **Recomendada:** ESLint + typescript-eslint para lint y Prettier para formato.
   El análisis con tipos utiliza el mismo proyecto TypeScript que la compilación
   y permite reglas explícitas sobre promesas y valores inseguros. Prettier asume
   el formato; eslint-config-prettier desactiva reglas que entren en conflicto.
2. **Alternativa:** Biome para lint y formato. Reduce herramientas y dispone de
   reglas sobre promesas, pero usa su propio análisis de tipos; no se presupone
   equivalencia de cobertura con typescript-eslint ni se compara con versiones
   antiguas como si describieran su estado actual.

Se conservan tsc y node --test. No se añade un segundo framework de pruebas.
Las versiones exactas de nuevas dependencias se elegirán y fijarán al implementar,
comprobando peerDependencies y engines contra TypeScript 5.9.3 y el Node probado.
Node observado: 24.22.1. El requisito actual del paquete es >=20: cualquier cambio
de compatibilidad debe explicitarse, sin subirlo accidentalmente por el linter.

## Alcance y configuración inicial

- `packages/aikit-installer/src/**/*.ts`: configuración plana de ESLint,
  recommendedTypeChecked, projectService y raíz tsconfig explícita. Mantener
  strict y noEmitOnError. Declarar no-floating-promises y no-misused-promises
  como errores y hacer que advertencias produzcan fallo (`--max-warnings 0`).
- `test/**/*.cjs` y configuración JavaScript: reglas recomendadas de JavaScript
  con entorno Node/CommonJS correcto, sin exigir que pertenezcan al tsconfig.
  No añadir globals de navegador al código de Node.
- Prettier sobre fuentes, pruebas y configuración editable del paquete. Excluir
  dist, node_modules y lockfile generado. No formatear notas, BMAD, plantillas ni
  el resto del repositorio por añadir este control.
- Estilo propuesto: dos espacios, punto y coma, comillas simples en JS/TS,
  ancho 100 y LF; reglas de formato a cargo de Prettier.
- Los fallos existentes se corrigen con cambios acotados y revisables. No desactivar
  reglas globalmente para obtener verde; toda excepción local requiere motivo.

## Comandos y correspondencia

Comandos TypeScript propuestos, ejecutados desde el paquete:

| Propósito | Python actual | TypeScript propuesto |
| --- | --- | --- |
| Preparar dependencias fijadas | uv sync --locked | npm ci |
| Tipos | uv run mypy | npm run typecheck → tsc --noEmit -p tsconfig.json |
| Lint | uv run ruff check . | npm run lint → eslint . --max-warnings 0 |
| Formato, solo comprobar | uv run ruff format --check . | npm run format:check → prettier --check con alcance explícito |
| Pruebas | uv run pytest | npm test, que compila y ejecuta node --test |
| Corrección solicitada | Ruff con opciones de escritura | npm run lint:fix / npm run format, separados de verificar |

Se añadiría `npm run verify` para typecheck, lint, format:check y test con fallo
si cualquiera falla. El conjunto de rutas de format y format:check será idéntico.
No se usa npx para descargar herramientas implícitamente ni instalaciones globales.
La compilación de npm test genera dist; verificar nunca aplica fixes de lint/formato.

## Verificación conjunta

Ampliar `scripts/verificar.ps1` conservando su resumen por comprobación:

1. Comprobar uv, Node y npm; anotar versiones observadas. Un requisito ausente
   impide declarar éxito y produce salida no cero, aunque se puedan verificar
   las partes independientes.
2. Ejecutar uv sync --locked en raíz y npm ci en el paquete. Si una preparación
   falla, marcar sus comprobaciones dependientes como no ejecutadas por fallo,
   sin usar dependencias antiguas como evidencia satisfactoria.
3. Ejecutar los controles Python existentes y cada control TypeScript de la tabla,
   con cwd explícito y código real de salida. Resumir todos los resultados posibles;
   no convertir una excepción de lanzamiento en código cero ni ocultar omisiones.
4. Devolver cero solo si todas las comprobaciones requeridas se ejecutaron y pasaron.

El comando conjunto conserva su alcance Windows. Los comandos uv y npm de la
tabla permiten ejecución directa en otros sistemas; esta propuesta no afirma que
el lanzador PowerShell sea un flujo multiplataforma ya validado.

## Validación al implementar

Ejecutar instalación reproducible y controles completos; comprobar de forma
reversible que un error de tipos, lint, formato o prueba produce salida no cero
y que no deja modificaciones de formato. Comprobar preparación fallida y comando
ausente sin ejecutar dependientes sobre una instalación obsoleta. Restaurar las
sondas y ejecutar una pasada final. La mera presencia de scripts no prueba cobertura.

Actualizar AGENTS.md y la documentación de comandos cuando el flujo esté aplicado
y verificado. Incorporar paquetes TypeScript futuros al mismo contrato al crearlos.

## Fuentes consultadas

- [typescript-eslint: análisis con tipos](https://typescript-eslint.io/getting-started/typed-linting/),
  presets y projectService; documentación consultada también mediante Context7.
- [Prettier: CLI](https://prettier.io/docs/cli) y
  [eslint-config-prettier](https://github.com/prettier/eslint-config-prettier),
  separación de formato y lint; consulta mediante Context7.
- [Biome: noFloatingPromises](https://biomejs.dev/linter/rules/no-floating-promises/javascript/),
  alternativa actual evaluada sin asumir que carece de análisis de tipos.
- [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/), instalación desde lockfile.

Evidencia local: package.json, tsconfig.json, pyproject.toml y verificar.ps1.
## Aplicación y versiones

Se aplicó la opción recomendada: ESLint 10.15.0, @eslint/js 10.0.1,
typescript-eslint 8.72.2, eslint-config-prettier 10.1.8, Prettier 3.10.1 y
globals 17.14.0, fijados en package.json y package-lock.json como dependencias
de desarrollo. Las secciones anteriores conservan el criterio y la comparación
que fundamentaron la elección; los comandos propuestos ya están implementados.

Entorno de desarrollo verificado: Node 24.22.1 y npm 11.19.1. ESLint 10 admite
Node ^20.19.0, ^22.13.0 o >=24: el desarrollo requiere esos mínimos, aunque el
runtime del instalador conserva >=20. No se actualizó TypeScript ni el runtime
del producto. format y format:check comparten exactamente el mismo alcance.

El primer lint detectó siete errores; se validó la versión leída de package.json,
se conservó cause al informar bloqueo existente, se eliminó una aserción redundante
y se usó rmSync sin recursión para la limpieza que ignoraba ENOENT. Prettier aplicó
el formato inicial únicamente dentro del paquete.

npm audit informó siete avisos moderados de desarrollo derivados de minimatch
transitivo en typescript-eslint. No se aplicó audit fix --force ni un override
incompatible; este informe no equivale a una auditoría de seguridad del producto.

## Evidencia de ejecución — 2026-11-14

Entorno: Windows, PowerShell 7.6.9, Python 3.14.9, uv 0.13.5, Node 24.22.1,
npm 11.19.1. Dependencias preparadas desde ambos lockfiles. El verificador utiliza
npm ci --include=dev, comprueba mínimos de Node y ejecuta controles Python con
uv run --no-sync después de preparar el entorno.

- Pasada Python final: 946 pruebas correctas, Ruff lint/formato correctos y mypy
  sin errores en 72 archivos. Incluye 13 casos del verificador con fallos de
  preparación, comandos, controles y directorios de ejecución.
- Pasada conjunta final: `scripts/verificar.ps1` devolvió 0; el paquete pasó
  typecheck, ESLint, Prettier, compilación y 53 pruebas Node, sin omisiones.
- Sondas reversibles reales: typecheck devuelve 2, lint 1, format:check 1 y test 1
  al introducir cada fallo deliberado. Cada sonda confirmó que la herramienta
  no reescribió el archivo; los archivos de prueba se retiraron después.
- Correcciones a las pruebas: doble Node.cmd acepta la consulta de compatibilidad;
  la prueba fuera de Git limita búsqueda con GIT_CEILING_DIRECTORIES para funcionar
  también cuando TEMP está dentro del checkout.
- Consulta online independiente npm audit: siete avisos moderados, sin altos ni
  críticos. La salida de auditoría de npm ci en modo offline no sustituye esa consulta.

Logs locales ignorados por Git: .aikit/033-verificacion-final.log,
.aikit/033-probe-*.log y .aikit/033-audit.json. No se enviaron a un modelo para
repetir la comprobación automática; la revisión independiente se centró en riesgos
del lanzador y cobertura no acreditada por lint o tipos.

### Resolución posterior de los avisos npm

La auditoría online identificó un único origen para los siete avisos:
minimatch 10.2.6, transitivo de typescript-estree 8.72.2. El aviso
[GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249) fija la
corrección desde 11.0.1. typescript-eslint 8.72.2 sigue siendo la versión más
reciente consultada y declara minimatch ^10.2.2; la degradación automática propuesta
por npm no soporta nuestro TypeScript 5.9 ni ESLint 10.

Se añadió un override limitado a typescript-estree 8.72.2 para usar minimatch
11.0.8, ya utilizado por ESLint. Queda fuera del rango original del consumidor:
la compatibilidad se valida para este proyecto, no se atribuye al soporte upstream.
La prueba tooling.test.cjs ejercita projectService/allowDefaultProject con un
archivo oculto, usando la llamada minimatch(path, pattern, {dot: true}) del parser.
Revisar y retirar el override cuando el consumidor admita una versión corregida.

npm conservó inicialmente una entrada obsoleta al recalcular el lockfile; se
respaldó y retiró esa entrada para que npm la regenerara, sin inventar integridades
ni editar módulos instalados. npm ci reproducible, npm ls sin dependencias inválidas
y npm audit online confirman ahora cero vulnerabilidades.
Evidencia local: .aikit/033-audit-corregida.json.
Validación posterior: npm run verify devolvió 0 (tipos, lint, formato y pruebas);
52 pruebas Node pasaron y dos pruebas de junctions se omitieron por restricciones
del sandbox. La nueva prueba del parser pasó. Python no cambió y no se repitió su
suite. Ejecutar auditoría online al actualizar dependencias; revisar el override
cuando typescript-estree publique compatibilidad con minimatch corregido.
