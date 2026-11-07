# AIKit: mecanismo go

Este directorio permite instalar el bloque de instrucciones `go` en un perfil
de Codex. Requiere Python 3.10 o posterior y no instala otras integraciones.

Desde este directorio, sustituye la ruta de ejemplo por el perfil deseado:

```powershell
python scripts/install_go.py --codex-home C:\ruta\perfil-codex
```

El instalador conserva instrucciones ajenas y guarda un respaldo en
`backups/aikit/` dentro del perfil. Repetirlo sin cambios devuelve `unchanged`.
Si existe un `AGENTS.override.md` no vacío o marcadores incorrectos, rechaza la
operación. No garantiza exclusión mutua frente a escrituras simultáneas.

Para retirar el mecanismo, revisa `AGENTS.md` y elimina solo el bloque entre
`<!-- AIKIT:GO:BEGIN -->` y `<!-- AIKIT:GO:END -->`, incluidos los marcadores.
Antes de restaurar un respaldo, compara los cambios posteriores para no perderlos.
La carga de instrucciones depende del cliente y puede requerir un chat nuevo.
