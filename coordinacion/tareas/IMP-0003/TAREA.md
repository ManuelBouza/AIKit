# Contrastar documentalmente las ideas maduradas

```json
{
  "schemaVersion": 1,
  "id": "IMP-0003",
  "titulo": "Contrastar documentalmente las ideas maduradas",
  "ideas": [
    40
  ],
  "chat": "01a1e56b-ec96-7960-b2ee-7f1d3f7366fb",
  "fase": "en_curso",
  "atencion": "bloqueada",
  "motivo": "Faltan BMAD local y skill en el worktree; intento anterior detenido por DNS al preparar dependencia. Condición de parada vigente.",
  "siguienteAccion": "Resolver y verificar disponibilidad aislada de BMAD y dependencias mediante IMP-0004, sin reintentos ciegos.",
  "origen": "Encargo040 y aviso040-reanudacion-bmad-02. Reanudación humana chat040 turno01a1e823-0b36-76c1-aa94-f43d57a2e516, mensaje01a1e823-200e-7341-82f4-b129d503643a.",
  "responsable": "Chat de Tarea040",
  "autorizacion": {
    "estado": "autorizada",
    "alcance": "Modificar Director de Ideas para contraste documental proporcional tras maduración; sin instalar en perfil, preparar entorno ni reintentar flujo fallido antes de resolverlo.",
    "referencia": "Chat040 turno01a1e823-0b36-76c1-aa94-f43d57a2e516 / 01a1e823-200e-7341-82f4-b129d503643a; ajuste de autonomía aprobado en turnoCoordinador01a1e584-117f-7481-b452-b1487fe9d7f5."
  },
  "dependencias": [
    "IMP-0004"
  ],
  "referencias": [
    {
      "tipo": "archivo",
      "destino": "notas/040-director-ideas-contraste-documental.md",
      "etiqueta": "Criterios de mejora"
    },
    {
      "tipo": "archivo",
      "destino": "coordinacion/paralelo-028-040/avisos/040-reanudacion-bmad-02.md",
      "etiqueta": "Aviso original y reanudación"
    }
  ],
  "projectId": "684a47fa-cf69-47a2-9625-5e7a8db806af",
  "creada": "2026-11-17T07:21:21Z",
  "actualizada": "2026-11-17T07:21:21Z"
}
```

## Resultado

Director de Ideas contrasta las ideas maduradas con documentación oficial y fuentes especializadas antes de recomendar implementación.

## Alcance

Criterios de Idea040, con profundidad proporcional, vigencia, hechos/supuestos separados y decisiones materiales devueltas al usuario.

## Exclusiones

Instalación en perfil, configuración global, preparación del entorno, cambios de instalador y publicación.

## Aceptacion

Validación de skill, escenarios de comportamiento y revisión independiente vinculada a la entrega exacta; criterios completos de Idea040.

## Historial

2026-11-17: migración del encargo040 existente; conserva reanudación humana y bloqueo, .venv y evidencias del intento fallido.
