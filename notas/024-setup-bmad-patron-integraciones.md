# Setup BMAD y patrón de adaptación de integraciones

Fecha: 2026-11-13.
Actualización: 2026-11-14.
Estado: Pendiente de debatir.

## Idea

Crear un `setup-bmad` similar a `aikit-setup` para configurar las preferencias
de uso de BMAD acordadas, con instalación local o global explícita.

- Detectar si un entorno utiliza BMAD y recomendar instalar la integración.
- Instalar únicamente cuando el usuario lo solicite o autorice.
- Usar por defecto el `AGENTS.md` local del proyecto.
- Si el usuario elige el `AGENTS.md` global, explicar el alcance y confirmar
  claramente esa elección antes de aplicarla.
- Recoger las preferencias de BMAD indicadas anteriormente, distinguiendo las
  generales de las específicas de cada proyecto.

Las demás integraciones deben seguir este patrón: descubrir su presencia y
proponer la instalación explícita de las adaptaciones globales o por proyecto.

## Contexto relacionado

- [012](012-referencia-bmad-en-agents.md): orientación con `bmad-help` y selección
  de skills según la tarea.
- [013](013-uso-bmad-proyecto-existente.md): adopción de BMAD por proyecto.
- [018](018-herramientas-recomendadas-setup.md): descubrimiento y aprobación de
  instalaciones durante el setup.
- `packaging/skills/aikit-setup/SKILL.md`: setup existente como referencia.

## Aclaración del usuario

Este chat se dedica a registrar ideas. La formulación «implementar» describe
el objetivo futuro de esta nota y no inicia su desarrollo desde este canal.
El usuario corrigió la propuesta de continuar la implementación el 2026-11-14.
La idea queda registrada para retomarla cuando se decida expresamente.
