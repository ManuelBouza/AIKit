# Validación de orquestación Codex/OpenCode

## Alcance y criterio de evidencia

Esta validación registra resultados de tareas y revisiones reales, pruebas
locales con fixtures y una instalación del complemento en el perfil local. Los
JSON de `.aikit/` son evidencia de trabajo local, no se distribuyen con AIKit.
No se publican logs, transcripciones ni contenido de configuración privada.

`review_evidence.py` comprueba que el informe concuerde con la expectativa del
coordinador: rol, sesión esperada, snapshot actual, veredicto, checks y
limitaciones. No ejecuta los comandos del informe ni demuestra criptográficamente
quién lo redactó, que un comando se ejecutara o que la revisión técnica fuera
correcta. La aceptación de metadata no sustituye la revisión independiente: el
coordinador verifica su consistencia y conserva los roles de Codex y Superpowers.

## Ejecuciones y revisiones independientes

Los modelos, variantes y conteos siguientes se transcriben de los resultados y
JSON de revisión disponibles. «Free» identifica el modelo/proveedor reportado;
un coste informado por el backend no es una factura verificada.

| Tarea | Ejecución | Revisión independiente y resultado |
| --- | --- | --- |
| 1 | OpenCode Beam Free, `medium`; 237 pruebas. | Beam Free, `medium`; aceptada, 237 pruebas. Las sesiones de implementación y revisión son distintas. No existe `task1-acceptance.json`; se conservan el resultado y `task1-review-attested.json`. |
| 2 | OpenCode Beam Free, `high`; 265 pruebas, incluidas 28 nuevas. | Beam Free, `high`; aceptada, 265 pruebas. `task2-acceptance.json` y `task2-review-attested.json` están presentes. |
| 3 | OpenCode Beam Free, `high`; implementación revisada. | El primer intento Free devolvió `free_limit_reached`; ese único error no demuestra que todos los modelos Free estuvieran agotados. El revisor seleccionado después fue Kimi K3.1 Pro en OpenCode Go, `high`; aceptada, 288 pruebas. El resultado guardó `cost: 0.0`, que se reporta como metadata del backend, no como precio verificado. |

Las tres revisiones aceptadas usan sesiones diferentes de las ejecuciones
correspondientes y snapshots registrados. Esta comprobación de metadata no
equivale a una firma ni a una certificación de autoría.

## Casos funcionales y de transporte

- **Ciclo con defecto deliberado:** la fixture semilla implementa por error
  `total_cents > 5000` en vez de `>= 5000`. El revisor encontró que falla
  `test_threshold_inclusive`: 1 de 4 pruebas falla y el proceso termina con 1.
  Tras la corrección, un revisor independiente nuevo aceptó la fixture con 4/4
  pruebas. `.aikit/validation-cycle/review-fixed-attested.json` registra
  `accepted` y el check `unittest` con código de salida 0.
- **Validador de metadata:** `validation-meta/results.json` registra aceptación
  positiva y restauración aceptada; rechaza snapshot obsoleto, checks omitidos,
  checks fallidos y autor/revisor iguales. Son comprobaciones locales del
  validador, no pruebas de identidad criptográfica.
- **Selección de ruta:** `.aikit/routing-selection-cases.json` contiene los
  casos de entrada simulados y `.aikit/validation-meta/routing-evaluation.json`
  registra su evaluación local. Comprueban decisiones esperadas del coordinador;
  no representan una ejecución real, cuotas, indisponibilidad real ni un router
  que seleccione modelos automáticamente.
- **Puente nativo a CLI:** el primer mensaje no pudo persistirse por un
  `PermissionError`; el resultado del backend quedó indeterminado. No se afirma
  que esa inferencia fallara ni se deduce su salida. Un intento posterior,
  autorizado con `require_escalated`, devolvió por stdout
  `NATIVE_BRIDGE_OK` con `opencode-go/gpt-6-luna`, esfuerzo `low` y coste `null`.
  Esto prueba el transporte nativo y la recuperación por stdout, no una revisión
  técnica ejecutada por Codex.

## Instalación real y estado de versiones

La primera instalación local del complemento se registró como versión `0.1.4`.
`.aikit/deployment-report.json` informa caché refrescada, preferencias ajenas y
bloque `go` preservados, routing presente, segunda ejecución `unchanged`, mtime
conservado y ningún respaldo adicional. `.aikit/deployment-result.json` informa
que el operador no expuso el código de salida del comando (`cmd_exit_code: null`);
no se interpreta como código 0.

La auditoría posterior de solo lectura se guarda en
`.aikit/profile-audit-0.1.4.json`. Comprueba la instalación/caché `0.1.4`, los
hashes del runtime funcional entre fuente y caché, los bloques de instrucciones y
la diferencia permitida de configuración mediante indicadores y hashes, sin
imprimir valores privados ni escribir en el perfil. Como la fuente candidata
`0.1.5` ya modifica `scripts/review_evidence.py`, ese archivo instalado se
contrasta con el hash `0.1.4` aceptado en `.aikit/task2-snapshot.json`; los demás
archivos estables del runtime se comparan con la fuente.

El árbol fuente prepara el candidato `0.1.5` con cambios de protocolo e
instrucciones; el runtime de la caché sigue siendo `0.1.4`. No se ha instalado
`0.1.5` ni se declara completada su actualización local. Después de la revisión
independiente, sigue el proceso de actualización y respaldo descrito en
[Instalar AIKit](plugin-aikit.md); registra el resultado nuevo en
`.aikit/deployment-report.json` y realiza una auditoría posterior antes de
afirmar qué versión está activa.

## Límites

- No se ha verificado cada chat, modelo o tarifa, ni se calcula porcentaje de
  ahorro de tokens o cuota.
- La selección Free/Go es una decisión del coordinador con información del
  catálogo y resultados observados; no existe selección automática en runtime.
- Un `free_limit_reached` aislado no prueba agotamiento de todo Free. Permisos,
  autenticación y privacidad no se eluden al cambiar de modelo o transporte.
- Una instalación observada no garantiza que las herramientas aparezcan en todo
  chat ni que futuras ejecuciones tengan cuota o disponibilidad.
- La revisión técnica final independiente de esta entrega aún no está registrada.
