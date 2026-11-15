# Revisión independiente de almacenamiento v1

Veredicto: **requiere concreción antes de implementar**. El documento es coherente
con escritor único y acuse recuperable; resuelve los problemas previos de
generaciones, igualdad de avisos y operaciones históricas. Quedan estos bloqueantes:

1. **Alta — No existe operación definida para mutaciones sin aviso.**
   Preparación exige aviso y generación base/propuesta, pero también deben pasar
   por el mismo mecanismo la activación, creación de PROYECTO/TAREA, nueva asignación,
   nuevo ciclo y relevo. PROYECTO carece de generation y esas mutaciones no tienen
   aviso. Dos implementaciones podrían saltarse el diario o inventar avisos de
   estado. Definir tipos de operación (aviso y administración), campos aplicables,
   generación/versión de cada destino y evidencia de aplicación recuperable de las
   administrativas. Incluir fallos durante creación y relevo en pruebas.

2. **Alta — El formato de intercambio todavía no es implementable sin inventar.**
   Se exige encabezado fijo y JSON estricto que rechaza claves desconocidas, pero
   no se fija el encabezado ni los modelos de operacion.json, lista.json,
   completada.json, history o resultado de consulta. En history se habla de los
   mismos campos de resultado, operación y fecha sin determinar si decision es
   obligatorio; sin él no se puede recuperar el tratamiento previo de un pendiente.
   Completar esos esquemas y reglas de serialización del documento Markdown (no
   solo del aviso) antes de distribuir implementación/lectores independientes.

3. **Media — Alcance de unicidad ante incidentes ambiguo.**
   Un ID de aviso es único en el proyecto, pero un aviso contradictorio con el ID
   de otra tarea debe conservarse como incidente. Aclarar que la unicidad identifica
   al aviso original admitido (receipts), mientras los incidentes pueden contener
   el mismo ID declarado sin convertirse en segundos originales. La búsqueda global
   debe distinguir ambos para no bloquear permanentemente el proyecto después de
   registrar una colisión legítimamente detectada.

No se encontró contradicción con el alcance operativo local ni con las
autorizaciones. La selección de Node y primitivas sigue correctamente señalada
como propuesta; la documentación de la rama 24 debe verificarse antes de programar.
