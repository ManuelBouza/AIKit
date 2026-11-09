# Prueba de setup con gestor ficticio

Fecha: 2026-11-09. El objetivo fue observar las decisiones de la skill de setup
ante estados de Context7 sin modificar instalaciones reales.

## Entorno y límites

Dos agentes independientes leyeron la skill de fuentes y usaron
`tests/fixtures/fake_plugin_manager.py`, que modifica únicamente el JSON de
estado indicado y no se conecta a Codex ni a Internet. La aplicación de
`AGENTS.md` se consideró realizada; no se volvió a probar en estos escenarios.
El simulador identifica Context7 por nombre y simplifica los estados, por lo
que no valida la identidad, autenticación ni la instalación en el catálogo real.

## Resultados observados

- Ausente: el agente ejecutó `search`, explicó la utilidad y pidió aprobación;
  no llamó a `install` antes de recibirla.
- Tras la aprobación ficticia: llamó a `install`, volvió a ejecutar `search` y
  comunicó que el gestor ficticio lo mostraba instalado y habilitado globalmente.
- Presente y habilitado globalmente: el otro agente ejecutó `search`, informó del
  estado y no llamó a `install`.
- Consulta fallida: el gestor devolvió código 1; el agente informó que el estado
  era desconocido y no llamó a `install`. El registro contiene solo `search`.

Las llamadas quedaron registradas en JSON bajo `.aikit/eval-setup/`, un directorio
local ignorado por Git. La primera consulta del caso ausente fue un preflight del
gestor; la siguiente la realizó el agente. No se modificaron complementos reales.
No se probó que el cliente real ofrezca una operación de instalación para un
complemento remoto ausente.
