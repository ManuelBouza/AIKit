# Identidad de AIKit

AIKit combina **AI** (inteligencia artificial) y **Kit** (conjunto de
herramientas). Su nombre también evoca *aiki* (合気), como en aikidō: una
inspiración en la unión y armonización de la energía. En AIKit expresa la
colaboración entre la persona, sus preferencias y sus agentes. Es una
asociación creativa, no una traducción literal del nombre.

## Icono aprobado

El [icono original aprobado](../packaging/assets/aikit-icon.png) representa dos
formas curvas que se encuentran alrededor de una luz central: la forma superior
es azul y la inferior naranja. La composición sugiere unión, movimiento y
equilibrio. El fondo es azul muy oscuro, con esquinas redondeadas. El diseño usa
gradientes suaves y un resplandor cálido central.

La imagen PNG incluida es la referencia visual. Es cuadrada, de 1254 × 1254
píxeles; no existe por ahora un original vectorial. Al reducirla, conservar su
proporción y revisar que el símbolo siga siendo reconocible a tamaño pequeño.

## Colores representativos

La imagen contiene degradados, por lo que los valores siguientes son muestras
aproximadas del PNG, no una especificación exhaustiva ni colores planos únicos:

| Uso | Muestra |
| --- | --- |
| Fondo azul oscuro | `#010123` |
| Azul principal | `#0257BC` |
| Azul claro | `#36A3E1` |
| Naranja ámbar | `#EF9828` |
| Naranja profundo | `#DD690E` |
| Luz central cálida | `#FEE2A2` |

## Aplicación

- El constructor copia el PNG a `assets/aikit-icon.png` del complemento.
- El manifiesto lo utiliza como `logo` y `composerIcon`, rutas relativas al
  paquete. Ambas referencias emplean la misma imagen aprobada.
- Mantener intactos la geometría y los colores aprobados; para otros tamaños,
  partir del original y evitar estiramientos o recoloreados accidentales.
- El icono identifica AIKit; Delegating to OpenCode es independiente y no debe
  asumir esta identidad visual.

El 2026-11-08 se actualizó la instalación local; se verificó que el manifiesto y
el PNG instalado corresponden a la fuente y que ambos ámbitos siguen actuales.
Una captura aportada por Manuel confirmó que el icono aparece en la lista de
complementos personales de Codex. Esta observación no comprueba por separado
su presentación en el compositor. Véase la [nota 017](../notas/017-identidad-visual-aikit.md).
