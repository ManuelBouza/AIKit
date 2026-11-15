# Distribución de la skill de coordinación — revisión 2026-11-15

## Recomendación

Incorporar la skill validada al complemento independiente existente
`aikit-preferencias`, mediante `scripts/build_aikit.py`. Mantener su instalación
y la activación de coordinación en cada proyecto como operaciones distintas.
Esta revisión concreta el cambio; no modifica el exportador ni instala el paquete.

## Cobertura existente

| Elemento | Cobertura y carencia observadas |
| --- | --- |
| `scripts/build_aikit.py` | Exporta AIKit independiente con lista explícita, rechazo de enlaces, destino nuevo y compilación del instalador. Incluye setup y Director de Ideas; omite los dos archivos de coordinación. |
| `packaging/aikit-plugin.json` | Identidad `aikit-preferencias`, versión 0.1.0, onboarding mediante aikit-setup. La descripción solo menciona go y Context7. |
| `tests/test_build_aikit.py` | Comprueba contenido exacto del paquete, catálogo, instalación en perfiles ficticios y conservación de configuración ajena. La comprobación basada en FILES no detecta por sí sola una skill omitida de esa lista. |
| `packaging/skills/coordinacion-chats/` | SKILL.md y references/avisos.md, autocontenidos y con carga explícita verificada. No incluye el auxiliar de registro. |
| `scripts/build_plugin.py` | Paquete histórico con OpenCode y MCP; no corresponde a esta incorporación. |
| `aikit-setup` | Configura preferencias; no implementa todavía alta de coordinación por proyecto, elección del coordinador ni programación. |

No hace falta otro instalador de skills, un MCP nuevo ni duplicar instrucciones
de roles. La distribución reutiliza el complemento; el auxiliar mantiene su
alcance y empaquetado pendientes. La revisión de fuentes no volvió a ejecutar
exportación o pruebas: todavía no hay cambios funcionales que validar.

La [documentación oficial de skills](https://learn.chatgpt.com/docs/build-skills)
recomienda plugins para distribución reutilizable y permite referencias dentro
del directorio de cada skill. También distingue invocación explícita e implícita:
la instalación no demuestra que se haya activado correctamente en una conversación.

## Alternativas

1. **Recomendada: ampliar aikit-preferencias.** Reutiliza identidad, catálogo y
   actualización existentes, coherente con las capacidades generales de AIKit.
2. Copiar la carpeta a `.agents/skills` de cada proyecto. Sirve para pruebas o
   uso local; introduce copias que hay que actualizar y posibles duplicados.
3. Crear otro complemento exclusivo de coordinación. Permite un ciclo separado,
   pero añade otra instalación y catálogo sin necesidad demostrada actualmente.

## Cambio concreto propuesto

1. Agregar al mapa FILES, conservando bytes y estructura:
   - packaging/skills/coordinacion-chats/SKILL.md →
     aikit-preferencias/skills/coordinacion-chats/SKILL.md.
   - packaging/skills/coordinacion-chats/references/avisos.md →
     aikit-preferencias/skills/coordinacion-chats/references/avisos.md.
2. Actualizar README y descripción del manifiesto para explicar la capacidad y
   sus límites. Mantener la identidad del paquete y el onboarding actual.
3. Añadir una comprobación independiente de FILES que exija ambos archivos,
   igualdad con fuentes y resolución del enlace relativo en la copia exportada.
4. Construir en una ruta nueva y ejecutar la suite del exportador, Ruff y mypy
   pertinentes. Comprobar ausencia de MCP/OpenCode y del auxiliar en la salida.
5. Consultar skills/list con un perfil ficticio y la CLI actual identificada por
   ruta absoluta. Verificar la skill desde el paquete instalado en ese perfil,
   no una copia de las fuentes del checkout. Conservar versiones y evidencia.

Antes de una actualización del perfil real, concretar versión de entrega y
fuente del catálogo de pruebas ya instalado; esa actualización no forma parte
de esta incorporación en fuentes. No eliminar ni duplicar una skill existente.

## Límites de aceptación

La entrega acredita que el paquete distribuye y descubre las instrucciones.
No activa coordinación por proyecto, no registra un coordinador, no distribuye
el auxiliar ni programa archivado. La skill ya requiere coordinación autorizada
y asignación identificable antes de operar. Su disponibilidad general permite
usarla en otros proyectos sin Git, BMAD u OpenCode; las capacidades del cliente
y la vía manual siguen teniendo sus límites documentados.

Flujo BMAD consultado: `bmad-help` y catálogo instalado. La siguiente modificación
funcional encaja en `bmad-build`, acotada al exportador existente y sus pruebas;
no requiere abrir otra especificación de coordinación. La instalación real y
las funciones restantes de la nota 025 conservan sus decisiones pendientes.
