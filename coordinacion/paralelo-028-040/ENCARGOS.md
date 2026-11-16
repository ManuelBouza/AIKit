# Preparación de dos tareas en paralelo

Fecha: 2026-11-16.
Estado actual: ambos encargos pausados por indicación expresa de Manuel el
2026-11-16 para continuar la corrección en el chat Coordinador. Se conservan
ramas, worktrees, cambios y evidencias. No ejecutar nuevas operaciones ni
reanudar por las condiciones ejecutables históricas que figuran debajo.

La pausa se trasladó a ambos chats con herramientas nativas. La confirmación
de cada sesión se referencia en ACUSES.md. No se archivan ni retiran recursos.

## Condiciones vigentes — sustituyen las esperas de preparación anteriores

Las huellas de las nueve fuentes revisadas se conservan en
[INSTRUCCIONES.json](INSTRUCCIONES.json). Identifican la entrega de fuentes,
no afirman que la caché instalada o los worktrees hayan sido actualizados.
Las condiciones efectivamente enviadas se conservan como texto inmutable de los
mensajes nativos de este turno del Coordinador, y su reconocimiento se referencia
abajo. El historial identifica la instrucción recibida aunque este archivo cambie.

Manuel aprueba el ajuste con «go» en el turno del Coordinador
`01a1e584-117f-7481-b452-b1487fe9d7f5`, mensaje humano
`01a1e584-1276-77f0-8b9e-22c493f623aa`. Aprueba eliminar la segunda orden de
arranque y permitir la continuidad directa con él en ambas tareas.
Su aclaración y autorización de reportes relevantes figura en el turno
`01a1e572-51bc-76a1-a8b3-d2775fa11d34`, mensaje humano
`01a1e572-5278-7b71-ac05-15ae8b3edc7a`. Las tareas pueden contrastar ambos
mensajes con `read_thread` en el chat Coordinador, sin tratar este resumen como
sustituto de la autorización humana.

- Los dos encargos conservan sus límites específicos de abajo y son ejecutables
  dentro del alcance autorizado. Tras comprobar el contexto, cada chat continúa
  investigación, decisiones de su ámbito, implementación y verificación con el
  usuario, sin solicitar otra orden del Coordinador. En 028 se concreta primero
  el diseño visual y se consulta directamente al usuario cualquier decisión material.
- Sustituida la prohibición inicial de reportar: cada tarea conserva sus avisos
  y comunica al Coordinador los hitos, bloqueos, decisiones con impacto transversal,
  cambios de alcance autorizados, necesidades de integración y cierre. Verificar
  la autorización humana aplicable con las referencias anteriores. No se habilita
  comunicación directa entre tareas ni se amplían permisos por un aviso.
- Un acuse pendiente o la inactividad del Coordinador no detiene trabajo propio
  independiente. Solo espera la operación afectada por autorización, decisión,
  dependencia o integración pendiente; informa del motivo y continúa lo permitido.
- El usuario dirige cada tarea en su chat. El Coordinador puede aportar contexto
  relevante y gestiona dependencias, registro y destino final; no controla cada
  paso ni reemplaza decisiones directas del usuario. Conservar y reportar decisiones
  que afecten al proyecto con origen contrastable. Conciliar contradicciones antes
  de operar sobre el recurso afectado.
- Solo el Coordinador modifica el registro canónico y las ramas principales.
  Se conservan las revisiones técnicas delegadas y la integración secuencial.
  Sin nuevas instalaciones, publicación, push ni retirada de recursos autorizados.
- Las fuentes revisadas están en la raíz principal bajo
  `packaging/skills/coordinacion-chats/`; las copias de la caché y de los worktrees
  anteriores al ajuste no se consideran actualizadas. Leer las nuevas instrucciones
  por su ruta absoluta; no copiar cambios del Coordinador a la rama de tarea.

## Historial de preparación (no prescribe el flujo vigente)

Envío del ajuste: el Coordinador empleó `send_message_to_thread` una vez para
cada chat, con las condiciones vigentes y referencias humanas de autorización.
Ambas herramientas devolvieron el `threadId` esperado sin error. Esto acredita
envío. El texto original se conserva
en el historial de ambos chats y en el turno del Coordinador citado arriba.

Reconocimiento observado mediante `wait_threads`, con ambas sesiones activas:

- 028, turno `01a1e586-ea1b-7c81-ae55-223665c6b69d`, mensaje
  `msg_0db3b5842777b04c016afb456d1b5c87d1a37e39eb6b9884d7`: confirma
  autorización y contrato contrastados y comienza investigación del tablero.
- 040, turno `01a1e587-0672-7ac0-97b1-2c1095116561`, mensaje
  `msg_04fda8e4ecae1c40016afb4570424087d1b55d3fb4aba40ba9`: confirma
  que puede avanzar directamente con el usuario y comunicar hitos al Coordinador.

Este reconocimiento no certifica implementación completa ni resultado de pruebas;
cada tarea conserva responsabilidad y continuidad propias.

## Revisión de diseño — 2026-11-16

Manuel corrige la dependencia de una nueva orden del Coordinador tras asignar
una tarea: el usuario interactúa directamente con cada Chat de Tarea y este
ejecuta autónomamente su encargo autorizado, reportando cuando corresponda.
La espera descrita abajo documenta la preparación histórica, no una regla de
dependencia permanente. Véase [nota 041](../../notas/041-autonomia-chat-tarea-tras-asignacion.md).
Esta revisión no arranca las implementaciones ni afirma haber comunicado ya
el nuevo criterio a los chats. Queda pendiente ajustar y trasladar sus encargos.

## Asignaciones creadas

- 028: chat `01a1e56b-ca0d-7370-b82d-7ca39b03e5ba`, host `local`;
  worktree `C:/Users/Manuel/.codex/worktrees/f8ad/AIKit`;
  rama prevista `tarea/028-tablero-notas`.
- 040: chat `01a1e56b-ec96-7960-b2ee-7f1d3f7366fb`, host `local`;
  worktree `C:/Users/Manuel/.codex/worktrees/a9c0/AIKit`;
  rama prevista `tarea/040-contraste-director`.

Inventario nativo y `git worktree list` confirman ambos checkouts y ramas.
Las dos sesiones reconocen el contrato y un índice propio; ambas finalizaron
su bootstrap sin investigación ni implementación y esperan orden de ejecución.

### Evidencia de preparación y recepción

- 028: turno `01a1e56b-cc9d-7680-b233-aeff629b759f`, respuesta final
  `msg_0db3b5842777b04c016afb3e8a933487d1920c81f4d7914639`.
  Confirma HEAD de base, rama creada, árbol limpio e índice propio en
  `C:/Manuel/Projects/AIKit/.git/worktrees/AIKit/index`.
- 040: turno `01a1e56b-ef97-71f0-abba-e4d2ce03731b`, respuesta final
  `msg_04fda8e4ecae1c40016afb3e8f99a887d18d9f4e40d56dec2d`.
  Confirma HEAD de base, rama creada, árbol limpio e índice propio en
  `C:/Manuel/Projects/AIKit/.git/worktrees/AIKit1/index`.
- El Coordinador consulta ambas respuestas con `wait_threads`; estado nativo
  `idle`, turnos completados sin error. Los originales completos se recuperan
  mediante el historial de cada chat y las referencias anteriores. Esta entrada
  es un resumen de recepción de bootstrap, no un acuse transaccional v1.
- Comprobación del Coordinador: tres worktrees, `main` conservada en la raíz,
  ramas propias de 028 y 040 en sus respectivos checkouts; `git diff --check`
  correcto. Backlog actualizado y tablero regenerado: 40 notas.

## Autoridad y modalidad

Manuel aprueba con «Go» la recomendación del Coordinador de preparar los
encargos y crear dos Chats de Tarea con worktrees separados para las notas 028
y 040. Esta etapa prepara las asignaciones; no inicia las implementaciones.
Coordinador vigente: `01a1da03-23f1-7eb0-b0a0-5cb5184e6941`.
Registro manual único: `C:/Manuel/Projects/AIKit/coordinacion/`.
Base comprobada al preparar: `6e302919625f185d615b6c9f74bd4c2780d933fb`.

Cada chat confirma identidad, cwd, HEAD, estado Git y lectura del contrato antes
de recibir la orden de ejecución. No escribe en la carpeta principal ni en su
registro canónico. Conserva avisos y evidencias en su worktree. Los avisos llevan
referencia estable, revisión creciente, estado, resumen y referencias completas;
el Coordinador contrasta el origen y conserva el original y su acuse.

La comunicación de trabajo es mediante el Coordinador. La aprobación humana de
esta etapa procede del historial de su chat, que las tareas pueden consultar;
un mensaje del Coordinador no sustituye la autorización humana necesaria para
otros envíos. Sin autorización verificable, devolver el resultado en el propio
chat para su consulta con herramientas nativas.

## Encargo 028 — Tablero

- Resultado previsto: modernización del tablero local, detalle centrado,
  navegación por teclado y adaptación a pantallas pequeñas, conservando Markdown
  como fuente de verdad y las funcionalidades existentes.
- Antes de implementar: investigar referencias oficiales y especializadas,
  concretar una propuesta visual; devolver las decisiones materiales al usuario.
- Archivos previstos: `scripts/tablero_notas.py`, `scripts/tablero_notas.html`,
  `tests/test_tablero_notas.py`, `docs/tablero-notas.md` y artefactos BMAD propios
  de 028. Ajustar este límite con el Coordinador si aparecen dependencias.
- No incluye la prueba con Sites, publicación ni instalación de herramientas.
- Verificación prevista: controles Python pertinentes y comprobación visual y de
  accesibilidad de la interacción; revisión técnica independiente de la entrega.

## Encargo 040 — Director de Ideas

- Resultado previsto: contraste explícito de la idea madurada con documentación
  oficial y fuentes especializadas antes de recomendar su implementación.
- Criterios: los de `notas/040-director-ideas-contraste-documental.md`; profundidad
  proporcional, fuentes vigentes, reutilización de investigación válida,
  separación de hechos y supuestos, cambios materiales devueltos al usuario.
- Archivos previstos: `packaging/skills/director-de-ideas/` y documentación,
  pruebas de comportamiento y artefactos BMAD propios de 040.
- Explorar cobertura instalada y seguir `skill-creator` antes de modificar la
  skill; no duplicar BMAD ni convertirlo en requisito del producto.
- No instala la nueva skill en el perfil ni cambia preferencias globales.
- Verificación prevista: validación de skill, escenarios de comportamiento y
  revisión independiente vinculada a la versión exacta entregada.

## Responsabilidades compartidas

El Coordinador mantiene notas, backlog y registro; regenera el tablero tras
modificar notas. Los chats solicitan esos cambios mediante sus entregas.
Cambios compartidos de setup, exportación o pruebas generales requieren reparto
explícito antes de escribir. Ninguna tarea cambia ramas principales ni integra
la otra. Cada una trabaja en checkout e índice propios, conserva evidencia y
solicita integración con versión exacta, controles y pendientes. El Coordinador
delega revisión técnica y coordina integración secuencial. Sin push ni publicación
autorizados por esta preparación. Limpieza y archivado se coordinan tras
persistencia y verificación de integración; no se retiran recursos ahora.

## Ruta de desarrollo prevista

Consulta realizada de `bmad-help`, catálogo instalado y configuración resuelta.
Para ambas: `bmad-build` al autorizar ejecución, con investigación y definición
visual previas en 028; `skill-creator` complementa la modificación de 040.
Esta selección no ejecuta esos flujos ni aprueba decisiones materiales pendientes.
