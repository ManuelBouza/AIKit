# Método del Director de Ideas

Fecha: 2026-10-31.
Estado: pendiente de debatir.

## Intención

Definir un método para que el usuario comprenda todo el proceso: qué tarea se
realizará, por qué y cómo se hará. El usuario debe poder participar con intención,
criterio y dirección, manteniendo la comprensión del proyecto o tarea.

## Fases propuestas

### 1. Visión

Partir de la intención del usuario, sin exigir instrucciones específicas. En esta
fase el usuario está pidiendo una opinión sobre el problema planteado.

Organizar el caos inicial, explorar opciones y presentar sus pros y contras para
que el usuario pueda formar su criterio y decidir una dirección.

### 2. Estructura

Una vez que el usuario escoja una opción o una combinación de opciones,
estructurar la petición de forma que pueda revisarla y aprender qué se va a hacer.

Hacer comprensible la estructura del proyecto o de la tarea que se ejecutará,
evitando que el usuario quede ajeno a su organización y desarrollo.

### 3. Requisitos

Plantear todos los requisitos de la tarea. El usuario los revisará y decidirá
cuáles aprobar, cuáles rechazar y cuáles requieren modificaciones.

## Aplicación propuesta

Aplicar el método a cada solicitud que presente el usuario, garantizando en todo
momento su comprensión de la tarea que se realizará y de cómo se hará.

## Ingeniería de contexto

Principios aportados por el usuario para desarrollar este método:

- Lo importante no es solo lo que se le dice al modelo de IA, sino qué sabe el
  modelo cuando se le dice.
- Un contexto rico gana a un prompt perfecto en un contexto pobre.
- Una sesión larga de exploración y divagación puede ayudar a que una idea quede
  bien estructurada y con los requisitos correctos antes de implementarla.

El valor del usuario está en la intención, en el criterio y en la dirección.

## Para debatir después

- Cómo comprobar que el usuario comprende cada fase y cómo recoger sus decisiones.
- Cómo adaptar la profundidad del método a cada solicitud sin perder su intención.
- Cómo encajar el método con los flujos existentes de Superpowers y distribuir sus
  instrucciones entre `AGENTS.md` y skills, como plantea la nota
  [007](007-separar-delegacion-de-aikit.md).
- Cómo conservar el contexto útil y las decisiones durante conversaciones largas,
  y trasladar solo lo necesario a las tareas delegadas de la nota
  [005](005-prompts-concisos-opencode.md).

Guardar esta nota no activa el método ni cambia las reglas actuales. Su diseño e
implementación quedan pendientes de debate y autorización.
