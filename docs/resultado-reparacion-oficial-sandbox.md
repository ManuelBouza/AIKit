# Intento oficial de reparación — 2026-11-15

Manuel autorizó expresamente «reparar» y confirmó que solo este chat trabajaba.
Se aplicó el [procedimiento preparado](procedimiento-reparacion-sandbox-windows.md)
hasta la condición de parada. La reparación no está acreditada.

## Respaldo y ejecución

Se creó una carpeta privada nueva, con herencia desactivada y acceso limitado
al usuario, SYSTEM y Administradores. Contiene descriptor (propietario, grupo,
DACL y herencia), respaldo icacls de 390 bytes y una entrada relativa
`.sandbox-bin` desde la base del perfil, inventario de cuatro archivos con hashes
y logs existentes. No se copiaron credenciales ni secretos. No se capturó SACL.

El esquema generado por CLI 0.153.4 confirmó disponibilidad de readiness y
setupStart. Una única conexión app-server inicializó el protocolo, consultó
readiness y solicitó setupStart en modo elevado. Resultado:

- readiness: ready.
- setupStart: started true.
- setupCompleted: success true, error null.

La solicitud no activó aprobación UAC automática. No se registró una interacción
UAC; no se afirma que hubiera ocurrido solo por solicitar el modo elevado.

## Verificación y parada

El descriptor SDDL y propietario después del intento son idénticos al respaldo.
El inventario y hashes tampoco cambiaron. Esto no acredita ausencia de cambios
en cuentas o firewall, que no se inventariaron íntegramente.

Al consultar ayuda, el agente usó erróneamente `codex sandbox windows --help`:
esta versión no tiene ese subcomando y trató `windows` como comando a aislar.
La invocación falló antes de ejecutarlo, con
`orchestrator_helper_exit_nonzero: setup helper exited with status Some(1)`.
El registro posterior de setup conserva `helper_sandbox_lock_failed`.
No se presenta esa invocación como una prueba válida de lectura.

Al reaparecer un fallo de preparación se aplicó la parada del procedimiento:
no se hicieron las dos lecturas ni se repitió la invocación de la skill. Tampoco
se repitió setup ni se concedieron derechos manuales. El éxito de la notificación
oficial no demuestra que los comandos puedan ejecutarse.

No se restauró la DACL: es idéntica al respaldo, por lo que escribirla de nuevo
no revertiría ningún cambio observado. No se declara restauración integral de
los efectos de setup. Las cuentas y red se mantienen bajo gestión del configurador.

## Evidencias y pendiente

Directorio privado ignorado por Git:
`.aikit/025-respaldo-sandbox-58e68951-4227-4563-8da9-9b8184e61531/`.
Incluye respaldos, descriptores/inventarios posteriores, transcript de setup y
logs antes/después. Script local `.aikit/025-setup-oficial.py`, con marcador
exclusivo de intento para impedir una segunda solicitud accidental.

La skill sigue sin carga completa verificada. Se recomienda preparar un reporte
redactado para soporte con este fallo posterior a setup exitoso, sin enviarlo
automáticamente. Cualquier corrección manual WRITE_DAC requiere alcance y
autorización separados de este intento oficial.
