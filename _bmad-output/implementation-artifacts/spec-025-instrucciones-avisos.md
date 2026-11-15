---
title: 'Instrucciones de avisos para coordinador y tarea'
type: 'chore'
created: '2026-11-15'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Incorporar el flujo probado de avisos y acuses a instrucciones reutilizables para
el coordinador y el chat de tarea. El usuario autorizó esta tarea mediante go.
Conservar el contrato de escritor único, origen contrastado, envío recuperable,
acuse consultable y transporte manual cuando falten herramientas. Distinguir los
acuerdos de producto del auxiliar local limitado: no instalar ni activar una skill,
configurar automatizaciones, enviar mensajes o modificar datos de chats reales.
No alterar el runtime, código, dependencias ni garantías del auxiliar.

</frozen-after-approval>

## Implementation Notes

- Baseline Git: `21da27024b97e505d5887ef122e0a349866cffbe`. Se conservan cambios
  locales previos; los documentos de la prueba anterior se enlazan sin atribuir
  al cambio actual una nueva prueba real.
- Alcance pequeño, reversible y sin decisiones materiales pendientes: ruta oneshot.
- Consultados bmad-help y catálogo, bmad-build, skill-creator, principios AIKit,
  SPEC/protocolo y arquitectura de coordinación, auxiliar y prueba conjunta.
  No existe skill de coordinación en packaging. Las herramientas nativas cubren
  transporte/consulta; el auxiliar cubre persistencia local parcial. Falta la guía
  reutilizable entre roles: se añaden documentos en docs/coordinacion/, no una
  skill o un adaptador que duplique esas herramientas.
- Archivos previstos: docs/coordinacion/{flujo-avisos,coordinador,tarea}.md,
  enlaces desde docs/auxiliar-coordinacion.md y protocolo de la especificación,
  trazabilidad en notas 025/032 e IDEAS. Mantener fuentes históricas intactas.
- Validación: JSON de ejemplo contra schema compilado, enlaces locales y
  git diff --check; revisión independiente de instrucciones y límites. No ejecutar
  mensajería ni repetir suites de código que no cambia. Regenerar tablero tras notas.
- Se añadieron las tres guías, enlaces desde auxiliar y protocolo y trazabilidad
  en las notas. No se creó ni instaló una skill; la activación queda pendiente.
- La revisión oneshot ejecutó su única capa Blind Hunter mediante subagente
  independiente sin contexto. Se corrigieron los cuatro hallazgos indicados abajo;
  no hubo capas adicionales configuradas ni hallazgos diferidos.
- Validación local: `.aikit/025-validar-instrucciones.mjs` comprueba siete documentos,
  47 enlaces locales y un aviso JSON con el parser/schema compilados; código 0.
  `git diff --check` pasó. Tablero regenerado correctamente: 35 notas (incluye una
  nueva nota ajena a este cambio que se conserva sin modificar).

## Review Triage Log

- medium, corregido: `apply` recibe objetos y no detecta sintaxis ya perdida por
  JSON.parse. La guía exige conservar bytes, strictJson y notice antes de aplicar.
- low, corregido: faltaban restricciones de IDs/números/campos. Se explicitan las
  del esquema v1 para evitar avisos completos en apariencia pero inválidos.
- low, corregido: faltaba un ejemplo de lectura de acuse. Se ilustra duplicado
  frente a consulta aplicado, aviso completo, current histórico y generación.
- medium, corregido: limpieza podía retirar aviso/evidencia aún no reconciliados.
  La guía exige copia persistida y verificada fuera del recurso que se retirará,
  o conservarlo como limpieza pendiente.
