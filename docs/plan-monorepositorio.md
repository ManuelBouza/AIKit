# Plan del monorepositorio AIKit y Delegating to OpenCode

## Objetivo y estado

Mantener ambos componentes en un repositorio con desarrollo, instalación y
actualización independientes. AIKit puede detectar la integración como capacidad
opcional; Delegating to OpenCode puede operar sin AIKit. Este documento propone
una migración: no afirma que los paquetes, interfaces o pruebas aisladas existan.
Hasta nuevo aviso del usuario, el desarrollo usa herramientas nativas de Codex y
no invoca Delegating to OpenCode.

## Organización propuesta

```text
packages/
  aikit/                    # Preferencias, go y capacidades generales
  delegating-to-opencode/   # Skill, CLI, MCP, estado y sesiones de OpenCode
docs/                       # Acuerdos, migración y evidencias compartidas
notas/                      # Ideas históricas y pendientes
```

Cada paquete tendrá manifiestos, documentación, pruebas y procedimientos de
instalación propios. Mantener una configuración de desarrollo común en la raíz
es una opción, siempre que cada artefacto se construya y pruebe aisladamente.
La ubicación definitiva de código compartido se decidirá tras examinar sus
dependencias; no se copiará automáticamente para crear dos implementaciones.

## Dependencias actuales observadas

El detalle de contratos y la primera unidad propuesta están en el
[inventario de separación](inventario-monorepositorio.md).

- `plugin.json`, `mcp.json` y `scripts/build_plugin.py` producen un único
  complemento `aikit` y un catálogo `aikit-local`; el exportador tiene una lista
  permitida que mezcla skill, MCP, `go`, routing y documentación.
- `pyproject.toml` y `uv.lock` son comunes. Pytest, mypy y las pruebas utilizan
  rutas actuales de `scripts/`, `skills/` y `.aikit/`; mover archivos requiere
  actualizar configuración, imports, fixtures, manifiestos y referencias.
- `scripts/global_instructions.py` sirve a los instaladores de `go` y routing;
  sus pruebas también comprueban convivencia de ambos bloques. El routing mezcla
  preferencias de coordinación con detalles de OpenCode y necesita delimitación.
- La ruta de estado `.aikit/`, los nombres del MCP y las rutas de respaldo
  aparecen en código o pruebas: cambiar una etiqueta puede afectar datos y
  compatibilidad. Inventariar consumidores antes de decidir cualquier cambio.
- Las notas se conservan versionadas en `notas/`. El historial de
  pendientes incluye disponibilidad incompleta, DEF-001 y validaciones en vivo
  pendientes; conservarlo y contrastarlo antes de cambiar estados.

## Etapas propuestas

1. **Inventario y contratos.** Registrar archivos, imports, rutas, identidades,
   estado compartido y responsables. Delimitar el routing, el contrato opcional
   entre componentes y el ciclo de vida de cada paquete. Documentar decisiones
   de nombres, versiones y compatibilidad antes de cambiar código.
2. **Pruebas de referencia.** Registrar resultados existentes y añadir solo las
   pruebas necesarias para exportación aislada, convivencia, configuración
   ajena y recuperación. Usar directorios temporales únicos y aislados.
3. **Separación por unidades.** Reorganizar archivos, rutas e imports en cambios
   pequeños; mantener accesibles los datos y respaldos existentes. Conservar
   notas y evidencias. Ajustar referencias y pruebas junto con cada unidad.
4. **Paquetes independientes.** Crear y validar los artefactos de AIKit y de
   Delegating to OpenCode por separado, con manifiestos y listas explícitas;
   ninguno debe incluir el código o dependencias exclusivas del otro. Decidir
   si un catálogo común es conveniente sin volver obligatoria su instalación.
5. **Compatibilidad e instalación.** Diseñar actualización y retirada desde el
   complemento histórico, detección de duplicados y restauración. Probar en un
   entorno temporal aislado antes de proponer cambios al perfil real de Codex.
6. **Cierre.** Ejecutar pruebas y comprobaciones por componente y las de
   integración; actualizar documentación, inventario y pendientes con evidencia.

## Criterios de aceptación

- Ambos artefactos se construyen desde fuentes limpias y funcionan por separado;
  AIKit sigue utilizable si la integración no está instalada.
- La instalación, actualización y retirada de cada uno preserva configuración
  ajena y no instala, activa o elimina el otro de forma implícita.
- Cuando se habilite la integración, la convivencia no duplica skills o MCP,
  ni intercepta subagentes; la ausencia de OpenCode se informa claramente.
- Las pruebas aisladas cubren exportación, rutas, dependencias y convivencia;
  la suite pertinente, Ruff y mypy pasan con evidencia identificable.
- Se conserva o migra explícitamente el acceso a estado, sesiones y respaldos;
  no se borran notas ni evidencias históricas. Los pendientes siguen abiertos
  hasta que exista evidencia de cierre.

## Decisiones pendientes

Precisar identidades y versiones de los paquetes, formato de distribución,
contrato de descubrimiento opcional, ubicación del código compartido y política
de compatibilidad de rutas y datos. Activar o probar Delegating to OpenCode
requiere que el usuario levante la restricción vigente; cualquier instalación en
el perfil real se abordará por separado de este plan.
