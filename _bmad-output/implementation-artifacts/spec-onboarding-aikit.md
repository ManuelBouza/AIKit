---
title: 'Configuración asistida de AIKit'
type: 'feature'
created: '2026-11-07'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'b799b12e6433ef4e5ea5a72d30253cee29377a36'
context: ['C:/Users/Manuel/.codex/skills/.system/skill-creator/SKILL.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Instalar AIKit no aplica sus instrucciones globales. El usuario acepta iniciar una configuración posterior y quiere probarla en este Codex.

**Approach:** Incluir una skill de configuración invocable por el mecanismo `onboardingSkill` documentado; reutilizar los instaladores existentes para `go` y Context7. Probar con perfiles ficticios en el Codex instalado y distinguir descubrimiento, ejecución de instaladores y recorrido gráfico.

## Boundaries & Constraints

**Always:** Conservar texto y configuración ajenos, marcadores `go` y respaldos; respetar permisos y reglas superiores. La configuración solo se ejecuta cuando se solicite configurar AIKit, no en otras tareas. Informar de cada fallo y de cualquier resultado parcial. La instalación del plugin no implica que se haya completado la configuración.

**Never:** Modificar perfiles reales durante las pruebas, activar o ejecutar OpenCode, instalar Context7 o eliminar datos. No afirmar que el onboarding gráfico se probó si solo se prueban metadatos e instaladores. No alterar archivos ni roles de Superpowers.

## I/O & Edge-Case Matrix

| Estado | Acción | Resultado esperado |
| --- | --- | --- |
| Paquete exportado | Leer manifiesto y skill | Ruta declarada existe y apunta a la skill incluida |
| Perfil ficticio con contenido ajeno | Ejecutar instaladores incluidos en orden | Dos bloques presentes, contenido ajeno preservado; repetición idempotente |
| Segundo instalador falla | Primer paso ya terminó | Informar resultado parcial y no afirmar éxito ni borrar contenido |
| Complemento recién instalado | Consultar metadatos en Codex aislado | Descubrir skill de configuración y, si el protocolo lo expone, referencia de onboarding; no modificar AGENTS.md |

</frozen-after-approval>

## Code Map

- `scripts/build_aikit.py`, `packaging/aikit-plugin.json`, `tests/test_build_aikit.py`: constructor, manifiesto portable y pruebas del paquete ya preparados.
- `scripts/install_go.py`, `scripts/install_context7.py`, `scripts/global_instructions.py`: instaladores idempotentes existentes; respetar sus resultados y no duplicar su lógica.
- `docs/diseno-configuracion-global-aikit.md`: diseño aceptado y límites de la prueba de interfaz.
- `C:/Users/Manuel/.codex/skills/.system/skill-creator/SKILL.md`: requisitos para crear y validar la nueva skill.
- La exploración de skills instaladas no encontró otra skill que configure los bloques de AIKit; `skill-creator` orienta su creación y los instaladores existentes cubren la escritura. La nueva skill solo cubre la coordinación de onboarding no cubierta por ellos.

## Tasks & Acceptance

**Execution:**
- [ ] `packaging/` y `scripts/build_aikit.py` — incorporar una skill de configuración y declararla como `onboardingSkill` sin sustituir metadatos existentes.
- [ ] `tests/` — comprobar contenido exportado, ruta de onboarding, instalación idempotente de ambos bloques y fallo parcial con perfiles ficticios.
- [ ] `docs/complemento-aikit-independiente.md` — documentar el paso de configuración, sus permisos y límites verificados.
- [ ] `_bmad-output/implementation-artifacts/` — registrar verificación de CLI y metadatos y toda limitación de interfaz.

**Acceptance Criteria:**
- Dado un paquete exportado, cuando Codex lo instala en un perfil ficticio, la skill de configuración está presente y sus metadatos se pueden inspeccionar.
- Dado un perfil ficticio con contenido ajeno, al ejecutar los instaladores desde el paquete ambos bloques se instalan y una segunda ejecución no altera el archivo.
- Dado que la configuración se inicia en el cliente, sus instrucciones usan los instaladores incluidos y no presentan como completo un resultado parcial.

## Implementation Notes

## Spec Change Log

## Review Triage Log

- `medium`: la activación desde la configuración podía no considerarse petición;
  la skill ahora la reconoce expresamente.
- `medium`: faltaba definir el tratamiento de JSON inválido o estados desconocidos;
  ahora la skill se detiene si el código, campos o valores no son válidos.
- `medium`: un fallo del segundo paso podía omitir el respaldo del primero; la
  skill exige informar ambos datos y el resultado parcial.
- `false`: el README no supone que el constructor esté en el paquete: indica
  expresamente que pertenece al repositorio fuente.
- `medium`: una ruta Unicode podía fallar al imprimir el respaldo con stdout de
  Windows limitado después de escribir; ambos instaladores emiten JSON ASCII
  con escapes y se probó con codificación ASCII estricta.
- `maybe-false`: sustitución concurrente de una ruta por enlace durante la
  exportación no está demostrada; requeriría una prueba adversarial específica.
- `medium`: los tests ejecutan los instaladores, pero no prueban la decisión de
  la skill en un recorrido real del cliente; ese recorrido queda pendiente.
- `medium`: no se comprobaba el contenido del respaldo de Context7 en el JSON;
  ahora se prueba el contenido exacto y `backup: null` al repetir.

Verificación: 58 pruebas aprobadas, 2 omitidas por permisos para crear junctions
reales; Ruff, mypy y el validador de skill pasaron. Codex CLI/App Server 0.153.4
en perfil ficticio descubre la skill, pero su `plugin/read` no expone el campo de
onboarding. Falta demostrar la ejecución gráfica de configuración.

## Verification

Validar la skill con `quick_validate.py`, ejecutar pruebas relevantes, Ruff y mypy. Usar exclusivamente CODEX_HOME ficticios, sin OpenCode ni perfiles reales. Registrar si la prueba no pudo cubrir el recorrido de interfaz gráfica.
