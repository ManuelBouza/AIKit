---
title: 'Filtrar avisos entre chats por necesidad operativa'
type: 'bugfix'
created: '2026-11-17'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/notas/044-notificaciones-por-impacto-y-coste.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Los mensajes sin efecto operativo activan otros chats y consumen inferencia.
Manuel elige la opción 1 de la nota 044: enviar ahora solo ante acción o decisión
operativa del destinatario que deba atenderse ahora, o riesgo que empeore al esperar.
Registrar o actualizar el tablero no justifica por sí solo un envío.

El Coordinador comunica dependencias resueltas, conflictos, decisiones aplicables
y resultados de integración que habiliten trabajo, corrección o limpieza. La
tarea solicita intervención fuera de su alcance, registro previo de una entrega
nueva, revisión/integración y cierre verificado que permita archivar o liberar
recursos. Los avances ordinarios, pruebas, commits/push sin impacto, esperas de
decisiones del usuario dentro de la tarea y acuses sin acción se conservan sin
despertar otro chat. Una pausa/cancelación humana detiene lo afectado; exige aviso
inmediato si hay trabajo compartido, integración o reservas que detener/corregir,
y en otro caso se recoge después. Resolver bloqueos propios dentro del alcance.

Las tareas mantienen título, estado y evidencia recuperable en su entorno
autorizado. Solo el Coordinador escribe el canónico. En revisión solicitada por el
usuario o necesaria para asignar, integrar o cerrar, recoge datos disponibles sin
pedir una mera repetición ni recorrer todos los historiales por comando. El tablero
refleja el último estado incorporado; generar no acredita conciliación de cada chat.

Conservar autonomía, autorización humana persistente, identidad, deduplicación y
reconciliación de envíos inciertos. Agrupar novedades que puedan esperar; no crear
bucles de confirmaciones. Esto refina relevancia, no obliga a pedir consentimiento
por cada aviso útil ni altera permisos, pausas o alcance de una tarea. No añade
mensajería directa entre tareas ni ejecución fuera de turnos activos.

</frozen-after-approval>

## Implementation Notes

- Patches tras triage independiente, BH1–BH4: referencia recuperable de novedades
  sin aviso, conservación verificada antes de retirar recursos, contraste de
  origen/encargo/vigencia en recogida y contexto aplazado al reanudar directamente.
  Se reutilizan medios existentes, sin archivo obligatorio, esquema o runtime nuevo.
  Coordinación validada de nuevo; exportación 1passed en5.21s y diffcheck código0.
  Resultados añadidos a docs/validacion-avisos-044.md sin borrar triage ni intent.

- Implementación: filtro central en responsabilidades y rutas desde entrypoint,
  avisos y seguimiento; acuses consultables separados de envío. Setup y cinco
  guías armonizados, y tablero documentado como instantánea incorporada. Sin
  cambios de esquema, runtime, instalación o versión. Resultado de validadores y
  exportación registrado en `docs/validacion-avisos-044.md`; evaluación independiente
  y cierre a cargo del Coordinador.

- Ruta oneshot: sin decisiones abiertas, irreversibles, esquema, API o runtime nuevos. Baseline:
  `231e8508a35394dd0ed0df2113bb404f315792af`. El Coordinador registra IMP-0006 y
  ya generó su vista antes de la implementación delegada.
- Cobertura: `coordinacion-chats` resuelve roles, destinatarios, autorización,
  trazabilidad, acuses e integración; `aikit-setup` ofrece activación local.
  `skill-creator` orienta a un ajuste estrecho en referencias. Director de Ideas
  ya maduró 044. Carencia: «hito/cambio relevante» y comunicar discrepancias permite
  envíos sin acción; seguimiento no distingue alta nueva de progreso ordinario.
  Reutilizar sin skill, flag, preferencia o framework adicional.
- Herramientas nativas consultadas: `read_thread` consulta sin enviar;
  `send_message_to_thread` exige autorización humana verificable y puede activar
  turno; `wait_threads` ofrece snapshots, no incorporación al registro. No existe
  buzón silencioso ni registro acreditado por transporte. Sin consulta accesible,
  conservar pendientes y explicar límites, sin prometer recuperación automática.
- Mapa de cambio: `packaging/skills/coordinacion-chats/SKILL.md` expresa el filtro
  compartido y enruta; `references/responsabilidades.md` concentra selección y
  revisión pertinente; `references/avisos.md` separa conservación/acuse de envío;
  `references/seguimiento.md` distingue alta previa de actualización diferida y
  explica frescura. No alterar los campos v1 ni identidades del tracker.
- `packaging/skills/aikit-setup/SKILL.md`: ajustar «reporta hitos relevantes» y
  «notifica cambios relevantes», remitiendo al filtro sin opción nueva del
  instalador. Armonizar `docs/coordinacion/coordinador.md`,
  `tarea.md`, `flujo-avisos.md`, `guia-uso.md` y
  `contrato-responsabilidades-propuesto.md` donde reproduzcan instrucciones
  anteriores; preservar contexto histórico. `docs/tablero-notas.md`: aclaración
  de snapshot incorporado, sin cambio de UI. No reescribir specs históricos.
- El Coordinador mantiene notas, índice, tickets y contrato; el ejecutor no los
  modifica. Sin instalación, versión, push, preferencias, nuevos chats, avisos
  reales, automatización ni recursos028/040. No exigir Git/BMAD/Python al usuario.
- Validación proporcional: `quick_validate.py` oficial de skill-creator para
  coordinación y setup; `uv run --locked pytest
  tests/test_build_aikit.py::test_export_and_install -q` para exportación e
  identidad de fuentes, referencias y preservación; `git diff --check`.
  Registrar entorno, comandos y resultados reales, sin tests que comparen prosa.
- Evaluación independiente de decisiones con casos ficticios y sin efectos
  externos: push sin impacto; progreso/espera local; bloqueo propio y externo;
  dependencia resuelta; nueva entrega sin ticket; integración lista y resultado
  habilitante; cierre con limpieza pendiente y verificada; pausa con/sin operación
  compartida; tarea pausada con cambio aplazable; acuse puro; revisión pertinente
  con datos accesibles/no accesibles; envío incierto. Contrastar selección,
  preservación, siguiente operación y límites de autorización en ambos roles.
  Estas decisiones descritas no prueban ahorro cuantificado ni ejecución nativa.
- Fuentes primarias contrastadas en 044: Anthropic sobre agentes efectivos y
  sistema multiagente; valorar beneficio/coste. Política de AIKit, sin extrapolar cifras.

## Review Triage Log

Revisor independiente: subagente nativo `avisos044_behavior`, 2026-11-17.
Dictamen postpatch: **accepted** sobre el snapshot SHA256 inferior. Revisión
limitada a BH1–BH5 y preservación del filtro/autonomía; no repitió los 18 casos
ni los comandos ya ejecutados. Se leyó el registro del ejecutor: validador de
coordinación código 0, exportación 1 passed en 5.21 s y diff check código 0.
Esos comandos son evidencia declarada del ejecutor, no ejecución del revisor.
La primera evaluación declarativa y el contraste completo están en
`docs/validacion-avisos-044.md`. No acredita mensajería nativa ni ahorro medido.

| Hallazgo | Clasificación / resolución | Evidencia postpatch |
| --- | --- | --- |
| BH1. Localización de novedades ordinarias | low / patch aceptado | `responsabilidades.md:158-160` y `tarea.md:56-59` exigen ubicación o referencia recuperable y accesibilidad real; historial identificable suficiente, sin archivo nuevo. |
| BH2. Supervivencia de novedades sin aviso | low / patch aceptado | `tarea.md:127-128` extiende expresamente la comprobación previa a retirar recursos a novedades y evidencias pendientes de recogida aunque no haya aviso. |
| BH3. Procedencia y vigencia al recoger sin aviso | medium / patch aceptado | `responsabilidades.md:165-167` y `coordinador.md:59-61` contrastan origen, encargo y vigencia, conservan fuente/versionado o fecha disponible y discrepancias; una fecha no prueba actualidad. |
| BH4. Contexto al reanudar directamente | medium / patch aceptado | `responsabilidades.md:207-210` y `tarea.md:21-24` verifican contexto aplazado antes de la operación afectada, conservan limitación y continúan lo independiente autorizado; sin segunda orden ni sincronización global. |
| BH5. Evidencia humana del filtro en contrato | low / patch aceptado | `PROYECTO.md:32-34` contiene turno y mensaje comunicados como verificados por el Coordinador. El revisor comprobó su incorporación exacta, sin repetir la lectura del historial humano. |
| BH6. Antecedente ambiguo en setup | false / reject | La versión leída ya tenía oración independiente «El Coordinador gestiona dependencias e integración»; no requería otro patch. |
| EP1. Intervención ante respuesta incierta | false / reject | Consulta y conciliación preceden al reenvío; pedir datos exige una operación actual. «Intervención» no obliga a mensaje automático. |
| EP2. Formato portable de archivo pendiente | false / reject | Cierre de entrega y archivo de chat se separan; mantener pendiente visible no exige un esquema nuevo. |
| EP3. Ubicación universal de persistencia | false / reject | Ubicación autorizada, verificación y referencia dependen legítimamente del entorno; BH2 precisa la supervivencia sin inventar ruta universal. |
| EP4. Recuperación al reanudar sin garantía automática | medium / patch parcial aceptado | Parte operativa cubierta por BH4; rechazo de automatización, vigilancia o inbox. No constituye otro defecto independiente. |

Los patches conservan el requisito de acción/decisión ahora o riesgo creciente
antes de enviar; no convierten registro, accesibilidad o reanudación en avisos
rutinarios. Tampoco amplían permisos, levantan pausas ni condicionan todo el
encargo a una respuesta: se limita la espera a la operación afectada. Sin
correcciones técnicas pendientes dentro del alcance revisado. El estado done
corresponde a esta entrega en fuentes, no a instalación ni publicación.

### Snapshot de archivos de producto y contrato

Hashes SHA256 de bytes locales obtenidos por el revisor con `Get-FileHash`.
Incluyen las superficies de producto modificadas de esta entrega y el contrato
local BH5; excluyen notas, tickets y artefactos de validación/spec editados después.

| Archivo | SHA256 |
| --- | --- |
| `packaging/skills/coordinacion-chats/SKILL.md` | `dbb58c36ff2014f8bcb5f6b462c65d9d25975a173f028e9a8c1d1a9be744990a` |
| `packaging/skills/coordinacion-chats/references/responsabilidades.md` | `dc880bf9c015b228a5e51a4129488b0e90963f3312875788f114128a64b81eab` |
| `packaging/skills/coordinacion-chats/references/avisos.md` | `2729bfa3f722348d71532d70edc4248a4758cc766cfcb5a81710804de71d8252` |
| `packaging/skills/coordinacion-chats/references/seguimiento.md` | `baf28a7930d1573000aabf2a1afc1e6073df924e46822a4361bab7e4ef50651f` |
| `packaging/skills/aikit-setup/SKILL.md` | `c00afbd382f530db750cdc4aba363558d46ccdfddaf359c058968f5db2d9a0a4` |
| `docs/coordinacion/contrato-responsabilidades-propuesto.md` | `cde610fdba896f8e58699feb3becca1cdae366f08dc76f5b5907766627421645` |
| `docs/coordinacion/coordinador.md` | `83755cbf89e04ae7ee66fb3f98061e66731449da95f435d39b425e0ef0242371` |
| `docs/coordinacion/flujo-avisos.md` | `6d37cfd021254da35ac643ccde56877c29cd7f8dd1f4bcc91df24d13529f91d5` |
| `docs/coordinacion/guia-uso.md` | `9d2e333b4c39a19756bf9427ce2e16ddf0d73d17f2b4f34176bbbcb46bab03af` |
| `docs/coordinacion/tarea.md` | `89135ed05815904bea0f444261d962826dbff7ef5b2f425d31a291c9df4d647a` |
| `docs/tablero-notas.md` | `3fdd4340ca1e631b29c62924da0a870f1e4a4f480f06581bb27f1021ede9d917` |
| `coordinacion/PROYECTO.md` | `554ee33932a0317004ef00d836c5d13a18fe0751a22ecfea0aabbd2b67c40b0f` |
