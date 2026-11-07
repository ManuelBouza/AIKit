# Plan de implantación de BMAD-METHOD

Fecha: 2026-11-07. Alcance: checkout principal `C:\Manuel\Projects\AIKit`.
El worktree de otros chats es independiente y no recibe esta instalación
automáticamente. La separación del monorepositorio y sus pendientes permanecen
pausados. Por instrucción del usuario no se utiliza Delegating to OpenCode.

## Versión y módulos

Se instaló **BMAD-METHOD 6.12.4 estable**, fijando la versión del paquete npm.
La [guía oficial](https://github.com/bmad-code-org/BMAD-METHOD/blob/main/docs/start/install-bmad.md)
distingue la serie estable 6.12 de la versión 7, que describe como preview alpha;
no se han mezclado sus procedimientos ni se ha registrado su catálogo de plugins.
Los [cambios publicados](https://github.com/bmad-code-org/BMAD-METHOD/releases)
identifican 6.12.4 y las versiones compatibles de módulos externos.

| Módulo | Decisión | Motivo |
| --- | --- | --- |
| Core | Instalado | Base compartida, ayuda y herramientas generales. |
| BMad Method (`bmm`) | Instalado | Planificación, arquitectura, implementación y revisión ajustables a la tarea. |
| Test Architect (`tea`) | Diferido | Evaluar si cubre necesidades de estrategia adicionales a pytest y revisiones existentes; evitar añadir procesos sin necesidad. |
| Creative Intelligence Suite (`cis`) | Diferido | Comparar con brainstorming incluido y la nota 009 antes de duplicar métodos. |
| BMad Builder (`bmb`) | Diferido | Comparar con la skill instalada `skill-creator` antes de añadir creación de skills o agentes. |
| BMad Loop | Diferido | Automatización desatendida y políticas adicionales; no se necesita para comenzar. |
| Game Dev Studio (`gds`) | No recomendado ahora | El repositorio no desarrolla videojuegos. |

Los [módulos oficiales](https://github.com/bmad-code-org/BMAD-METHOD/blob/V6.12/README.md)
pueden añadirse posteriormente según una necesidad concreta y su compatibilidad
con la serie elegida. Ningún módulo diferido está instalado por esta decisión.

## Instalación realizada

1. Se comprobó Node 24.22.1, npm 11.19.1, Git y uv 0.13.5. Se hizo primero
   una instalación de ensayo aislada bajo `.aikit/`.
2. Se ejecutó el instalador oficial fijado a 6.12.4 en la raíz principal, con
   `--modules bmm --tools codex`, usuario Manuel y comunicación y documentos en
   español. Core se añadió automáticamente. No se modificó el perfil global.
3. `_bmad/_config/manifest.yaml` registra `core` y `bmm` 6.12.4 y `codex`;
   `_bmad/core/config.yaml` registra el nombre del proyecto y español. El
   instalador informa de 29 skills bajo `.agents/skills/`; se contaron 29
   directorios. `_bmad-output/` es la salida configurada para artefactos.

La presencia de los archivos no demuestra que este chat, abierto en otro
worktree antes de la instalación, haya cargado las skills. Tampoco se ejecutó
un flujo BMAD ni se validó todavía su integración con el trabajo real.

## Puesta en marcha y verificación

1. Abrir un chat nuevo en `C:\Manuel\Projects\AIKit` o recargar el catálogo
   del cliente; comprobar que aparecen las skills BMAD del proyecto.
2. Invocar `bmad-help` para consultar los flujos de un cambio pequeño y
   verificar que resuelve configuración y rutas. Registrar versión y resultado.
3. Probar, con una tarea acotada, que la profundidad del proceso se ajusta al
   trabajo y que respeta las instrucciones del usuario, `go`, datos existentes
   y permisos. Una skill instalada, incluida `bmad-build-auto`, no implica que
   se haya iniciado automatización desatendida.
4. Mantener el trabajo previo y `notas/`; no recrear decisiones o tareas ya
   documentadas. Revisar la configuración de salida y evitar registrar datos
   sensibles. Comprobar qué archivos generados deben versionarse antes de commit.
5. Tras una experiencia real, contrastar cobertura con `skill-creator` y las
   capacidades ya instaladas, y evaluar TEA, CIS o Builder individualmente.

## Verificación en chat nuevo — 2026-11-07

En el checkout principal, el catálogo de skills publicado en el nuevo chat
incluye las 29 skills BMAD de `.agents/skills/`. Se invocó `bmad-help`
leyendo y siguiendo su `SKILL.md`, el catálogo `_bmad/_config/bmad-help.csv`
y la configuración combinada. El manifiesto confirma core y bmm 6.12.4.

Resultado esperado: descubrir las skills y resolver usuario, idiomas y rutas
sin iniciar implementación. Resultado observado: el resolvedor terminó con
código 0 usando `.venv/Scripts/python.exe -B _bmad/scripts/resolve_config.py
--project-root C:/Manuel/Projects/AIKit`. Resolvió Manuel, comunicación y
documentos en Spanish, nivel intermediate y salida `_bmad-output`; las rutas
de planificación e implementación apuntan a sus subdirectorios
`planning-artifacts` e `implementation-artifacts`. El conocimiento del proyecto
apunta a `docs/`. Los marcadores `{project-root}` devueltos en JSON se
interpretaron con la raíz de este checkout; no se confundieron con rutas literales.

La invocación prescrita con `uv run` falló al escribir su caché de intérpretes
fuera del workspace (acceso denegado). Se usó el intérprete existente sin
instalar dependencias ni cambiar permisos o configuración. El valor English
de `_bmad/config.toml` queda reemplazado por Spanish en la capa personal,
por lo que no requiere corrección.

No se encontraron archivos en `_bmad-output/`: no se acredita un flujo BMAD
de planificación o implementación completado. Para una futura prueba acotada,
el catálogo ofrece `[SPC] bmad-spec` si hace falta concretar el alcance y
`[BD] bmad-build` para ejecutar un cambio autorizado; no se invocaron.
La comprobación de ayuda queda realizada, pero la adaptación del proceso a
una tarea real sigue sin probarse. El monorepositorio y la prueba de junction
real del constructor go continúan pausados. No se utilizó OpenCode ni se
hizo commit o push.

## Límites de la instalación

Las 29 skills son instalación local del proyecto, no una prueba de activación en
todos los clientes o worktrees. La instalación (`_bmad/` y
`.agents/skills/bmad-*/`) y sus salidas (`_bmad-output/`) se excluyen de Git;
este documento conserva el procedimiento y la evidencia. Al terminar la
instalación, los cambios generados y los cambios anteriores estaban sin commit;
no se hizo push. npm mostró una advertencia de deprecación
para la dependencia transitoria `glob@11.1.0`; no se ha realizado una auditoría
independiente completa de dependencias.
