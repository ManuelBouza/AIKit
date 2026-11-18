# Preparar BMAD aislado en los worktrees de tareas

```json
{
  "schemaVersion": 1,
  "id": "IMP-0004",
  "titulo": "Preparar BMAD aislado en los worktrees de tareas",
  "ideas": [],
  "chat": "01a1da03-23f1-7eb0-b0a0-5cb5184e6941",
  "fase": "en_curso",
  "atencion": "esperando_usuario",
  "motivo": "Entorno040 preparado y verificado. Queda la preparación028, fuera de la autorización actual.",
  "siguienteAccion": "Cuando proceda, decidir la preparación del entorno028; la dependencia040 ya está resuelta.",
  "origen": "Dependencia reportada por040-bloqueo-bmad-01 y040-reanudacion-bmad-02; investigación de preparación nativa de worktrees pendiente en el Coordinador.",
  "responsable": "Coordinador; preparación técnica por delegar",
  "autorizacion": {
    "estado": "autorizada",
    "alcance": "Resolver y verificar el entorno BMAD del chat040, con recursos existentes, salidas aisladas y conservación de su trabajo; no preparar028 ni cambiar configuración global, ACL o trabajos de implementación.",
    "referencia": "ChatCoordinador01a1da03-23f1-7eb0-b0a0-5cb5184e6941, turno01a1eb0f-e6ea-72c3-bbf5-721ad56afa12, mensajehumano01a1eb0f-e7e4-7843-a9bc-872c89a2ce81: go tras recomendar preparar y verificar el entornoBMAD040 medianteIMP0004."
  },
  "dependencias": [],
  "referencias": [
    {
      "tipo": "archivo",
      "destino": "coordinacion/paralelo-028-040/ACUSES.md",
      "etiqueta": "Dependencia de entorno y condición de parada"
    },
    {
      "tipo": "archivo",
      "destino": "docs/preparacion-bmad-worktree-040.md",
      "etiqueta": "Porción040 resuelta y verificada"
    }
  ],
  "projectId": "684a47fa-cf69-47a2-9625-5e7a8db806af",
  "creada": "2026-11-17T07:21:21Z",
  "actualizada": "2026-11-17T20:05:46Z"
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

2026-11-17: Manuel autoriza resolver el entorno040. Se reutiliza este ticket sin
duplicar la dependencia. La preparación028 sigue pendiente y no autorizada; el
cierre parcial de040 no acreditará disponibilidad del otro worktree. Diagnóstico
y preparación técnica delegados; comprobar documentación antes de intervenir.

2026-11-17: porción040 completada. Helper revisado aplicado con código0:
234recursos BMAD6.12.4 copiados y verificados,43dependencias instaladas según lock
propio, Python3.13.14 local y pip check/config/render correctos. Revisión posterior
aceptó329archivos tracked, dos avisos anteriores, rama/HEAD/índice y fuentes de
origen intactos. Snapshot generado dentro de040; no se siguió su implementación.
La preparación028 sigue pendiente. Este ticket permanece abierto por esa porción;
IMP-0003 deja de depender operativamente de su finalización global y conserva
el enlace como evidencia de la dependencia040 resuelta.
