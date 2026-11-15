---
title: Distribuir la skill de coordinación en AIKit
type: feature
created: 2026-11-15
status: done
route: oneshot
---

<frozen-after-approval>

## Intent

Incorporar la skill validada y su referencia al complemento independiente
aikit-preferencias, reutilizando build_aikit.py. Verificar bytes, enlace y
descubrimiento desde un paquete instalado en perfil ficticio. Mantener separada
la activación del proyecto y la instalación real. No distribuir el auxiliar.

</frozen-after-approval>

## Implementation Notes

- Alcance aprobado mediante go sobre la propuesta docs/distribucion-skill-coordinacion.md.
- Cambio pequeño sin decisiones materiales ni efectos irreversibles; ruta oneshot.
- Se preservan los cambios previos conocidos de diagnóstico, notas y AGENTS.md;
  la autorización vigente permite continuar sin pedir confirmación por ese estado.
- Reutilización: mapa FILES, catálogo y manifiesto existentes; no se crea instalador.
- Archivos: scripts/build_aikit.py, tests/test_build_aikit.py, manifiesto y README.
- Conservada versión 0.1.0 para la prueba en perfil ficticio; la versión de entrega
  real se resolverá antes de actualizar la instalación habitual.

- Verificación Windows: pytest tests/test_build_aikit.py, 15 correctas;
  Ruff check y format --check correctos; mypy scripts/build_aikit.py correcto.
- Exportación nueva en .aikit/025-paquete-coordinacion; instalación CLI en
  CODEX_HOME ficticio .aikit/025-perfil-paquete. CLI actual 0.169.0-alpha.11.1.
- skills/list desde un directorio temporal externo descubre exactamente una
  aikit-preferencias:coordinacion-chats habilitada, pluginId esperado y ruta en
  caché del perfil ficticio. Ambos archivos son idénticos a las fuentes.
- La primera sonda buscaba incorrectamente el nombre sin prefijo y el proyecto
  inicial estaba dentro del checkout. Se corrigió el filtro al nombre publicado
  y se utilizó un proyecto externo; no se atribuye aislamiento a la primera.
  Evidencias discovery-result.json, skills-list.json y transcript en el perfil.
- Sin inferencia, autenticación copiada ni cambios al perfil real. Descubrimiento
  del paquete no equivale a invocación conversacional de la copia instalada.

## Review Triage Log

- Revisor independiente review_distribution: sin hallazgos accionables, tras
  revisar exportador, prueba, manifiesto y README. Sin pendientes derivados.
