# Validación del filtro de avisos044

Fecha: 2026-11-17. Encargo: IMP-0006. Alcance: instrucciones en fuentes;
el complemento instalado0.1.5 y los chats028/040 no se modificaron.

## Entorno y cobertura

Windows, PowerShell, Python mediante uv y lockfile existente. Se reutilizan
coordinacion-chats, sus tres referencias, aikit-setup y guías documentales.
La carencia era selección por «hito/cambio relevante» sin necesidad operativa
actual del receptor. El filtro central vive en responsabilidades.md, con rutas
desde las otras superficies. No se crea servicio, buzón, flag ni dependencia.

## Comprobaciones ejecutadas

| Comando | Esperado | Observado |
| --- | --- | --- |
| `python C:/Users/Manuel/.codex/skills/.system/skill-creator/scripts/quick_validate.py packaging/skills/coordinacion-chats` | Skill válida | Código0, Skill is valid |
| Mismo validador sobre `packaging/skills/aikit-setup` | Skill válida | Código0, Skill is valid |
| `uv run --locked pytest tests/test_build_aikit.py::test_export_and_install -q` | Exportación idéntica, referencias y conservación correctas | 1passed en5.18s |
| `git diff --check` | Sin errores de whitespace | Código0; solo avisos de conversión LF/CRLF de Git |

Para uv se usaron TEMP, TMP y UV_CACHE_DIR apuntando a `.aikit/uv-temp`
únicamente en el proceso. No se alteraron variables globales ni dependencias.
El primer ensayo de exportación detectó que su comprobación de enlaces trata
fragmentos como parte del archivo. Se cambió la ruta del entrypoint a la referencia
completa, conservando el filtro localizable por título; el segundo ensayo pasó.
No se modificó el test ni el exportador para acomodar la prosa.

## Límites

Los validadores comprueban estructura y empaquetado, no decisiones de un agente.
La evaluación independiente de casos y la revisión postpatch constan abajo.
No se enviaron mensajes reales ni se midió ahorro de tokens o latencia.
La lectura nativa de historiales y el envío siguen dependiendo de herramientas
y autorizaciones disponibles. Estado conservado, enviado e incorporado siguen
siendo distintos; el tablero puede tener avances pendientes de conciliación.

## Evaluación independiente de comportamiento

Evaluación declarativa del 2026-11-17 por el subagente nativo
`avisos044_behavior`. Primera pasada limitada a la skill y sus tres referencias,
sin leer nota, spec ni informes; segunda pasada de triage con spec044, diff y
guías. No hubo mensajería real, inferencia externa, subdelegación ni cambios de
producto por este evaluador. Se presupone identidad, asignación, cauce y
autorización comprobados. «Enviar» describe una decisión simulada, no una acción
ejecutada. Los resultados de comandos anteriores pertenecen a la implementación;
esta evaluación no los repitió ni acredita su autoría independiente.

| Caso | Qué se conserva | Envío ahora: destinatario y propósito | Operación que continúa o se detiene |
| --- | --- | --- | --- |
| 1. Push del Coordinador sin efecto sobre diseño | Cambio y versión | Ninguno | Diseño continúa |
| 2. Pruebas completadas y avance | Evidencias y estado propios recuperables | Ninguno por el mero hito | Continúa encargo autorizado |
| 3. Espera de color elegido por su usuario | Decisión pendiente, origen, estado y título propios | Al usuario de la tarea si falta plantear la elección; ningún aviso rutinario al Coordinador | Espera solo lo dependiente del color |
| 4. Fallo de lint corregible por la tarea | Diagnóstico, corrección y verificación | Ninguno por rutina | Corrige dentro del alcance |
| 5. Recurso reservado por otra tarea | Recurso, necesidad, conflicto e impacto | Al Coordinador: coordinar acceso/reserva | Espera uso conflictivo; continúa trabajo independiente |
| 6. Dependencia resuelta por el Coordinador | Evidencia y versión de resolución | A la tarea afectada: indicar trabajo habilitado | Continúa lo autorizado; no levanta pausa humana |
| 7. Entrega nueva pedida por usuario sin ticket | Origen humano, alcance y búsqueda de encargo existente | Al Coordinador: alta y generación de vista | Detiene solo implementación nueva hasta registro y vista correctos |
| 8. Entrega lista para revisión/integración | Versión exacta, destino, evidencias y pendientes | Al Coordinador: solicitar revisión/integración | Espera operación dependiente; continúa trabajo independiente |
| 9. Integración permite limpieza | Resultado y referencia exacta | Coordinador a tarea: resultado operativo habilitante | Tarea verifica cuando corresponda y limpia con autorización aplicable |
| 10. Terminado con recursos sin persistir | Trabajo, recursos y pendiente de preservación | Ninguno si puede resolverlo; al Coordinador si requiere intervención o hay riesgo creciente | Persiste y limpia sin pérdida; no declara cierre acreditado ni retira recurso necesario |
| 11. Persistencia/limpieza verificadas; archivo pendiente | Evidencias y aviso de cierre recuperable | Un aviso al Coordinador: archivado/liberación pendiente | Coordinador archiva con capacidad y autorización; sin cadena de confirmaciones |
| 12. Pausa humana sin recurso compartido | Origen, alcance y estado de pausa | Ninguno si no hay otro impacto operativo | Detiene lo pausado; recoge después |
| 13. Pausa con integración en cola | Origen y operación afectada | Al Coordinador: detener/corregir integración | Detiene integración afectada y trabajo pausado |
| 14. Documentación útil solo al reanudar tarea pausada | Cambio, versión y contexto pendiente | Ninguno ahora | Conserva pausa; recupera contexto al reanudar autorizadamente |
| 15. Recepción simple y acuse canónico | Original, decisión y acuse verificable consultable | Ninguno sin operación pendiente | Sin acuse del acuse; sigue lo autorizado |
| 16. Respuesta de envío incierta | Original íntegro, referencias e incertidumbre | Primero consulta registro e historial; envío posterior solo justificado y autorizado | No reenvía a ciegas; espera solo operación dependiente de decisión desconocida |
| 17. Revisión de dos tareas con historiales accesibles | Evidencias pertinentes y conclusiones trazables | Ninguna petición para repetir datos disponibles | Coordinador consulta, concilia e incorpora; genera vista si modifica fuentes |
| 18. Historial inaccesible; solo refrescar tablero | Limitación y novedades potencialmente no conciliadas | Ninguno para refrescar vista | Genera desde incorporado; no afirma revisión reciente de chats |

La selección en los 18 casos es consistente con el intent de spec044. No se
observó contradicción que obligue a avisos ordinarios ni acuses rutinarios. La
primera pasada detectó cuatro posibles insuficiencias, reevaluadas a continuación
con el contexto documental completo; no se consideran automáticamente defectos.

## Triage técnico independiente

Clasificación: high/medium/low expresan impacto; false descarta el defecto en el
contexto leído; maybe-false conserva una duda sin evidencia suficiente. Patch
propone corrección acotada al Coordinador, defer deja un límite explícito y reject
rechaza la propuesta como defecto. Este evaluador solo modifica este documento;
no aplica los patches de producto. Las líneas siguientes corresponden a la lectura
previa a las correcciones que coordine el responsable y pueden desplazarse.

| ID | Clasificación / decisión | Evidencia y contraste | Tratamiento acotado |
| --- | --- | --- | --- |
| BH1. Novedades ordinarias sin ubicación/referencia recuperable explícita | low / patch | `responsabilidades.md:158-164` ya exige que sean recuperables y permite consultar historiales; `:96` exige ubicación de evidencias al encargar. Por tanto no existe ausencia total de conservación. Sin embargo, `tarea.md:51-56` exige registrar ubicación y accesibilidad solo después de preparar un aviso: queda implícito cómo localizar una novedad que nunca produjo aviso. | Precisar referencia recuperable en el medio autorizado ya disponible y accesibilidad real al recogerla. Un historial identificable basta; no crear buzón, archivo obligatorio ni esquema nuevo. |
| BH2. Preservación al retirar worktree menciona solo aviso y envío | low / patch | `tarea.md:106-110` ya ordena persistir trabajo y evidencias antes de limpiar, y prohíbe retirar trabajo no persistido; `avisos.md:92-95` mantiene deber general de persistencia. `tarea.md:113-117` sí concreta supervivencia y copia verificada únicamente para avisos no reconciliados. Es una asimetría de precisión, no permiso expreso de borrar novedades. | Incluir novedades/evidencias pendientes de recogida en la comprobación de supervivencia, referencia y verificación antes de retirar el recurso; reutilizar mecanismo existente. |
| BH3. Recogida sin aviso no concreta procedencia y versión/fecha | medium / patch | `coordinador.md:53-59` habilita incorporar datos/historiales, mientras `:63-81` contrasta origen y versión bajo Recepción de avisos. El filtro nuevo puede recoger una noticia sin aviso formal. El contrato general exige referencias recuperables y contexto vigente, pero falta trasladar expresamente el contraste a esa ruta de incorporación. Una entrada antigua accesible no demuestra estado actual. | Antes de incorporar, contrastar origen, tarea y vigencia; conservar referencia de fuente y versión o fecha disponible, y discrepancias. No usar fecha como orden total ni imponer nuevos campos v1. |
| BH4. Contexto aplazado sin comprobación explícita al reanudar directamente el usuario | medium / patch | `responsabilidades.md:200-205` aplaza contexto hasta retomar. `:98-101` y `tarea.md:16-19` exigen comprobar contexto antes de ejecutar un encargo, lo cual mitiga el problema. `tarea.md:68` solo nombra consultar acuse al retomar; no nombra cambios aplazados del Coordinador. La reanudación directa puede conservar una visión anterior aunque esté autorizada. | Explicitar comprobación del contexto pertinente disponible al reanudar antes de la operación afectada. Sin acceso, conservar limitación y pedir solo datos necesarios ahora; sin segundo permiso de arranque ni sincronización obligatoria de todo el proyecto. |
| BH5. Contrato identifica filtro por fecha/nota sin referencia humana exacta | low / patch | `PROYECTO.md:33-43` identifica elección y fecha, pero otras autorizaciones del mismo contrato incluyen turno y mensaje. La skill requiere evidencia humana verificable. Root comunicó referencia contrastada: turno `01a1eae0-937b-7213-861d-7404d1bf4a34`, mensaje `01a1eae0-9480-7e52-9284-59ef998f6cdb`. Este evaluador no volvió a leer ese historial. | Añadir referencia mínima recuperable que aporte el Coordinador, sin ampliar la autorización. Evidencia de contraste humano delegada al root y declarada como tal. |
| BH6. Antecedente ambiguo de «que gestiona dependencias» en setup | false / reject | La versión efectivamente leída de `aikit-setup/SKILL.md:32-35` dice «conserva avances ordinarios para revisión. El Coordinador gestiona dependencias e integración». La oración independiente tiene sujeto explícito; el defecto descrito ya no está presente. | No aplicar otro patch por este hallazgo; conservar la redacción leída. |
| EP1. «Respuesta incierta requiere intervención» no identifica quién | false / reject | `avisos.md:55-61` exige consultar antes de reenviar; `tarea.md:80-84` precisa que sin acceso se solicita acuse solo si una operación actual lo necesita y en otro caso se conserva para revisión. El filtro también se aplica a ambos roles. La intervención puede ser conciliación local, sin mensaje automático. | El contexto ya resuelve la duda de la primera pasada; no hace falta nueva regla. |
| EP2. Falta formato portable de entrega finalizada con archivado pendiente | false / reject | `seguimiento.md:39-41` separa cierre acreditado de cerrar un chat; `tarea.md:119-123` exige pendientes visibles por separado y asigna el archivo al Coordinador. La skill no debe imponer un esquema portable que el usuario no eligió. | Usar representación acordada en el proyecto y mantener pendiente visible; no inventar campo/estado. |
| EP3. Falta ubicación universal de preservación fuera del recurso retirado | false / reject | `tarea.md:113-117` exige ubicación autorizada, copia verificada y referencia, o mantener recurso pendiente. El medio depende legítimamente del cliente y los permisos. No prescribir una ruta universal evita duplicar registros o imponer dependencias. | Rechazar procedimiento universal. La precisión para novedades sin aviso se trata exclusivamente en BH2. |
| EP4. Recogida al reanudar sin garantía automática | medium / patch parcial | El límite de ejecución automática es explícito en `responsabilidades.md:133-135,168-170,212-214` y en spec044. No es defecto carecer de automatización. Sí permanece el chequeo operativo de contexto aplazado descrito en BH4. | Reutilizar únicamente el patch de BH4. Rechazar garantía de recuperación automática, vigilancia o inbox. No contar como segundo defecto independiente. |

Conclusión del triage: tres mejoras low de claridad/trazabilidad (BH1, BH2 y BH5),
dos medium de contraste operativo (BH3 y BH4), cuatro propuestas descartadas
(BH6, EP1, EP2 y EP3), y EP4 absorbida por BH4 con rechazo de su interpretación
automática. Ningún hallazgo high. Las mejoras no justifican nuevo runtime,
esquema, buzón, automatización ni autorización humana adicional. La aceptación
final corresponde al Coordinador tras decidir/aplicar los ajustes y verificar
el diff resultante; este documento no declara probada la mensajería nativa.

## Patches posteriores al triage

El ejecutor aplicó BH1–BH4 por decisión del Coordinador: las novedades sin aviso
conservan ubicación/referencia recuperable en el medio existente y accesibilidad
contrastada; su persistencia se verifica antes de retirar el recurso que las
contiene. La recogida sin aviso contrasta origen, encargo y vigencia, conservando
fuente y versión o fecha disponible sin ordenar por fecha. La reanudación directa
comprueba contexto aplazado disponible antes de la operación afectada; si falta,
detiene solo esa operación y continúa lo independiente autorizado. No exige
archivo nuevo, otro arranque, sincronización global ni avisos rutinarios.

Repetición tras estos cambios: `quick_validate.py` sobre coordinación devuelve
Skill is valid, código0; exportación `test_export_and_install` devuelve 1passed
en5.21s; `git diff --check` código0 con los avisos LF/CRLF ya documentados.
Setup no cambió después de su validación anterior. BH5 lo atiende el Coordinador
en su contrato; este ejecutor no modificó registro, notas ni AGENTS. No se
aplicaron BH6/EP1–EP3 descartados ni se duplicó EP4.

## Dictamen independiente postpatch

**accepted**, 2026-11-17, revisor nativo `avisos044_behavior`. Se contrastaron los
patches BH1–BH4 y la referencia BH5 efectivamente incorporados, manteniendo el
filtro, la autorización persistente, las pausas y la continuación del trabajo
independiente. No se repitieron los 18 casos ni los comandos del ejecutor. No
quedan correcciones técnicas exigidas por esta revisión acotada.

BH1 conserva referencia recuperable sin archivo obligatorio; BH2 extiende la
supervivencia comprobada a novedades sin aviso; BH3 exige origen, encargo y
vigencia antes de incorporar; BH4 comprueba contexto aplazado al reanudar sin
otro arranque ni sincronización global. BH5 incorpora exactamente los IDs que el
Coordinador comunicó como contrastados; el revisor no volvió a leer ese historial.
La clasificación completa de los diez hallazgos y los SHA256 de los once archivos
de producto más el contrato están en `## Review Triage Log` de
`_bmad-output/implementation-artifacts/spec-044-avisos-por-impacto.md`.

La aceptación corresponde al snapshot de fuentes identificado allí. No instala
el complemento, no publica cambios ni acredita funcionamiento del transporte.
