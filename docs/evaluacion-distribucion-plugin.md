# Distribución de AIKit como complemento

Investigación del coordinador: 29 de octubre de 2026. Propuesta pendiente de
elegir enfoque y aprobar diseño; no es una instalación ni validación del paquete.

## Cobertura existente

- Superpowers aporta diseño, planificación, pruebas y revisión; AIKit conserva
  esos flujos y roles.
- `skill-installer` instala skills desde GitHub, también privado; no empaqueta
  ni configura automáticamente el runtime MCP de AIKit.
- `plugin-management` descubre integraciones y administra conexiones; no genera
  el paquete.
- La documentación menciona `plugin-creator`, pero no aparece en el catálogo de
  skills disponible ni en las rutas locales consultadas. No se da por instalado.
- AIKit ya contiene la skill, el servidor MCP y su núcleo CLI. Se reutilizarán.

## Formato documentado

La documentación oficial recomienda un `plugin.json` portable en la raíz,
`skills/` para workflows y `mcp.json` para servidores. El manifiesto
`.codex-plugin/plugin.json` sigue admitido como compatibilidad. Los catálogos
locales o de repositorio usan `.agents/plugins/marketplace.json` y rutas relativas
a su raíz. La instalación carga una copia en caché, por lo que no puede depender
de la `.venv` del checkout ni de rutas personales.

Fuente: [Empaquetar plugins](https://developers.openai.com/plugins/build/plugins).
Se consultó también el manifiesto instalado de Superpowers, sin modificarlo.

## Alternativas

1. **Complemento nativo privado (recomendado).** Añadir manifiesto y catálogo al
   repositorio, reutilizar `skills/` y preparar un arranque MCP independiente del
   checkout. Codex gestiona descubrimiento e instalación. Requiere comprobar el
   formato y la resolución de rutas con el cliente instalado.
2. **Instalador propio.** Automatizar la copia manual y la edición de configuración.
   Permite controlar el runtime, pero duplica parte de la gestión que ofrece el
   cliente y añade mantenimiento de actualización y retirada.

## Validaciones necesarias

- Descubrimiento e instalación en un entorno temporal; comparar con Superpowers
  habilitado y comprobar ausencia de skills y servidores duplicados.
- Resolver dependencias y runtime desde la copia instalada, sin rutas de Manuel
  ni credenciales en el paquete.
- Definir migración explícita de la skill personal y el MCP registrado actuales:
  conservar respaldo, configuración ajena y posibilidad de restauración.
- Comprobar retirada y actualización. No afirmar compatibilidad solo porque el
  manifiesto sea JSON válido.

No se ha creado el paquete ni cambiado la instalación personal en esta revisión.
