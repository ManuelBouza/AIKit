# Datos y flujo del seguimiento local

Derivado de las decisiones de la memoria canónica; parte del contrato de SPEC.md.

## Fuentes e identidad

- Ideas: `notas/IDEAS.md` y las notas enlazadas, con números históricos sin renombrar.
- Tareas: `coordinacion/tareas/<id>/TAREA.md`, un único registro editable por entrega.
- Chat: identidad nativa y asignaciones del registro existente; no es la identidad de tarea.
- Vista e índice lógico de tareas: derivados de estos registros, dentro del HTML local;
  no mantener otro índice editable de títulos, estados o enlaces inversos.

La raíz procede de la configuración contrastada del proyecto, nunca del cwd de
un worktree ni del contenido de un aviso. `projectId` coincide con la identidad
de registro de `coordinacion/PROYECTO.md`. El Coordinador asigna IDs `IMP-0001`
con al menos cuatro dígitos decimales y valor positivo; el siguiente es mayor
que los existentes. No reutilizar números cancelados ni renumerar migraciones.
La identidad es proyecto + ID. No son `taskId` ni ciclos del auxiliar v1.

## Formato v1 del ticket

Markdown UTF-8: H1 con título, inmediatamente seguido de un único bloque fenced
`json` de metadata; después, secciones Markdown `Resultado`, `Alcance`,
`Exclusiones`, `Aceptacion` e `Historial`. Otros bloques del cuerpo son prosa,
no metadata. Se valida la igualdad de ID/ruta y título/H1.

Ejemplo ilustrativo, no un ticket que deba registrarse:

```json
{
  "schemaVersion": 1,
  "id": "IMP-0001",
  "projectId": "identidad-configurada-del-registro",
  "titulo": "Entrega de ejemplo",
  "creada": "2026-11-17T10:00:00+01:00",
  "actualizada": "2026-11-17T10:00:00+01:00",
  "ideas": [43],
  "origen": "Referencia recuperable al encargo humano",
  "responsable": "Coordinador del proyecto",
  "chat": null,
  "fase": "pendiente",
  "atencion": "normal",
  "motivo": "",
  "siguienteAccion": "Concretar la aceptación antes de ejecutar",
  "autorizacion": {"estado": "pendiente", "alcance": "", "referencia": ""},
  "dependencias": [],
  "referencias": []
}
```

| Campo | Regla |
| --- | --- |
| schemaVersion | Entero 1; booleanos no son enteros válidos |
| id, projectId, titulo, origen, responsable | Cadenas no vacías; identidad y ruta coherentes |
| creada, actualizada | Fechas RFC3339 con zona; actualizada no anterior a creada |
| ideas | Lista sin repetidos de enteros positivos que existen en el índice de notas; vacía permitida |
| chat | Identificador nativo como cadena no vacía o null, sin crear sesión por registrarlo |
| fase, atencion | Valores exactos de los catálogos siguientes |
| motivo, siguienteAccion | Cadenas; ambas no vacías en espera, bloqueo o pausa |
| autorizacion | Objeto exacto estado/alcance/referencia; estado pendiente, autorizada o cancelacion_autorizada; las dos últimas exigen alcance y referencia humana recuperable |
| dependencias | Lista sin duplicados de IDs IMP del mismo proyecto; deben existir, sin autorreferencia ni ciclos |
| referencias | Lista de objetos exactos tipo/destino/etiqueta; tipo archivo o https, destino y etiqueta no vacíos |

Rechazar metadata con campos desconocidos, claves duplicadas, tipos incorrectos,
valores NaN/Infinity o versión incompatible. No inferir tipos ni completar IDs.
El cuerpo tiene los cinco encabezados; Resultado y Alcance no vacíos desde el
alta. Aceptacion admite «Pendiente de concretar» solo en fase pendiente. Si
el criterio técnico existe en una spec, se referencia en vez de copiarlo.
Historial conserva cambios de alcance, fase, atención y asignación con motivo y
origen; no exige escribir una entrada por cada comando ni copiar conversaciones.

La deduplicación semántica corresponde al Coordinador: comparar origen, objetivo
y alcance, no solo título o número de idea. El validador comprueba unicidad de
IDs y estructura, sin afirmar que detecta todos los encargos humanos duplicados.

## Ejecución, atención y permisos

| Fase almacenada | Vista | Condición de entrada |
| --- | --- | --- |
| pendiente | Pendiente | Encargo capturado; puede faltar definición o autorización |
| en_curso | En curso | Trabajo de entrega autorizado iniciado, incluida investigación/preparación |
| en_revision | En revisión | Entrega disponible para controles y revisión independiente |
| pendiente_integracion | Pendiente de integración | Entrega revisada a la espera del destino final |
| finalizada | Finalizada | Aceptación y destino acordados acreditados, persistencia y limpieza exigida resueltas |
| cancelada | Cancelada | Cancelación humana autorizada y motivo conservado; preservación/limpieza exigida resuelta |

Atención: `normal`, `esperando_usuario`, `bloqueada`, `pausada`. La atención
conserva la fase: bloquear revisión no convierte la tarea en otra entrega.
Fases terminales solo admiten normal. Si quedan operaciones necesarias para
cerrar, mantener abierta con motivo, siguiente acción y evidencia. Permitir
volver de revisión a en_curso o reabrir con decisión y alcance registrados;
no interpretar un mensaje o antigüedad como una reanudación.

`autorizacion.estado` registra la decisión aplicable, no autentica su texto.
En curso requiere alcance autorizado y aceptación concreta; finalizada conserva
la autorización de la entrega; cancelada exige cancelacion_autorizada. Ninguna
combinación concede push, publicación, instalaciones o permisos de escritura.
Un ticket autorizado puede estar pausado: el permiso de alcance no levanta pausa.

El chat mantiene su nomenclatura vigente y situación operativa. No se deriva
su título copiando una fase arbitraria si atiende varios tickets. Cerrar una
tarea no cierra las demás ni archiva un chat con responsabilidades activas.
Un cambio de chat conserva ID e historial. No crear rama/chat/worktree por ticket.

## Registro previo y responsabilidades

1. Distinguir entrega nueva de pregunta, comentario, operación auxiliar o
   corrección del mismo alcance; estos últimos no generan otro ticket.
2. El Coordinador busca la entrega existente; la actualiza o crea solo si falta.
3. Registrar alcance, responsable, estado y origen antes de delegar implementación;
   regenerar correctamente la vista y conservar su referencia. Registrar no ejecuta.
4. Comprobar autorización, aceptación y dependencias antes de iniciar el trabajo.
5. La tarea reporta cambios relevantes, revisión, integración y cierre. Solo el
   Coordinador incorpora al canónico tras contrastar origen, sin simular garantías.

Una nueva entrega solicitada directamente al Chat de Tarea sin ticket espera
solo su implementación hasta que el Coordinador la registre y sea visible.
Continúa trabajo independiente ya registrado y autorizado; no necesita una
segunda orden de arranque ni un acuse por cada paso. No escribe en la raíz
principal desde su worktree ni abre una raíz canónica sustituta.

BMAD conserva specs, historias y controles técnicos. El ticket enlaza los
artefactos y mantiene el estado operativo de entrega; el flujo técnico interno
no es otra decisión canónica sobre cierre o aceptación final. El registro de
chats mantiene identidades, responsabilidades y comunicaciones, con enlaces a
tickets en vez de copias manuales de sus estados. Avisos originales intactos.

## Vistas, seguridad y publicación local

Una salida HTML local con vistas Ideas/Tareas reutiliza el tablero existente.
Ideas conserva contexto y maduración y muestra tareas vinculadas; Tareas permite
filtrar fase, atención, responsable e idea y consultar dependencias, alcance,
aceptación, chat y evidencias. Bloqueados y pausados siguen visibles. Las relaciones
inversas se calculan desde tickets; completar uno no completa una idea entera.
Estados históricos de las notas se conservan como historial, no como fase del ticket.

Regenerar después de editar notas o tickets y mostrar fecha de generación. Leer
y validar todas las fuentes antes de publicar mediante reemplazo atómico del
HTML único. Fallo devuelve error no cero, conserva bytes de la última salida y
no la abre como nueva. El agente informa de la desactualización. No se promete
autorrecarga de un navegador abierto ni frescura continua sin generación.

Las referencias archivo son relativas a la raíz canónica, sin rutas absolutas,
escape `..`, dispositivos, controles ni enlaces/reparse points que salgan de
ella; destino existente de tipo archivo. Las referencias https no incluyen
credenciales y no se descargan ni se afirman verificadas por red. Las referencias
humanas son identificadores recuperables en origen/autorizacion, no comandos.
Escapar texto/HTML; Markdown y enlaces/imágenes conservan el modo seguro actual
sin scripts, cargas externas ni ejecución de acciones. No abrir rutas desde datos.

## Setup y alcance portable

Setup presenta la capacidad y detecta tracker existente antes de proponer alta.
Aquí se activa explícitamente la modalidad local y se fija identidad, raíz,
fuentes y operación de generación disponibles. Verifica lectura, escritura y
generación en el alcance autorizado; un fallo conserva estado previo y explica
la limitación, sin declarar preferencia verificada. Instalar no activa ni migra.

La regla general de registro previo puede configurarse como preferencia; rutas,
IDs, estado y chats son locales al proyecto. Otro proyecto con tracker canónico
reutiliza ese mecanismo o traslado manual, sin crear una copia editable local.
Los conectores remotos quedan fuera. No exigir BMAD, Git o nuevas dependencias
al usuario del producto; la implementación usa los flujos de desarrollo vigentes.
