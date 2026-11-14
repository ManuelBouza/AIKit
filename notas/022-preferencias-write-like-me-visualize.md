# Uso contextual de write-like-me y visualize

Fecha: 2026-11-12.
Estado: implementada en fuentes; instalación real pendiente.

## Idea

Incorporar a AIKit preferencias para detectar cuándo conviene utilizar las
capacidades existentes `write-like-me` y `visualize`.

### Redacción con el estilo del usuario

Usar `write-like-me` cuando se detecte que el usuario está redactando un correo
o un escrito destinado a otras personas que deba llevar su forma de escribir.
La intención es que AIKit reconozca la necesidad y active la capacidad pertinente
sin exigir que el usuario la mencione en cada ocasión.

### Decisión de Manuel — 2026-11-13

Aplicar automáticamente su estilo a los escritos preparados en su nombre para
otras personas, salvo que indique otro estilo. Aprovechar `write-like-me` cuando
esté disponible y respetar el contenido, destinatario y preferencias del encargo.

### Explicaciones gráficas con aprobación previa

Cuando se detecte que lo que se necesita explicar o mostrar se entendería mejor
gráficamente, proponer el uso de `visualize`. Explicar brevemente qué aportaría
y solicitar aprobación del usuario antes de utilizarlo, por su consumo de tokens.

Detectar la oportunidad no autoriza a ejecutar `visualize`: la aprobación debe
referirse al uso propuesto y respetar el mecanismo de autorización vigente.

### Decisión de Manuel — 2026-11-13

Si el asistente detecta que `visualize` sería útil y Manuel no lo ha pedido,
primero debe proponerlo y esperar autorización, por su consumo de tokens. Una
solicitud expresa de la visualización correspondiente ya la autoriza; no hace
falta repetir la pregunta. Esto no aprueba publicar ni otras acciones ajenas.

## Para debatir después

- Precisar las señales que indican que un escrito para terceros requiere el
  estilo del usuario y cómo respetar preferencias específicas de cada encargo.
- Definir cuándo una representación gráfica aporta suficiente claridad como para
  proponerla y cómo pedir la aprobación de forma breve.
- Consultar las instrucciones de ambas skills al concretar estas preferencias;
  reutilizarlas sin duplicar sus procedimientos ni modificar sus archivos.
- Decidir qué regla corresponde a las instrucciones generales de AIKit y cómo
  comprobar la disponibilidad de cada capacidad en el entorno de destino.

Relacionada con la nota [007](007-separar-delegacion-de-aikit.md), sobre la
distribución de responsabilidades entre instrucciones, skills y herramientas,
y la [018](018-herramientas-recomendadas-setup.md), sobre capacidades recomendadas
durante la configuración.

Guardar esta nota no instala herramientas ni implementa estas preferencias.

## Diseño propuesto — 2026-11-13

Añadir un bloque breve y opcional de preferencias de comunicación al mecanismo
existente de AIKit, aplicable al ámbito elegido mediante setup explícito. No crear
skills nuevas, modificar las existentes ni convertir su instalación en requisito.

1. Para escritos destinados a otras personas y preparados en nombre de Manuel,
   usar su estilo; si `write-like-me` está disponible, seguir sus instrucciones.
   Respetar una indicación de estilo distinta o una edición menor. Si no hay
   ejemplos suficientes, no inventarlos: explicar la limitación cuando sea relevante
   y trabajar con el contexto disponible.
2. Cuando `visualize` pudiera ayudar y Manuel no lo haya solicitado, explicar
   brevemente su utilidad y esperar autorización. Una petición expresa del visual
   autoriza su creación dentro del alcance; no autoriza publicación. Si la skill no
   está disponible, informar cuando sea relevante y ofrecer alternativas.
3. La preferencia no obliga a generar gráficos para tareas simples ni modifica
   procedimientos de terceros. Las instrucciones de mayor prioridad y las
   capacidades reales del cliente prevalecen; una regla de preferencias no puede
   garantizar comportamiento en todos los clientes o sesiones.

Propuesta de implementación posterior: integrar plantillas versionadas en el
instalador existente, con vista previa, idempotencia y preservación de bloques
ajenos; incluirlas en el exportador y validar con perfiles ficticios. Evaluar
con `bmad-help` el flujo adecuado para implementar en este repositorio. No se
ha modificado el instalador ni se han aplicado preferencias globales en este paso.

## Implementación — 2026-11-13

Se añadieron dos opciones independientes al instalador y a la exportación;
setup pregunta solo por elecciones no decididas y no desactiva bloques previos.
Se probaron vista previa, perfiles ficticios, combinaciones y preservación: 40
pruebas Node aprobadas, dos junctions omitidas; 15 pruebas de exportación
aprobadas. La revisión identificó y corrigió dos carencias. No se ha actualizado
el complemento instalado ni aplicado estas preferencias al perfil real.
Especificación: [preferencias de comunicación](../_bmad-output/implementation-artifacts/spec-022-preferencias-comunicacion.md).
