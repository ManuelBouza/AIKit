# Migración manual inicial del seguimiento local

Fecha: 2026-11-17. Responsable: Coordinador vigente en PROYECTO.md.
Alcance: 043, encargos 028/040 y dependencia BMAD; sin migración retrospectiva.

## Resultado y fuentes

Se inventariaron los encargos vigentes y sus orígenes humanos antes de escribir;
el registro de tickets no existía. Simulación y preestado recuperable conservados
en `.aikit/043-migracion/`, excluidos de la distribución del complemento.

- IMP-0001 conserva el encargo043 y su autorización de implementación.
- IMP-0002 conserva el encargo028 y su espera de decisión visual.
- IMP-0003 conserva el encargo040 y su bloqueo por entorno.
- IMP-0004 registra preparación BMAD pendiente, sin autorizar ejecutarla.

Los documentos y avisos previos se conservan; INDICE.md y ENCARGOS.md enlazan
la fuente única de estado. No se cambió ningún worktree ni se preparó BMAD.
Los originales copiados conservan sus bytes. La vista se generó con 43 ideas
y cuatro tareas; el inventario posterior encontró cero altas necesarias.

## Procedimiento reproducible de conciliación y repetición

Es una migración manual del Coordinador; no existe un comando que migre o
reescriba tickets automáticamente. El lector y generador no mutan sus fuentes.

1. Consultar el contrato y confirmar Coordinador, raíz canónica y autorización.
   Leer los cuatro tickets y cotejar origen/alcance, no solo título o idea.
   Contrastar el estado humano vigente en los chats cuando esté disponible.
2. Anotar las altas que faltan. Si los cuatro encargos ya están representados,
   el plan de altas es vacío. No volver a asignar números ni reemplazar contenido
   con el snapshot del diseño. Una discrepancia de origen exige conciliación.
3. Conservar copia y huellas antes de cualquier cambio necesario. Incorporar
   solo ausentes o actualizaciones autorizadas, sin borrar originales. No tocar
   ramas ni recursos de las tareas. Si hay escrituras parciales, registrar cuáles.
4. Validar y generar con el comando de docs/tablero-notas.md. Comprobar cuatro
   entregas, relaciones y estados vigentes; si falla, conservar última vista válida.
5. Repetir inventario y generación: cero altas si siguen presentes los mismos
   encargos; comparar huellas de tickets antes/después para comprobar que la
   generación no los modifica. Conservar cualquier decisión posterior al snapshot.

Para comprobar preservación de decisiones posteriores sin operar en los chats,
usar una copia ficticia de las fuentes: cambiar fase/espera con origen simulado,
repetir los pasos 1–5 y confirmar que se conserva el cambio. No ejecutar esta
simulación sobre los registros reales ni inventar autorizaciones humanas.
El cierre no atribuye a la consulta de solo lectura una migración automática
ni garantías transaccionales multiarchivo.
