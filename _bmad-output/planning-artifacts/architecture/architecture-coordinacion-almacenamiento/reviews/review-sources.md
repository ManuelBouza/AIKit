# Revisión de fuentes — 2026-11-14

Veredicto: aceptable como borrador; sin hallazgos bloqueantes de atribución o tecnología.

- El código real de `packages/aikit-installer/src/cli.ts` usa apertura exclusiva
  `wx`, temporal con nombre único, respaldo, comprobación de cambios antes de
  publicar y sustitución diferenciada en Windows. `replace-recovery.ts` devuelve
  diagnóstico conservador y conserva la inspección como acción; no prueba autoría
  ni contenido. La descripción de reutilización del borrador coincide con ello.
- La [fuente oficial Node.js 22.23.4](https://raw.githubusercontent.com/nodejs/node/v22.23.4/doc/api/fs.md)
  se consultó directamente: documenta que la exclusión puede fallar en sistemas
  de archivos de red y que la sincronización depende del sistema y dispositivo.
  El borrador expresa ambos límites y no atribuye durabilidad universal.
- No se fija runtime ni una versión de despliegue; 22.23.4 figura como referencia
  consultada, por lo que no necesita presentarse como versión más reciente.
- Las reglas AD-2 a AD-5 están identificadas como supuestos de diseño, no como
  capacidades ya implementadas o demostradas por el instalador. Los fallos de
  publicación y la recuperación deben verificarse en el nuevo mecanismo.

Límite: esta revisión verifica fuentes y realidad del repositorio; no ejecuta
pruebas del almacenamiento aún inexistente ni sustituye la revisión de coherencia.
