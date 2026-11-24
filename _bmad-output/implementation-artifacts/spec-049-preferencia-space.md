---
title: 'Preferencia de conocimiento en ChatGPT Space'
type: 'feature'
created: '2026-11-23'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: ['docs/complemento-aikit-independiente.md']
---

<frozen-after-approval reason="alcance del usuario">

## Intent

AIKit debe ofrecer Space como preferencia optativa de proyecto. Al activarla
desde aikit-setup o desde el instalador, se guarda en AGENTS.md el enlace de la
página raíz elegida y la instrucción de usar Space para conocimiento del proyecto.
Los documentos operativos y los registros que necesitan las herramientas
siguen siendo accesibles en el repositorio. La configuración se puede
previsualizar, comprobar, actualizar y retirar mediante el instalador existente.
Pages aporta las operaciones sobre contenido. La preferencia configura cómo
usar esas operaciones y el destino, sin iniciar una migración.

</frozen-after-approval>

## Implementation Notes

- El catálogo de `aikit-setup` presenta Space para el ámbito de proyecto. El
  instalador reutiliza los bloques gestionados y el exportador distribuye la
  plantilla. El paquete usa una plantilla portable y recibe el enlace al
  activar la preferencia.
- La CLI comprueba el formato y el estado local. Pages permite verificar el
  acceso y que el enlace apunta a la raíz, y aporta las operaciones sobre
  contenido.
- En Windows con Node 24.22.1, `npm run verify` pasó con 65 pruebas y 4
  omisiones de plataforma. La suite `tests/test_build_aikit.py` pasó sus 30
  pruebas, incluida la comprobación del instalador exportado en un repositorio
  ficticio. Ruff y mypy sobre los archivos Python modificados pasaron.
  El mypy general no pudo comprobar la prueba del tablero por falta de los
  módulos de Playwright.
- La vista previa con la raíz del Space de AIKit confirmó el contenido del
  bloque y que el `AGENTS.md` real seguía intacto.

## Review Triage Log

- Se corrigió la expectativa de la prueba de selección global. Space se
  excluye de la activación global y de la selección predeterminada.
- Se corrigió la retirada de Space para consumir el salto de línea del bloque,
  y la prueba confirma la restauración byte a byte de la configuración previa.
- Se documentaron los respaldos y los límites de la comprobación local del
  enlace. Las instrucciones indican qué comunicar si Pages no permite guardar.
- Se añadió la comprobación de que un enlace anterior devuelve `different`
  sin modificar el archivo.

## Estructura de notas y memoria

El usuario pidió que la activación mediante `aikit-setup` prepare una
estructura común. La plantilla del bloque define las cuatro entradas que
setup crea o reutiliza en la portada. Si Pages no puede comprobar la
estructura o prepararla, esa activación queda pendiente. La CLI sigue
aplicando exclusivamente el bloque local.

La verificación en un Space de prueba cubrió la creación de las cuatro
entradas de memoria y del registro de tareas. Una segunda activación
conservó la página, el enlace y la fila de prueba en el registro. La
preferencia se activó en AIKit y un chat nuevo comprobó que la versión
instalada de setup detectaba el registro existente sin requerir cambios.
