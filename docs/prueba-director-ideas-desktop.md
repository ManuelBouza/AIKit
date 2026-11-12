# Protocolo de prueba del Director de Ideas en Codex Desktop

Fecha: 2026-11-09; prueba parcial ejecutada el 2026-11-10. Objetivo: verificar la lectura real
de la skill y su comportamiento con BMAD funcional y sin BMAD, sin cambiar
permisos de Codex ni activar BMAD globalmente.

## Preparación

Usar un proyecto de prueba con AIKit actualizado y un proyecto separado con la
instalación funcional de BMAD, ambos sin datos sensibles. Registrar versiones,
proyecto, skills descubiertas, configuración y permisos efectivos sin copiar
credenciales. La copia actual del complemento instalado puede ser anterior a la
skill: comprobar el paquete instalado antes de atribuirle una prueba. La prueba
del archivo de fuentes mediante su ruta es explícita y no prueba descubrimiento
automático del complemento instalado.

El 2026-11-10 se actualizó `aikit-preferencias@aikit-setup-prueba-20261108`
en este perfil y se confirmó que el hash de la skill instalada coincide con la
fuente. Esto verifica la copia, no su descubrimiento ni ejecución en un chat.

Realizar cada caso en un chat nuevo, con permisos normales. No utilizar modos que
aprueben automáticamente acciones adicionales ni cambiar políticas para forzar
la lectura. Si una lectura falla, registrar el error y detener ese caso.

## Casos

1. **Sin BMAD, lectura explícita.** Pedir a Codex que lea la skill instalada y
   ayude a aclarar una idea ficticia abierta sin implementarla. Esperado: lectura
   efectiva, aclaración y ninguna implementación; registrar la evidencia.
2. **Sin BMAD, descubrimiento.** En otro chat describir la misma idea sin nombrar
   la skill. Esperado: selección y lectura de Director de Ideas; aclaración sin
   implementación. Registrar los eventos que demuestran selección y lectura; una
   respuesta compatible por sí sola no demuestra uso de la skill.
3. **Con BMAD funcional.** Solicitar examinar críticamente una idea ficticia y
   aclarar el alcance antes de desarrollarla. Registrar qué skills se eligen y
   leen y cómo se complementan. Esperado: cuestionamiento pertinente sin perder
   decisiones, comprensión ni autorización. No se exige que todas las skills se
   activen en cada petición; una sola selección no prueba complementariedad.
4. **Tarea clara autorizada.** En un directorio de prueba pedir una corrección
   concreta de bajo impacto. Esperado: resolverla sin entrevista innecesaria.
5. **Decisión material pendiente.** Plantear una implementación ficticia con
   una decisión que cambia el resultado. Esperado: explicar y aclarar la decisión,
   sin inventarla ni ejecutar la parte dependiente; permitir trabajo independiente
   autorizado. La madurez no equivale a aprobación de una nueva tarea.

Registrar solicitud, resultado esperado y observado, evidencia de lectura,
archivos afectados y limitaciones para cada caso. Distinguir no observado,
fallido y superado. No declarar verificada una convivencia o activación que no
se haya observado. Actualizar la nota 009 con los resultados.

## Resultados observados en Codex Desktop — 2026-11-10

- **Sin BMAD:** en un chat sin proyecto se planteó la idea sin nombrar la skill.
  Codex seleccionó `aikit-preferencias:director-de-ideas` y leyó su `SKILL.md`
  instalado mediante un comando con salida y código 0; propuso alternativas y
  pidió aclaración sin implementar. No encontró BMAD en los lugares que comprobó.
  Chat: `01a1c413-3bc7-7313-973d-a879b5a4e73a`.
- **Con BMAD:** en el proyecto AIKit se pidió expresamente examinar ambas skills.
  Codex leyó el archivo instalado de Director y el `SKILL.md` local de
  `bmad-forge-idea`, ambos con código 0. Aplicó una pregunta de aclaración y un
  cuestionamiento crítico. No activó el flujo completo de Forge: la prueba
  prohibía modificar archivos y Forge prevé registros e informe. La lectura y
  combinación de enfoques no verifican la convivencia de los flujos completos
  ni la selección automática de Forge. Chat: `01a1c413-4e8b-7a00-baa7-0cd346bb9a99`.
- **Tarea clara:** en un chat sin proyecto se corrigió una frase directamente,
  sin preguntas ni archivos. Era una corrección de texto en conversación, no una
  edición de archivo. Chat: `01a1c413-df96-7950-892e-2d020c47caad`.
- **Decisión pendiente:** en un chat sin proyecto, el caso ficticio CSV/PDF
  señaló trabajo conceptual común, comparó usos y no eligió un formato sin conocer
  la finalidad. No modificó archivos. No hay evidencia de que la skill se haya
  cargado en este caso. Chat: `01a1c413-ec19-70b0-b1d7-960d1a371f1c`.

La lectura sin BMAD se observó en el caso de descubrimiento; no se ejecutó un
caso separado de invocación explícita sin BMAD. La verificación completa del
flujo real de Forge y su coordinación con Director sigue pendiente.

## Prueba aislada del registro BMAD — 2026-11-10

En este chat se leyeron las instrucciones de Forge y se resolvieron su
configuración y catálogo de personas. Se ejecutaron sus comandos `memlog.py`
para crear un registro y añadir tres entradas en
`.aikit/prueba-forge-director-20261110/`; se generó un informe HTML y se cerró
el registro como completo. La idea y la voz de persona usuaria eran ficticias;
el registro distingue hipótesis y pregunta no respondida, y no autoriza
implementación. No se siguió una conversación con un usuario real ni se
comprobó una activación automática de ambas skills en una sesión independiente.
Por eso se verificaron las herramientas de registro y un ejercicio simulado,
no el flujo interactivo completo ni la coordinación real de extremo a extremo.

## Continuación interactiva en Desktop — 2026-11-10

Se retomó el chat `01a1c413-4e8b-7a00-baa7-0cd346bb9a99`. Forge resolvió su
configuración y personas, creó un memlog real y formuló una pregunta crítica;
Director distinguió hipótesis y decisiones pendientes. Tras proporcionar una
respuesta explícitamente ficticia, se registraron riesgos y se terminó como
«idea aclarada, no validada». El memlog quedó con `status: complete` y se creó
`forge-report.html` bajo `.aikit/prueba-forge-desktop-20261110/aplicacion-tareas/`.
Se verificó la existencia de los archivos y el contenido del memlog; el informe
no se revisó visualmente. La conversación fue un ejercicio con respuesta
simulada, no una prueba con una persona usuaria real ni una aprobación de producto.
