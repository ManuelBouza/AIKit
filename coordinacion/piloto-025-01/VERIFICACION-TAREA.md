# Verificación de entrega, versión 1

- Entorno: Windows, PowerShell; raíz C:/Manuel/Projects/AIKit. Fecha: 2026-11-16.
- Archivo: entrega/guia-uso.md. SHA256: a53b345620e5882884548f3ae7ab93d6f185b7f8d7aa3748a1a47f964182ed7b.
- Extensión esperada: 400–700 palabras. Observada: 541, contando secuencias separadas por espacios con regex \S+.
- Enlace esperado: ../../coordinacion/PROYECTO.md resoluble desde docs/coordinacion. Observado: Test-Path True.
- Se contrastó el contenido con el encargo, plan y skill 0.1.2. Pendiente de dictamen independiente sobre este hash.
- AV-001: envío confirmado por transporte; ACUSES.md consultado, todavía sin acuse al realizar esta comprobación. Incorporación no acreditada.
- Pendientes: acuses, revisión independiente, integración, verificación de bytes en destino y cierre.

## Acuse AV-001 contrastado

El 2026-11-16 se consultó coordinacion/piloto-025-01/ACUSES.md, registro canónico. Declara incorporada la versión 1 y referencia el original íntegro. Su contenido coincide con el aviso propio; Get-FileHash SHA256 produjo 3974201c2b42bb8cf05f5a164b5ca980c0934ba853caed380b7a4fa9b819baec para ambas copias. El acuse no aprueba entrega ni integración. AV-002, revisión, integración y cierre siguen pendientes de comprobación.

## Acuse AV-002 contrastado

El 2026-11-16 se consultó coordinacion/piloto-025-01/ACUSES.md, registro canónico. Declara incorporada la versión 2 y referencia el original íntegro. Su contenido coincide con el aviso propio; Get-FileHash SHA256 produjo 498f9e9d979f344576cddb3f027b75d9378308beff8a799403f8dc31fe96bfc1 para ambas copias. El hash de la guía sigue siendo a53b345620e5882884548f3ae7ab93d6f185b7f8d7aa3748a1a47f964182ed7b. El acuse no aprueba la entrega ni acredita integración o cierre; se espera dictamen e integración.

## Integración y revisión contrastadas

El 2026-11-16 REVISION.md declara accepted sin correcciones para SHA256 a53b345620e5882884548f3ae7ab93d6f185b7f8d7aa3748a1a47f964182ed7b. Get-FileHash de entrega y destino produjo ese mismo valor y SequenceEqual confirmó igualdad de bytes; el enlace desde destino existe. INTEGRACION.md declara commit f94fa03639026ca693e693ed3a9145829306774d. La salida de commit en el historial del coordinador confirma ese identificador y la creación de docs/coordinacion/guia-uso.md; no se ejecutaron operaciones Git en este chat ni se comprobó directamente el blob del commit. El historial muestra avisos de conversión LF/CRLF de Git: la comparación de bytes realizada corresponde a los archivos de trabajo.

Los originales AV-001 y AV-002 y sus verificaciones se conservan en este entorno; sus copias y acuses están en el registro canónico. No se han eliminado recursos ni evidencias. Pendientes de coordinación: acuse AV-003, persistencia del cierre y archivado por el coordinador.

## Acuse AV-003 contrastado

El 2026-11-16 se consultó coordinacion/piloto-025-01/ACUSES.md, registro canónico. Declara incorporada la versión 3 y enlaza el original íntegro. El contenido de la copia canónica coincide con el aviso propio; Get-FileHash SHA256 produjo 4223264e07107af89f741e8fcd5107a759fed28f74e064e1b9d1b24a069f1fde para ambas copias. El acuse no acredita archivado. El coordinador comunica el commit de cierre a86c04411e7ece3e6f2177665758ae88ee3bc36c; no se ha comprobado personalmente mediante Git. Evidencias conservadas, sin limpieza adicional identificada.
