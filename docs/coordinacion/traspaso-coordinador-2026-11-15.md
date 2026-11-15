# Traspaso del coordinador AIKit — 2026-11-15

## Autoridad y alcance

Manuel solicitó probar coordinación en el chat actual y, una vez comprobada,
empezar con un chat coordinador nuevo. Chat saliente:
`01a1da03-23f1-7eb0-b0a0-5cb5184e6941`. Raíz de proyecto:
`C:/Manuel/Projects/AIKit`. Proyecto Codex: `4ac70d03-d0eb-43ab-a38c-7bb84ff7d85b`.
Coordinador entrante creado: `01a1dfb7-840e-7243-8577-ff634015c31f`, host local,
título `AIKit · Coordinador principal`. Recepción comprobada por el saliente:
turno `01a1dfb7-867d-7942-8266-9812fe19ba02` completado; confirma acceso al
traspaso, skill, nota, instalación y resultado de prueba y conserva sus límites.
El saliente cede la coordinación conversacional al entrante y cambia su título a
`AIKit · Coordinador anterior · Traspaso verificado`. No hay dos escritores
autorizados del registro de prueba: el histórico permanece bajo identidad fija
del saliente y no recibirá avisos del proyecto operativo.

El entrante coordina trabajo y decisiones con el usuario. Los registros del
auxiliar creados durante pruebas son históricos y no se transfieren cambiando
IDs a mano. No hay registro transaccional de producción activado: el prototipo
no soporta relevo, reasignación ni nuevos ciclos. No afirmar lo contrario.

## Resultado de la prueba del chat saliente

Se reutilizó la tarea de prueba `01a1db23-4c5b-7453-a692-64727ccfc2a7`, worktree
ad1c, sin crear otro chat de tarea ni worktree. Título verificado:
`[Finalizada] T-001 · PRUEBA coordinación principal`.

Registro privado de prueba:
`C:/Manuel/Projects/AIKit/.aikit/025-prueba-chat-principal/canonico`.
Proyecto ficticio `a5ac91bc-6929-4839-b8ae-f2b4bc6d7c91`, ciclo 1, epoch 1,
T-001; coordinador fijo saliente. Aviso
`9f656643-1ad8-4549-8852-fa284ebaa37c`, revisión 1, Finalizada.

La tarea conservó el JSON original; el coordinador contrastó origen mediante
historial, copió los bytes y validó con parser estricto antes de aplicar.
Resultado aplicado, reconstrucción de índices, consulta desde instancia nueva
y duplicado controlado con idéntico recibo aplicado. Sin escritura.lock final.
Evidencia ignorada: `.aikit/025-prueba-chat-principal/resultado.json`, entrada
original y diario canónico. Runners de prueba `.aikit/025-*-principal.mjs`.
No son un adaptador de recepción de producción. La prueba no acredita archivado,
programación diaria ni integración Git. No hubo entrega de código que integrar.

La tarea contrastó después el aviso íntegro con el canónico, verificó decisión
aplicado, proyecto/asignación/ciclo y guardó un acuse local. Turno
`01a1dfb6-7eba-7f63-bb2a-95bcb9d19e77`, completado. No retiró recursos reutilizados
de pruebas previas; conservó aviso y evidencia y no creó ramas/worktrees nuevos.

## Estado de producto y entorno

- AIKit preferencias 0.1.1 instalado en perfil habitual desde catálogo
  aikit-setup-prueba-20261108; tres skills verificadas desde caché. Fuente privada
  `.aikit/025-actualizacion-0.1.1`; conservar esa carpeta. Ver
  [actualización](../actualizacion-aikit-025.md).
- Skill coordinacion-chats instruccional; auxiliar TypeScript en
  packages/aikit-installer, Node 24. No runtime Python requerido por el auxiliar.
- CLI del PATH 0.153.4 está desfasada. Usar la CLI actual del paquete Desktop
  identificado en [diagnóstico](../resolucion-validacion-sandbox-windows.md),
  actualmente 0.169.0-alpha.11.1 y MXC. No repetir arreglos de ACL del sandbox legado.
- Carpeta compartida de prueba retirada del proyecto por Manuel y eliminada;
  no volver a añadirla. Avisos por mensajería/historial; coordinador único escritor.
- Commit c990cb0 empaqueta coordinación. Hay cambios previos sin commit en
  diagnóstico, notas, AGENTS.md y nuevas ideas: inspeccionar y preservar, no
  incluirlos a ciegas en otro commit. No hay push autorizado.
- No invocar OpenCode. BMAD es del desarrollo de este repositorio, no requisito
  del producto AIKit. Antes de resolver procedimientos investigar documentación.

## Pendientes directamente relacionados

Nota 025 y especificaciones en `_bmad-output/specs/spec-coordinacion-chats`.
Distribución verificada, activación completa pendiente. Roles en
docs/coordinacion/{coordinador,tarea,flujo-avisos}.md.
No implementar automáticamente todos los pendientes:

- Concretar alta y registro operativo de este proyecto bajo el nuevo coordinador,
  conservando evidencia y distinguiendo el registro histórico de prueba.
- Relevo/administración del auxiliar, pendientes y nuevos ciclos no implementados.
- Automatización en el chat coordinador, frecuencia configurable en setup (diaria
  propuesta); si cambia el coordinador deberá retargetearse. Aún no se ha creado.
- Archivado por coordinador tras fin/cancelación, con persistencia y limpieza a
  cargo de la tarea; no borrar recursos ajenos ni trabajo no integrado.
- Coordinador protege datos finales y ramas principales; tareas gestionan sus
  ramas. Sin Git, secuenciar escrituras; paralelismo requiere decisión del usuario.

## Arranque del nuevo chat

Leer este traspaso, AGENTS.md, la skill instalada y la nota 025; comprobar estado
con herramientas. Confirmar identidad y recepción del contexto al usuario y
explicar el siguiente paso concreto de activación. No crear chats, enviar
mensajes, ejecutar automatizaciones, archivar ni modificar el canónico de prueba
durante este arranque. El saliente verifica la recepción antes de dejar de coordinar.
