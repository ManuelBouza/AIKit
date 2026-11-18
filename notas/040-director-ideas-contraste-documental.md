# Contraste documental después de madurar una idea

Fecha: 2026-11-15.
Estado inicial: Pendiente de debatir.

Estado actual: Integrada y verificada en fuentes; cierre de recursos e instalación pendientes.

## Entrega — 2026-11-18

Integración posterior: `46b9c6ed34e163016989226df11ac6d4590c8a1f` en main,
con ambos blobs de la entrega idénticos y exportación aislada correcta.
[Evidencia de integración y cierre](../docs/integracion-director-040.md).
La persistencia/limpieza del chat sigue en IMP-0003; instalación en perfil separada.

Chat040 solicita revisión e integración de
`b9cb2247b11216717ae1983be456f7a1c3ac16f2`, con skill y artefacto Build.
El aviso original se conserva en
[040-entrega-03](../coordinacion/paralelo-028-040/avisos/040-entrega-03.md).
La revisión previa aceptó el contenido final de la skill; la verificación
independiente del commit completo se aceptó antes de integrar. La entrega
se sigue en IMP-0003, sin declarar instalación ni publicación.

## Dependencia resuelta — 2026-11-17

El Coordinador prepara el entorno040 mediante la porción autorizada de
[IMP-0004](../coordinacion/tareas/IMP-0004/TAREA.md): BMAD6.12.4 local,
dependencias del propio lockfile y render con salidas aisladas. La revisión
posterior acepta la conservación del trabajo y de las evidencias anteriores.
[IMP-0003](../coordinacion/tareas/IMP-0003/TAREA.md) puede continuar bajo su
autorización humana previa. Esto no declara implementada la mejora ni preparada028.
Véase [preparación y evidencia](../docs/preparacion-bmad-worktree-040.md).

## Reanudación — 2026-11-17

Manuel indica «continuemos» directamente en el chat 040, turno
`01a1e823-0b36-76c1-aa94-f43d57a2e516`, mensaje humano
`01a1e823-200e-7341-82f4-b129d503643a`, contrastado por el Coordinador.
La pausa queda levantada solo para 040. Sigue pendiente preparar BMAD y las
dependencias de forma aislada; no se ha repetido el flujo fallido ni instalado
herramientas. Aviso `040-reanudacion-bmad-02`, revisión 2, conservado en el
[registro canónico](../coordinacion/paralelo-028-040/ACUSES.md).

## Pausa — 2026-11-16

Manuel pide mantener en espera los chats 028 y 040 y continuar la corrección
en el Coordinador. No reanudar investigación, implementación ni preparación
del entorno hasta nueva indicación. Se conservan rama, worktree y evidencias;
la incidencia de entorno permanece registrada como pendiente.

## Continuidad autónoma — 2026-11-16

El chat reconoce la corrección de autonomía de la [nota 041](041-autonomia-chat-tarea-tras-asignacion.md).
Al preparar el flujo, uv falla por DNS antes de renderizar; además falta `_bmad`
en su checkout. Conserva el resultado y detiene el flujo conforme a su instrucción.
No espera otra orden general de arranque ni ha iniciado implementación.
El Coordinador coordinará la resolución aislada del entorno; véanse
[aviso y acuse](../coordinacion/paralelo-028-040/ACUSES.md).

## Preparación — 2026-11-16

Manuel aprueba preparar un Chat de Tarea y worktree propio para esta nota en
paralelo con la 028. [Encargo y límites](../coordinacion/paralelo-028-040/ENCARGOS.md).
No se instala ni se modifica la skill del perfil durante esta preparación.

## Solicitud del usuario

Incorporar al Director de Ideas un paso explícito: una vez madurada la idea con
el usuario, contrastarla con documentación oficial y fuentes especializadas
fiables para aproximarse mejor a cómo implementarla con herramientas actuales.

El contraste debe realizarse antes de cerrar la propuesta de implementación.
Complementa la maduración con el usuario y la investigación contextual previa;
no sustituye ninguna de ellas.

## Criterios para la implementación posterior

- Partir del objetivo, requisitos, restricciones y decisiones acordados, y buscar
  enfoques, herramientas y prácticas actuales pertinentes a esa idea concreta.
- Priorizar documentación oficial y fuentes primarias; complementar con fuentes
  especializadas fiables cuando aporten experiencia o alternativas relevantes.
  Usar Context7 cuando corresponda y esté disponible, conforme a la preferencia.
- Comprobar vigencia, versiones y capacidades reales, diferenciando funciones
  disponibles de propuestas, funciones experimentales o afirmaciones sin verificar.
- Comparar lo encontrado con la idea madurada: qué respalda, qué corrige, qué
  alternativas abre y qué limitaciones o dependencias introduce.
- Valorar compatibilidad y herramientas ya disponibles en el proyecto. Actualidad
  no significa adoptar automáticamente lo más nuevo ni imponer un framework.
- Conservar fuentes y conclusiones verificables; distinguir hechos documentados,
  inferencias y supuestos. Si las fuentes no resuelven algo, identificar la
  comprobación dirigida necesaria sin sustituir la investigación por ensayo y error.
- Devolver al usuario los cambios materiales que el contraste sugiera sobre la
  idea, antes de tratarla como lista para implementar. No reabrir decisiones sin
  motivo ni exigir confirmaciones entre pasos ya autorizados.
- Ajustar la profundidad al alcance y reutilizar investigación todavía vigente;
  evitar búsquedas repetidas sin necesidad. El resultado debe justificar el
  enfoque recomendado, sin afirmar que existe una única implementación correcta.
- Mantener este paso independiente de BMAD y de otras herramientas concretas.
  El contraste no autoriza implementar ni instalar nuevas herramientas.

## Contexto y relaciones

La solicitud surge tras contrastar el reparto entre coordinador y chats de tarea
con fuentes de agentes de IA. La investigación permitió corregir criterios
preliminares antes de preparar el contrato propuesto; véase el
[contraste documentado](../docs/coordinacion/contraste-reparto-agentes.md).

- [009 — Método del Director de Ideas](009-metodo-director-de-ideas.md).
- [016 — Investigar antes de experimentar](016-investigacion-antes-de-experimentar.md).
- [036 — Reforzar investigación antes de pruebas](036-reforzar-investigacion-antes-de-pruebas.md).
- [039 — Setup como centro de activación](039-setup-centro-activacion-capacidades.md).

Esta nota registra una mejora para su implementación posterior. No modifica
la skill instalada ni activa una nueva preferencia en setup.
