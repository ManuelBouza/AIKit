# Inspección de permisos del helper — 2026-11-15

Comprobación dirigida de solo lectura tras el
[contraste documental](contraste-documental-sandbox-windows.md). No se ejecutó el
helper ni se modificaron ACL, propietarios o configuración. Se guardaron copias
locales de los descriptores, token y registros existentes, sin incluir identidades
personales ni SIDs de usuario en este documento.

## Observado

Sobre `~/.codex/.sandbox-bin`, Get-Acl mostró:

- Propietario: grupo Administradores; no el usuario actual.
- DACL protegida: herencia desactivada.
- Cuatro ACE explícitas Allow: SYSTEM, Administradores y usuario actual con
  Modify/Synchronize; el otro principal con ReadAndExecute/Synchronize.
- Ninguna de esas ACE concede ChangePermissions/WRITE_DAC; no hay ACE Deny en
  la DACL observada.

Se capturó también el contexto del proceso de inspección fuera del sandbox
exterior: el rol Administrador no está activo según WindowsPrincipal.IsInRole.
La captura whoami/all se conserva localmente. La captura inicial desde el sandbox
emitió un error al obtener información de notificaciones de usuario; no se
presenta esa captura como un inventario completo del token.

El setup_error existente identifica helper_sandbox_lock_failed. El log del día
contiene dos menciones de ese error y dos de SetNamedSecurityInfoW con código 5,
coherentes con el stderr de la prueba. Son registros históricos, no un nuevo
intento de preparación.

## Interpretación y límites

La DACL observada no otorga WRITE_DAC y el usuario actual no es propietario
individual. Junto con el proceso no elevado y la denegación registrada, esto
respalda la discrepancia de derechos descrita por las fuentes. Modificar archivos
no concede el derecho a cambiar su descriptor de seguridad.

No se capturó el token exacto del helper en el instante del fallo ni se ejecutó
AccessCheck con ese token. La pertenencia al grupo propietario, privilegios y
filtrado UAC requieren consideración; IsInRole por sí solo no calcula todos los
derechos efectivos. Por ello no se afirma una demostración exhaustiva de la
decisión de acceso histórica ni que una ACE concreta vaya a resolver el problema.

Evidencias ignoradas por Git: `.aikit/025-inspeccion-permisos/`, con acl.json,
reglas.json, token-cliente.txt, token-sandbox.txt, resumen-cliente.json,
setup_error.json y sandbox-log.txt. Contienen datos locales y no deben publicarse
sin revisión y redacción. La inspección no alteró el sandbox compartido.

Siguiente paso: preparar un procedimiento de reparación respaldado por fuentes,
con captura previa del descriptor, alcance limitado al helper y recuperación,
antes de ejecutar cualquier modificación o reinicialización. No conceder control
total ni borrar el directorio como consecuencia automática de este diagnóstico.
