# Inventario de referencias históricas a .aikit

Fecha: 2026-11-07. Revisión de solo lectura del checkout principal y del worktree
histórico `orquestacion-opencode` registrado por Git. Las huellas son SHA-256 de
los archivos observados, no certifican autoría ni contenido y pueden cambiar.
No se han copiado datos de ejecución, sesiones, respaldos ni credenciales.

La búsqueda recogió rutas literales `.aikit/` en documentos Markdown de `docs/`
y `notas/`; no cubre referencias construidas dinámicamente ni otros archivos.
Incluye rutas de ejemplo y directorios: «no localizado» no significa pérdida de
una evidencia, ni que el archivo haya existido. Algunas referencias se refieren
al worktree histórico, no al checkout principal. Se conserva el texto original.

Resultado: 4 archivos en el checkout principal, 46 archivos en el worktree histórico, 13 rutas de directorio disponibles y 5 rutas literales no localizadas en ninguno de los dos.

Los archivos del worktree histórico siguen fuera de Git y no son un respaldo
portable. La documentación versionada conserva resúmenes de los resultados,
pero no sustituye los originales ni demuestra su autoría. Antes de archivar
contenido, revisar individualmente datos privados, permisos y necesidad.

Se han conservado cinco [extractos seleccionados](evidencias-historicas/README.md)
de las evidencias prioritarias. Sus campos omitidos y las huellas originales se
documentan en cada archivo; no deben confundirse con copias íntegras.

## Evidencia relevante para reanudar

- **Reconciliación y cierre REC-001:** los informes y aceptaciones citados por
  [pendientes](pendientes.md) y [revisión de reconciliación](revision-reconciliacion-2026-11-02.md)
  están en el worktree histórico; los resúmenes y límites constan en Git.
- **DEF-001:** el informe `seleccion-modelo-requisitos/coordinator-recovery.json`
  está en el worktree histórico y el fallo se resume en `docs/pendientes.md`.
  No se ha diagnosticado ni cerrado con esta búsqueda.
- **Disponibilidad, instalación y binding:** varias revisiones y reportes están
  en el worktree histórico. Las rutas `validation-managed-binding/` y
  `validation-sessions/` no se localizaron literalmente; revisar su necesidad
  antes de depender de esas verificaciones. El registro de disponibilidad puede
  contener información de cuentas y no debe copiarse sin revisión individual.
- **Rutas de salida:** `aikit-go-exportado` y `distribucion-v1` son ejemplos de
  directorios de salida, no pruebas de que deba existir un archivo histórico.
  `session-locks` es una ruta de estado operativo, no una evidencia por sí sola.
- **Trabajo actual del constructor go:** el contrato y pruebas están en Git;
  la especificación BMAD conserva el resultado de la prueba de junction real.

## Rutas encontradas

| Ruta citada | Estado observado | SHA-256 | Referencias (máximo dos) |
| --- | --- | --- | --- |
| `.aikit/aikit-go-exportado` | No localizado como ruta literal | — | [contrato-artefacto-go.md](../docs/contrato-artefacto-go.md#L75) |
| `.aikit/availability-note001/bootstrap/review-fix1.json` | Archivo en worktree histórico | 60441f3d8d1e57a0fe21e8cb55a682af0dc0d254b3730aec4093dcddfafde1b8 | [2026-10-31-disponibilidad-opencode.md](../docs/superpowers/plans/2026-10-31-disponibilidad-opencode.md#L206) |
| `.aikit/availability-note001/implementation/phase1-review.json` | Archivo en worktree histórico | 13f151c2946ac975dc85923a10ea63b5ee27e2929b232e044b008e3b14e2876a | [2026-10-31-disponibilidad-opencode.md](../docs/superpowers/plans/2026-10-31-disponibilidad-opencode.md#L171) |
| `.aikit/availability-note001/implementation/phase2-review-fix1.json` | Archivo en worktree histórico | 4a6058465bac97a39fe839e93dd18778961227bc933d94940f54152f8e0f9d6e | [2026-10-31-disponibilidad-opencode.md](../docs/superpowers/plans/2026-10-31-disponibilidad-opencode.md#L177) |
| `.aikit/availability-note001/implementation/phase3-review-fix1.json` | Archivo en worktree histórico | 02a8fa7631f652a117ed24602303134a07e3d0d9b190df7ffbec91037c703405 | [2026-10-31-disponibilidad-opencode.md](../docs/superpowers/plans/2026-10-31-disponibilidad-opencode.md#L185) |
| `.aikit/availability-note001/instructions/review.json` | Archivo en worktree histórico | 5810e7d990d225da8372f59b8dfc4551aadd302d039da4b6a2549ced6c956440 | [2026-10-31-disponibilidad-opencode.md](../docs/superpowers/plans/2026-10-31-disponibilidad-opencode.md#L197) |
| `.aikit/availability-note001/inventory/review.json` | Archivo en worktree histórico | 83decb9376b62f13a4468ca509942e2a16fc7d7ca52b08c8bc5877dd1a148187 | [2026-10-31-disponibilidad-opencode.md](../docs/superpowers/plans/2026-10-31-disponibilidad-opencode.md#L226) |
| `.aikit/availability-note001/public-terms/availability-state.json` | Archivo en worktree histórico | 2b01c61100c6bc24eeeedb49a657195b0f8ad6b9cb7276997fb1753a234c9cfe | [2026-11-01-gratuidad-publica-opencode-design.md](../docs/superpowers/specs/2026-11-01-gratuidad-publica-opencode-design.md#L72) |
| `.aikit/availability-note001/public-terms/cloudflare-workers-ai-public-terms.json` | Archivo en worktree histórico | a53aae57da65bea318a5fa84be5ff5b47386fda60842b178fecfbbbdaf9eb9b4 | [2026-11-01-gratuidad-publica-opencode-design.md](../docs/superpowers/specs/2026-11-01-gratuidad-publica-opencode-design.md#L69) |
| `.aikit/availability-note001/public-terms/review-fix1.json` | Archivo en worktree histórico | d4944d64c9f232a7285e06c747dc10c1cb8e524116336f470b89eea015fb96fb | [2026-10-31-disponibilidad-opencode.md](../docs/superpowers/plans/2026-10-31-disponibilidad-opencode.md#L217) |
| `.aikit/binding-task1/review-final.json` | Archivo en worktree histórico | 0ecbbfc7b79858ddb4dcbc41c8c466f28fae186c24894ba21e08465f83f85b08 | [2026-10-31-binding-servicio-existente.md](../docs/superpowers/plans/2026-10-31-binding-servicio-existente.md#L70) |
| `.aikit/binding-task2/review.json` | Archivo en worktree histórico | 0b5588c4a2af6d9580b6794fd73718557329cbafc14ef9bfc812f6bf68caa4ca | [2026-10-31-binding-servicio-existente.md](../docs/superpowers/plans/2026-10-31-binding-servicio-existente.md#L97) |
| `.aikit/binding-task3/review-final.json` | Archivo en worktree histórico | 58ba932867aca0861e7bef34d9fe66773fc04a256f5572584d82148e5fb0e82c | [2026-10-31-binding-servicio-existente.md](../docs/superpowers/plans/2026-10-31-binding-servicio-existente.md#L119) |
| `.aikit/completion-wait-implementation/report.json` | Archivo en worktree histórico | 0499b676acb8f871e3601970f9f7a758f9df9ed3483e01a1ffc9c6aec9c2b694 | [2026-11-01-espera-finalizacion.md](../docs/superpowers/plans/2026-11-01-espera-finalizacion.md#L109) |
| `.aikit/deployment-report.json` | Archivo en worktree histórico | 32c1c37bcbb5ca71ed0010056bf1d7cd112fc7e306984506bbd5927d535c7bda | [validacion-orquestacion-opencode.md](../docs/validacion-orquestacion-opencode.md#L61), [validacion-orquestacion-opencode.md](../docs/validacion-orquestacion-opencode.md#L81) |
| `.aikit/deployment-result.json` | Archivo en worktree histórico | 26949a328d465a605b4540973516ad46923231c279c23beb0e2a1698b29042c9 | [validacion-orquestacion-opencode.md](../docs/validacion-orquestacion-opencode.md#L63) |
| `.aikit/distribucion-v1` | No localizado como ruta literal | — | [plugin-aikit.md](../docs/plugin-aikit.md#L18), [plugin-aikit.md](../docs/plugin-aikit.md#L19) |
| `.aikit/ent002-clean-20261104/` | Directorio en worktree histórico | — | [contraste-host-2026-11-04.md](../docs/contraste-host-2026-11-04.md#L26) |
| `.aikit/ent002-clean-20261104/distribution/` | Directorio en worktree histórico | — | [contraste-host-2026-11-04.md](../docs/contraste-host-2026-11-04.md#L7) |
| `.aikit/ent002-install-021/` | Directorio en worktree histórico | — | [instalacion-0.2.1.md](../docs/instalacion-0.2.1.md#L26) |
| `.aikit/ent002-install-021/coordinator-acceptance.json` | Archivo en worktree histórico | 24d6726b6cd74dbd59ce8c97bfea47ec6c3a6106d32307d5d61688b61c0d59cb | [pendientes.md](../docs/pendientes.md#L26) |
| `.aikit/ent002-install-021/reload-verification-20261105.json` | Archivo en worktree histórico | 493abfc9d490e964baeab7c7a2b937c820d51b8eebdf2edca4c596ac2eb543ce | [instalacion-0.2.1.md](../docs/instalacion-0.2.1.md#L41) |
| `.aikit/ent002-update-021/` | Directorio en worktree histórico | — | [actualizacion-0.2.1.md](../docs/actualizacion-0.2.1.md#L47) |
| `.aikit/ent002-update-021/host/` | Directorio en worktree histórico | — | [actualizacion-0.2.1.md](../docs/actualizacion-0.2.1.md#L8) |
| `.aikit/ent002-update-021/portable/` | Directorio en worktree histórico | — | [actualizacion-0.2.1.md](../docs/actualizacion-0.2.1.md#L7) |
| `.aikit/go-profile-validation.json` | Archivo en checkout principal | b122a83c7252257a0846608b1179eda0c1e63c9fc1e08bff00499ec333b2acdc | [mecanismo-go.md](../docs/mecanismo-go.md#L104) |
| `.aikit/mcp-reconciliation-fix1/report.json` | Archivo en worktree histórico | 208274f3f2e918289dc914f7d88acb0282ccc3e78d864fd2b922ce3e88b766bd | [revision-reconciliacion-2026-11-02.md](../docs/revision-reconciliacion-2026-11-02.md#L51) |
| `.aikit/mcp-reconciliation-task5/coordinator-acceptance.json` | Archivo en worktree histórico | 94b2696eb5b14786bb6ec8a76505eb826f77eb54ca8ab9a21aa7c5cf134a7788 | [2026-11-01-reconciliacion-terminal-opencode.md](../docs/superpowers/plans/2026-11-01-reconciliacion-terminal-opencode.md#L17) |
| `.aikit/mcp-reconciliation-task5/report.json` | Archivo en worktree histórico | 8185d9f3121ee0e30c97abd1e55914ea322b5f3e62657c19389dd9be3643e1b9 | [2026-11-01-reconciliacion-terminal-opencode.md](../docs/superpowers/plans/2026-11-01-reconciliacion-terminal-opencode.md#L17), [2026-11-01-reconciliacion-terminal-opencode.md](../docs/superpowers/plans/2026-11-01-reconciliacion-terminal-opencode.md#L213) |
| `.aikit/mcp-reconciliation-task6-review.md` | Archivo en worktree histórico | 1f625a07a316221b4683284e2c0f0f9561b6e364440498d66f0614da1776621f | [revision-reconciliacion-2026-11-02.md](../docs/revision-reconciliacion-2026-11-02.md#L47) |
| `.aikit/mcp-reconciliation-task6/review.json` | Archivo en worktree histórico | 4579889a7483956f7caa6a5c10ede04d357334b002f0abbf947371e0d4ad5d0f | [revision-reconciliacion-2026-11-02.md](../docs/revision-reconciliacion-2026-11-02.md#L66) |
| `.aikit/mcp-terminal-contract/report.json` | Archivo en worktree histórico | 7f700c6a198f3941ea2172018701517381f280f96c81004111a24cca9ef2c912 | [2026-11-01-reconciliacion-terminal-opencode-design.md](../docs/superpowers/specs/2026-11-01-reconciliacion-terminal-opencode-design.md#L7) |
| `.aikit/mcp-terminal-events/report.json` | Archivo en worktree histórico | 22f6ab51207a7a51f86bd0f25ada7dd478a6d4d0f3e596d6d77df1f320373adc | [2026-11-01-reconciliacion-terminal-opencode-design.md](../docs/superpowers/specs/2026-11-01-reconciliacion-terminal-opencode-design.md#L7) |
| `.aikit/opencode-wait-study/report.json` | Archivo en worktree histórico | dd32894423d8c27fc19ec0dbf7978f50534ef3d219eb9ddf9d48f7bbd4280a05 | [espera-finalizacion-opencode.md](../docs/espera-finalizacion-opencode.md#L49) |
| `.aikit/opencode-wait-study/tool-wait-probes.json` | Archivo en worktree histórico | 5ad511ced0fbf1426f48321db7f32df76d5a87740c7513addd80386d063c435d | [espera-finalizacion-opencode.md](../docs/espera-finalizacion-opencode.md#L48) |
| `.aikit/plugin-update-020/distribution-v020-final` | Directorio en worktree histórico | — | [validacion-plugin.md](../docs/validacion-plugin.md#L109), [validacion-plugin.md](../docs/validacion-plugin.md#L141) |
| `.aikit/profile-audit-0.1.4.json` | Archivo en worktree histórico | 6cdfe2785d1248e1606556aa6ed7b2cf7e5fdb56680d1e1b4c2cb7869fb2254a | [validacion-orquestacion-opencode.md](../docs/validacion-orquestacion-opencode.md#L68) |
| `.aikit/reconciliation-real-minimum/coordinator-acceptance.json` | Archivo en worktree histórico | 6c246efe7a120cb7bf0bdd8f6bf77a052767109ab374d6e07937e1fc26120432 | [pendientes.md](../docs/pendientes.md#L12), [2026-11-01-reconciliacion-terminal-opencode.md](../docs/superpowers/plans/2026-11-01-reconciliacion-terminal-opencode.md#L227) |
| `.aikit/reconciliation-real-minimum/native-events.jsonl` | Archivo en worktree histórico | 23cfaa4a6e2ae6b928c48a775d945e676c8c610305151e42f871d5bb678825f6 | [revision-reconciliacion-2026-11-02.md](../docs/revision-reconciliacion-2026-11-02.md#L267) |
| `.aikit/rev003004-builder-report.json` | Archivo en worktree histórico | 97f0f96ed052e777706a07b5393f65b6e2ebaa11cee3f550e7b4905f1720fc5b | [2026-11-03-evidencia-reconciliacion-design.md](../docs/superpowers/specs/2026-11-03-evidencia-reconciliacion-design.md#L115) |
| `.aikit/rev003004-unit1-review/review.json` | Archivo en worktree histórico | 992770b4d50d8ed1d8480c0711e375771587eae984c04e089d40ee16e0a60510 | [revision-reconciliacion-2026-11-02.md](../docs/revision-reconciliacion-2026-11-02.md#L133) |
| `.aikit/rev003004-unit1/coordinator-acceptance.json` | Archivo en worktree histórico | 0177ad5e4b64905e01c77e1ab060d1c6ebbc3d9daa3aeb23a7cc91dc6031d32d | [revision-reconciliacion-2026-11-02.md](../docs/revision-reconciliacion-2026-11-02.md#L135) |
| `.aikit/rev003004-unit2-fix1/report.json` | Archivo en worktree histórico | d13401ab10198ee93f4950bc255b8d27f36c753ca0d2d0e5d218284560a89742 | [revision-reconciliacion-2026-11-02.md](../docs/revision-reconciliacion-2026-11-02.md#L56) |
| `.aikit/rev003004-unit2-rereview/review.json` | Archivo en worktree histórico | d2d18d02a12b799fd359af28bed7dbe8af2650b45815aed13cce090d5842f585 | [revision-reconciliacion-2026-11-02.md](../docs/revision-reconciliacion-2026-11-02.md#L164) |
| `.aikit/rev003004-unit2-review/review.json` | Archivo en worktree histórico | 1a7d17e5e300995f86e2d829f554dd449b32b37d4c01e3e498223aed8d6260fc | [revision-reconciliacion-2026-11-02.md](../docs/revision-reconciliacion-2026-11-02.md#L156) |
| `.aikit/rev003004-unit2/coordinator-acceptance.json` | Archivo en worktree histórico | 4ed7c6d4d05a1728e7a70b1cf2446695c694876cfeaea892ba924ac624d7ef9f | [revision-reconciliacion-2026-11-02.md](../docs/revision-reconciliacion-2026-11-02.md#L168) |
| `.aikit/rev003004-unit3-native-review/review.json` | Archivo en worktree histórico | fb128d5daf1d8fab8e7ee74169a990f1fe7e04d20e6c653dd58f9517ccd44451 | [revision-reconciliacion-2026-11-02.md](../docs/revision-reconciliacion-2026-11-02.md#L195) |
| `.aikit/rev003004-unit3-native/coordinator-acceptance.json` | Archivo en worktree histórico | 2702a50c5729b89d465719db80df449787c239faddc6833ac3c89b8e1715da30 | [revision-reconciliacion-2026-11-02.md](../docs/revision-reconciliacion-2026-11-02.md#L199), [2026-11-03-evidencia-reconciliacion.md](../docs/superpowers/plans/2026-11-03-evidencia-reconciliacion.md#L167) |
| `.aikit/rev003004-unit4-review/review.json` | Archivo en worktree histórico | 2320734f32d6f65e67de17843e400b0bbb86043e44f56a2fa7f490356239e28b | [revision-reconciliacion-2026-11-02.md](../docs/revision-reconciliacion-2026-11-02.md#L229) |
| `.aikit/rev003004-unit4/coordinator-acceptance.json` | Archivo en worktree histórico | 7b9d71efe5c4bcf0a3615a6c0fe1b895d02031ccfab3b7783cb529f6933cb2fe | [pendientes.md](../docs/pendientes.md#L12), [revision-reconciliacion-2026-11-02.md](../docs/revision-reconciliacion-2026-11-02.md#L236) |
| `.aikit/rev003004-unit4/dist/aikit` | Directorio en worktree histórico | — | [revision-reconciliacion-2026-11-02.md](../docs/revision-reconciliacion-2026-11-02.md#L221), [2026-11-03-evidencia-reconciliacion.md](../docs/superpowers/plans/2026-11-03-evidencia-reconciliacion.md#L182) |
| `.aikit/review-rev001/review.json` | Archivo en worktree histórico | d2eb470c17cf6dcb15313a832c9cbd524b31b285b8980a90b5683b3ee73b714c | [revision-reconciliacion-2026-11-02.md](../docs/revision-reconciliacion-2026-11-02.md#L105) |
| `.aikit/routing-selection-cases.json` | Archivo en worktree histórico | f6de8450701cb97e2471a7915006d094e29c5c49b11eaade2fb7e89ebb2afb56 | [validacion-orquestacion-opencode.md](../docs/validacion-orquestacion-opencode.md#L45) |
| `.aikit/seleccion-modelo-requisitos/coordinator-recovery.json` | Archivo en worktree histórico | b3736ef7bce10a5d81e83382f6d95956aa2bd4553855d2cbfe7d2892975adc15 | [pendientes.md](../docs/pendientes.md#L19) |
| `.aikit/seleccion-tarea-smoke/resultado.txt` | Archivo en checkout principal | e3d6ffddad9f7cf8935b9f8988d32d0b458e9df2e4110516dfdbadbf7f6f67f3 | [seleccion-modelos-opencode.md](../docs/seleccion-modelos-opencode.md#L36) |
| `.aikit/session-locks` | No localizado como ruta literal | — | [inventario-monorepositorio.md](../docs/inventario-monorepositorio.md#L40) |
| `.aikit/sessions` | Directorio en worktree histórico | — | [inventario-monorepositorio.md](../docs/inventario-monorepositorio.md#L39) |
| `.aikit/sessions/` | Directorio en worktree histórico | — | [2026-10-30-sesiones-opencode.md](../docs/superpowers/plans/2026-10-30-sesiones-opencode.md#L64) |
| `.aikit/smoke-final/verificado.txt` | Archivo en checkout principal | 240a3d9c105c3a6fdfc9cc6ab26d9d831e87a13a9f8e9413f88ef0c3b8588aae | [validacion-opencode.md](../docs/validacion-opencode.md#L37) |
| `.aikit/subagent-e2e-8ae6895ee2f3416d922a15f98b027307/` | Directorio en checkout principal | — | [balance-carga.md](../docs/balance-carga.md#L206) |
| `.aikit/subagent-e2e-coordinator-verification.json` | Archivo en checkout principal | 1c8c4eeece4c91bd893d0c2e4c26051547f0f91ca698b196de43d5f259746342 | [balance-carga.md](../docs/balance-carga.md#L208) |
| `.aikit/task2-snapshot.json` | Archivo en worktree histórico | ffbdea745355c46958b41c01ebccfdf9cc8d9ab70e8bcc0fea5f6170b29c4f71 | [validacion-orquestacion-opencode.md](../docs/validacion-orquestacion-opencode.md#L73) |
| `.aikit/timeout-real` | Directorio en checkout principal | — | [validacion-opencode.md](../docs/validacion-opencode.md#L25) |
| `.aikit/tmp` | Directorio en checkout principal | — | [validacion-opencode.md](../docs/validacion-opencode.md#L19) |
| `.aikit/validation-cycle/review-fixed-attested.json` | Archivo en worktree histórico | 0e18a330f057168720c116468c6781817e205f201094fd877669114cc1f910d6 | [validacion-orquestacion-opencode.md](../docs/validacion-orquestacion-opencode.md#L39) |
| `.aikit/validation-managed-binding/` | No localizado como ruta literal | — | [2026-10-31-binding-servicio-existente.md](../docs/superpowers/plans/2026-10-31-binding-servicio-existente.md#L128) |
| `.aikit/validation-meta/routing-evaluation.json` | Archivo en worktree histórico | 4601ac816a165f594a0d3d84197a3bfbd98102ee5e8248c3dd3538bd3038fdb8 | [validacion-orquestacion-opencode.md](../docs/validacion-orquestacion-opencode.md#L46) |
| `.aikit/validation-sessions/` | No localizado como ruta literal | — | [2026-10-30-sesiones-opencode.md](../docs/superpowers/plans/2026-10-30-sesiones-opencode.md#L140) |
