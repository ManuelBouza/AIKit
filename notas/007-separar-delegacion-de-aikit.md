# Separar delegating-to-opencode del complemento AIKit

Fecha: 2026-10-31.
Estado inicial: pendiente de debatir.
Estado actual: En planificación. Decisión de monorepositorio tomada;
separación y verificación de los complementos independientes pendientes.

## Decisión y estado — 2026-11-07

AIKit y Delegating to OpenCode se desarrollan en un único monorepositorio y
deben distribuirse como dos complementos con instalación y actualización
independientes. AIKit podrá usar Delegating to OpenCode como integración opcional;
Delegating to OpenCode podrá utilizarse sin AIKit. No se requieren repositorios
distintos. Véanse los [límites](../docs/limites-delegacion-aikit.md) y el
[plan del monorepositorio](../docs/plan-monorepositorio.md).

La separación del empaquetado y la migración no están terminadas ni verificadas:
los manifiestos y el exportador siguen siendo los del complemento histórico.
El constructor portable de `go` es una pieza inicial, no acredita la separación
completa. Se retoma la planificación mediante la [especificación BMAD](../_bmad-output/specs/spec-complementos-independientes/SPEC.md);
no se usa Delegating to OpenCode hasta nuevo aviso. Esta planificación no autoriza
instalar ni modificar un perfil real.

AIKit gestionará preferencias e instrucciones generales y sus propias skills,
incluida la escritura de sus instrucciones en `AGENTS.md` global. Delegating to
OpenCode será un complemento independiente con su MCP y skills; solo se usará
por indicación expresa o instrucciones aplicables en `AGENTS.md` que regulen su
uso. La mera instalación no lo activa como política de delegación habitual.

Decisión posterior del usuario: probar primero las instrucciones de AIKit en el
`AGENTS.md` local; cuando se libere e instale el complemento, sus instrucciones
deben instalarse globalmente. La primera versión parte de `go` y Context7. La
[estrategia propuesta](../_bmad-output/specs/spec-complementos-independientes/instalacion-y-migracion.md)
mantiene el complemento histórico hasta verificar la transición y evita duplicar
el servidor. El mecanismo del cliente para la escritura global sigue por probar.

El texto siguiente conserva la idea y preguntas originales; las decisiones ya
tomadas en esta sección prevalecen sobre sus alternativas históricas.

## Idea

Separar `delegating-to-opencode` del complemento AIKit para que sean dos elementos
independientes. AIKit debe utilizarlo como una de las herramientas disponibles,
igual que utiliza Superpowers y Context7.

La capacidad de delegar a OpenCode debe poder instalarse y utilizarse de forma
independiente de AIKit. AIKit conserva sus preferencias y criterios para decidir
cuándo y cómo usar esa capacidad.

## AIKit como forma global de trabajar con Codex

AIKit debe establecer la forma global de trabajar con Codex. Al instalarse,
debe agregar sus instrucciones al `AGENTS.md` global, siguiendo el mecanismo que
ya utiliza. Cada proyecto tendrá su `AGENTS.md` local para complementar esas
instrucciones con las particularidades del proyecto.

Además de las instrucciones globales, AIKit tendrá skills propias para apoyar
su trabajo. Definir correctamente qué responsabilidad corresponde a cada pieza:

- `AGENTS.md` global: instrucciones generales de la forma de trabajo de AIKit.
- `AGENTS.md` local: instrucciones específicas que aporta cada proyecto.
- Skills propias de AIKit: procedimientos y capacidades de apoyo que se activen
  cuando corresponda.
- Herramientas independientes, externas o nuestras: capacidades que AIKit utiliza,
  como `delegating-to-opencode`, Superpowers y Context7, respetando la naturaleza
  de cada integración.

Esta distribución es una intención para desarrollar al debatir la nota; queda
pendiente concretar los límites sin duplicar instrucciones o responsabilidades.

## Para debatir después

- Delimitar qué pertenece a la herramienta de delegación y qué son políticas de
  coordinación propias de AIKit.
- Clasificar las responsabilidades de AIKit entre `AGENTS.md` global, instrucciones
  locales de proyecto, skills propias y herramientas independientes. Definir cómo
  se complementan, se activan y se mantienen sin duplicaciones.
- Precisar cómo el instalador agrega y actualiza las instrucciones globales y las
  skills propias, conservando instrucciones ajenas y la configuración de proyectos.
- Definir distribución, instalación, versiones y actualización independientes;
  la decisión posterior mantiene ambos componentes en un monorepositorio.
- Establecer cómo AIKit descubre y utiliza la herramienta, comprueba su
  compatibilidad y actúa cuando no está instalada o disponible.
- Planificar la migración del complemento actual sin duplicar skills o servidores
  MCP ni perder configuraciones existentes.
- Revisar el empaquetado, la documentación y las pruebas que dependan de que la
  delegación forme parte del complemento AIKit.

Relacionada con la nota [006](006-herramientas-skills-opencode.md), sobre las
capacidades disponibles en cada entorno y el lugar de instalación de AIKit.

Guardar esta nota no cambia el empaquetado actual ni autoriza la separación o
migración de componentes.

## Avance — 2026-11-07

Se incorporó al checkout principal el constructor de un complemento independiente
de Delegating to OpenCode y su documentación y pruebas. El empaquetado histórico
se conserva. La [especificación de implementación](../_bmad-output/implementation-artifacts/spec-complemento-delegating-independiente.md)
registra la revisión y la prueba de descubrimiento con servidor ficticio. Sigue
pendiente verificar el MCP real cuando se levante la restricción temporal,
comprobar la convivencia y migración, y construir AIKit como complemento
independiente. Los cambios están sin commit.

Después se preparó el complemento independiente de AIKit con `go` y Context7,
sin MCP de delegación. La instalación explícita de bloques se probó en perfiles
ficticios; la instalación global automática y la retirada siguen pendientes.

## Actualización de AIKit — 2026-11-08

Se eligió setup explícito mediante la skill del complemento en lugar de escritura
automática al instalar. El complemento se instaló y su instalador aplicó los
bloques en el perfil global y en el proyecto reales. En un chat nuevo se reconoció
la skill y las vistas previas indicaron que ambos ámbitos estaban actualizados.
Esto no acredita la migración ni la convivencia de Delegating to OpenCode.
