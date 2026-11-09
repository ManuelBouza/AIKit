# 016 — Investigar antes de experimentar

- Fecha: 2026-11-07
- Estado: Implementada e instalada en los ámbitos global y proyecto

El usuario prefiere consultar primero la documentación oficial y después las
fuentes especializadas para saber cómo realizar una tarea. Reservar las pruebas
exploratorias y el ensayo y error para cuestiones que no estén resueltas o
documentadas en esas fuentes. Esta preferencia orienta el trabajo actual y debe
formar parte de las instrucciones de AIKit una vez que la idea esté madura.
El usuario autorizó su implementación el 2026-11-08. La plantilla gestionada
`config/codex/investigacion.md` se incluye en el instalador y el complemento;
prioriza documentación oficial y fuentes especializadas cuando aporten valor,
sin suprimir pruebas de verificación. La configuración aplicada anteriormente
se actualizó mediante setup el 2026-11-08. Se previsualizó la incorporación
conservando el contenido previo, se aplicó en global y proyecto con respaldos,
y `status` devolvió `current` en ambos ámbitos. Esto verifica la configuración,
no el comportamiento del agente en todas las tareas futuras.
