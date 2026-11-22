---
title: 'Integrar las capacidades de AIKit en setup'
type: 'feature'
created: '2026-11-18'
status: 'done'
route: 'oneshot'
baseline_commit: 'ac71b49456abec4f438559d7fcab6d461125d415'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="alcance acordado en la nota 039 y el ticket IMP-0009">

## Intent

**Problema.** Las capacidades distribuidas podían quedar sin una vía de descubrimiento o configuración en setup.

**Resultado.** Setup presenta cada capacidad propia y su tratamiento. El exportador rechaza las omisiones y las referencias inválidas antes de generar un paquete.

</frozen-after-approval>

## Implementation Notes

- El exportador activo es `scripts/build_aikit.py`. El histórico de OpenCode queda fuera del alcance.
- El inventario vive en las referencias distribuidas de setup. La comprobación compara rutas de skills, plantillas y flujos con las fuentes y los archivos que se van a exportar.
- Setup reutiliza el instalador Node y los flujos guiados. Las skills que solo se descubren se presentan según la disponibilidad del cliente.
- La revisión y la integración se coordinan a partir de una copia local aislada de la revisión indicada. La implementación se autorizó en IMP-0009. Quedan fuera el perfil habitual, la publicación y el push.
- El manifiesto del instalador define los ids de las opciones y sus valores para una invocación sin selección. El exportador comprueba que coincidan con las plantillas, copias de configuración e inventario.

## Revisión independiente

El dictamen final fue aceptado. Se corrigieron el acceso al campo de onboarding,
las preguntas fuera del alcance elegido, la cobertura de opciones y plantillas,
los destinos Markdown rotos y la descripción de Context7 en la documentación.

En el paquete exportado, el revisor explicó el Director de Ideas, encontró el
tracker canónico ficticio y comprobó si había evidencia de coordinación.
Desde un subdirectorio aplicó solo visualización tras la vista previa. El
`AGENTS.md` de la raíz coincidió con la vista previa, los respaldos coincidieron
con el original y se conservaron el perfil ficticio y las fuentes del tracker.
La prueba guiada deja pendiente el onboarding de la interfaz, el descubrimiento
por el cliente y el reconocimiento desde otra sesión.

## Verificación

- Windows, Python 3.14.9 y Node 24.22.1. Se usaron perfiles y proyectos
  ficticios y un catálogo generado en la copia local.
- `pytest tests/test_build_aikit.py` aprobó 30 casos. El paquete válido se
  exportó, las omisiones y referencias inválidas se rechazaron antes de escribir
  la salida y funcionaron la vista previa, aplicación y retirada selectiva.
- `npm run verify` aprobó tipos, lint y formato. Pasaron 83 pruebas de Node;
  seis se omitieron por las condiciones de plataforma o permisos del sandbox.
- Ruff, mypy sobre los archivos Python cambiados y el validador de la skill
  pasaron. La suite Python general se interrumpió durante pruebas de
  disponibilidad ajenas a esta entrega. Mypy general informó que falta
  Playwright para la prueba del tablero.
