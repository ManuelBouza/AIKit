# AIKit 0.1.7 — actualización privada instalada

Fecha: 2026-11-18. Encargo: [IMP-0008](../coordinacion/tareas/IMP-0008/TAREA.md).
La candidata distribuye el Director de Ideas actualizado, aceptado en el código
fuente; el tablero sigue siendo una herramienta del repositorio y no se incorpora
al plugin. La actualización se aplicó al perfil habitual y fue aceptada por
revisión independiente posterior: configuración e instrucciones conservadas,
respaldo verificado y tres skills habilitadas descubiertas. La fuente activa es
`.aikit/040-actualizacion-0.1.7`; conservarla junto al respaldo y la fuente0.1.6.
El descubrimiento no acredita que todos los chats abiertos hayan recargado.

La exportación contiene 29 archivos autorizados, de los cuales 28 pertenecen al
plugin. Sus contenidos coinciden con las fuentes, salvo el nombre del catálogo,
que conserva la identidad privada `aikit-setup-prueba-20261108`. El selector es
`aikit-preferencias@aikit-setup-prueba-20261108`. La fuente anterior 0.1.6 se
conserva en `.aikit/044-actualizacion-0.1.6`; la candidata se encuentra en
`.aikit/040-actualizacion-0.1.7` y debe conservarse mientras sea fuente activa.

Se consultaron la [documentación de plugins](https://developers.openai.com/plugins/build/plugins)
y los [comandos de desarrollo](https://learn.chatgpt.com/docs/developer-commands?surface=cli).
La prueba utiliza la CLI instalada `codex-cli 0.169.0-alpha.11.1` y perfiles
ficticios con `CODEX_HOME` independiente, sin setup ni inferencia.

## Comprobaciones

- Instalación nueva 0.1.7 y migración 0.1.6 → 0.1.7 completadas.
- Descubrimiento de tres skills habilitadas y archivos instalados idénticos a la
  candidata, mediante `skills/list` con recarga.
- Recuperación 0.1.6 mediante el gestor, con descubrimiento y contenido comprobados.
- Ensayo del helper completo en perfil ficticio: ACL privada, respaldo de
  configuración y ZIP de caché comprobado, conservación de instrucciones y fuente
  anterior, comparación de configuración y descubrimiento satisfactorios.
- Los hashes observados del perfil habitual, instrucciones y fuente anterior
  permanecieron iguales tras las pruebas.

El primer ensayo del helper se detuvo antes de copiar datos: dentro del sandbox,
`icacls` informó éxito pero la ACL seguía heredada. La guardia detectó el fallo;
se conservó la evidencia y el ensayo con un destino nuevo pasó fuera del sandbox.
La variante exitosa difiere del helper habitual únicamente en `PROFILE` y `E`.

## Aplicación y recuperación

El helper preparado es `.aikit/040-aplicar-paquete017.py`, SHA-256
`f19e176c5505813ec13a7cefa01d990847b53cee511de6df6d5dec05e1fa1fa3`.
La variante ensayada es `.aikit/040-prueba-final017-escalada.py`, SHA-256
`ec64db48545d3bd93ea045ffa233e850a790b75fd3406f4bfebca61fb6de4455`.
Las evidencias privadas están en `.aikit/040-preparacion-0.1.7/` y
`.aikit/040-prueba-final-0.1.7-escalada/`; no deben publicarse.

El helper exige una carpeta exclusiva, protege y verifica la ACL antes del
respaldo, comprueba la candidata y la versión de la CLI, y conserva la fuente
anterior. Solo admite el cambio del origen del catálogo en la configuración.
Si falla conserva la fase y se detiene; la operación no es atómica ni reintenta
automáticamente. La recuperación ensayada registra de nuevo la fuente 0.1.6 e
instala el mismo selector. Antes de restaurar una configuración, se deben
conciliar eventuales cambios concurrentes.

La instalación y el descubrimiento no demuestran que las conversaciones abiertas
hayan cargado las nuevas instrucciones. Para los antecedentes y guardias del
procedimiento, véase [la actualización 0.1.6](actualizacion-aikit-0.1.6.md).
