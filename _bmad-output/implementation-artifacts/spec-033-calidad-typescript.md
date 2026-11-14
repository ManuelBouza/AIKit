---
title: Controles de calidad equivalentes para TypeScript y Python
type: chore
created: 2026-11-14
status: done
route: oneshot
review_loop_iteration: 0
context: [docs/calidad-python-typescript.md]
---

<frozen-after-approval>

## Intent

Aplicar ESLint con análisis de tipos, Prettier, comprobación tsc y pruebas Node al
paquete TypeScript existente, e integrarlos con los controles Python en verificar.ps1.
Usar herramientas deterministas para detectar errores, reservando inferencia para
interpretar y corregir. Una preparación o comprobación fallida debe impedir éxito.
No modificar el comportamiento del instalador, migrar lenguajes ni implementar
el auxiliar de coordinación. Preservar modificaciones previas del usuario.

</frozen-after-approval>

## Implementation Notes

- Alcance acotado: package.json/lock, configuración lint/formato, correcciones
  diagnosticadas en src/test, verificar.ps1 y documentación/nota 033.
- No hay decisiones materiales ni operaciones irreversibles pendientes.
- Árbol previamente modificado por este trabajo conversacional; se preserva.
- npm requiere acceso de red fuera del sandbox; versiones consultadas con permiso
  acotado. ESLint 10.15.0 exige Node >=24 o ramas 20/22 con mínimos específicos;
  se documentará requisito de desarrollo separado del runtime >=20 del instalador.
- Pruebas añadidas: herramientas ausentes, preparación fallida, fallo de controles,
  directorio correcto, comando descubierto pero no ejecutable. Sondas reales de
  tipos/lint/formato/pruebas negativas detectan fallos sin modificar fuentes.
- El primer conjunto completo detectó dos fallos del doble Node.cmd de las nuevas
  pruebas (código JavaScript como argumento); corregidos y 13 casos pasan.
- Una prueba previa de ámbito usaba TEMP dentro del checkout y descubría el Git
  padre; se limita GIT_CEILING_DIRECTORIES. El bloque GO que esa prueba actualizó
  incidentalmente se restauró a su contenido previo; solo permanece el nuevo
  apartado de calidad y las modificaciones anteriores del usuario.

## Review Triage Log

- medium, patch: npm ci omitía dev con NODE_ENV=production; se usa --include=dev.
- low, patch: uv run podía resincronizar; controles usan --no-sync tras sync exitoso.
- medium, patch: Push-Location fuera del try; ahora se captura y solo se hace pop
  después de cambiar ubicación correctamente.
- medium, patch: cualquier Node pasaba versión; se comprueban mínimos de ESLint
  por separado del requisito de ejecución del producto.
- low, reject: probar simultáneamente PowerShell 5.1 y 7 ampliaría la matriz;
  esta actualización declara validación real con PowerShell 7 sin atribuirla a 5.1.
- low, patch parcial: se cubren todos los fallos TypeScript y un control Python;
  los demás Python usan el mismo ejecutor, con secuencia exitosa completa comprobada.
- medium, patch: prueba exitosa comprobaba solo dos pasos; ahora exige todos los controles.
- medium, patch: se registra cwd en los dobles y se comprueba raíz/paquete por comando.
- low, patch: añadido programa descubierto pero no ejecutable, con resumen y fallo.
- low, patch: evidencia y resultados concretos incorporados a documentación.

## Verification

- Verificación conjunta final: código 0; 946 pruebas Python, Ruff lint/formato,
  mypy en 72 archivos, tsc, ESLint, Prettier y 53 pruebas Node, todas correctas.
- Sondas negativas reales de tipos, lint, formato y pruebas: códigos no cero
  esperados, fuentes sin reescritura; retiradas las sondas.
- Revisión independiente: diez observaciones triadas arriba; correcciones simples
  aplicadas, sin duplicar con inferencia los controles ya ejecutados.
- npm audit online: siete avisos moderados de desarrollo por minimatch transitivo;
  pendiente resolución compatible, sin force ni override inseguro.
