# Filtrar avisos de coordinación por impacto operativo

```json
{
  "schemaVersion": 1,
  "id": "IMP-0006",
  "projectId": "684a47fa-cf69-47a2-9625-5e7a8db806af",
  "titulo": "Filtrar avisos de coordinación por impacto operativo",
  "creada": "2026-11-17T19:00:12Z",
  "actualizada": "2026-11-17T19:10:19Z",
  "ideas": [44],
  "origen": "Chat Coordinador 01a1da03-23f1-7eb0-b0a0-5cb5184e6941: go del usuario para implementar el filtro recomendado tras elegir explícitamente opción 1 en la nota044.",
  "responsable": "Coordinador; implementación y revisión técnica delegadas",
  "chat": "01a1da03-23f1-7eb0-b0a0-5cb5184e6941",
  "fase": "finalizada",
  "atencion": "normal",
  "motivo": "",
  "siguienteAccion": "Preparar e instalar la actualización privada requiere un encargo separado autorizado.",
  "autorizacion": {
    "estado": "autorizada",
    "alcance": "Implementar y verificar en fuentes el filtro de avisos por impacto de nota044; sin instalación, push, publicaciones, automatizaciones ni mensajes de prueba a chats reales.",
    "referencia": "Chat Coordinador 01a1da03-23f1-7eb0-b0a0-5cb5184e6941, turno 01a1eae0-937b-7213-861d-7404d1bf4a34, mensaje humano 01a1eae0-9480-7e52-9284-59ef998f6cdb: go para implementar este filtro en ambos roles y verificar sus decisiones con casos concretos."
  },
  "dependencias": [],
  "referencias": [
    {"tipo": "archivo", "destino": "notas/044-notificaciones-por-impacto-y-coste.md", "etiqueta": "Decisiones y casos aprobados"},
    {"tipo": "archivo", "destino": "_bmad-output/implementation-artifacts/spec-044-avisos-por-impacto.md", "etiqueta": "Build terminado, triage y snapshot aceptado"},
    {"tipo": "archivo", "destino": "docs/validacion-avisos-044.md", "etiqueta": "Controles, 18 casos y revisión independiente"}
  ]
}
```

## Resultado

Ambos roles distinguen conservar una novedad de activar otro chat: envían cuando
hay acción, decisión operativa o riesgo que empeora al esperar; recogen avances
ordinarios en la siguiente revisión pertinente.

## Alcance

Reutilizar la skill de coordinación y sus referencias de roles, avisos y
seguimiento. Resolver contradicciones y documentar validación proporcional.

## Exclusiones

Sin nuevos servicios, buzones, scheduler, garantías de entrega silenciosa,
instalación del complemento, cambios028/040 ni avisos sin valor operativo.

## Aceptacion

Con instrucciones actualizadas, casos de ambos roles conservan novedades
ordinarias y envían solicitudes accionables; no generan acuses de acuse ni
consultan todos los historiales rutinariamente. Autonomía, registro previo,
evidencias, reconciliación y autorizaciones existentes se conservan. Validación
de skill y exportación correctas y revisión independiente con resultado registrado.

## Historial

2026-11-17: alta antes de implementar, tras elección explícita de opción1 y go
para materializar el filtro. La nota044 y su entrada pendientes son trabajo
autorizado de esta misma iniciativa y se conservan.

2026-11-17: implementación en fuentes aceptada por revisión técnica independiente
tras cuatro patches y aclaración de procedencia humana del contrato. Dos skills
válidas, exportación/instalación aislada correcta y 18 casos declarativos
consistentes. Snapshot y clasificación completos en los artefactos enlazados.
El Coordinador incorpora el dictamen a este cierre; sin instalación, avisos reales
ni cambios028/040. No se crearon ramas o worktrees para esta entrega. Los
artefactos útiles se persisten en Git; fuentes activas y respaldos ajenos se conservan.
