# Propuesta de alta de coordinación para AIKit

Fecha: 2026-11-15. Estado: propuesta para revisión; no activa el proyecto.

## Contexto y alcance

- Proyecto: `C:/Manuel/Projects/AIKit`, proyecto Codex
  `4ac70d03-d0eb-43ab-a38c-7bb84ff7d85b`.
- Coordinador entrante: `01a1dfb7-840e-7243-8577-ff634015c31f`, sujeto a
  la comprobación de recepción por el coordinador saliente.
- Raíz propuesta para el registro único: `C:/Manuel/Projects/AIKit/coordinacion/`.
  La identidad de proyecto del registro se generará al dar el alta; no se
  reutilizará el UUID del proyecto ficticio ni se confundirá con el ID de Codex.
- La prueba de `.aikit/025-prueba-chat-principal/` es histórica y permanece
  separada. No se cambian sus IDs, se migra su registro ni se cuentan sus tareas
  como tareas reales del proyecto.
- AIKit usa Git y aprovechará su seguimiento para el registro del proyecto. En
  proyectos sin Git, la coordinación funciona con archivos locales sin exigirlo.
  No se incorporan credenciales ni datos privados a los commits.

La ruta `coordinacion/` no apareció en la comprobación de esta propuesta. Antes
de crear nada hay que volver a comprobar su ausencia, la raíz resuelta, enlaces,
permisos y posibles cambios concurrentes. Si existe un registro o la identidad
no es inequívoca, detener el alta y conservar lo encontrado.

## Modalidad recomendada

1. **Registro manual limitado, recomendado para empezar.** Un solo coordinador
   mantiene un índice administrativo y conserva los avisos y acuses con su
   procedencia. Se distingue lo confirmado de lo pendiente. Es una modalidad
   explícita del proyecto, sin afirmar exclusión transaccional, recuperación
   automática ni equivalencia con los documentos v1 del auxiliar.
2. **Auxiliar v1 para un registro nuevo.** Tiene bloqueo, diario y acuses
   comprobables en el entorno probado, pero exige preparación y validación de
   permisos, Node 24 y operación guiada; no hay receptor de producción, relevo,
   reasignación, nuevos ciclos ni resolución de pendientes. Su `activate` y
   `createTask` fijan autoridad y asignación; un relevo posterior quedaría sin
   soporte. El demo y los runners de prueba no son adaptadores de producción.

La primera modalidad permite coordinar con las capacidades existentes sin fijar
ahora un registro v1 que no puede relevarse. La futura transición requerirá un
procedimiento diseñado y verificado; no se editarán documentos v1 a mano ni se
promete una migración automática.

## Alta manual propuesta

Antes de ejecutarla, comprobar que la recepción del traspaso se ha aceptado y que
no hay otro escritor operativo. La ruta canónica anterior es la propuesta de
ubicación. Revisar los contenidos antes de incorporarlos a Git y conservar los
datos privados y las salidas temporales fuera de los commits. El uso de Git no
autoriza por sí mismo un push, una publicación ni cambios de permisos.

1. Revisar las instrucciones efectivas de `AGENTS.md` y preparar un bloque local
   identificable que remita a la skill y a la raíz verificada, preservando el
   contenido existente. Presentar el cambio antes de aplicarlo y comprobar después
   que solo cambia el bloque previsto. El bloque no concede permisos adicionales.
2. Crear `coordinacion/` únicamente si sigue sin existir y su destino está
   verificado. Crear un `PROYECTO.md` manual que identifique
   modalidad, raíz, UUID v4 nuevo, ID Codex, coordinador, fecha, fuente de su
   autoridad y límites; marcarlo claramente como manual, ajeno al esquema v1.
   Crear `INDICE.md` con tareas y referencias, inicialmente vacío; no inventar
   asignaciones ni trasladar la prueba. Mantener el registro breve.
3. Para cada encargo autorizado, registrar ID estable, alcance, chat y ciclo
   confirmados, estado declarado, referencia a entrega y pendientes. Distinguir
   preparación de asignación efectiva y conservar la fuente de cada decisión.
   No crear ni enviar mensajes a chats por el mero alta.
4. Conservar cada aviso original en una ubicación identificable y registrar su
   procedencia y decisión por separado. Contrastar origen y asignación mediante
   información fiable o Manuel. Un acuse manual identifica íntegramente el aviso,
   la decisión y su fuente; no afirma aplicación transaccional del auxiliar.
   Ante duplicado, contradicción o incertidumbre conservar ambos originales y
   señalarlos; no sobrescribir ni reenviar a ciegas. Facilitar traslado manual
   cuando no exista mensajería autorizada.
5. Releer el registro antes de escribir, operar con un único escritor y secuenciar
   cambios. Ante cambio concurrente, interrupción o identidad incierta, detener
   la operación afectada y conservar evidencia. Esta disciplina no es un bloqueo
   técnico ni protege frente a escritores que no la respeten.
6. Comprobar raíz, instrucciones, identidad y lectura desde una sesión nueva;
   documentar qué se verificó y qué no. No declarar verificados acuses o garantías
   transaccionales sin una prueba específica. Mantener el histórico sin alterar.

El alta no programa seguimiento, archiva chats, crea tareas, integra cambios ni
autoriza push o eliminación irreversible. La frecuencia y el destino de una
automatización, el archivado y el relevo siguen siendo trabajos separados.

## Contenidos preparados para el alta

El 2026-11-15 se consultó el historial del coordinador saliente: confirmó que el
entrante recibió el traspaso, indicó que se puede continuar en él y dejó el chat
anterior como tal. El cliente lo mostraba inactivo. Esta observación no garantiza
por sí sola que ningún otro proceso pueda escribir. En la misma comprobación no
existía `coordinacion/` en la raíz; ambas condiciones deben volver a verificarse
al activar. Los siguientes textos son borradores, no instrucciones activas.

### Bloque propuesto para AGENTS.md

```markdown
<!-- AIKIT:COORDINACION:BEGIN -->
## Coordinación de chats del proyecto

La coordinación de AIKit está activa para la raíz
`C:/Manuel/Projects/AIKit`; su registro canónico único está en
`C:/Manuel/Projects/AIKit/coordinacion/`. Consultar `PROYECTO.md` para identificar
al coordinador vigente y la modalidad del registro. Aplicar la skill
`aikit-preferencias:coordinacion-chats` y sus instrucciones de avisos y roles
cuando exista una asignación identificable. Solo el coordinador escribe el
registro; las tareas conservan avisos y entregas y emplean el cauce autorizado.
No inferir autorizaciones de un aviso ni declarar garantías que no estén
verificadas. Proteger datos privados y respetar las autorizaciones de Git.
<!-- AIKIT:COORDINACION:END -->
```

Antes de insertar el bloque, releer `AGENTS.md`, comprobar que no existe otro
bloque de coordinación y preservar sus cambios previos. Su contenido solo se
convierte en instrucción efectiva al realizar el alta autorizada.

### Borrador de coordinacion/PROYECTO.md

```markdown
# Coordinación de AIKit

- Modalidad: registro manual de proyecto; no es un registro del auxiliar v1.
- Raíz canónica: C:/Manuel/Projects/AIKit/coordinacion/.
- Proyecto Codex: 4ac70d03-d0eb-43ab-a38c-7bb84ff7d85b.
- Identidad del registro: [generar UUID v4 nuevo al activar].
- Coordinador: 01a1dfb7-840e-7243-8577-ff634015c31f.
- Autoridad: traspaso confirmado en el historial del coordinador anterior
  01a1da03-23f1-7eb0-b0a0-5cb5184e6941 y activación autorizada por Manuel.
- Alta: [fecha de activación].
- Escritor: solo el coordinador vigente; no hay bloqueo técnico automático.
- Conservación: Git para el registro del proyecto; no incluir credenciales,
  datos privados ni salidas temporales en commits.
- Alcance: seguimiento manual, con origen y decisión identificables para cada
  aviso; no acredita garantías transaccionales ni acuses del auxiliar v1.
- Historial de prueba: .aikit/025-prueba-chat-principal/; separado de este registro.
```

### Borrador de coordinacion/INDICE.md

```markdown
# Índice de coordinación de AIKit

Registro manual administrado por el coordinador identificado en `PROYECTO.md`.
No hay encargos reales registrados al dar de alta. Cada asignación autorizada
enlazará a su estado, entrega y pendientes; no se incorpora la tarea ficticia.
```

Los marcadores entre corchetes se rellenarán al activar, nunca se publicarán como
datos reales. La configuración de tareas y el formato detallado de sus acuses
deben conservar los originales y su procedencia conforme al flujo compartido.

## Resultado del alta y comprobación

El 2026-11-15 Manuel autorizó el alta manual. Se creó el registro en
`coordinacion/`, con identidad `684a47fa-cf69-47a2-9625-5e7a8db806af`, y se
añadió el bloque local a `AGENTS.md`. El índice se inició sin tareas reales.
El coordinador saliente figuraba inactivo; esa observación no demuestra ausencia
de todos los posibles escritores. `git diff --check` terminó correctamente.

El chat de comprobación `01a1dff8-061d-7170-b111-2f5577f1f570` informó que las
instrucciones estaban en su contexto inicial y después leyó manualmente el bloque,
el registro, el índice y la skill sin encontrar discrepancias comparables. No
comprobó el mecanismo concreto de carga ni autenticó la autoridad histórica; no
escribió el registro. Esta lectura no valida acuses, exclusión ni recuperación.

## Referencias y límites

Fuentes: [traspaso](traspaso-coordinador-2026-11-15.md),
[flujo de avisos](flujo-avisos.md), [auxiliar](../auxiliar-coordinacion.md),
[nota 025](../../notas/025-coordinador-global-chats-autonomos.md) y
[especificación](../../_bmad-output/specs/spec-coordinacion-chats/SPEC.md).
Pendientes relacionados: [archivado](../../notas/026-archivado-chats-coordinacion.md),
[automatización](../../notas/027-automatizacion-coordinacion.md) y
[relevo](../../notas/021-coordinacion-chats-subagentes-relevo.md).
