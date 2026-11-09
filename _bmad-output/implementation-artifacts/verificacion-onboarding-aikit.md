# Verificación de configuración asistida de AIKit

Fecha: 2026-11-07. Windows, Codex CLI instalado; perfiles y catálogo ficticios bajo `.aikit/uv-temp` del worktree. No se ejecutó OpenCode ni se modificó un perfil real.

- Exportación y `codex plugin marketplace add`, `codex plugin add` y `codex plugin list`: complemento 0.1.0 instalado y habilitado; `skills/aikit-setup/SKILL.md` presente en la caché instalada; `AGENTS.md` no existía tras instalar. El manifiesto exportado declara la ruta de onboarding. La CLI no mostró metadatos de descubrimiento de skill ni la referencia de onboarding.
- Python 3.14.9 del entorno del checkout principal: `pytest tests/test_build_aikit.py`, 10 pruebas aprobadas; `ruff check .`, `ruff format --check .` y `mypy`, correctos. Las pruebas verifican ambos bloques, contenido ajeno, repetición y fallo del segundo instalador conservando el primero.
- `quick_validate.py packaging/skills/aikit-setup` con Python del sistema y PyYAML: skill válida. El entorno del checkout principal carece de PyYAML; se usó el Python del sistema para este validador.
- `uv run` en el worktree no pudo obtener dependencias debido a fallo DNS de la red restringida; las comprobaciones anteriores usaron las dependencias ya instaladas del checkout principal.

No se probó el descubrimiento por el protocolo del cliente ni el recorrido gráfico de configuración. La presencia del archivo y la instalación CLI no demuestran que la interfaz lo invoque. No se instalaron preferencias en ningún perfil real ni se instaló Context7.

## Consulta de metadatos posterior

En Codex CLI 0.153.4, con un perfil y catálogo ficticios nuevos, `skills/list`
encontró la skill habilitada y `plugin/read` mostró el complemento y la skill.
La respuesta de `plugin/read` no incluyó un campo `onboardingSkill`; tampoco
aparece en el esquema de respuesta generado por esa versión. `AGENTS.md`
ficticio permaneció idéntico. No se acredita con ello que el botón de
configuración invoque la skill: sigue pendiente el recorrido gráfico aislado.

## Revisión e integración

La revisión independiente corrigió validación de resultados, comunicación de
respaldos y salida JSON compatible con rutas Unicode en stdout limitado. Tras
integrar en el checkout principal se ejecutaron 69 pruebas: aprobadas; dos pruebas
de junction real se omitieron por permisos. Ruff y mypy pasaron. Se repitió la
consulta de metadatos en Codex CLI/App Server 0.153.4 con perfil ficticio: skill
descubierta, sin campo de onboarding en `plugin/read`, y `AGENTS.md` sin cambios.
La comprobación de que la interfaz invoca la configuración sigue pendiente.

## Vista del complemento en este Codex

El usuario autorizó registrar el catálogo local e instalar el complemento de
prueba en su perfil de Codex, sin ejecutar configuración ni modificar el
`AGENTS.md` global. La captura aportada muestra el complemento instalado,
la habilidad «Aikit Setup» y los botones «Gestionar» y «Probar ahora». No muestra
un botón llamado «Configurar». La imagen confirma la presentación de la habilidad,
pero no demuestra que «Probar ahora» inicie el onboarding ni que los bloques se
escriban. La configuración global sigue sin ejecutarse como parte de esta prueba.
