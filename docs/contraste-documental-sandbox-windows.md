# Contraste documental del sandbox Windows — 2026-11-15

Alcance: investigar los dos errores de la prueba de coordinación antes de
proponer reparaciones. No se ejecutaron nuevos ensayos ni cambios de permisos.
Los hechos locales están en el [informe de invocación](invocacion-aislada-skill-coordinacion.md).

## Fuentes y correspondencia

1. [Guía oficial Windows](https://learn.chatgpt.com/docs/windows/windows-sandbox):
   distingue implementaciones nativas y permisos del proceso. El backend elevado
   requiere preparación administrativa, pero los comandos aislados no se ejecutan
   como administrador. La documentación actual incluye opciones para clientes
   más recientes: no trasladarlas sin comprobar compatibilidad con CLI 0.153.4.
2. [Reporte técnico 42172](https://github.com/openai/codex/issues/42172): describe
   rechazos antes de ejecutar comandos al omitir el selector Windows con
   ignore-user-config. La comparación local ya realizada es compatible con ese
   reporte: al explicitar elevated cambió el error. Es evidencia de un problema
   de configuración de la prueba; no acredita por sí sola la causa del siguiente.
3. [Microsoft: SetNamedSecurityInfoW](https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-setnamedsecurityinfow):
   modificar la DACL exige WRITE_DAC o ser propietario. Poder modificar archivos
   no equivale a poder cambiar sus permisos. Esto explica por qué una lectura
   puede fallar durante la preparación del helper, antes de abrir su destino.
4. [Reporte 45153](https://github.com/openai/codex/issues/45153) y
   [reaprovisionamiento 46380](https://github.com/openai/codex/issues/46380):
   describen fallos al reescribir la DACL de .sandbox-bin, incluso después de una
   operación exitosa. Las identidades y permisos varían entre equipos: incluyen
   usuario sin WRITE_DAC y elevación con otra cuenta. No son un diagnóstico local.
5. [Reporte 40550](https://github.com/openai/codex/issues/40550): los testimonios
   incluyen arreglos de ACL que solo funcionan una vez, porque el helper vuelve
   a establecer permisos que causan otro fallo. No justifican aplicar cambios
   amplios, conceder control total o borrar directorios como solución general.
6. [Código actual de OpenAI](https://github.com/openai/codex/blob/main/codex-rs/windows-sandbox-rs/src/setup_provisioning.rs):
   lock_sandbox_bin_dir incorpora WRITE_DAC al acceso del usuario real y explica
   que el refresco no elevado debe poder reaplicar la DACL protegida. Es coherente
   con la clase de fallo investigada. main es mutable y no prueba qué contiene
   el binario instalado. La consulta del tag rust-v0.153.4 en esa ruta devolvió
   404; no se da por comprobada la implementación de esa versión ni una versión
   mínima que lo corrija.

## Conclusión y decisión

La hipótesis mejor respaldada para el segundo error es una discrepancia entre
propietario/DACL y el token con el que el helper intenta preparar .sandbox-bin.
Se retira la prioridad dada anteriormente a la ejecución anidada: las fuentes
muestran el mismo síntoma fuera de ese contexto, sin demostrar su causa aquí.

El primer error y el segundo se mantienen separados. El selector omitido explica
el cambio observado en el primer rechazo; el log del segundo acredita denegación
en SetNamedSecurityInfoW, pero no identifica qué derecho o identidad concreta falta.
No se concluye que la skill, PowerShell, Defender o los archivos de referencia
sean defectuosos, ni que actualizar a una versión particular garantice corregirlo.

Antes de diseñar una reparación, la siguiente comprobación dirigida debe ser
solo de lectura: obtener propietario, DACL, herencia e identidad/token pertinentes
y contrastarlos con los registros de preparación existentes. No inferir permisos
efectivos únicamente de una ACE Allow aislada; considerar grupos, denegaciones
y token filtrado. Conservar los datos de identidad localmente, redactados en
cualquier informe compartido. Esa comprobación resuelve una laguna concreta de
las fuentes, sin volver a gastar inferencia en ensayos de invocación de la skill.

No se recomienda todavía cambiar ACL, tomar propiedad, borrar o renombrar el
helper. Las recetas comunitarias son observaciones técnicas, no instrucciones
oficiales de reparación validadas para este entorno. Una reparación deberá
definir alcance y recuperación antes de modificar el sandbox compartido.
