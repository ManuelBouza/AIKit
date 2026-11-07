# Espera pasiva y vigilancia económica de OpenCode

Fecha: 2026-10-31.
Estado: implementada en fuentes; pendiente de empaquetado e instalación.

## Idea

Minimizar el gasto de Codex en vigilar las ejecuciones de OpenCode. Dejar trabajar
al ejecutor y evitar ciclos frecuentes de razonamiento, sondeos de archivos,
lectura de metadatos y mensajes que solo anuncian que sigue activo.

Conservar la multitarea: si hay otro trabajo útil de orquestación, Codex debe
atenderlo. Si solo queda esperar, usar una espera pasiva durante un plazo
prudente, interrumpible por mensajes del usuario. En este chat se están usando
bloques de hasta cinco minutos, sin convertir ese intervalo en una regla fija.

Al entrar en espera, mostrar un aviso breve: «En espera de OpenCode. Puedes
solicitarme otras tareas; puedo atenderlas mientras OpenCode continúa trabajando».
El aviso debe dejar clara la disponibilidad del coordinador sin generar mensajes
periódicos que solo repitan el mismo estado.

## Para debatir después

- Comparar la espera y las notificaciones de subagentes nativos con las
  capacidades efectivamente disponibles para procesos externos de OpenCode.
- Priorizar avisos de finalización, error, permisos o bloqueo acreditado; si
  hace falta sondeo, ejecutarlo mediante código determinista y despertar al
  coordinador solo ante un evento relevante o un plazo de control razonable.
- No lanzar otro modelo o subagente únicamente para vigilar. No confundir una
  espera de herramienta con una garantía de consumo total cero de la cuenta.
- Un timeout del cliente no demuestra que el trabajo haya terminado. Conservar
  el intento y la sesión, recuperar la salida sin otra inferencia y comprobar
  procesos vivos antes de cualquier reintento.
- Incorporar la política a las reglas portables y a la documentación adecuada,
  reutilizando herramientas y skills existentes sin alterar Superpowers.
- Validar número de activaciones de Codex, latencia de aviso, interrupción por
  el usuario y conservación de la multitarea, con pruebas sin modelos reales.

## Estado observado

La espera pasiva se aplica manualmente en este chat y está anotada en su registro
de coordinación. No está implementada ni instalada como política permanente de
AIKit. La documentación oficial describe herramientas de espera para subagentes;
no acredita por sí sola un canal equivalente para el puente externo actual:
[Multi-agent](https://developers.openai.com/api/docs/guides/responses-multi-agent).

Relacionada con [003 — Coste de delegación](003-heuristica-coste-delegacion.md) y
[002 — OpenCode como subagente acotado](002-opencode-como-subagente-acotado.md).

Guardar esta nota no aprueba su diseño ni autoriza su implementación.

## Investigación del 2026-11-01

Se comprobó en este chat una espera ligada al proceso: un máximo de 300 segundos retornó al finalizar un proceso de 35 segundos. También se comprobó que una notificación asíncrona de la herramienta interrumpe la espera activa. Se aplicó a trabajos reales de OpenCode, sin un modelo o subagente dedicado a vigilar.

La notificación observada procede de la herramienta que espera la CLI; no es un push directo de OpenCode al chat. La salida del cliente es una señal que obliga a comprobar resultado, sesión y procedencia: pending o uncertain no autorizan duplicar la inferencia. No se demostró despertar de un chat cerrado o sin turno activo.

OpenCode publica SSE en /api/event, con filtro por tipos. El flujo es global y volátil: una integración necesita correlación por tarea/sesión y reconciliación tras desconexiones, sin exponer eventos de otros trabajos.

La estimación estadística queda como respaldo: duraciones por intento, proveedor/modelo/esfuerzo/rol, mediana y dispersión cuando existan muestras comparables; separar errores y censurados. Los totales de sesiones reutilizadas no son duraciones de una única ejecución y no se usarán para predecir.

La mecánica está probada y aplicada en este chat; su integración permanente en la skill/complemento sigue pendiente. La 001 continúa abierta y no se activa aquí ninguna automatización. Investigación documentada en docs/espera-finalizacion-opencode.md del worktree de orquestación.

## Implementación autorizada

El usuario aprobó con `go` integrar en las fuentes de AIKit la espera por finalización y el registro de duraciones por intento. La implementación se delega a OpenCode con revisión independiente posterior. No implica instalación, activación de la automatización de la 001 ni cambios del servidor.


## Cierre de implementación en fuentes — 2026-11-01

Revisión independiente aceptada en el worktree de orquestación. Las reglas
portables priorizan la finalización de herramienta cuando el host la ofrece,
con aviso de disponibilidad para otras tareas y sin un modelo dedicado a vigilar.
El núcleo conserva la espera acotada por resultado disponible, sin esperar la
limpieza posterior del supervisor. Un timeout pendiente no autoriza reenviar.

Se registran duraciones por intento y se exponen mediante `delegate.py timing`;
la recuperación actualiza la muestra parcial sin duplicarla ni degradar una
muestra final. Hay prueba con un subproceso real que sigue vivo al entregar el
resultado. El autor informa 778 pruebas aprobadas; el revisor ejecutó las pruebas
focalizadas de los cambios, Ruff, formato y mypy. La aceptación de sesiones y
hashes se validó mediante `scripts/review_evidence.py`.

Pendiente: empaquetar e instalar las fuentes aceptadas y comprobar la política
en un chat nuevo. No se garantiza aviso a un chat cerrado/inactivo ni se ha
activado la automatización de la 001. Las estimaciones condicionadas de tiempo
restante y su calibración con datos reales no se declaran implementadas.
