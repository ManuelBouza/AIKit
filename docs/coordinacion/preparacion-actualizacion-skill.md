# Preparación de la actualización de coordinacion-chats

Fecha: 2026-11-15.
Estado: preparación completada; implementación y validación pendientes.

Actualización posterior: alcance implementado y verificado en fuentes. Véase
la [entrega](../../_bmad-output/implementation-artifacts/spec-025-actualizacion-roles.md).
Instalación habitual y piloto pendientes. Los apartados siguientes conservan
la preparación que guio esa implementación.

## Resultado esperado

Actualizar la skill existente para que un agente distinga coordinación de
ejecución, elija apoyos acotados o Chats de Tarea y documente su creación y
reutilización conforme al [contrato consolidado](contrato-responsabilidades-propuesto.md).
Mantener un coordinador del proyecto y el mismo mecanismo para chats con
encargo concreto o propósito especializado. No crear una familia de skills de
especialistas ni duplicar herramientas nativas de chats o subagentes.

## Cobertura comprobada y carencias

| Recurso existente | Cobertura y uso previsto |
| --- | --- |
| coordinacion-chats, en fuentes y caché instalada 0.1.1 | Reconoce ambos roles y cubre avisos, acuses, escritor canónico, solicitud de integración y limpieza. Actualizarla; no crear otra skill de coordinador. |
| references/avisos.md | Conserva contrato v1 y reglas de recuperación. Aclarar «el coordinador revisa» como revisión de coordinación con evaluación técnica delegada. |
| Herramientas nativas del cliente | Se identificaron capacidades de crear, consultar, renombrar, enviar mensajes y archivar chats. Usarlas solo si están publicadas y autorizadas en el entorno de ejecución; su existencia no acredita todos los flujos. |
| skill-creator | Guía estructura, descubrimiento, referencias y validación. Mantener entrada breve y cargar detalle por necesidad. |
| bmad-help y catálogo instalado | Consultados; flujo recomendado para la implementación acotada: bmad-build, apoyado en skill-creator. No necesita PRD, arquitectura nueva o un flujo completo de sprint. |
| aikit-setup | Solo presenta actualmente cinco preferencias. Falta una entrada para coordinación; incorporarla a la entrega para no repetir la omisión registrada en la nota 039. |
| scripts/build_aikit.py y tests/test_build_aikit.py | Lista explícita de exportación y prueba de contenido. Añadir cualquier nueva referencia al paquete y comprobar que llega íntegra. |
| Registro manual de AIKit | Permite conservar identidad, alcance y decisiones sin atribuir garantías del prototipo. Las pruebas no deben reemplazar ni contaminar su autoridad. |

Las guías de roles en docs/coordinacion y las skills de desarrollo disponibles
son recursos reutilizables; ninguna reemplaza el reparto acordado. BMAD apoya el
desarrollo en este repositorio y no se convierte en requisito del producto.

## Cambios delimitados

1. Ajustar descripción y entrada de `packaging/skills/coordinacion-chats/SKILL.md`
   para cubrir asignación, roles y reutilización, además de avisos y acuses.
   La activación del proyecto sigue siendo explícita; leer la skill no activa nada.
2. Añadir una referencia interna breve de responsabilidades y selección del medio,
   enlazada desde la entrada. Debe cubrir:
   - Coordinador dedicado a coordinar, con revisión de coordinación y evaluación
     técnica delegada; integración autorizada y protección del destino final.
   - Chats de Tarea con encargo concreto o propósito especializado dentro del
     mismo mecanismo; elección y documentación por el coordinador según necesidad.
   - Consulta de identidades existentes antes de crear; reutilización con contexto
     vigente, alcance, estado y referencias recuperables.
   - Subagentes para apoyos de una sola ejecución; las implementaciones con
     continuidad corresponden a Chats de Tarea. No crear un chat por cada comando.
   - Diferencia entre responsabilidad, conversación, encargo/ciclo y ejecución.
   - Comunicación inicialmente mediante el coordinador, con un responsable del
     siguiente paso y traspaso identificable. La comunicación directa queda
     pendiente para el futuro, sin habilitarla ni prohibirla universalmente.
   - Límites de creación, mensajería, archivado y recuperación del cliente;
     alternativa manual, sin atribuir automatización a las instrucciones.
3. Ajustar `references/avisos.md` para que sus reglas no contradigan ese reparto.
   Conservar estados, esquema estricto, evidencia del origen y acuses; no alterar
   el protocolo v1 ni administrar ciclos que su auxiliar no soporta.
4. Incorporar en `packaging/skills/aikit-setup/SKILL.md` el acceso explícito a
   coordinación: explicar finalidad, ámbito local, detección del estado existente
   y ruta hacia las instrucciones correspondientes. Distinguir entrada guiada
   de configuración automática; no inventar una opción CLI de instalación.
   La activación manual necesita el contrato del proyecto y alcance acordado.
   Si implementar esa activación exige un cambio adicional del instalador,
   identificarlo y devolver la decisión antes de ampliar este encargo.
5. Actualizar exportador, comprobación de contenido y guías de rol afectadas.
   Evitar copiar en la skill rutas, IDs o decisiones privadas de este checkout.

La entrada específica de coordinación en setup forma parte de esta entrega.
El mecanismo automático general de cobertura de todas las capacidades sigue
siendo el trabajo de la nota 039; no se declara resuelto por añadir esa entrada.

## Criterios de aceptación

- El coordinador asigna la implementación y la revisión técnica; no las absorbe.
  Su integración no se convierte en resolución propia de conflictos de código.
- Un encargo con continuidad y una consulta breve llevan a decisiones distintas
  sin exigir modelos, metodologías, Git o runtimes ajenos al uso real del proyecto.
- Un propósito especializado usa el mismo registro y reglas que otra tarea;
  no origina automáticamente un departamento, otra skill o un segundo coordinador.
- Las correcciones relacionadas vuelven al responsable comprobado, sin duplicar
  tareas ni dar por segura una recuperación que el cliente no soporte.
- Cada traspaso deja claros objetivo, responsable, límites, referencias,
  dependencias y destino de respuesta. Envío, recepción y registro siguen distintos.
- Setup permite descubrir la coordinación y explicar su ruta de activación;
  instalar, leer o seleccionar una capacidad no activa el proyecto en silencio.
- El paquete exportado contiene todas las referencias necesarias, con enlaces
  internos válidos. Las fuentes y la versión instalada se distinguen al informar.
- La entrega preserva los invariantes previos de avisos, integración y limpieza.

## Validación prevista

1. Validación estructural con el `quick_validate.py` de skill-creator para las
   skills modificadas; comprobar enlaces internos y exportación íntegra.
2. Pruebas del exportador y controles Python pertinentes. Si cambia TypeScript,
   ejecutar también su verificación establecida; no exigirla por una edición Markdown.
3. Evaluación independiente de comportamiento con casos ficticios: implementación
   con continuidad, apoyo breve, revisión técnica, chat especializado reutilizable,
   identidad incierta, ausencia de Git/mensajería y petición de comunicación directa
   entre tareas. Observar decisiones y artefactos, no solo coincidencias de texto.
4. Revisión independiente de la entrega mediante el flujo de desarrollo. El
   coordinador contrasta resultados y pendientes, sin sustituir el dictamen técnico.
5. Conservar resultados y límites: validación estructural y evaluación ficticia
   no acreditan instalación, activación ni mensajería real. El piloto en AIKit y
   la prueba posterior en otro proyecto siguen siendo validaciones separadas.

## Exclusiones y siguiente ejecución

Esta preparación no modifica fuentes de la skill, instalador, caché ni paquete
habitual; tampoco crea chats, envía mensajes, instala, publica o hace push.
No implementa automatización, comunicación entre pares, relevo del auxiliar,
nuevos ciclos transaccionales ni la mejora de Director de Ideas de la nota 040.

Siguiente encargo recomendado: implementar y verificar estos cambios en fuentes,
con bmad-build y skill-creator, manteniendo revisión independiente. El coordinador
asignará la ejecución con el medio y permisos pertinentes, conservando el estado
del trabajo existente. Actualizar la instalación habitual y realizar el piloto
se prepararán a partir de la entrega comprobada.
