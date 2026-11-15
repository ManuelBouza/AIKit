---
title: Primer auxiliar local de registro y recuperación
type: feature
created: 2026-11-14
status: done
completed: 2026-11-15
route: dispatch
baseline_commit: 1d687f994ee9cc31391039fb3ffa9c2e23c8bbbf
review_loop_iteration: 0
context:
  - _bmad-output/planning-artifacts/architecture/architecture-coordinacion-almacenamiento/almacenamiento-v1.md
  - docs/calidad-python-typescript.md
---

<frozen-after-approval>

## Intent

Implementar y probar el primer auxiliar de registro y recuperación de la nota 025,
autorizado por go. El coordinador escribe una fuente canónica; las tareas declaran
avisos. Esta entrega demuestra el almacenamiento en un proyecto ficticio vacío,
no activa la coordinación ni integra herramientas de chats reales.

## Boundaries & Constraints

TypeScript en el paquete existente, JavaScript ESM compilado, Node 24, sin Python
ni dependencias nuevas de producción. Reutilizar windows-replace/replace-recovery.
Conservar configuraciones y cambios previos. Modelo JSON/Markdown v1 y AD-1 a AD-5
del diseño aceptado; elecciones concretas del documento v1 son la base aprobada
por la autorización de implementar el prototipo. Primer ciclo y asignación fija.
No se implementa todavía relevo, reasignación ni apertura de ciclos adicionales:
se rechazan/retienen como pendientes, nunca se simulan. Excluir empaquetado público,
setup, automatización, mensajes, limpieza o archivado de chats, integración Git y
restauración automática de bloqueos. No declarar durabilidad ante apagones o red.

## I/O & Edge-Case Matrix

| Caso | Entrada | Resultado |
| --- | --- | --- |
| Aviso nuevo | Identidad/ciclo correctos, revisión superior | Estado y acuse juntos |
| Duplicado | Mismo ID y contenido | Acuse existente, sin nueva aplicación |
| Antiguo | Revisión inferior | Recepción antigua, estado conservado |
| Contradicción | ID con otro contenido o revisión incompatible | Incidente, original intacto |
| Procedencia/ciclo | No corresponden a asignación vigente | Pendiente, sin cambiar current |
| Documento inválido | Duplicados JSON, versión, campos, UTF-8 o números inválidos | Error/incierto sin mutación |
| Fallo de publicación | Antes/después de sustitución | Diario y bloqueo conservados |
| Recuperación | Base/propuesta verificables o versión posterior con evidencia | Completar una vez o conservar incertidumbre |
| Bloqueo ocupado | Incluido archivo vacío | Sin segundo escritor ni borrado por edad |

</frozen-after-approval>

## Code Map

- packages/aikit-installer/src/windows-replace.ts: sustitución y diagnóstico Windows.
- packages/aikit-installer/src/coordination/schema.ts: validación estricta y formatos.
- packages/aikit-installer/src/coordination/state.ts: decisiones de avisos puras.
- packages/aikit-installer/src/coordination/store.ts: exclusión, diario y recuperación.
- packages/aikit-installer/src/coordination-demo.ts: demostración solo en carpeta vacía
  explícita; no cambia el comando/bin del instalador ni el exportador de AIKit.
- packages/aikit-installer/test/coordination-*.test.cjs: pruebas Node de comportamiento.
- docs/auxiliar-coordinacion.md: uso del demo, límites y recuperación supervisada.
- package.json, tsconfig y ESLint existentes: extender comandos/alcance solo si necesario.

## Tasks & Acceptance

- [x] Esquema y parser estrictos; igualdad canónica, acuses y conflictos por proyecto.
- [x] Motor de estado puro para avisos, sin escrituras de tareas ni regresión de revisión.
- [x] Store con raíz absoluta verificada, un escritor, generación/epoch comprobados,
  preparación completa y sincronizada, respaldo, publicación y relectura antes de acuse.
- [x] Recuperación de operaciones no completadas sin repetir decisiones y sin
  restaurar una versión anterior encima de una posterior. Ambigüedad conserva todo.
- [x] Consulta del acuse sin afirmar registro si falta o es inválido; índice derivado.
- [x] Demo reproducible en carpeta ficticia, con resultado comprobable y sin afectar
  datos existentes. Probar fallos y concurrencia con procesos y adaptadores controlados.
- [x] Ejecutar typecheck, lint, formato y pruebas; revisión independiente centrada
  en riesgos que las herramientas no comprueban; actualizar nota y tablero.

Given un proyecto ficticio vacío, when se inicializa y aplica un aviso válido,
then el estado y el acuse persistidos se pueden consultar tras reabrir el store.
Given un duplicado/aviso antiguo/contradictorio, when se procesa, then no reemplaza
la revisión vigente ni destruye el aviso original.
Given una interrupción en cada fase, when se recupera tras supervisar el bloqueo,
then se conserva base o propuesta completa y nunca se declara éxito de un parcial.
Given dos escritores, when compiten, then solo uno publica y el otro informa bloqueo.

## Implementation Notes

- Autorización existente: go para implementar/probar el primer auxiliar; sin
  decisiones materiales nuevas ni acciones irreversibles. Los cambios previos
  proceden de esta conversación y se preservan. No pedir aprobaciones intermedias.
- Prueba local primero, sin prometer completar todas las capacidades de la nota 025.
- En el prototipo, identidad y procedencia son referencias proporcionadas por el
  llamante de prueba; no autentican chats de Codex ni sustituyen sus permisos.
- Revisar preservación de permisos/ACL con los adaptadores disponibles; cualquier
  resultado incierto detiene la publicación. Las pruebas del demo no acreditan
  una política organizativa de acceso para proyectos reales.
- Los derivados se reconstruyen mediante llamada explícita posterior a apply,
  como en el demo. El acuse acredita TAREA; no presupone índices al día. La prueba
  de fallo de derivados conserva el acuse y permite reconstruir después.
- Evidencia comprobada por el coordinador: npm run verify código 0 (75 pruebas
  correctas, tres omisiones explícitas del sandbox), y demo ACL nativo fuera del
  sandbox código 0 sin omisiones. Corpus adicional de parser: 1000 casos válidos
  y tres claves duplicadas, sin errores. La matriz está cubierta por las pruebas
  coordination-schema/store y la sonda nativa independiente.
- Cambios anteriores preservados: el diff de revisión se limita a los nuevos
  módulos, pruebas y documentación del auxiliar; comparación global conservada
  aparte en .aikit/uv-temp, sin reabrir trabajos ya verificados.

## Verification

- npm run verify desde packages/aikit-installer: tipos, lint, formato y suite Node.
- AIKIT_REQUIRE_NATIVE_ACL=yes con test-name-pattern demo nativo fuera del sandbox:
  exige ruta positiva ACL/File.Replace, sin permitir omitirla por la política.
- Evidencia: .aikit/025-verify-final.log y .aikit/025-native-acl.log.

## Review Triage Log

- H1 medium, patch: reproducidos 1.0000000000000001→1 y 1e-999→0; validar el
  literal antes de conversión con pérdida. Fuente: strictJson y sonda Node.
- H2 medium, patch: mistune convierte la referencia entre comillas JSON en imagen
  activa; las referencias deben quedar como texto literal en el derivado.
- H3 medium, patch: decide excluye explícitamente recibos pendientes de la búsqueda
  de revisión incompatible; falta registrar contradicción sin perder información.
- H4 high, patch: búsqueda global de IDs solo usa receipts; un ID conservado solo
  en incidents puede llegar a aplicarse con contenido distinto. Debe permanecer reservado.
- H5 high, patch: ACL comprueba Allow y conserva Owner en SDDL pero no valida quién
  es el propietario; falta cubrir su capacidad implícita de modificar la DACL.
- H6 high, patch: operaciones y raíz verificadas no acreditan ACL de .control ni
  lock; un padre interno permisivo puede permitir sustituir la exclusión.
- H7 medium, patch: rename POSIX de temporal 0600 altera base 0400 admitida antes
  del chequeo posterior. Preservar modo o rechazar antes de publicación.
- H8 medium, patch: el ejecutor solo libera lock tras retorno normal; rechazos
  conocidos sin operación incierta dejan bloqueo innecesario. Separar ambos casos.
- H9 medium, patch: consulta ACL carece de timeout; limitarla y fallar de forma cerrada.
- E1 high, patch, mismo grupo que H4: corroborada la reutilización de ID presente
  únicamente en incidents; la revisión de casos límite indica el mismo guard ausente.
- V1 medium, patch: hueco de pruebas pre-verificado; rebuildIndex se llama pero no
  se comprueban enlaces ni referencias aplicadas/excluidas. Añadir aserciones de contenido.
- V2 medium, patch: hueco de pruebas pre-verificado; el caso que anuncia enlaces
  solo prueba raíz relativa, no enlaces/junctions reales ni destino externo intacto.

Todos son déficits de implementación/pruebas frente a invariantes ya fijadas;
no requieren nuevas capacidades ni decisiones de alcance. Las correcciones se
delegaron al mismo implementador y se verificarán con herramientas tras su retorno.

### Cierre de correcciones — 2026-11-15

H1–H9, E1 y V1–V2 corregidos: números decimales exactos antes de conversión,
referencias cercadas como JSON literal, contradicciones pendientes y reserva de
IDs presentes solo en incidentes; propietario, padres y lock verificados, timeout
ACL de 15 s, rechazo POSIX antes de publicación y liberación limitada a rechazos
explícitos conocidos. Se mantienen los bloqueos de operaciones inciertas.
Regresiones comprueban contenido de ambos derivados y enlaces/junctions reales.

Comprobación final del coordinador: npm run verify código 0, 89 pruebas totales,
83 correctas y seis omisiones explícitas (POSIX nativo en Windows y restricciones
del sandbox). La sonda nativa posterior a correcciones fuera del sandbox pasó
los tres casos Windows: raíz enlazada, subdirectorio enlazado y demo ACL/File.Replace,
sin omisiones. Corpus adicional de parser: 1000 casos válidos y tres duplicados,
correctos también tras las correcciones. No hay hallazgos de revisión abiertos
dentro de este alcance. No se repitió Python: no cambió su código ni configuración.

Evidencia final: .aikit/025-verificacion-coordinador.log,
.aikit/025-review-fixes-tests.log y .aikit/025-review-fixes-native.log.
