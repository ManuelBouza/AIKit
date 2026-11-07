# OpenCode como subagente con una tarea acotada

Fecha: 2026-10-30.
Actualización: 2026-11-04.
Estado: pendiente de debatir.

## Idea

Considerar cada sesión de OpenCode como el subagente que se habría lanzado si
OpenCode no estuviera disponible. Su intervención debe limitarse a una tarea
específica, con alcance y resultado definidos, sin encargarle una gestión extensa
del trabajo.

El coordinador conserva la gestión global y las decisiones sobre qué tarea
asignar. Usar OpenCode no debe ampliar las responsabilidades del subagente ni
convertir una subtarea en una delegación de todo el proceso.

## Investigar y reproducir la interacción con subagentes de Codex

Investigar cómo Codex interactúa con sus subagentes durante todo su ciclo de vida
para reproducir ese funcionamiento al delegar en OpenCode. La equivalencia debe
abarcar tanto el encargo acotado como la coordinación durante su ejecución y la
recepción del resultado.

- **Lanzamiento:** cómo decide lanzar un subagente, cómo lo crea, qué instrucciones
  y contexto le transmite y cómo identifica la tarea y la sesión.
- **Durante la ejecución:** qué controla Codex, qué estado y avances puede conocer,
  cómo recibe mensajes o solicitudes de intervención y qué trabajo puede seguir
  haciendo el coordinador mientras tanto.
- **Espera y finalización:** cómo se entera Codex de que el subagente terminó, qué
  mecanismos de espera o notificación utiliza y cómo distingue finalización,
  bloqueo, error o necesidad de respuesta del usuario.
- **Resultado y continuación:** cómo recibe y utiliza la entrega, comprueba el
  resultado, envía aclaraciones o continúa el trabajo con el mismo subagente.
- **Control del ciclo de vida:** cómo gestiona interrupciones, cancelaciones,
  límites de tiempo y tareas que siguen vivas, evitando duplicar ejecuciones.

Consultar documentación oficial y contrastarla con observaciones del entorno,
distinguiendo comportamiento comprobado, inferencias y mecanismos internos no
documentados. Identificar qué puede reproducir OpenCode, qué necesita adaptación
y qué diferencias quedan pendientes de resolver.

El resultado buscado es una descripción del ciclo completo y una propuesta de
equivalencia con OpenCode basada en evidencia.

## Para debatir después

- Cómo definir los límites de cada sesión y cuándo dividir una tarea demasiado amplia.
- Qué información mínima necesita el ejecutor y qué resultado debe devolver.
- Cómo mantener esta equivalencia con los roles de Codex y Superpowers.

Relacionada con la nota [005](005-prompts-concisos-opencode.md), sobre el encargo
que recibe el ejecutor, y la [008](008-espera-pasiva-opencode.md), sobre esperas y
avisos durante el trabajo de OpenCode.

La investigación queda pendiente. Guardar esta nota no modifica las reglas
actuales ni autoriza su implementación.
