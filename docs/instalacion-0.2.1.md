# Instalación local de AIKit 0.2.1

Fecha: 2026-11-04. Autorización: go sobre la instalación descrita en el [plan](actualizacion-0.2.1.md). No incluye push, cierre automático de Codex ni inferencia de prueba.

## Estado comprobado

- Registro aikit@aikit-local: instalado y habilitado, versión **0.2.1+host.1**, origen estable nuevo.
- Fuente: `<CODEX_HOME>/plugin-sources/aikit/0.2.1-host.1/`; 43 archivos verificados, incluido catálogo.
- Caché: `<CODEX_HOME>/plugins/cache/aikit-local/aikit/0.2.1+host.1/`; los 42 archivos de paquete coinciden con el manifiesto aprobado. Runtime preparado allí con `uv sync --locked --no-dev --extra mcp`.
- Overlay conservado: AIKIT_STATE y AIKIT_OPENCODE_REGISTRATION, mismos paths que la versión anterior. No se copió el registro del servicio ni credenciales al paquete.
- SDK MCP: initialize/list_tools de una instancia del servidor instalado devolvió **opencode_catalog** y **opencode_delegate**. No se invocaron esas herramientas ni se inició una tarea con modelos.
- Fuente y caché anteriores 0.2.0+host.1 conservadas; 42 hashes de cada ubicación coinciden con el registro previo. No se ejecutó rollback.

## Desviación de respaldo

El ejecutor creó `<CODEX_HOME>/backups/aikit/20261104-212825/`, pero la carpeta estaba vacía tras instalar. El paso exigido de respaldo previo no se cumplió; no se presenta como correcto.

El coordinador creó después un punto de recuperación separado: `<CODEX_HOME>/backups/aikit/20261104-recovery-after-021-203103/`. Contiene inventory-before.json (inventario grabado antes), package-hashes-before.json, overlay-paths-before.json y provenance.json con created_after_install=true. Los archivos antiguos se verificaron intactos antes de construirlo. No contiene auth, registro del servicio, config global completa, runtime ni datos de otros plugins. Permite preparar la restauración selectiva de AIKit, pero no elimina la desviación ni constituye una fotografía global previa.

## Fallo y corrección del comprobador

El primer smoke devolvió connection closed porque el harness pasó `${PLUGIN_ROOT}` literalmente al SDK y contenía una línea residual. Se conservó como evidencia y se corrigió exclusivamente el harness: expansión de variables del manifiesto y eliminación del residuo. La comprobación posterior pasó; no hubo reinstalación ni cambios del paquete para ocultar el fallo.

## Evidencia y límites

Artefactos: `.aikit/ent002-install-021/`, incluidos inventory-after.json, tool-evidence.json, recovery-point.json y coordinator-acceptance.json. Sesión OpenCode `ses_e57ddf720ffeDc36a60A1gyLQo`; instalación Beam/Kilo medium gratuito y comprobaciones acotadas low gratuito. El coordinador contrastó hashes, metadata real de checks y punto de recuperación; no repitió suite ni revisión técnica.

Los comandos de registro se dirigieron solo a aikit-local. No hay baseline independiente de metadata de otros plugins, por lo que no se afirma haber contrastado exhaustivamente su estado. El servicio compartido de OpenCode no se reinició.

**Pendiente:** el usuario recarga Codex y se comprueba la carga real de la skill/MCP nuevos. El smoke de una instancia separada no demuestra qué servidor o skill conserva este chat. No reinstalar ni repetir inferencia por ese hecho. La prueba real anterior cubrió CLI/API/helper; no se convierte en prueba del supervisor completo por instalar.
