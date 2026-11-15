# Responsabilidades de lenguajes y controles de calidad

Fecha: 2026-11-14.
Estado inicial: Pendiente de debatir.
Estado actual: Implementada y verificada; avisos npm resueltos.

Manuel aclara que no pretende declarar un lenguaje mejor que otro: necesita
responsabilidades bien definidas para Python y TypeScript y aplicación coherente
de sus controles de calidad. Señala que Python tiene uv y linters mientras
TypeScript no tiene el mismo tratamiento. Relacionada con la nota 025 y el
auxiliar de coordinación propuesto, todavía sin implementar.

Inspección del repositorio: Python dispone de uv, uv.lock, pytest, Ruff y mypy.
El instalador TypeScript tiene npm, package-lock.json, compilación tsc con strict
y noEmitOnError, y pruebas con node --test. No tiene scripts ni configuración
propia de lint/formato; scripts/verificar.ps1 solo ejecuta controles Python.
La compilación comprueba tipos, pero no cubre por sí sola el papel de lint y formato.

Pendiente: acordar responsabilidades por componente y un conjunto equivalente de
controles (dependencias reproducibles, tipos, lint, formato y pruebas), con un
comando de verificación que cubra ambos. Elegir herramientas tras consultar su
documentación, sin migrar lenguajes ni instalar dependencias por esta nota.

La [propuesta concreta](../docs/calidad-python-typescript.md) recomienda ESLint
con typescript-eslint, Prettier, tsc y node --test; compara Biome como alternativa.
Define alcance, comandos y verificación conjunta, manteniendo los controles Python.
Manuel autorizó definir esta propuesta; aún no se aplicó la configuración.
Manuel precisa el objetivo económico: priorizar herramientas instaladas para
detectar errores automáticamente, evitando gastar inferencia en reproducir sus
comprobaciones. El modelo interpreta diagnósticos, corrige y aborda los aspectos
no cubiertos; la propuesta de calidad incorpora este criterio de ejecución.

Manuel autorizó aplicar los controles mediante go. ESLint con tipos y Prettier
están instalados como dependencias de desarrollo fijadas; npm run verify agrupa
tipos, lint, formato y pruebas. verificar.ps1 integra ambos lenguajes, omite
dependientes cuando falla la preparación y devuelve error ante controles omitidos.
La pasada Python final pasó 946 pruebas, Ruff y mypy; se conservan sondas negativas
reales y pruebas del verificador. La evidencia final y las versiones están en
docs/calidad-python-typescript.md. npm audit registra siete avisos moderados de
dependencias de desarrollo, pendientes de resolución compatible; no se aplicó force.
La pasada conjunta final devolvió código 0: 946 pruebas Python y 53 pruebas Node,
sin omisiones, con tipos, lint y formato correctos. Los avisos npm se conservan
como pendiente independiente; no impiden que los controles configurados funcionen.

Resolución posterior autorizada mediante go: override acotado de minimatch 11.0.8
en typescript-estree 8.72.2, fuera de su rango original y probado para el uso actual
del parser. npm ci y npm ls válidos; auditoría online posterior con cero avisos.
La prueba de regresión y los límites del override constan en la documentación.
