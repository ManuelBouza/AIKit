# 031 — Aislamiento de trabajos paralelos sin Git

- Fecha: 2026-11-14.
- Estado inicial: Pendiente de debatir.
- Estado actual: Decisión de secuenciación o Git por proyecto; detalles pendientes.

Manuel pregunta cómo evitar interferencias entre chats de tareas en proyectos
sin Git, ante el uso de worktrees en proyectos que sí lo emplean. Relacionada con
[025](025-coordinador-global-chats-autonomos.md) y
[027](027-automatizacion-coordinacion.md). No se decide instalar Git ni se
autoriza construir o activar un mecanismo nuevo.

## Alternativas para estudiar

1. Repartir archivos o recursos por responsable y secuenciar las escrituras
   que coincidan. Conserva una sola carpeta, pero necesita coordinación y manejo
   de fallos; no aísla puertos, bases de datos o servicios compartidos.
2. Crear copias de trabajo separadas a partir de una base identificada y comparar
   e integrar después los cambios, detectando divergencias. Puede permitir más
   paralelismo, pero una copia no aporta por sí misma historial, integración ni
   prevención de conflictos; hay que decidir cómo tratar binarios, archivos
   privados, enlaces y recursos externos. No sobrescribir cambios ni eliminar
   copias sin comprobación y autorizaciones aplicables.
3. Aprovechar aislamiento o versionado que el proyecto ya tenga, si está disponible
   y el usuario lo elige. Ninguna herramienta específica es un requisito universal.

Recomendación inicial: reparto y secuenciación como opción mínima portable; evaluar
copias aisladas para trabajos que justifiquen su coste y cuyo proceso de integración
se pueda verificar. Decidir por proyecto y tarea. Ninguna opción se ha implementado.

La [documentación de Git](https://git-scm.com/docs/git-worktree) confirma que los
worktrees proporcionan árboles de trabajo asociados a un mismo repositorio; comparten
parte de su configuración y metadatos. Aíslan las carpetas de trabajo, pero no
resuelven por sí solos conflictos al integrar ni recursos externos compartidos.
Falta contrastar estrategias de copia, integración, recuperación y seguridad con
fuentes y pruebas apropiadas antes de incorporarlas como garantía al producto.

## Decisión de Manuel — 2026-11-14

No exigir Git ni worktrees en todos los proyectos. El usuario decide si necesita
varias tareas de escritura en paralelo: si las necesita, se le indica que debe
disponer de Git y activar su uso en el proyecto para emplear worktrees; si no,
se realiza una tarea de escritura a la vez para evitar escrituras dobles. No se
instala Git, inicia un repositorio ni crean worktrees sin la autorización aplicable.
Las alternativas de copias anteriores quedan como investigación histórica, no
como diseño elegido. El alcance exacto de las operaciones de solo lectura y de
los recursos compartidos externos debe concretarse sin prometer aislamiento total.

Cuando los chats de tarea solicitan integrar cambios, el coordinador es responsable
de coordinarlos e integrar sus resultados, con revisión de integración como en una
PR. Esto sustituye el reparto previo que asignaba esa integración a otro chat.
Los chats conservan sus propias revisiones y verificaciones; el coordinador no
asume que un worktree elimina los conflictos de integración ni de servicios.
Las solicitudes se trasladan por el mecanismo persistente acordado, sin imponer
mensajería directa. Los detalles de revisión, resolución de conflictos, permisos
y destino de integración siguen por definir y probar.

Manuel establece además que el coordinador es responsable de los datos finales,
su salud y la prevención de pérdida. Si el proyecto usa Git, gestiona las ramas
principales del proyecto, como `master` o `develop`; cada chat de tarea gestiona
su respectiva rama. Las autorizaciones de acciones sensibles siguen vigentes.

## Protocolo de integración aceptado — 2026-11-14

1. **Solicitud.** El chat de tarea termina sus verificaciones y registra una
   solicitud persistente identificable con tarea y ciclo, objetivo, rama y commit
   exacto cuando haya Git, destino propuesto, pruebas, limitaciones y recursos
   afectados. Incluye dependencias y pendientes relevantes; no copia logs ni envía
   mensajes directos. Debe existir antes del cierre final si integrar forma parte
   del alcance, para no crear una dependencia circular con la entrega final.
2. **Recepción y orden.** El coordinador consulta las solicitudes, identifica sus
   versiones y determina el orden a partir de dependencias y prioridades acordadas.
   Si falta una decisión material o hay conflictos de recursos, consulta a Manuel;
   no cambia el alcance por su cuenta. Evita dos integraciones simultáneas en el
   mismo destino y no trata un acuse de lectura como aprobación de integración.
3. **Comprobación previa.** Verifica identidad, autorización, destino, alcance,
   commit solicitado y estabilidad del origen; revisa el cambio y la evidencia
   como una PR, junto a los efectos sobre otros encargos. Protege los datos finales
   y los cambios locales preexistentes. Si la fuente o el destino cambian durante
   la revisión, vuelve a comprobar lo afectado antes de aplicar la integración.
4. **Integración y conflictos.** Aplica los cambios en el destino autorizado con
   el flujo del proyecto y verifica el resultado. Resuelve las cuestiones técnicas
   dentro del alcance; si una resolución cambia requisitos o exige una decisión
   de Manuel, detiene esa parte y la presenta. Ante conflicto o fallo conserva
   información recuperable y no sobrescribe trabajo ajeno. La documentación de
   [Git merge](https://git-scm.com/docs/git-merge) advierte que iniciar un merge
   con cambios locales significativos puede dificultar la recuperación.
5. **Resultado.** Registra solicitud y versión, destino y versión resultante,
   comprobaciones, conflictos, resultado y pendientes; el chat de tarea consulta
   el resultado persistente y completa cierre y limpieza autorizados. Diferenciar
   recibido, revisión pendiente, corrección necesaria, integrado y bloqueado como
   resultados de integración candidatos, sin añadirlos automáticamente a los
   estados generales de tarea.

Sin Git se permite una sola tarea de escritura a la vez. El coordinador protege
los datos finales y registra la recepción y verificación del resultado en la carpeta
del proyecto, sin inventar ramas, commits ni una fusión. El chat sigue siendo
responsable de su trabajo y limpieza. La selección de operaciones precisas, las
notificaciones sin mensajería directa y el mecanismo para evitar concurrencia
accidental requieren diseño y pruebas. `push`, publicación y eliminaciones
irreversibles mantienen su autorización específica; no se presume que un pedido
de integración autorice esas acciones.

Manuel acepta este protocolo. Sus mecanismos técnicos y pruebas siguen pendientes;
su aceptación no ejecuta una integración concreta.
