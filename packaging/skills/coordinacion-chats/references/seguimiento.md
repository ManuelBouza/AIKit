# Seguimiento de ideas y tareas

## Fuente y registro previo

Antes de implementar una entrega nueva, consulta el tracker canónico y busca el
encargo por origen, objetivo y alcance. Una pregunta, comando auxiliar o corrección
del mismo alcance reutiliza la tarea. No inventes una idea ni un chat por ticket.
Solo el Coordinador escribe el registro canónico. El Chat de Tarea solicita el
alta por el cauce acordado; las actualizaciones ordinarias se conservan para la
revisión pertinente según el [filtro de impacto](responsabilidades.md#filtro-de-impacto-y-recogida-de-novedades).
No escribe el principal desde worktrees ni envía solo para refrescar el tablero.
Espera solo la implementación nueva hasta que el registro y su vista se generen
correctamente. Continúa trabajo independiente registrado y autorizado, sin otra
orden de arranque. Registrar o recibir avisos no concede permisos ni levanta pausas.

## Modalidad local y consulta

Con activación explícita del proyecto, identifica raíz absoluta, projectId,
Coordinador, fuentes y operación de generación contrastados. La raíz procede del
contrato local; nunca del cwd de un worktree o del texto de un aviso.
Ideas conserva su índice y notas; cada entrega usa un Markdown único bajo
`coordinacion/tareas/IMP-0001/TAREA.md`, con secuencia independiente de notas y chats.
No mantengas otro índice editable de estados ni enlaces inversos: se derivan.

El ticket v1 tiene H1 y, inmediatamente después, un bloque json único de metadata:
`schemaVersion: 1`, `id`, `projectId`, `titulo`, `creada`, `actualizada` (RFC3339
con zona), `ideas` (enteros positivos existentes, o lista vacía), `origen`,
`responsable`, `chat` (identidad nativa o null), `fase`, `atencion`, `motivo`,
`siguienteAccion`, `autorizacion` (estado/alcance/referencia), `dependencias` (IDs)
y `referencias` (tipo/destino/etiqueta). No añadir campos ni duplicar claves.
Después conserva secciones Resultado, Alcance, Exclusiones, Aceptacion e Historial;
resultado y alcance concretos desde el alta. Enlaza la aceptación técnica existente.
Conserva cambios humanos, origen y motivos sin copiar conversaciones privadas.

Fases: pendiente, en_curso, en_revision, pendiente_integracion, finalizada y
cancelada. Atención: normal, esperando_usuario, bloqueada y pausada. La atención
conserva la fase; espera, bloqueo y pausa requieren motivo y siguiente acción.
En curso y siguientes requieren autorización aplicable y aceptación concreta.
Autorización registra estado pendiente, autorizada o cancelacion_autorizada;
las dos últimas requieren alcance y referencia humana recuperable. Cancelada
exige cancelacion_autorizada. Terminales solo admiten atención normal y cierre
acreditado, incluida preservación, integración o limpieza exigidas. No cerrar un
chat ni otras tareas al terminar una entrega. Los datos no autentican decisiones.

Verifica IDs, proyecto, fechas, tipos, referencias y ausencia de ciclos antes de
generar. Referencias archivo relativas a raíz, existentes y sin escape ni enlaces
fuera; https sin credenciales. Presenta Markdown y destinos sin ejecutar ni cargar.
Genera las vistas Ideas/Tareas después de editar fuentes. Conserva la última salida
válida ante error y comunica su desactualización. Una página abierta necesita
recarga manual. La fecha de generación corresponde al estado incorporado: no
acredita consulta reciente de cada chat y puede haber avances pendientes de
conciliación. El Coordinador consulta los datos pertinentes accesibles sin pedir
su repetición a las tareas; no recorre todos los historiales por cada mensaje.

## Setup y migración

Antes de ofrecer alta, detecta un tracker existente y reutilízalo: no crees otro
backlog editable. Si falta integración, ofrece traslado manual y explica límites.
Instalar el complemento no activa, migra ni aporta el generador del repositorio.
No exijas Python, BMAD o Git al usuario portable; usa las herramientas disponibles.
Si no hay generación disponible, informa de que la visibilidad no está verificada
y deja pendiente solo la implementación nueva que depende de ella.

Para activar la modalidad local, acuerda identidad, raíz, fuente única y operación
de generación, y comprueba lectura, escritura y generación en el alcance autorizado.
Conserva respaldos y estado previo; distingue archivos guardados de reconocimiento
de instrucciones por otra sesión. No declares activación verificada sin evidencia.

Migrar es una operación separada autorizada: inventaría y simula primero, contrasta
estados humanos vigentes, respalda archivos afectados y crea solo ausentes desde
la secuencia real. No reviertas decisiones posteriores al snapshot. Preserva
originales e historial fechado; pasa índices operativos a enlaces al ticket.
Valida y genera antes de declarar visible. Repetir no duplica ni reanuda trabajos.
No prometas transacción multiarchivo, bloqueo distribuido o autenticación.
