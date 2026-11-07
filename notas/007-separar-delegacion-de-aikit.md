# Separar delegating-to-opencode del complemento AIKit

Fecha: 2026-10-31.
Estado: pendiente de debatir.

## Idea

Separar `delegating-to-opencode` del complemento AIKit para que sean dos elementos
independientes. AIKit debe utilizarlo como una de las herramientas disponibles,
igual que utiliza Superpowers y Context7.

La capacidad de delegar a OpenCode debe poder instalarse y utilizarse de forma
independiente de AIKit. AIKit conserva sus preferencias y criterios para decidir
cuándo y cómo usar esa capacidad.

## AIKit como forma global de trabajar con Codex

AIKit debe establecer la forma global de trabajar con Codex. Al instalarse,
debe agregar sus instrucciones al `AGENTS.md` global, siguiendo el mecanismo que
ya utiliza. Cada proyecto tendrá su `AGENTS.md` local para complementar esas
instrucciones con las particularidades del proyecto.

Además de las instrucciones globales, AIKit tendrá skills propias para apoyar
su trabajo. Definir correctamente qué responsabilidad corresponde a cada pieza:

- `AGENTS.md` global: instrucciones generales de la forma de trabajo de AIKit.
- `AGENTS.md` local: instrucciones específicas que aporta cada proyecto.
- Skills propias de AIKit: procedimientos y capacidades de apoyo que se activen
  cuando corresponda.
- Herramientas independientes, externas o nuestras: capacidades que AIKit utiliza,
  como `delegating-to-opencode`, Superpowers y Context7, respetando la naturaleza
  de cada integración.

Esta distribución es una intención para desarrollar al debatir la nota; queda
pendiente concretar los límites sin duplicar instrucciones o responsabilidades.

## Para debatir después

- Delimitar qué pertenece a la herramienta de delegación y qué son políticas de
  coordinación propias de AIKit.
- Clasificar las responsabilidades de AIKit entre `AGENTS.md` global, instrucciones
  locales de proyecto, skills propias y herramientas independientes. Definir cómo
  se complementan, se activan y se mantienen sin duplicaciones.
- Precisar cómo el instalador agrega y actualiza las instrucciones globales y las
  skills propias, conservando instrucciones ajenas y la configuración de proyectos.
- Definir distribución, instalación, versiones y actualización independientes,
  y decidir si esa separación requiere también repositorios distintos.
- Establecer cómo AIKit descubre y utiliza la herramienta, comprueba su
  compatibilidad y actúa cuando no está instalada o disponible.
- Planificar la migración del complemento actual sin duplicar skills o servidores
  MCP ni perder configuraciones existentes.
- Revisar el empaquetado, la documentación y las pruebas que dependan de que la
  delegación forme parte del complemento AIKit.

Relacionada con la nota [006](006-herramientas-skills-opencode.md), sobre las
capacidades disponibles en cada entorno y el lugar de instalación de AIKit.

Guardar esta nota no cambia el empaquetado actual ni autoriza la separación o
migración de componentes.
