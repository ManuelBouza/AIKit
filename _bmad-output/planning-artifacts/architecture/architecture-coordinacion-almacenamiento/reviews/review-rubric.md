# Revisión independiente del borrador

Veredicto: requiere ajustes antes de usarlo como contrato de implementación.
Se revisaron ARCHITECTURE-SPINE.md y el protocolo de spec-coordinacion-chats.

1. **Alta — Ciclo de vida de operaciones preparadas ambiguo (AD-3/AD-4).**
   No se distingue una operación pendiente de una ya completada y conservada como
   evidencia. Tras aplicar A y luego B, el documento vigente no coincide con base
   ni propuesta de A: una recuperación que inspeccione todas las operaciones
   preparadas se detendrá ante trabajo legítimo. Definir cómo se reconoce una
   operación resuelta y cómo se comprueba su resultado histórico sin exigir que
   siga siendo la versión vigente; probar dos operaciones consecutivas y reinicio.

2. **Alta — Identidad de operaciones e igualdad sin fijar (AD-2/AD-4, Diferido).**
   Se difieren esquema, codificación e IDs aunque la recuperación exige comparar
   documentos íntegros y asociar acuses. Dos implementaciones conformes pueden
   discrepar sobre revisión de documento frente a revisión de tarea/ciclo, alcance
   del ID y equivalencia de contenido. Antes de construir unidades independientes,
   fijar identificador de versión del documento distinto de revisión de tarea,
   alcance de ID y comparación exacta o canonicalización común; el formato completo
   puede seguir diferido si existe una única unidad responsable del almacenamiento.

3. **Media — Lectura segura de acuses no tiene contrato propio.**
   AD-3 exige releer para confirmar, pero la consulta puede observar un archivo
   mientras otra operación publica o una sustitución falla. Definir que una lectura
   solo devuelve acuse positivo de un documento completo validado y una versión
   identificada; si el archivo falta, es parcial o inválido, devolver incertidumbre
   conservando originales. Incluir prueba de lectura durante publicación fallida.

Las decisiones de escritor único, alternativa manual, conservación ante conflicto
y limitación inicial a almacenamiento local respetan el contrato aceptado. El
borrador no promete durabilidad universal ni fija un runtime sin justificación.
