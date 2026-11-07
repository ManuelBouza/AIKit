# Guardarraíles para evitar filtraciones al delegar a OpenCode

Fecha: 2026-10-30.
Estado: pendiente de debatir.

## Idea

Filtrar el contenido de las tareas enviadas a OpenCode para proteger información
privada, empresarial y sensible, incluida aquella que podría acabar utilizándose
en el entrenamiento de modelos. Establecer guardarraíles fuertes que eviten
filtraciones.

La protección debe contemplar tanto el contenido enviado al iniciar la tarea como
los datos que el ejecutor pueda leer o transmitir durante la sesión. No basta con
limpiar el texto inicial si después puede acceder a archivos sensibles.

## Para debatir después

- Qué datos no pueden salir del entorno y cómo detectarlos antes de delegar.
- Cuándo anonimizar o reducir el contexto, cuándo bloquear el envío y cuándo
  resolver la tarea en un entorno autorizado.
- Cómo limitar los archivos, herramientas y destinos accesibles al ejecutor.
- Cómo verificar las condiciones de privacidad, retención y entrenamiento de cada
  proveedor y cuenta, sin asumir que son iguales ni que un entorno local es privado.
- Cómo comprobar que los controles bloquean filtraciones sin incluir información
  sensible en registros o mensajes de error.

Guardar esta nota no modifica las reglas actuales ni autoriza su implementación.
