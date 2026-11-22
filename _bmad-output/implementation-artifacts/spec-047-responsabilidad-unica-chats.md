---
title: 'Responsabilidad única de los chats en AIKit'
type: 'feature'
created: '2026-11-22'
status: 'done'
baseline_commit: '31a71f89f29171b90b0896ed7c5f66e67be9ca93'
route: 'dispatch'
review_loop_iteration: 0
context: ['notas/047-responsabilidad-unica-chats.md', '_bmad-output/planning-artifacts/plan-047-responsabilidad-unica-chats.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problema:** Las solicitudes ajenas a la responsabilidad de un chat se mezclan
con su trabajo y pueden duplicar encargos.

**Enfoque:** Ofrecer en `aikit-setup` una activación optativa por proyecto.
Cada chat tiene una responsabilidad, se identifica por su ID nativo completo,
y refleja su estado en el título. Para solicitudes fuera de alcance, el chat
recomienda reutilizar, abrir o bifurcar según el contexto disponible.

## Boundaries & Constraints

**Siempre:** Un inventario por raíz local explícita, sin exigir Git. ID estable,
título `[Estado] Proyecto · Responsabilidad breve`, cinco estados acordados:
Disponible, En curso, En espera, Pausado y Cerrado. Guardar fecha, ID de origen
en forks y motivo y condición de continuación cuando esté en espera o pausado.
El inventario prevalece si el título no puede actualizarse. Consultar sin
escribir. Activar por decisión explícita y preservar instrucciones ajenas.

En un worktree, reutilizar la raíz de inventario configurada para el proyecto.
El directorio de trabajo y la rama del chat no determinan esa raíz. No crear
inventarios por worktree ni usar Git para fusionar copias del inventario.

**Nunca:** Activar en el perfil global, inventar IDs, copiar conversaciones al
inventario, recuperar el antiguo Coordinador, crear servicios externos,
enviar mensajes por rutina o crear/bifurcar por inferir una autorización.
Sin instalación en el perfil habitual, publicación ni push en esta entrega.

## I/O & Edge-Case Matrix

| Escenario | Entrada | Resultado | Si falta evidencia |
| --- | --- | --- | --- |
| Dentro del alcance | Responsabilidad actual cubre la solicitud | Continuar en el chat actual | Aclarar límites si hay duda material |
| Fuera del alcance | Otro chat vigente cubre el tema | Recomendarlo por título e identidad | Informar de coincidencias ambiguas |
| Nueva responsabilidad | Basta un resumen / se necesita historial | Recomendar chat nuevo / fork, respectivamente | Ofrecer traslado manual si falta la acción nativa |
| Registro o título | ID confirmado / ID no verificable | Mantener registro por ID / dejar alta pendiente | Si falla el título, conservar el estado registrado e informar |
| Escritura concurrente | Dos altas distintas o dos cambios de la misma ficha | Conservar altas distintas; confirmar versión esperada al editar | Rechazar edición obsoleta y permitir relectura |
| Worktree con acceso a la raíz configurada | Permisos de lectura y escritura | Consultar y actualizar el mismo inventario que en el checkout principal | Aplicar el mismo control de versiones de ficha |
| Worktree con acceso limitado | Solo lectura o sin acceso | Consultar si puede leer y dejar pendiente la actualización que no pueda aplicar | Informar del permiso que falta y ofrecer traslado manual; nunca crear una copia |

</frozen-after-approval>

## Code Map

- `packaging/skills/aikit-setup/SKILL.md` y `references/capacidades.json`
  ya describen y detectan flujos guiados. Reutilizar la modalidad.
- `scripts/build_aikit.py` valida cobertura y referencias del paquete.
- `packages/aikit-installer/src/cli.ts` ya aplica vistas previas, guardias de
  rutas y respaldo de `AGENTS.md`. Reutilizar la protección de escrituras.
- Base del principal: `bb84e316491a42be7da124ab5b098503930420bb`. Copia limpia
  para la implementación en `.aikit/build-047/source`. Los cambios previos de
  preferencias y notas quedan en el árbol principal.

## Tasks & Acceptance

**Ejecución:**

- [x] `packaging/skills/aikit-setup/references/`: declarar la capacidad y
  documentar el recorrido local, los destinos, las autorizaciones y el fallback.
- [x] `packages/aikit-installer/src/`: añadir operación explícita de proyecto
  por raíz absoluta para consulta y cambios con vista previa, y un registro
  local por ID con igualdad de revisión esperada y publicación segura.
- [x] `scripts/build_aikit.py` y `docs/complemento-aikit-independiente.md`:
  incluir recursos y documentar activación, desactivación y límites.
- [x] `tests/test_build_aikit.py` y `packages/aikit-installer/test/`:
  comprobar cobertura, estados, escrituras seguras y recorrido aislado.

**Aceptación:**

- Dado un proyecto con instrucciones ajenas, al consultar no cambian sus
  archivos. Al activar se añade una sola regla y al desactivar se retira solo
  esa regla, conservando el inventario.
- Dados dos chats del proyecto, al consultar la raíz autorizada ambos leen las
  mismas fichas. Cambiar estado y nombre conserva el ID. Un fork queda como
  ficha distinta y enlaza su origen sin copiar texto de conversación.
- Dados el checkout principal y un worktree, al consultar con los permisos
  adecuados ambos leen el mismo inventario y pueden verificar cambios cruzados.
  Con escritura denegada, la consulta sigue disponible si hay lectura. Sin
  acceso de lectura, la disponibilidad de destinos queda sin verificar.
- Dadas dos modificaciones a partir de la misma revisión, al aplicarlas la
  segunda se detecta y no pisa la primera. Un fallo de acceso no habilita un
  registro alternativo.
- Dada una solicitud de prueba, al aplicar la regla se distingue cada destino.
  Se acredita por separado el comportamiento de setup y del título en el
  cliente, con evidencia explícita si una acción nativa queda sin comprobar.

## Implementation Notes

- La implementación y las pruebas de producto se realizan en la copia limpia
  indicada en el mapa. Esta especificación y sus fuentes de contexto se leen
  desde el principal. Reutilizar las dependencias instaladas del principal si
  la copia no puede prepararlas sin red. No integrar, confirmar ni publicar
  modificaciones del principal desde la copia.
- La CLI compilada activó la referencia desde el checkout principal y un
  worktree real de prueba. Una ficha escrita desde el worktree se leyó desde el
  principal. Al desactivar el worktree se recuperó el hash inicial de su
  AGENTS.md y siguió disponible la ficha en el inventario compartido.
- Los escenarios de destino se evaluaron sobre fichas ficticias aplicando la
  guía. Los errores de acceso se simularon mediante EACCES sobre un worktree
  real. El renombrado y fork en conversaciones nativas siguen sin ejercitarse.
- Entrega en el commit aislado `c39816eae298622494bc5f729f43b5b17469e31f`.
  Tras corregir los hallazgos de las tres revisiones, pasaron 63 pruebas del
  instalador y 29 del exportador. Cuatro casos de Node se omitieron por
  plataforma o permisos. `git apply --check --whitespace=error-all` confirmó
  que el parche final aplica sobre el principal con su trabajo previo intacto.
- Integración en el principal: los diez archivos de producto coinciden con
  la entrega, normalizando finales de línea. El paquete combinado con las
  preferencias locales pasó las 29 pruebas del exportador. El renombrado y
  fork en chats nativos siguen pendientes de prueba.

## Spec Change Log

## Review Triage Log

| Capa | Hallazgo | Veredicto y ruta |
| --- | --- | --- |
| Blind | Baja altera CRLF adyacente | Medio, corrección. La reproducción dejó un CR aislado. |
| Blind | Override impide retirar bloque local | Medio, corrección. La baja puede retirar su bloque sin tocar el override. |
| Blind | Estado legible sin abrir las fichas | Medio, corrección. Enumerar nombres no comprueba permisos ni JSON. |
| Blind | Worktree admite otra raíz | Medio, corrección. Contrastar la configuración del principal cuando se pueda identificar. |
| Blind | Alias de CODEX_HOME evita comprobación | Medio, corrección. La comprobación debe incluir el destino real del alias. |
| Blind | ACL explícita de Windows se pierde al reemplazar ficha | Medio, corrección. El temporal hereda su ACL del directorio. |
| Blind | Renombrado concurrente puede confirmar estado obsoleto | Medio, corrección del protocolo. Comparar contra la revisión vigente. |
| Blind | Falta recorrido nativo de cliente | Medio, verificación pendiente. Exportación y escenarios guiados no prueban reconocimiento, título ni fork nativo. |
| Edge | Separadores CRLF mutilados | Medio, misma corrección de CRLF. |
| Edge | Ruta Windows sin unidad depende del cwd | Medio, corrección. En Windows la raíz del drive se resuelve desde el proceso. |
| Edge | Confirmación de título con revisión anterior | Medio, misma corrección de sincronización. |
| Edge | Umask POSIX cambia permisos de la ficha | Medio, corrección. Aplicar al temporal el modo del archivo existente. |
| Edge | Alias de perfil habilita cambio global | Medio, misma corrección de rutas de perfil. |
| Gap | Denegación de escritura por ficha omitida | Medio, prueba dirigida de apertura r+ sin impedir crear el bloqueo. |
| Gap | Concurrente no fuerza revisión entre lectura y bloqueo | Medio, prueba determinista del segundo control. |
| Gap | Marcadores cruzados GO y chats sin prueba | Medio, prueba de rechazo y conservación de bytes. |
| Gap | CRLF adyacente dañado | Medio, misma corrección de CRLF; cubrir conversión real del bloque. |

## Design Notes

Propuesta técnica: inventario JSON por ficha bajo una carpeta local del proyecto.
Derivar el nombre de archivo del ID de forma segura y validar la identidad de
la ficha. Serializar cambios a la misma ficha con bloqueo exclusivo y validar
la versión dentro del bloqueo. Setup debe mostrar la raíz de inventario y
comprobar el acceso efectivo de la sesión. Si la sesión está en un worktree,
activar la referencia local a la raíz compartida requiere identificarla y
verificarla. Un fork de chat no aísla por sí solo el checkout.

## Verification

- `npm run verify` desde `packages/aikit-installer`.
- `uv run --locked pytest tests/test_build_aikit.py`.
- Exportar el complemento y probar la activación y desactivación de la
  capacidad guiada en un proyecto ficticio, incluido un proyecto sin Git.
- Probar desde un worktree real del proyecto ficticio y comprobar los casos
  de acceso completo, solo lectura y sin acceso. Identificar si la restricción
  se comprobó en el sandbox del cliente o se simuló en un control del instalador.
