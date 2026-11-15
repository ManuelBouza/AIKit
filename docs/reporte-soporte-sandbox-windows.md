# Codex Windows: setup informa éxito, pero el helper sigue fallando al preparar .sandbox-bin

Borrador para soporte. Fecha: 15 de noviembre de 2026. No enviado.

## Problema

Estoy intentando validar la lectura de una skill local en un proyecto temporal,
con una sesión de solo lectura. Codex descubre la skill, pero sus intentos de
leer archivos fallan antes de crear el proceso. Un intento del configurador
oficial informa éxito sin recuperar la ejecución del helper.

Necesito una vía de reparación compatible con el sandbox nativo que conserve
sus límites, sin conceder control total ni cambiar de propietario manualmente.

## Entorno

- Windows nativo, PowerShell; API de versión del proceso informa 10.0.26300.0.
  No se capturó edición/UBR mediante inventario del sistema.
- Codex CLI 0.153.4, utilizado desde un entorno de Codex Desktop. No se capturó
  la versión exacta de la interfaz Desktop; no debe inferirse de la versión CLI.
- Perfil habitual: windows.sandbox = elevated.
- Sesión de prueba: proyecto temporal fuera del repositorio, sin archivos de
  trabajo reales, con skill copiada en .agents/skills.
- Flags: --ephemeral --ignore-user-config --sandbox read-only
  --skip-git-repo-check --json. Se utilizó la autenticación existente, sin copiarla.
- Las invocaciones se lanzaron desde el contexto de herramientas de Desktop.
  No se ha hecho una comparación independiente desde una terminal interactiva.

## Secuencia observada

1. El descubrimiento mediante app-server skills/list reconoce la skill en una
   copia temporal y devuelve su ruta y enabled true, sin errores de descubrimiento.
2. Una invocación explícita intenta ejecutar Get-Content sobre SKILL.md y su
   referencia local. El stderr registra rechazo antes de crear proceso:

   ```text
   CreateProcess ... rejected: blocked by policy
   ```

   La CLI termina con código 0 y una respuesta del modelo que reconoce no haber
   leído la referencia. Los eventos JSONL no contienen una ejecución de lectura
   completada con éxito; el stderr sí conserva el rechazo.
3. Evaluar el comando frente al archivo de reglas del usuario con execpolicy
   check devuelve matchedRules vacío. No se comprobó exhaustivamente toda capa
   de política efectiva.
4. Repetir el mismo caso añadiendo únicamente
   `-c windows.sandbox="elevated"` cambia el fallo por:

   ```text
   helper_sandbox_lock_failed:
   lock sandbox bin dir <CODEX_HOME>\.sandbox-bin failed:
   SetNamedSecurityInfoW sandbox dir failed: 5
   ```

5. Con autorización del usuario y sin otros trabajos usando el sandbox, se
   respaldaron descriptor, DACL, inventario y hashes del helper y logs existentes.
   Se solicitó un único intento oficial por app-server:

   ```json
   {"id":2,"method":"windowsSandbox/readiness","params":null}
   {"id":2,"result":{"status":"ready"}}
   {"id":3,"method":"windowsSandbox/setupStart","params":{"mode":"elevated","cwd":"<PROYECTO>"}}
   {"id":3,"result":{"started":true}}
   {"method":"windowsSandbox/setupCompleted","params":{"mode":"elevated","success":true,"error":null}}
   ```

   Se omiten del extracto initialize/initialized y metadatos temporales.
   No se automatizó UAC ni se registró una interacción UAC en este intento.
6. Después, SDDL, propietario e inventario con hashes del helper son idénticos
   al respaldo. No se inventariaron íntegramente cuentas o firewall.
7. Una consulta de ayuda mal formada (`codex sandbox windows --help`) fue
   interpretada por esta versión como un comando para aislar. Falló durante
   preparación con orchestrator_helper_exit_nonzero, status Some(1). El registro
   posterior conserva helper_sandbox_lock_failed. Este paso fue un error del
   agente: no constituye una prueba válida de lectura ni debe copiarse como
   reproducción recomendada. No se ejecutó otra prueba después de ese fallo.

## Permisos observados

En .sandbox-bin:

- Propietario: grupo Administradores; DACL protegida, sin herencia.
- SYSTEM, Administradores y usuario actual: Allow Modify/Synchronize.
- Otro principal: Allow ReadAndExecute/Synchronize.
- Sin ACE Deny ni ACE que conceda ChangePermissions/WRITE_DAC en la DACL observada.

El proceso de inspección fuera del sandbox exterior no tiene activo el rol
Administrador. No se capturó el token exacto del helper en el instante del fallo
ni se calculó AccessCheck con ese token. Por tanto, se sospecha una discrepancia
de derechos al reaplicar la DACL, pero no se afirma una causa exhaustivamente probada.

## Resultado esperado y preguntas

Una lectura permitida por el sandbox debería ejecutarse, o el cliente debería
explicar qué requisito concreto falta. El éxito del configurador debería poder
contrastarse con la capacidad real de iniciar comandos aislados.

¿Cuál es el procedimiento oficial de recuperación para este estado de .sandbox-bin?
¿Hay una corrección publicada para el ciclo de permisos/refresco en esta versión,
y qué versión concreta la incluye? ¿Qué diagnóstico adicional permite distinguir
un problema de token/ACL de una limitación de ejecución anidada sin modificar
manualmente la seguridad del directorio?

No se modificaron ACL ni propietario del helper manualmente, no se borró o
renombró el directorio, no se desactivaron reglas y no se usó Full Access para
las sesiones de evaluación. El código 0 de la invocación no se considera éxito
de lectura. La coordinación de producción no está activada.

## Referencias técnicas

- [Documentación oficial Windows](https://learn.chatgpt.com/docs/windows/windows-sandbox).
- [API de configuración del sandbox](https://learn.chatgpt.com/docs/app-server).
- [Reporte coincidente sobre ignore-user-config](https://github.com/openai/codex/issues/42172).
- [Reporte de fallos recurrentes de WRITE_DAC](https://github.com/openai/codex/issues/45153).
- [Microsoft: requisitos de SetNamedSecurityInfoW](https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-setnamedsecurityinfow).

Estos reportes aportan contexto; no se presentan como una reparación aprobada
ni como prueba de identidad de causa. Los logs originales permanecen locales.
Antes de adjuntarlos deben redactarse rutas personales, nombres, SIDs de usuario,
IDs de chats y cualquier dato ajeno. No adjuntar autenticación, secretos del
sandbox, config completa o inventarios privados sin revisión específica.
