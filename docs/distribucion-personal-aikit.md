# Distribución personal desde GitHub

Actualización: la interfaz principal acordada es el complemento con skill de
configuración, descrito en `docs/decision-aikit-complemento-setup.md`; npx queda
como alternativa. El resto de este documento conserva la propuesta anterior.

Decisión de alcance, 2026-11-08: distribuir AIKit únicamente entre los PC de
Manuel. Se aplaza la publicación en npm y la automatización de publicación.
Conservar lo implementado del instalador TypeScript y sus respaldos.

Vía recomendada: ejecutar mediante npx un paquete obtenido del repositorio Git
privado. Preparar un punto de entrada npm en la raíz del monorepositorio que
distribuya solo AIKit y permita preparar el código compilado; el paquete actual
vive en un subdirectorio y el comando remoto todavía no está implementado.
Git y Node/npm deben estar disponibles y Git debe poder acceder al repositorio
en cada PC. La sesión de npm no sustituye al acceso a GitHub.

Interfaz propuesta (no disponible todavía):

```powershell
npx --yes --package git+https://github.com/ManuelBouza/AIKit.git aikit install --global
npx --yes --package git+https://github.com/ManuelBouza/AIKit.git aikit install --project
```

`--global` aplica a CODEX_HOME/AGENTS.md o ~/.codex/AGENTS.md. `--project`
localiza la raíz del repositorio desde el directorio actual y aplica a su
AGENTS.md. Fuera de un repositorio informa del problema, sin escribir en un
directorio arbitrario. Ambos modos preservan instrucciones ajenas, usan bloques
administrados y respaldan. Si falta el alcance, preguntar global o proyecto en
terminal interactiva; en ejecución no interactiva exigir el indicador. Rechazar
indicadores incompatibles. La ruta de destino debe mostrarse antes de aplicar.

Las reglas específicas del proyecto mantienen su ámbito; el modo proyecto debe
respetar AGENTS.override.md y no trasladar instrucciones ajenas al perfil global.
Los respaldos locales de proyecto deben quedar fuera de Git sin sobrescribir
reglas de exclusión existentes; decidir y probar esa ubicación al implementar.

Repetir el comando aplica la versión obtenida. Para actualización reproducible,
usar una etiqueta Git aprobada mediante #etiqueta y verificar la resolución y
caché de npx en pruebas. Todavía se debe comprobar el flujo completo desde GitHub;
la validación actual cubre tarballs locales. No requiere registro npm público,
workflow de publicación ni distribuir Delegating to OpenCode.

Fuente: [especificación Git de npm y preparación del paquete](https://docs.npmjs.com/cli/v11/configuring-npm/package-json/#git-urls-as-dependencies).
