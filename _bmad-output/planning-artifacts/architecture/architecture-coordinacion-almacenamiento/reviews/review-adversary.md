# Revisión adversaria del almacenamiento

Veredicto: requiere aclaraciones antes de implementar; borrador con supuestos.

## Alta — Ciclo de vida de operaciones preparadas

AD-3 conserva una operación preparada y AD-4 examina las operaciones al reanudar,
pero no fija cómo distinguir pendientes de completadas. Implementación A conserva
todas como preparadas; implementación B marca o retira las completadas. Ambas
cumplen las reglas. Tras aplicar sucesivamente revisiones 2 y 3 y reiniciar, A
encuentra la operación de revisión 2 cuyo documento base y propuesto no coinciden
con el canónico de revisión 3 y bloquea por conflicto; B continúa. Fijar estado
terminal recuperable y condiciones para reconocer operaciones ya completadas sin
reinterpretar operaciones históricas como pendientes. Nunca retirar evidencia
antes de confirmar que el canónico contiene el resultado y su identidad.

## Alta — Orden de publicación de la preparación

AD-3 exige conservar una operación preparada, pero no exige que esté completa y
validada antes de tocar el canónico. A puede preparar fragmentos, publicar y acabar
metadatos después; B prepara y valida íntegramente primero. Un fallo intermedio en
A deja una preparación insuficiente para comparar base/propuesta, por lo que la
recuperación de AD-4 no está disponible aunque el sistema cumpla su lectura literal.
Exigir fase de preparación completa, validada y reconocible antes de publicar;
preparaciones parciales se conservan pero no se ejecutan ni se interpretan como
evidencia positiva. La resistencia a apagones sigue pendiente de pruebas.

## Media — Historial de recepciones frente a ID de actualización

AD-2 define acuses por ID; AD-4 requiere conservar un aviso contradictorio de igual
ID. Una implementación sobrescribe el acuse para expresar conflicto y otra añade
un incidente preservando el acuse aplicado. Debe fijarse que el acuse aplicado y el
contenido original permanecen recuperables y los intentos contradictorios se guardan
como incidentes independientes, sin usar el ID de actualización como clave única
de todos los contenidos recibidos.
