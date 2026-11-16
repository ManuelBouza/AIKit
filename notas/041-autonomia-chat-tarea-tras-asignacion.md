# Autonomía del Chat de Tarea tras recibir su encargo

Fecha: 2026-11-16.
Estado inicial: Pendiente de debatir.
Estado actual: Fuentes ajustadas y comunicación reconocida por ambos chats;
validación y revisión completadas. Caché instalada sin actualizar.

## Corrección del usuario

En los encargos 028 y 040, los chats terminaron esperando otra orden del
Coordinador. Manuel identifica un error de diseño: una vez realizado el encargo,
el Chat de Tarea es independiente para ejecutarlo y el usuario interactúa
directamente con él. Reporta al Coordinador cuando corresponde y recibe de él
información relevante. El Coordinador no dirige cada paso de su ejecución.

La aclaración se revisa aplicando Director de Ideas. No equivale a iniciar las
implementaciones durante esta revisión ni concede permisos nuevos.

## Diagnóstico

- La preparación separada se convirtió en una puerta de autorización recurrente:
  verificar identidad y checkout terminó exigiendo una segunda orden incluso
  cuando se podría trasladar un encargo completo y autorizado desde el comienzo.
- Se confundió canal entre agentes con canal de interacción del usuario.
- El bootstrap prohibió mensajes y no trasladó una autorización verificable de
  reportes posteriores. Las herramientas mantienen sus requisitos de autorización.
- Los documentos describían ejecución y decisiones técnicas propias de la tarea,
  pero no explicitaban la continuidad directa con el usuario ni qué esperas son
  obligatorias y cuáles no.

## Diseño recomendado

1. El encargo completo contiene objetivo, alcance autorizado, recursos, criterios,
   restricciones, dependencias reales, comunicación y decisiones pendientes.
   Distinguir encargo ejecutable de preparación sin ejecución autorizada.
2. La tarea verifica su identidad y entorno. Con encargo ejecutable y requisitos
   satisfechos, continúa sin una segunda orden del Coordinador. Solo detiene la
   operación que dependa de un requisito esencial ausente o contradictorio.
3. El usuario conversa directamente con cada tarea. El chat conduce investigación,
   decisiones de su alcance, implementación, pruebas y correcciones. Solicita al
   usuario las decisiones materiales que le correspondan, sin intermediación
   rutinaria del Coordinador. Conserva las reglas de autorización aplicables.
4. La tarea comunica hitos relevantes, bloqueos, decisiones que afecten al proyecto,
   cambios de alcance autorizados por el usuario, necesidades de coordinación,
   solicitudes de integración y cierre. No reporta cada comando ni espera un
   acuse para continuar trabajo independiente permitido.
5. El Coordinador conserva registro, visión transversal, dependencias, asignaciones,
   integración y salud de los datos finales. Puede aportar información pertinente
   y trasladar decisiones autorizadas; sus mensajes no son autorización humana
   ni una orden que sustituya una decisión directa del usuario.
6. Una decisión del usuario tomada en una tarea se conserva y comunica con origen
   verificable. Si afecta a otras tareas, recursos compartidos o integración,
   coordinar antes de operar sobre esa dependencia. Continuar las partes propias
   que sigan siendo independientes y autorizadas. Ante instrucciones contradictorias,
   aclararlas sin sobrescribir trabajo ni escoger silenciosamente una versión.
7. Se conserva la integración centralizada: la tarea solicita integración, no
   escribe ramas principales ni registro canónico. Revisión técnica delegada,
   limpieza y archivado conservan sus requisitos existentes.
8. Autonomía de responsabilidad no promete ejecución permanente en segundo plano:
   las posibilidades de continuar o activar otro turno dependen del cliente.

## Contraste documental

- [OpenAI: orquestación y handoffs](https://developers.openai.com/api/docs/guides/agents/orchestration):
  distingue especialistas llamados como capacidades acotadas de especialistas
  que asumen la conversación. No equiparar un Chat de Tarea persistente con una
  llamada de subagente cuyo único interlocutor es el gestor.
- [Anthropic: agentes efectivos](https://www.anthropic.com/engineering/building-effective-agents):
  distingue flujos predefinidos y agentes que dirigen dinámicamente sus procesos;
  los agentes pueden trabajar con el usuario, pedir aclaraciones y realizar
  comprobaciones durante la ejecución.

Aplicación a AIKit: propuesta propia de coordinación central del proyecto con
ejecución y conversación autónomas por tarea; no adopción de un framework ni
afirmación de capacidades nativas de mensajería o ejecución no verificadas.

## Aceptación del ajuste posterior

- Encargo ejecutable válido: bootstrap y continuación sin segunda orden.
- Decisión de diseño pendiente: consulta al usuario en el Chat de Tarea.
- Coordinador sin responder a un aviso: el trabajo independiente continúa.
- Dependencia compartida o integración pendiente: espera solo de esa operación.
- Decisión transversal del usuario en una tarea: evidencia y reporte al Coordinador.
- Cambios contradictorios: conciliación explícita sin pérdida de información.

## Relación y alcance

- [025 — Coordinación](025-coordinador-global-chats-autonomos.md).
- [032 — Coordinador escritor](032-coordinador-escritor-mensajes-tareas.md).
- [Encargos de prueba](../coordinacion/paralelo-028-040/ENCARGOS.md).

Fuentes de coordinación, setup y guías ajustadas; encargos revisados y trasladados
con autorización humana contrastada. Ambos chats reconocen la autonomía y han
reportado por el cauce autorizado. Validación estructural de ambas skills y
15 pruebas de exportación correctas; revisión independiente de tres enfoques y
evaluación independiente de seis casos completadas. La evaluación comprueba
decisiones descritas, no garantiza ejecución nativa permanente. Se observan
además reconocimiento, continuidad y reportes reales de ambos chats. No se
modifica la caché instalada ni las ramas de 028/040.

Especificación y triage: [spec 041](../_bmad-output/implementation-artifacts/spec-041-autonomia-chat-tarea.md).
La especificación se produjo con bmad-build, que no generó `.memlog.md`;
no procede inventar una fuente de bmad-spec para esta entrega.
Huellas de las fuentes revisadas: [INSTRUCCIONES.json](../coordinacion/paralelo-028-040/INSTRUCCIONES.json).

La prueba encuentra un pendiente distinto: preparar BMAD y dependencias de forma
aislada en los worktrees. Responsable de coordinar su resolución: Coordinador.
028 mantiene la decisión visual directamente con el usuario; 040 declara bloqueo
de entorno. No confundir ese bloqueo técnico con una segunda orden de ejecución.
