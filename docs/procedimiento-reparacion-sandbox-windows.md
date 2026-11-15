# Procedimiento propuesto de reparación — 2026-11-15

Preparado para revisión; no ejecutado. Se apoya en la
[investigación documental](contraste-documental-sandbox-windows.md) y la
[inspección local](inspeccion-permisos-sandbox-windows.md). Objetivo: recuperar
lecturas confinadas del cliente, manteniendo el aislamiento y sin alterar AIKit.

## Alternativas y recomendación

1. **Recomendada: un intento de configuración oficial elevada**, con respaldo
   previo, ventana sin otros escritores y comprobación posterior. La
   [guía oficial](https://learn.chatgpt.com/docs/windows/windows-sandbox) propone
   reintentar la configuración del backend legado cuando falla. No garantiza
   solucionar esta DACL concreta. Puede requerir intervención UAC del usuario.
2. **Alternativa posterior: corrección puntual de WRITE_DAC**, solo si el intento
   oficial falla y tras decisión expresa. Los
   [reportes técnicos](https://github.com/openai/codex/issues/45153) muestran que
   puede funcionar temporalmente y que el helper puede revertirla. No es una
   reparación oficial garantizada. No queda autorizada por aprobar la opción 1.

No se propone control total, tomar propiedad, habilitar herencia, borrar o
renombrar .sandbox-bin, cambiar a Full Access ni desactivar reglas. Tampoco
actualizar el cliente o migrar backend dentro de este procedimiento.

## Antes de iniciar la opción 1

- Reservar una ventana sin chats, automatizaciones ni procesos que ejecuten
  comandos mediante el sandbox. El usuario debe detener o pausar su trabajo
  pertinente; este procedimiento no cancela tareas ni termina procesos ajenos.
  Si hay que reiniciar la aplicación, persistir primero esta conversación y el
  trabajo abierto, y retomar después mediante este documento.
- Confirmar ruta absoluta de .sandbox-bin en el perfil usado, sin enlaces o
  redirecciones, versión de cliente y backend elevado. No deducir el perfil
  desde el directorio actual del proyecto. Si difiere de la inspección, parar y
  actualizar el diagnóstico antes de cambiar nada.
- Crear un respaldo NUEVO en una ubicación privada fuera de directorios de
  descubrimiento y fuera de .sandbox-bin. Capturar descriptor con propietario,
  grupo, DACL y estado de herencia, además de inventario y hashes de los archivos
  existentes del directorio. Guardar también los registros de preparación y la
  selección pertinente del backend. No copiar autenticación, secretos del sandbox
  ni el perfil completo. No afirmar que se capturó la SACL si no se pudo leer.
- Conservar la DACL con `icacls /save` y su representación SDDL legible para
  contraste. Comprobar código de salida y contenido del respaldo; documentar la
  carpeta base y nombres relativos que necesitará `/restore`. Una copia de la
  salida en pantalla no sustituye un respaldo recuperable.
- Si cualquier captura falla o no puede garantizarse exclusividad, detenerse
  sin iniciar setup. Los diagnósticos ya guardados no sustituyen este respaldo
  inmediatamente anterior a la operación.

## Un solo intento oficial

Usar la configuración de sandbox de la interfaz del cliente y la vía oficial
elevada. Si se utiliza app-server, comprobar primero qué métodos admite el
cliente instalado; no asumir que CLI 0.153.4 implementa toda la documentación
actual. La [API oficial](https://learn.chatgpt.com/docs/app-server) documenta
windowsSandbox/readiness y windowsSandbox/setupStart, con resultado asíncrono
windowsSandbox/setupCompleted. Si una API no existe, usar la interfaz oficial
compatible, sin invocar ejecutables privados ni reconstruir su protocolo.

Antes de aceptar UAC, el usuario comprueba que corresponde al configurador de
Codex esperado. No automatizar aceptación ni usar credenciales de otra cuenta
sin entender el cambio de identidad. Conservar resultado y logs. Si el cliente
indica ready pero persiste el fallo de lectura, no forzar ciclos de setup ni
dar por resuelto el problema basándose solo en ese indicador.

El configurador puede afectar usuarios de sandbox y configuración de red de
Windows, además de la DACL. Este alcance se debe exponer al autorizar el intento;
no se presenta como una modificación exclusiva de un archivo o directorio.

## Verificación y parada

Una vez finalizado el intento y desde el contexto normal no administrador:

1. Comparar descriptor e inventario con el respaldo; identificar cambios reales.
2. Ejecutar dos lecturas consecutivas de un archivo ficticio preparado para la
   prueba, mediante sandbox read-only. Verificar resultados reales de comandos y
   ausencia de errores del helper, no solo código 0 de codex exec.
3. Solo si ambas lecturas pasan, repetir la invocación explícita de la skill en
   el proyecto temporal. Exigir evidencia de lectura de SKILL y referencia.

Si setup falla, las lecturas no pasan o cambia de nuevo la DACL, conservar
evidencias y detenerse. No conceder permisos adicionales automáticamente.
Una operación exitosa seguida de otra fallida es reparación no acreditada.

## Restauración y límites

Si se decide revertir, detener primero escritores de sandbox y comparar estado
actual con el capturado al terminar setup. No sobrescribir cambios concurrentes
o de una actualización posterior. La autorización del intento incluye comprobar
el resultado; cualquier restauración debe identificar previamente qué cambios
se revertirán y confirmar que el respaldo corresponde al mismo objeto.

[Microsoft documenta](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls)
que `/save` y `/restore` conservan y aplican DACL: no son un respaldo completo
del descriptor, contenido, cuentas o firewall. Restaurar solo la DACL respaldada,
desde la base relativa registrada y con permisos administrativos apropiados,
puede devolver también el estado defectuoso inicial. Releer y comparar DACL y
herencia después; no sustituir esa comprobación por eliminar una ACE por nombre.

Si cambian propietario, SACL, contenido del helper, cuentas o red, no intentar
reconstruirlos con ese respaldo DACL: conservar el estado y usar un procedimiento
de recuperación oficial o soporte con alcance específico. No se promete una
reversión integral de setup. Si se exige esa garantía antes de intervenir,
detenerse y escalar a soporte en vez de iniciar el configurador.

Los reportes para soporte deben redactar identidades y rutas personales y
excluir secretos. Prepararlos no autoriza enviarlos. La alternativa manual de
WRITE_DAC necesitaría otro procedimiento, limitado al directorio y SID concreto,
sin herencia ni recursión, con validación y restauración propias.
