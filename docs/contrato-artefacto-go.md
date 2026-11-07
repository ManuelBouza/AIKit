# Contrato propuesto: artefacto independiente de `go`

Fecha: 2026-11-07. Contrato de la primera unidad de separación. El constructor
produce una salida bajo demanda; no instala el artefacto. La restricción de no utilizar
Delegating to OpenCode continúa vigente.

## Formato y límites

Primera entrega recomendada: un directorio portable `aikit-go/`, construido por
lista permitida en una ruta nueva. Un directorio es suficiente para probar
distribución e instalación sin introducir de momento otro formato o catálogo.
Puede archivarse posteriormente, pero la creación de archivos comprimidos no
forma parte de esta unidad.

```text
aikit-go/
  README.md                      # uso, requisitos, límites y restauración
  config/codex/go.md             # plantilla existente con marcadores AIKIT:GO
  scripts/global_instructions.py # motor de instalación existente
  scripts/install_go.py          # entrada de instalación explícita
```

Solo estos archivos se distribuyen, sin credenciales, perfil, pruebas,
estado local, routing, skill de OpenCode, servidor MCP ni su código. El
instalador y motor usan Python estándar; el artefacto requiere Python 3.10 o
posterior. El constructor se mantiene en el repositorio, fuera de la salida.
No se incluyen manifiestos de complemento ni se afirma que el directorio sea
un plugin instalable desde la interfaz.

## Instalación y contrato

Desde el directorio exportado, el usuario ejecuta explícitamente:

```powershell
python scripts/install_go.py --codex-home C:\ruta\perfil-codex
```

El destino de ejemplo debe sustituirse por el perfil autorizado. El instalador
existente admite `CODEX_HOME` o el perfil predeterminado cuando se omite el
argumento; para pruebas debe suministrarse siempre una ruta temporal explícita.
La plantilla predeterminada se resuelve desde el propio artefacto. La operación
solo pretende insertar o actualizar el bloque delimitado por
`<!-- AIKIT:GO:BEGIN -->` y `<!-- AIKIT:GO:END -->` en el `AGENTS.md` del
perfil elegido; no activa routing ni instala otras capacidades.

El resultado JSON existente declara `changed` o `unchanged` y, cuando procede,
la ruta del respaldo. Conservar instrucciones ajenas y marcadores, detectar
marcadores inválidos y rechazar un `AGENTS.override.md` global no vacío. Una
repetición idéntica debe ser idempotente. El respaldo existente usa
`backups/aikit/go-<uuid>/`; no debe cambiarse en esta unidad. El instalador
actual detecta ciertos cambios concurrentes, pero no garantiza exclusión mutua.

La retirada es manual y selectiva: quitar el bloque delimitado tras revisar el
archivo. La restauración desde un respaldo requiere comparar cambios posteriores;
el artefacto no ofrece aún un desinstalador automático.

La documentación oficial describe las [instrucciones mediante AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
y los [catálogos y manifiestos de complementos](https://developers.openai.com/plugins/build/plugins).
Estas capacidades no prueban que instalar un complemento aplique el bloque de
forma automática. El instalador explícito y la carga efectiva en un chat son
operaciones distintas; la segunda necesita verificación propia.

## Construcción propuesta

- Recibir raíz fuente y destino explícitos; validar los cuatro archivos antes de
  escribir, rechazar enlaces simbólicos y destinos existentes, y no exportar
  archivos ajenos a la lista. Un error de escritura puede dejar una salida
  parcial: informarla sin borrar nada automáticamente.
- Resolver rutas con espacios y comprobar que ninguna fuente sale de la raíz
  permitida. Rechazar enlaces y puntos de reanálisis en las rutas y sus
  antecesores. Esta comprobación no protege contra modificaciones concurrentes
  de rutas entre la validación y la escritura. No modificar el exportador
  histórico ni instalaciones existentes.
- Construir desde la raíz mediante `python scripts/build_go.py --output
  .aikit/aikit-go-exportado`, eligiendo una salida que no exista. Los tests
  permanecen en el repositorio.

## Verificación aislada requerida

1. Exportar a un directorio temporal nuevo con espacios, comparar su contenido
   con la lista permitida y comprobar que no contiene componentes de OpenCode.
2. Ejecutar el instalador exportado con `--codex-home` apuntando a un perfil
   temporal con texto ajeno y routing ficticio; verificar su preservación, el
   bloque `go` y el respaldo byte a byte.
3. Ejecutar una segunda vez: `unchanged`, sin otro respaldo ni cambios al archivo.
4. Probar destino inexistente, marcadores inválidos, override no vacío, salida
   existente y fuentes inválidas; comprobar que los rechazos no sobrescriben
   datos y que los errores de escritura parcial se notifican.
5. Ejecutar las pruebas pertinentes del instalador y constructor, Ruff y mypy
   según su alcance. No iniciar OpenCode ni requerir red, cuentas o un modelo.

Estas pruebas acreditan el artefacto y el instalador, no la carga de `go` en
todos los clientes o chats. Una comprobación posterior de Codex con perfil
temporal tendría que demostrar por separado qué cliente y versión la soportan.

## Evolución a complemento

Un catálogo local y un manifiesto portable son una alternativa futura para la
distribución visible de AIKit. Antes de adoptarlos hay que comprobar en un
perfil temporal que Codex descubre y conserva los archivos auxiliares y
documentar cómo el usuario ejecuta el instalador. No se propone autoinstalación,
hooks, modificación del perfil real ni recrear el catálogo `aikit-local` en esta
unidad. Identidad, versionado y actualización del complemento siguen abiertos.
