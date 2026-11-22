# Responsabilidad única de los chats

La activación es optativa por proyecto. Localiza el
[instalador de AIKit](../../../../installer/dist/cli.js) y ejecuta su ruta
absoluta con Node.js. En los ejemplos, `<cli>`, `<proyecto>` y
`<inventario>` son rutas absolutas pasadas como argumentos separados.

## Consultar y configurar

1. Identifica la raíz local explícita del proyecto donde se aplicará el bloque
   de `AGENTS.md`. Un proyecto puede carecer de Git. Usa
   `node <cli> project-chats status --root <proyecto>` para consultar sin escribir.
   Si `status` devuelve `shadowed`, el cliente puede usar `AGENTS.override.md`.
   Explica el conflicto y conserva el archivo de sustitución.
2. Usa la raíz explícita de inventario configurada para el proyecto. En un
   checkout principal o proyecto sin Git, las raíces local y de inventario
   normalmente coinciden. En un worktree, confirma la raíz compartida con el
   usuario o con la referencia ya configurada. Nunca la deduzcas del
   directorio actual o de la rama. Ejecuta
   `node <cli> project-chats list --root <inventario>` desde esta sesión para
   verificar lectura. Una consulta fallida deja los destinos sin verificar.
3. Previsualiza la activación con
   `node <cli> project-chats enable --root <proyecto> --inventory-root <inventario> --dry-run`.
   Muestra la raíz de inventario, el destino `AGENTS.md`, el bloque y la
   ubicación del respaldo. Cuando el usuario haya autorizado explícitamente
   el cambio para ese proyecto, aplica el mismo comando sin `--dry-run`.
   Vuelve a consultar el estado y comprueba el resultado y el respaldo.
4. Para la desactivación, usa `node <cli> project-chats disable --root <proyecto> --dry-run`
   y el mismo comando sin `--dry-run` al contar con autorización. Solo se quita
   la regla local. Las fichas permanecen accesibles en la raíz de inventario.

La consulta verifica lectura. La escritura efectiva se comprueba al aplicar
un cambio autorizado. Si falta permiso para actualizar la raíz compartida,
aprovecha la lectura cuando sea posible, informa del permiso que falta, deja
la actualización pendiente y ofrece traslado manual. No crees una copia ni
uses Git para fusionar inventarios.

## Registrar el encargo y actualizar el estado

- Busca primero las acciones nativas de identificación y consulta de chats
  disponibles en el cliente. Confirma el ID completo de este chat con
  evidencia que lo vincule a la sesión actual. Un título coincidente por sí
  solo no confirma la identidad. Si falta evidencia, deja el alta pendiente.
  Cuando ya se haya autorizado un fork, obtén del cliente su ID y el de origen.
- Consulta `list` antes de preparar un cambio. Pasa una ficha JSON por entrada
  estándar a `node <cli> project-chats upsert --root <inventario> --expected-revision <revisión> --dry-run`.
  Usa `0` para un alta y la revisión leída para una actualización. Tras la
  vista previa, aplica sin `--dry-run` para el encargo o transición autorizados.
  Si se rechaza una revisión obsoleta o hay un bloqueo activo, relee y comprueba
  los cambios antes de reintentar. Si el bloqueo persiste, informa y conserva
  el inventario para inspección.

```json
{
  "id": "00000000-0000-4000-8000-000000000001",
  "project": "Proyecto ficticio",
  "responsibility": "Validar exportaciones",
  "state": "En espera",
  "reason": "Falta aprobar el ejemplo",
  "continuation": "Retomar al recibir la aprobación"
}
```

Los estados son **Disponible**, **En curso**, **En espera**, **Pausado** y
**Cerrado**. `reason` y `continuation` son obligatorios en espera o pausa y
se omiten en los demás estados. Añade `originId` con el ID nativo de origen
si el chat es un fork. Guarda únicamente los campos de ficha. La CLI añade
fecha, revisión y título con el formato `[Estado] Proyecto · Responsabilidad breve`.

Antes de renombrar, vuelve a consultar la revisión de la ficha del ID
confirmado. Si cambió, usa el título de la última revisión. Tras la acción
nativa, lee el título visible del mismo ID y vuelve a consultar la ficha.
Confirma la sincronización solo si el título visible coincide con la última
revisión. Si el renombrado falla, falta alguna lectura o el título discrepa,
informa de lo que queda pendiente y usa la ficha como referencia. Conserva
ID, proyecto y responsabilidad al cambiar solo el estado.

## Recomendar el destino

- Si la responsabilidad actual cubre la petición, atiéndela aquí. Aclara
  el límite cuando la duda pueda cambiar el destino.
- Si la cubre otro chat vigente, recomienda ese chat por título e ID.
  Un chat Cerrado carece de responsabilidad vigente. Para un chat En espera
  o Pausado, informa de su condición antes de proponer continuarlo. Si hay
  varias coincidencias, indica la ambigüedad para que se pueda elegir.
- Si la consulta está completa y ningún chat vigente la cubre, recomienda
  abrir un chat cuando baste un resumen. Recomienda un fork si el contexto
  del historial es imprescindible. Un fork no aísla los archivos compartidos.
- Si falta acceso al inventario o a una acción nativa, indica la limitación y
  ofrece el título y el ID conocidos o un resumen para el traslado manual.
  Conserva el encargo del chat de origen. Crear o bifurcar exige autorización
  específica. No envíes mensajes de forma rutinaria.
