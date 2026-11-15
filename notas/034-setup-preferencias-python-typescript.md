# Preferencias de preparación y calidad para Python y TypeScript en aikit-setup

Fecha: 2026-11-14.
Estado inicial: Pendiente de debatir.
Estado actual: Pendiente de debatir; implementación solicitada para más adelante.

## Petición

Manuel solicita añadir posteriormente a `aikit-setup` un apartado de preferencias
de configuración para trabajar con Python y TypeScript. Ese apartado debe definir
qué herramientas instalar y cómo configurarlas para trabajar de forma óptima con
cada lenguaje, con responsabilidades claras y controles de calidad coherentes.

## Contexto que debe conservarse

- La [nota 033](033-responsabilidades-lenguajes-calidad.md) y
  [los controles aplicados en este repositorio](../docs/calidad-python-typescript.md)
  proporcionan una referencia: Python con uv, Ruff, mypy y pytest; TypeScript con
  npm, tsc, ESLint/typescript-eslint, Prettier y node --test. Son una base para
  evaluar al diseñar el setup, no una obligación universal para otros proyectos.
- Priorizar herramientas instaladas para las comprobaciones automáticas y usar
  inferencia para interpretar diagnósticos, corregir causas y cubrir lo que las
  herramientas no comprueban.
- Distinguir herramientas de desarrollo de requisitos de ejecución del producto;
  respetar las herramientas, configuraciones y versiones compatibles del proyecto.

## Aspectos por concretar al retomarla

Detectar los lenguajes y las herramientas existentes; permitir elegir Python,
TypeScript o ambos; definir dependencias, tipos, lint, formato, pruebas y comandos
de verificación. Aclarar alcance local/global y cómo instalar o configurar lo que
falte mediante las capacidades y autorizaciones disponibles. Evitar sobrescribir
configuración ajena o instalar herramientas innecesarias.

Relacionada con la [nota 018](018-herramientas-recomendadas-setup.md), sobre
herramientas recomendadas en setup. Reutilizar sus mecanismos al implementar.
Las herramientas y versiones concretas se verificarán con documentación actual
al retomar el diseño. Esta nota registra el trabajo futuro; no activa preferencias
ni autoriza su implementación ahora.
