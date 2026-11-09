# Preferencia de Context7 en AIKit

Fecha: 2026-11-07.
Estado inicial: Pendiente de debatir.
Estado actual: Implementada y configurada mediante setup explícito; comportamiento futuro sujeto a verificación.

Manuel aclaró que Context7 debe estar disponible globalmente. La preferencia
global no demuestra por sí sola la disponibilidad del complemento en otros
equipos; queda pendiente verificar y resolver esa capacidad.

## Idea

Incorporar a AIKit una preferencia portable para utilizar Context7 al consultar
documentación técnica actualizada de bibliotecas, frameworks y tecnologías que
cubra. El `AGENTS.md` de este proyecto recoge ya la preferencia local.

## Para concretar

- Decidir dónde distribuir la preferencia en AIKit y cómo aplicarla en otros
  proyectos sin modificar configuraciones ajenas.
- Comprobar disponibilidad, cobertura y versión de la documentación; utilizar
  fuentes oficiales u otras fuentes primarias adecuadas cuando sea necesario.
- Respetar las fuentes pedidas por el usuario y evitar duplicar capacidades o
  instrucciones ya instaladas.
- Verificar el comportamiento en un entorno de destino antes de declararlo
  implementado de forma portable.

El usuario incluyó esta preferencia en la primera versión de AIKit; su diseño e
integración se recogen en la [especificación](../_bmad-output/specs/spec-complementos-independientes/SPEC.md).
Esa decisión no instala cambios ni modifica el perfil global real.

## Avance — 2026-11-07

El complemento AIKit preparado incluye una plantilla propia de Context7 y un
instalador explícito de bloques. La instalación se probó en perfiles ficticios;
instalar el complemento por CLI no escribió `AGENTS.md` automáticamente. La
[evidencia](../_bmad-output/implementation-artifacts/validacion-complemento-aikit.md)
y la [especificación de implementación](../_bmad-output/implementation-artifacts/spec-complemento-aikit.md)
conservan resultados y limitaciones. La instalación global automática, la
retirada selectiva y la migración siguen pendientes; no se modificó el perfil real.

La [propuesta de configuración global](../docs/diseno-configuracion-global-aikit.md)
recoge el mecanismo documentado y la decisión pendiente sobre el paso posterior
de configuración.

## Actualización — 2026-11-08

El usuario eligió un complemento con setup explícito, en lugar de escritura
automática al instalarlo. La preferencia se aplicó en los archivos `AGENTS.md`
global y del proyecto mediante el instalador incluido; ambos devolvieron estado
`current`. En un chat nuevo se reconoció e invocó la skill instalada y las vistas
previas no indicaron cambios. La [evidencia](../docs/evidencias/prueba-setup-ambitos-real.md)
recoge la prueba real. Esto verifica configuración, no cada futura selección de
fuentes ni la instalación de Context7 en otros equipos.
