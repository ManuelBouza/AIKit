# Diseño: gratuidad condicionada y contraste público de proveedores

Estado: implementación en curso tras aprobación del usuario (`go`) el 2026-11-01.
No instala, publica ni activa automatización.

## Problema

La implementación anterior llamaba `free_candidate` a cualquier modelo con tarifa
publicada cero. Eso confunde tres cosas distintas:

1. tarifa cero publicada por el catálogo;
2. acceso condicionado mediante franquicia o documentación pública;
3. plan, cuota real y disponibilidad actual verificadas.

La tabla compartida inicial tiene 872 modelos, 71 con tarifa cero y 801 con tarifa
positiva. Cloudflare tiene 28 modelos con tarifa positiva, pero al menos 3 son
compatibles con Workers Free según documentación oficial. La oferta pública no
acredita cuota restante ni plan de la cuenta.

## Decisiones cerradas

- `free_candidate` conserva su contrato legacy: solo tarifa publicada cero.
- Se añade una capa tipada de hechos públicos (`PublicTerm`) independiente de la
  cuota autenticada.
- Un hecho público incluye proveedor, modelo, alcance, condiciones comprobables,
  URL oficial, fecha de comprobación, fecha de publicación cuando exista,
  procedencia/estado de consulta y última validez separada.
- La oferta pública con plan o cuota restante desconocidos no prueba ejecución
  sin coste.
- No se marcan los 28 modelos de Cloudflare como gratuitos; solo los 3 con
  franquicia documentada se registran como `conditional_access`.
- No se transfiere la oferta de Cloudflare a modelos homónimos en Kilo u
  OpenRouter.
- El routing por capacidad y adecuación del esfuerzo no cambia.
- No se ejecutan inferencias de prueba ni sondas de cuota.
- No se activa automatización diaria todavía; los permisos desatendidos siguen
  pendientes.

## Fuentes verificadas

- https://developers.cloudflare.com/changelog/post/2026-07-28-models-require-workers-paid/
  enumera `@cf/zai-org/glm-4.7-flash`, `@cf/google/gemma-4-26b-a4b-it` y
  `@cf/nvidia/nemotron-3-120b-a12b` como disponibles en Workers Free.
- https://developers.cloudflare.com/workers-ai/platform/pricing/
  documenta 10.000 neuronas diarias compartidas, reset a 00:00 UTC, fallo por
  agotamiento en Free, posible cobro de exceso en Paid y modelos que requieren
  pago.

Estos datos documentan condiciones públicas, no el plan ni la cuota restante de
una cuenta.

## Arquitectura

- Nuevo módulo `availability_public_terms.py` con `PublicTerm`, validación
  estricta, parseo, fusión y lectura de artefactos.
- `AvailabilitySnapshot` gana campos aditivos `public_terms` y alias
  compatibles (`public_facts`, `public_access`, `public_access_terms`,
  `conditional_access`), todos normalizados al mismo conjunto.
- La serialización es aditiva y compatible con esquema 1.
- `availability_refresh` conserva los hechos públicos entre refrescos.
- CLI: `availability import` y alias incorporan un artefacto tipado validado.
- MCP: `opencode_availability` expone la tabla local sin consultas externas.
- Doctor muestra recuentos separados: tarifa cero, acceso condicional y hechos
  públicos, sin doble contar.

## Primera incorporación reproducible

Artefacto:
`.aikit/availability-note001/public-terms/cloudflare-workers-ai-public-terms.json`

Estado de prueba:
`.aikit/availability-note001/public-terms/availability-state.json`

Se incorporan exactamente los 3 modelos verificados como `conditional_access`.

## Tarea diaria futura

Codex09Madrid orquestará una revisión diaria que contraste fuentes oficiales de
todos los proveedores conectados con modelos:

- cloudflare-workers-ai
- google
- kilo
- nvidia
- opencode
- opencode-go
- openrouter
- zai

La lista no se hardcodea como límite: el siguiente inventario delimitará los
proveedores conectados. Los 238 proveedores soportados no son conectados. Si un
modelo o proveedor no tiene fuente verificable, el resultado es `unknown` o
`missing` con diagnóstico preciso; no se habilita trabajo basado en documentación
errónea. Se conservarán fuente, fecha de comprobación, errores y última validez.
Se aprovecharán caché, ETag o hash público cuando existan. No se construirá un
crawler general ni scrapers frágiles para los 8 proveedores si la ingesta
validada cubre el caso. No se ejecutará automatización ni se relanzará
investigación por cada inferencia.

## Dominios oficiales verificados para contraste futuro

- cloudflare-workers-ai: developers.cloudflare.com (verificado).
- opencode y opencode-go: opencode.ai / dev.opencode.ai (verificado en documentación del repositorio).
- google: ai.google.dev (verificado, HTTP 200, 2026-11-01T09:11:45Z).
- kilo: kilo.ai (verificado, HTTP 200, 2026-11-01T09:11:45Z).
- nvidia: docs.api.nvidia.com (verificado, HTTP 200, 2026-11-01T09:11:45Z).
- openrouter: openrouter.ai (verificado, HTTP 200, 2026-11-01T09:11:45Z).
- zai: docs.z.ai (verificado, HTTP 200, 2026-11-01T09:11:45Z).

## Límites honestos

- La oferta pública no acredita plan ni cuota restante.
- No se afirma que ningún modelo se haya probado en OpenCode sin evidencia.
- Los tests usan transporte falso y estado temporal.
- La revisión técnica independiente la coordina Codex.