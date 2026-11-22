# Plan 047: responsabilidad única de los chats

Fecha: 2026-11-22. Estado: plan preparado, implementación pendiente de autorización.
Origen: [nota 047](../../notas/047-responsabilidad-unica-chats.md).

## Resultado y alcance

Desde `aikit-setup`, el usuario puede consultar, activar y desactivar por
proyecto la preferencia. Cada chat registra una sola responsabilidad con su
ID nativo. Las solicitudes fuera de alcance se encaminan a un chat existente,
a uno nuevo o a un fork nativo. El chat original conserva su responsabilidad.

Reutilizar el inventario de capacidades de setup y su modalidad guiada. El
`AGENTS.md` local contiene la regla y la referencia al inventario del proyecto.
No modificar el perfil global al activar esta capacidad local. No reintroducir
un coordinador, automatizaciones, mensajería entre chats ni servicios externos.
La recomendación de destino no concede permiso para crear o bifurcar chats.

## Secuencia de entrega

1. **Configuración.** Añadir la entrada de setup, con consulta sin escritura,
   activación explícita, previsualización de destinos y desactivación que
   conserva el inventario. Reutilizar las guardias de escritura y preservación
   de instrucciones disponibles. Resolver la raíz del proyecto sin exigir Git.
2. **Inventario.** Mantener una sola fuente por proyecto. Cada entrada guarda
   ID nativo completo, título, responsabilidad, estado y fecha de actualización.
   En un fork registra el ID de origen. En espera o pausa conserva el motivo y
   cómo continuar. Si falta un ID verificable, dejar el alta pendiente. Definir
   ubicación, formato y control de escrituras concurrentes en Build antes de
   modificar producto. No mantener copias alternativas desde entornos aislados.
3. **Nombre y estado.** Aplicar `[Estado] Proyecto · Responsabilidad breve`.
   Usar Disponible, En curso, En espera, Pausado o Cerrado. Actualizar la entrada
   por ID y reflejar el estado en el título mediante la acción nativa, cuando
   esté disponible. Si falla el renombrado, informar de la discrepancia y
   conservar el inventario como referencia.
4. **Destino.** Atender en el chat actual si la solicitud encaja. Si otro
   chat vigente ya cubre el tema, recomendarlo. Si no lo cubre ninguno, recomendar
   un chat nuevo cuando baste un resumen o un fork cuando sea imprescindible
   conservar el historial. Ante coincidencias ambiguas o acceso insuficiente,
   indicarlo y ofrecer traslado manual. El fork no aísla por sí solo los archivos.
5. **Verificación y entrega.** Revisar el cambio, ejecutar los controles del
   paquete y documentar las pruebas en proyecto y perfil ficticios. Preparar
   la incorporación a AIKit sin instalar en el perfil habitual ni hacer push.

## Criterios de aceptación

- Setup ofrece la opción, una consulta no escribe, repetir el alta no duplica
  el bloque y desactivar conserva tanto el inventario como las instrucciones ajenas.
- Dos chats autorizados consultan el mismo inventario y pueden distinguir
  sus responsabilidades aunque compartan título. El cambio de nombre conserva
  el ID y un fork tiene su propio ID y referencia de origen.
- Los cinco estados son distinguibles. Una transición actualiza el inventario y
  el nombre visible si la herramienta está disponible. Dos cambios simultáneos
  se conservan o uno se rechaza de forma recuperable, sin sobrescritura silenciosa.
- Se demuestran los cuatro destinos, incluyendo continuar en el chat actual,
  y la respuesta cuando falte acceso al inventario, al ID o a una acción nativa.
- El exportador incluye la entrada y sus referencias. Se documenta qué se pudo
  verificar de la interfaz y qué requiere una prueba adicional de cliente.

## Ruta BMAD

El catálogo instalado, consultado con `bmad-help`, permite tratarlo como una
entrega acotada. Usar **[BD] Build** (`bmad-build`) con este plan y la nota como
entrada. La fase de planificación de Build concreta las decisiones técnicas que
sigan abiertas. La entrega incluye revisión y pruebas antes de proponerse para
integración. Este plan no inicia la implementación.
