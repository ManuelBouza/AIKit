# Entorno BMAD del worktree 028

Fecha: 2026-11-18. Encargo: IMP-0004, porción028.
Estado: entorno preparado y verificado; listo para la implementación aprobada.

## Resultado de aplicación

El Coordinador ejecutó la variante revisada v2 con código0. La verificación
independiente posterior aceptó los 234 recursos y sus fuentes, 377 archivos
tracked, tres avisos previos, rama/HEAD/índice conservados y snapshot íntegro.
Python 3.13.14 funciona dentro de la nueva `.venv` local, con 43 dependencias
compatibles; sincronización, `pip check`, configuración y render pasaron.
No se siguió el workflow de implementación ni se alteró el tablero.

Workflow generado y comprobado:
`C:/Users/Manuel/.codex/worktrees/f8ad/AIKit/_bmad/render/bmad-build/aikit-c54c352828e4/5ee7601bf199397ff8a4/workflow.md`.
SHA256 del manifiesto del snapshot:
`072e797a2cd2277c67cc7b581f60210b7efeec389809eb73e2fa79e3a4a5ce7b`.
El Chat028 continúa desde ese flujo, sin repetir el render por rutina.

El primer intento se detuvo en preflight por el alias de versión menor de uv,
antes de escribir en028. La corrección documentada selecciona la ruta física
ya instalada y conserva las guardias de reparse. Se preservan helper, manifiesto
y evidencia del intento original. No se modifican enlaces, ACL ni configuración
global para resolver el fallo.

## Base y alcance

Worktree: `C:/Users/Manuel/.codex/worktrees/f8ad/AIKit`.
Rama: `tarea/028-tablero-notas`.
HEAD observado: `36cbde57eff20dde73a968e44665957178e4aaa0`.
Árbol limpio confirmado por consulta Git sin optional locks. El propio Chat028
adoptó antes esta base; preparar el entorno no integra ni actualiza su rama.

Se reutiliza la preparación puntual ya revisada de
[040](preparacion-bmad-worktree-040.md), con los recursos instalados de
BMAD6.12.4. La adaptación copió234archivos de BMAD y sus29skills,
sin renders, bytecode, enlaces, entornos virtuales, credenciales ni datos de
coordinación. Mantiene las comprobaciones de confinamiento y conservación.

Antes de preparar028 no existía `.venv`. Se creó una local mediante su propio
`uv.lock`, usando el intérprete Python3.13.14 ya instalado y comprobado por
lectura. No se copió la venv de040 o main ni se descargó otro Python. Se conserva
el comando `uv sync --locked --no-python-downloads --link-mode copy`, con
TEMP, TMP, caché, entorno virtual y selección de Python limitados al proceso.

Después se comprobaron dependencias, configuración y un único render local de
bmad-build. La continuidad pertenece al Chat028 desde el snapshot verificado.
Aunque se seleccionó el ejecutable físico, uv escribió el alias minor en
`pyvenv.cfg`: se acredita la versión3.13.14 actual, no fijación permanente al
patch ante cambios futuros de ese alias. No se alteró manualmente esa configuración.

## Artefactos aplicados

- Helper: `.aikit/028-entorno/preparar028-v2.py`.
  SHA256 `9ba83e79411f4a031888fc7a3d2c014c782d4e2792c3763fbc24ecc3ca5971bd`.
- Manifiesto: `.aikit/028-entorno/manifest028-v2.json`.
  SHA256 `ad949e8099322df9703c189e852f58307a5d388c13c773fe07cdd190a5aeffae`.
- Inventario:234recursos fuente,377archivos tracked y3evidencias previas028.
- Evidencia de aplicación exclusiva:
  `.aikit/028-entorno/aplicacion-20261118-02/`.
- Revisión posterior: `.aikit/028-entorno/revision-posterior.md`.

Compile y AST pasaron antes de ejecutar el helper. El primer preflight fallido
se conserva en `aplicacion-20261118-01`; no se reintentó a ciegas ni se rebajaron
guardias. Las comprobaciones posteriores acreditan el resultado de la v2.

Fuentes oficiales y límites de la preparación se conservan en la documentación
040 enlazada: se reutiliza una solución ya verificada para un worktree existente,
sin añadir configuración de creación automática para futuros chats.
