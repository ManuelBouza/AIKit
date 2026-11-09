# 019 — Go aprueba la próxima tarea indicada

- Fecha: 2026-11-09
- Estado inicial: Pendiente de debatir
- Estado actual: Corrección implementada y aplicada

Manuel aclaró que `go` aprueba la tarea concreta indicada en «Próxima Tarea»,
incluido un push expresamente descrito. La versión anterior decía que `go` no
aprobaba push, lo que contradijo esa intención y causó una solicitud redundante.
La autorización no se extiende a acciones que no formen parte de la tarea.
La regla corregida se aplicó el 2026-11-09 a las plantillas y a los archivos
global y del proyecto mediante el instalador; ambos devolvieron `current` y se
crearon respaldos. Las pruebas del instalador terminaron con 30 aprobadas y dos
omitidas por falta de permisos para crear junctions. La carga de instrucciones
actualizada se recibió en este chat. Queda sin probar su interpretación en todos
los casos y la corrección aún no está en un commit.

## Decisión posterior

Manuel decidió proteger acciones sensibles con una palabra concreta que debe
indicarse en «Próxima Tarea». `go` sigue aprobando tareas ordinarias, pero no
sustituye la palabra solicitada para un push u otra acción sensible. Una orden
directa y explícita del usuario también autoriza la acción descrita. Esta
decisión sustituye la interpretación anterior de esta nota.
La regla actualizada se instaló en los ámbitos global y proyecto; ambos
devolvieron `current`. Las pruebas del instalador terminaron con 30 aprobadas y
dos omitidas por falta de permisos para crear junctions.
