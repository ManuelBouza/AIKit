# Revisión de fuentes v1 — 2026-11-14

Veredicto: sin bloqueantes técnicos de fuentes; una corrección documental menor.

## Hallazgo

- Bajo: `almacenamiento-v1.md` propone Node 24 pero su sección de fuentes sigue
  enlazando fs v22 y aplaza verificar 24. Ya puede citarse la
  [API oficial v24](https://nodejs.org/docs/latest-v24.x/api/fs.html), consultada
  en esta revisión: confirma apertura exclusiva, límites en red y sincronización
  dependiente del sistema/dispositivo. El spine puede conservar la referencia
  histórica de v22 si queda clara su función histórica.

## Comprobaciones

- `node --version` devolvió `v24.22.1`; la referencia local es correcta y no afirma
  ser el último parche. El [calendario oficial](https://nodejs.org/en/about/previous-releases)
  mantiene 24 como rama LTS.
- [ReplaceFileW oficial](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew)
  confirma respaldo, estados parciales de error 1175–1177 y que WRITE_THROUGH no
  está soportado. También exige mismo volumen para original, reemplazo y respaldo;
  las rutas propuestas bajo una sola raíz, sin junctions ni enlaces, lo permiten.
- El adaptador existente llama File.Replace con ignoreMetadataErrors=false,
  conserva rutas ante incertidumbre y no restaura automáticamente. La propuesta
  añade verificación ACL explícita; no la atribuye al adaptador existente.
- El requisito Node de este auxiliar está diferenciado del instalador y de la vía
  manual. No hay una dependencia nueva de producción ni ejecutable privado de Codex.

No se ejecutaron primitivas destructivas ni pruebas de recuperación; este informe
solo verifica la adecuación de las fuentes y las afirmaciones de tecnología.
