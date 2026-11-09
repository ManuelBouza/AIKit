# Validación del complemento AIKit independiente

Fecha: 2026-11-07. Windows; Python 3.14.9, pytest 9.2.0 y codex-cli
0.153.4. Se utilizaron exclusivamente perfiles ficticios bajo `.aikit/` o
perfiles temporales de pytest. No se invocó OpenCode ni se modificó un perfil
real.

- Esperado: exportar dos preferencias sin MCP, instalar explícitamente en perfiles
  aislados, preservar texto y go, rechazar conflictos y mantener idempotencia.
  Observado: `pytest tests/test_build_aikit.py tests/test_build_go.py
  tests/test_install_go.py tests/test_plugin_export.py`: 50 aprobadas, 2 omitidas;
  las pruebas de junction real se omitieron por acceso denegado. Las simulaciones
  de puntos de reanálisis sí pasaron. El exportador histórico pasó sus pruebas.
- Esperado: formato, lint y tipos correctos. Observado: `ruff check .`,
  `ruff format --check .`, `mypy` y `mypy scripts/build_aikit.py
  scripts/install_context7.py` correctos, usando el entorno virtual existente de
  la raíz. La creación del entorno propio con `uv` no pudo descargar paquetes por
  DNS restringido.
- Esperado: instalar el catálogo y el paquete en CLI aislada sin escribir
  automáticamente AGENTS.md. Observado: `codex plugin marketplace add` con ruta
  absoluta y `codex plugin add aikit-preferencias@aikit-preferencias-local`
  terminaron correctamente en CODEX_HOME ficticio; el `AGENTS.md` con contenido
  ficticio permaneció igual. Un intento previo con ruta relativa se interpretó
  como repositorio remoto y falló por DNS, sin instalación.

La instalación global automática, coexistencia, actualización, retirada selectiva,
desinstalación y migración no están verificadas. Esta prueba de CLI no demuestra
compatibilidad con otros clientes ni con su interfaz gráfica.

## Integración y revisión posterior

Tras la revisión independiente se protegió el motor común contra puntos de
reanálisis y se ampliaron las pruebas de catálogo y enlaces. En el checkout
principal, con Python 3.14.9, las pruebas conjuntas de AIKit, go, el constructor
histórico y Delegating to OpenCode dieron 66 aprobadas y 2 omitidas por permisos
para crear junctions reales; las simulaciones pasaron. Ruff y mypy pasaron. No se
invocó OpenCode ni se modificaron perfiles reales. Instalación automática,
retirada y migración continúan pendientes.
