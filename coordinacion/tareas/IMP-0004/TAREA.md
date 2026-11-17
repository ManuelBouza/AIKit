# Preparar BMAD aislado en los worktrees de tareas

```json
{
  "schemaVersion": 1,
  "id": "IMP-0004",
  "titulo": "Preparar BMAD aislado en los worktrees de tareas",
  "ideas": [],
  "chat": "01a1da03-23f1-7eb0-b0a0-5cb5184e6941",
  "fase": "pendiente",
  "atencion": "normal",
  "motivo": "",
  "siguienteAccion": "Concretar preparación nativa de entornos/worktrees con recursos existentes y permisos aplicables; obtener autorización de ejecución cuando corresponda.",
  "origen": "Dependencia reportada por040-bloqueo-bmad-01 y040-reanudacion-bmad-02; investigación de preparación nativa de worktrees pendiente en el Coordinador.",
  "responsable": "Coordinador; preparación técnica por delegar",
  "autorizacion": {
    "estado": "pendiente",
    "alcance": "",
    "referencia": ""
  },
  "dependencias": [],
  "referencias": [
    {
      "tipo": "archivo",
      "destino": "coordinacion/paralelo-028-040/ACUSES.md",
      "etiqueta": "Dependencia de entorno y condición de parada"
    }
  ],
  "projectId": "684a47fa-cf69-47a2-9625-5e7a8db806af",
  "creada": "2026-11-17T07:21:21Z",
  "actualizada": "2026-11-17T07:21:21Z"
}
```

## Resultado

Disponer de BMAD y dependencias utilizables en los worktrees028/040, con salidas confinadas a cada checkout.

## Alcance

Definir preparación con capacidades nativas disponibles, revisar documentación oficial y preservar evidencia; preparar y verificar solo con autorización aplicable.

## Exclusiones

Cambios globales, perfiles, ACL, ejecuciones de OpenCode o reintentos ciegos. Registrar esta dependencia no la ejecuta.

## Aceptacion

Disponibilidad y configuración verificadas por raíz, intérprete y dependencias operativos, salidas confinadas a cada checkout y condición de parada resuelta antes de reanudar el flujo.

## Historial

2026-11-17: alta desde dependencia de coordinación existente, sin inventar idea previa; pendiente de concretar y autorizar ejecución.
