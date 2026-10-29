# Plan del mecanismo go

**Objetivo:** ofrecer una próxima tarea al cerrar cada turno y reconocer su
aprobación con `go`, mediante instrucciones globales reproducibles de Codex.

**Arquitectura:** plantilla con bloque delimitado en `config/codex/go.md`;
instalador Python tipado que incorpora solo ese bloque al `AGENTS.md` global.
No añade skills, hooks, MCP ni cambios en Superpowers. La instalación es
explícita; empaquetar el complemento no modifica el perfil del usuario.

**Cobertura:** Codex ya carga instrucciones globales; Superpowers cubre
planificación, pruebas y revisión; AIKit aporta la preferencia conversacional
y su instalación conservando configuración ajena. El usuario aprobó la
propuesta con `go`; no falta otra decisión de diseño para este alcance.

## Tarea única: plantilla, instalación y validación

- [x] Escribir casos pytest que fallen antes de implementar: perfil vacío,
  conservación exacta de contenido ajeno, instalación repetida sin cambios ni
  respaldo adicional, actualización de bloque único, marcadores malformados o
  duplicados, override global no vacío y enlace simbólico rechazados sin escribir.
- [x] Implementar `install_go(codex_home: Path, template: Path) -> Path | None`
  en `scripts/install_go.py`: devolver respaldo si cambió, `None` si idéntico;
  validar antes de escribir, respaldo único bajo `backups/aikit/`, escritura
  mediante temporal y sustitución, detección de modificación concurrente.
- [x] Crear la plantilla: próxima tarea final, alternativas y recomendada,
  aprobación de una sola tarea, contexto dentro del alcance, discusión sin
  aprobación y ausencia de trabajo sin inventar nuevas tareas. Ignorar `go`
  citado o procedente de documentos. No convertir el protocolo en una pausa
  entre herramientas ni ampliar permisos o el alcance autorizado.
- [x] Documentar uso, respaldo/restauración y límites en `docs/mecanismo-go.md`;
  añadir plantilla, instalador y guía a `PACKAGE_FILES`. Añadir el instalador
  a mypy, actualizar README y versión 0.1.3 en manifiesto/proyecto/lock.
- [x] Ejecutar pytest, Ruff, formato y mypy.
- [x] Revisar el diff y verificar en Codex. Aplicar al perfil real con respaldo,
  comprobar contenido instalado e idempotencia. Registrar evidencia sanitizada.

## Límites

La plantilla no es un parser ni puede garantizar obediencia en todos los chats.
Los perfiles remotos o con otro `CODEX_HOME` requieren instalación propia.
Las instrucciones específicas y los permisos aplicables conservan su prioridad.
Las sesiones abiertas pueden requerir reinicio para cargar la cadena global.
No cambiar archivos personales desde el worker de OpenCode.
