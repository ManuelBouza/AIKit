# Implementar seguimiento local de ideas y tareas

```json
{
  "schemaVersion": 1,
  "id": "IMP-0001",
  "titulo": "Implementar seguimiento local de ideas y tareas",
  "ideas": [
    43
  ],
  "chat": "01a1da03-23f1-7eb0-b0a0-5cb5184e6941",
  "fase": "finalizada",
  "atencion": "normal",
  "motivo": "",
  "siguienteAccion": "Entrega local completada; instalación en perfil o publicación requieren encargo separado.",
  "origen": "Chat Coordinador, turno 01a1e85d-1934-7672-9cc3-6a4d7b0314e1, mensaje humano 01a1e85d-1aaa-7183-a8df-7baafeaeefe8: go de implementación043.",
  "responsable": "Coordinador; implementación y revisión delegadas",
  "autorizacion": {
    "estado": "autorizada",
    "alcance": "Registro local, vistas conectadas, setup y migración inicial de la especificación043; sin instalación en perfil ni push.",
    "referencia": "01a1e85d-1934-7672-9cc3-6a4d7b0314e1 / 01a1e85d-1aaa-7183-a8df-7baafeaeefe8, chat Coordinador."
  },
  "dependencias": [],
  "referencias": [
    {
      "tipo": "archivo",
      "destino": "_bmad-output/specs/spec-seguimiento-ideas-tareas/SPEC.md",
      "etiqueta": "Contrato funcional y compañeros"
    },
    {
      "tipo": "archivo",
      "destino": "coordinacion/implementacion-seguimiento-043.md",
      "etiqueta": "Encargo previo al arranque del sistema"
    },
    {
      "tipo": "archivo",
      "destino": "docs/validacion-seguimiento-043.md",
      "etiqueta": "Pruebas, revisión y huellas de la entrega"
    },
    {
      "tipo": "archivo",
      "destino": "coordinacion/MIGRACION-043.md",
      "etiqueta": "Migración y repetición manual verificable"
    }
  ],
  "projectId": "684a47fa-cf69-47a2-9625-5e7a8db806af",
  "creada": "2026-11-17T07:21:21Z",
  "actualizada": "2026-11-17T10:51:04Z"
}
```

## Resultado

Seguir encargos de implementación en tickets conectados con las ideas y visibles en el tablero.

## Alcance

Cumplir las seis capacidades de SPEC-seguimiento-ideas-tareas y sus compañeros. Este ticket conserva el encargo manual inicial, sin duplicarlo.

## Exclusiones

Sin preparación BMAD, cambios de perfil, push ni publicación. No moderniza el diseño visual reservado a 028.

## Aceptacion

Criterios de SPEC.md y migracion-y-aceptacion.md; pruebas, exportación, comportamiento, revisión independiente y resultado de migración vinculados a la entrega.

## Historial

2026-11-17: alta tras simulación y respaldo, durante arranque del sistema; implementación delegada con contrato aprobado.

2026-11-17: implementación delegada terminada, estado En revisión y contraste
independiente con correcciones. Cierre local: 988 pruebas aprobadas, Ruff/mypy
correctos y revisión aceptada. Evidencia y huellas del candidato revisado en
docs/validacion-seguimiento-043.md; procedimiento de migración en
coordinacion/MIGRACION-043.md. Instalación en perfil y push excluidos del alcance.
