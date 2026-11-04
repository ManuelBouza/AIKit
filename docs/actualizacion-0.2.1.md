# Actualización AIKit 0.2.1: plan de preparación

**Seguimiento 2026-11-04:** instalación autorizada y ejecutada. Ver [resultado y desviaciones](instalacion-0.2.1.md). El procedimiento siguiente conserva el plan previo; la recarga y carga real en Codex siguen pendientes.

## Paquetes revisables

- Portable: `.aikit/ent002-update-021/portable/`, manifiesto `portable-manifest.json`.
- Este host: `.aikit/ent002-update-021/host/`, manifiesto `host-manifest.json`.
- Cada distribución tiene 42 archivos de paquete y un catálogo, sin extras ni runtime.
- Fuente/proyecto/lock: 0.2.1. Identificador del plugin local: 0.2.1+host.1.
- El local solo cambia plugin.json (identificador) y mcp.json (dos variables de paths existentes). No contiene credenciales de servicio.

## Estado observado y precondiciones

Inventario: aikit@aikit-local instalado y habilitado, versión 0.2.0+host.1. Marketplace anterior: <CODEX_HOME>/plugin-sources/aikit/0.2.0-host.1/. Paquete anterior dentro de aikit/. Esto describe el registro, no prueba qué runtime está cargado en este chat.

Antes de cualquier escritura: volver a listar solo aikit-local; exigir ese origen/versión/estado y ausencia de otros plugins en ese marketplace. Comprobar hashes de los 43 archivos del paquete nuevo y de los 42 archivos antiguos observados. Abortar ante cambios concurrentes, paths distintos, symlinks, destinos existentes o falta de respaldo seguro. Verificar ayuda CLI de los comandos siguientes antes de ejecutarlos; si cambió la interfaz, detener y adaptar el plan sin improvisar mutaciones.

## Respaldo selectivo que se creará al instalar

Destino nuevo: <CODEX_HOME>/backups/aikit/<fecha-hora>/. Registrar inventory-before.json (solo entrada AIKit, source y marketplaceSource), package-hashes-before.json, y overlay-paths-before.json (solo AIKIT_STATE y AIKIT_OPENCODE_REGISTRATION). No copiar auth, registro de servicio, config.toml entero, otros plugins ni .venv. Esas rutas son privadas y el respaldo queda fuera de directorios descubribles.

Se conserva la fuente anterior completa y su caché sin sobrescribirlas ni borrarlas. La restauración del registro se hará con CLI y el inventario selectivo, no reescribiendo archivos internos de metadata compartida cuyo formato no está contratado. Así no se reemplaza configuración ajena.

## Instalación futura, pendiente de autorización

1. Tras respaldo validado, copiar exclusivamente los 43 archivos verificados de host/ a <CODEX_HOME>/plugin-sources/aikit/0.2.1-host.1/, destino NUEVO. Sin sobrescrituras ni importación de módulos. Volver a verificar conjunto y hashes.
2. Cambiar solo marketplace aikit-local con la CLI documentada:
   - `codex plugin marketplace remove aikit-local`
   - `codex plugin marketplace add <CODEX_HOME>/plugin-sources/aikit/0.2.1-host.1`
   - `codex plugin add aikit@aikit-local --json`
   Hay un intervalo sin registro entre remove y add. Si algo falla, pasar inmediatamente a la reversión, sin modificar otro marketplace.
3. Capturar installedPath devuelto por add, validarlo dentro de la caché esperada y preparar allí el runtime: `uv sync --project <installedPath> --locked --no-dev --extra mcp`. No preparar únicamente la fuente, porque PLUGIN_ROOT corresponde a la copia instalada. Puede requerir red; si falla, restaurar el registro anterior y conservar evidencia, sin inferencias de prueba ni reintentos ciegos.
4. `codex plugin list --marketplace aikit-local --json`: confirmar versión 0.2.1+host.1, enabled, fuente nueva y overlay intacto. Validar manifests/hashes instalados y runtime sin inferencia antes de dar por correcta la preparación.
5. El usuario recarga Codex; después se contrasta el catálogo real de herramientas. No cerrar la aplicación automáticamente ni detener el servicio compartido de OpenCode. La recarga y la carga real siguen sin estar verificadas ahora.

## Reversión

Si se retiró el marketplace antiguo pero no se pudo registrar el nuevo: registrar directamente el origen antiguo del inventario. Si se llegó a registrar el nuevo: retirar solo aikit-local y añadir el origen anterior. Reinstalar aikit@aikit-local desde ese origen y comprobar inventario/versión 0.2.0+host.1/estado enabled anterior. Usar la caché anterior conservada; restaurar solo el estado de AIKit mediante CLI, sin reemplazar metadata compartida completa ni configurar otras cuentas/MCP.

Comparar con inventory-before.json y hashes previos; usuario recarga Codex. Conservar la fuente nueva y evidencias como diagnóstico fuera del registro activo; no borrados recursivos ni parada del servidor. Si cambió otro registro o no puede demostrarse restauración exacta, parar e informar del estado concreto, sin escribir sobre cambios ajenos.

## Límites de aceptación

Esta entrega prepara paquetes y procedimiento. No crea aún respaldos en CODEX_HOME, no instala, no prepara runtime de la nueva caché, no recarga y no acredita runtime vivo. La prueba real previa cubrió CLI/API/helper, no supervisor E2E. No se amplía la validación de comportamiento por este cambio de versión.

Evidencia de preparación: `.aikit/ent002-update-021/`, sesión OpenCode `ses_e57ddf720ffeDc36a60A1gyLQo`, Beam/Kilo low gratuito. 12 pruebas de exportación aprobadas y lock offline correcto; hashes y overlay comprobados por el coordinador. Fuente oficial de empaquetado: https://developers.openai.com/plugins/build/plugins.
