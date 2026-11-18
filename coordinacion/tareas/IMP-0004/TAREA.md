# Preparar BMAD aislado en los worktrees de tareas

```json
{
  "schemaVersion": 1,
  "id": "IMP-0004",
  "titulo": "Preparar BMAD aislado en los worktrees de tareas",
  "ideas": [],
  "chat": "01a1da03-23f1-7eb0-b0a0-5cb5184e6941",
  "fase": "finalizada",
  "atencion": "normal",
  "motivo": "",
  "siguienteAccion": "Entornos040 y028 verificados; mantener recursos activos mientras sus tareas los necesiten.",
  "origen": "Dependencia reportada por040-bloqueo-bmad-01 y040-reanudacion-bmad-02; investigación de preparación nativa de worktrees pendiente en el Coordinador.",
  "responsable": "Coordinador; preparación técnica por delegar",
  "autorizacion": {
    "estado": "autorizada",
    "alcance": "Preparar y verificar los entornos locales040 y028 con BMAD existente y dependencias de sus lockfiles, salidas aisladas y conservación del trabajo.028 se prepara como requisito técnico de la implementación visual aprobada; sin configuración global, ACL ni herramientas nuevas ajenas al proyecto.",
    "referencia": "040: go humano en Coordinador, turno01a1eb0f-e6ea-72c3-bbf5-721ad56afa12 / mensaje01a1eb0f-e7e4-7843-a9bc-872c89a2ce81.028: aprobación directa de implementación en chat028, turno01a1ed3a-39d9-7ac2-b5f6-cf3eca31a2b0 / mensaje01a1ed3a-3bf8-79e1-81cb-2036f9801ce4, contrastada por el Coordinador; preparación local necesaria dentro de ese alcance."
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
    },
    {
      "tipo": "archivo",
      "destino": "docs/preparacion-bmad-worktree-028.md",
      "etiqueta": "Porción028 resuelta y verificada"
    }
  ],
  "projectId": "684a47fa-cf69-47a2-9625-5e7a8db806af",
  "creada": "2026-11-17T07:21:21Z",
  "actualizada": "2026-11-18T06:19:06Z"
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

2026-11-18: tras aprobación directa de la implementación visual028, el Coordinador
reanuda la porción pendiente como preparación técnica necesaria de esa entrega.
Se reutilizan recursos ya instalados; no se autoriza instalación global o nueva
infraestructura. Primero se coordina su base con043 sin perder trabajo; después
se adaptará el procedimiento040 a su raíz y lockfile efectivo.

2026-11-18: porción028 completada y revisión posterior aceptada. El primer
preflight detectó un alias uv antes de escribir; v2 usa su destino físico y
preserva guardias. Código0 en sync/pip/config/render, 234recursos, 377tracked,
tres avisos, rama/HEAD/índice y fuentes conservados. Nueva .venv local con
Python3.13.14 y43dependencias compatibles. El alias minor que uv escribe no
garantiza fijación permanente al patch. Ambas porciones terminadas; no se
implementó producto ni se deben retirar recursos que las tareas aún necesitan.
