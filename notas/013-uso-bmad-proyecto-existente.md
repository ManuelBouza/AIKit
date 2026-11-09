# Uso de BMAD en el proyecto existente

Fecha: 2026-11-07.
Estado inicial: Pendiente de debatir.
Estado actual: Adoptado para el trabajo del proyecto; ajustes posteriores según necesidad.

Manuel confirmó que BMAD solo se activará en los proyectos que lo necesiten;
no forma parte de la configuración global general de AIKit.

## Pregunta

Determinar cómo programar con BMAD y adaptarlo al repositorio ya iniciado,
conservando instrucciones, trabajo en curso y decisiones existentes.

## Hallazgos

- BMAD-METHOD 6.12.4 core y bmm están instalados; la configuración combinada
  usa español, `docs/` para conocimiento y `_bmad-output/` para artefactos.
- La guía de proyectos existentes recomienda `bmad-build` para un cambio
  acotado y `bmad-spec` seguido de Build por pieza cuando requiere varias
  sesiones. No exige recrear documentos antiguos ni adoptar project-context.
- `bmad-project-context` es opcional si las instrucciones existentes sirven;
  adoptar un archivo existente requiere preservar sus reglas y presentar el
  bloque y el inventario de cambios antes de escribir.
- Build carga el flujo mediante `uv run --no-cache ... render_skill.py` y su
  configuración por defecto pide subagentes para implementación y revisión.
  Su paso inicial se detiene ante un árbol sucio o rama inadecuada; su revisión
  calcula el diff desde el commit base e incluye archivos sin seguimiento.
- Hay trabajo previo sin commit del constructor go. No debe mezclarse con el
  diff de otra tarea. El usuario prefiere conservarlo así hasta necesitar commit.
- `_bmad-output/` y `_bmad/` están ignorados: los artefactos de ejecución y las
  personalizaciones locales no se comparten automáticamente por Git. Decidir
  expresamente dónde conservar los artefactos que deban ser duraderos.
- El `uv run` de la verificación anterior falló por acceso denegado a su caché;
  no se ha probado todavía el comando exacto de renderizado de Build.

## Propuesta pendiente de decisión

Usar `bmad-help` para elegir ruta; probar `bmad-build` con un cambio real y
acotado elegido por el usuario, con aislamiento que preserve los cambios previos.
Revisar primero compatibilidad de instalación local, entorno uv y subagentes en
ese contexto. Mantener go, las restricciones del proyecto y la prohibición
temporal de OpenCode. Evaluar personalizaciones solo ante una necesidad probada.
No se ha iniciado Build, modificado AGENTS.md ni reanudado el trabajo pausado.

## Fuentes

- [Proyecto existente, BMAD 6.12.4](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/docs/existing-codebases/start-in-an-existing-codebase.md).
- [Build, BMAD 6.12.4](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/docs/build/build-a-change.md).
- [Elegir planificación, BMAD 6.12.4](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/docs/plan/choose-a-planning-path.md).
- [Contexto del proyecto, BMAD 6.12.4](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/docs/existing-codebases/set-and-maintain-project-context.md).
- Skills y configuración instaladas en `.agents/skills/` y `_bmad/`.

## Actualización posterior — 2026-11-07

Se ejecutó Build para corregir el constructor go; su especificación y evidencia
están en `_bmad-output/implementation-artifacts/spec-junction-constructor-go.md`.
Se resolvió el acceso a la caché temporal de uv usando un directorio del proyecto.
Los artefactos de proyecto de `_bmad-output/` dejan de estar excluidos de Git;
la instalación `_bmad/` y las personalizaciones locales permanecen excluidas.

## Actualización — 2026-11-08

El proyecto usa la orientación y las skills instaladas de BMAD según la tarea;
no se ha decidido distribuir BMAD como parte del complemento AIKit. Las
limitaciones y validaciones de cada flujo se conservan en sus artefactos.
