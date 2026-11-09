# Preparación de publicación del instalador AIKit

Estado: aplazado desde 2026-11-08. La distribución personal desde el repositorio
se define en `docs/distribucion-personal-aikit.md`. No publicado.

Se prepara `@manuelbouza/aikit` como identidad del paquete y `aikit` como
comando ejecutable. `npm whoami` confirmó la cuenta `manuelbouza`. El 2026-11-07
una consulta autenticada de `npm view @manuelbouza/aikit` devolvió E404: no se
encontró un paquete accesible con ese nombre. No constituye reserva ni prueba
definitiva de que el registro aceptará la publicación. Hay otros productos
llamados AIKit, por lo que un ámbito propio facilita distinguir el paquete.
El paquete sigue siendo privado; no se ha reservado ningún nombre ni publicado.

Uso previsto, solo ilustrativo, tras publicar y verificar el paquete:

```powershell
npx --yes @manuelbouza/aikit@latest install
```

Antes de publicar:

1. Comprobar la disponibilidad del nombre y acceso al repositorio. Elegir nombre
   definitivo y comprobar posibles confusiones.
2. Manuel eligió MIT y confirmó «Manuel Bouza» como titular. La licencia se ha
   incorporado al paquete del instalador AIKit; revisar la autoría y licencias
   de terceros antes de publicar. No establece licencia para otros componentes
   del monorepositorio.
3. La suite pasó en Windows con Node 20.0.0 y 20.20.2, además de Node 24;
   comprobar otras plataformas y los límites de recuperación antes de publicar.
4. Definir versión y notas de cambios; revisar qué archivos y preferencias se
   distribuyen. El paquete actual contiene código compilado y plantillas, no
   el complemento Delegating to OpenCode.
5. Preparar publicación desde GitHub Actions con npm trusted publishing cuando
   se confirme que el registro y la cuenta lo permiten. Configurar la relación
   para el repositorio y workflow exactos, con `id-token: write`. La primera
   publicación y la configuración del publicador requieren resolver el proceso
   específico del registro; no se asume que ya estén habilitados.
6. Revisar el artefacto final y autorizar por separado la publicación. Después,
   comprobar instalación y actualización de la versión publicada en perfiles
   ficticios antes de recomendar su uso global.

`private: true` continúa evitando la publicación accidental mientras faltan
estas decisiones. La validación local de `npx` se registra en
`docs/evidencias/validacion-npx-aikit.md`. No se afirma disponibilidad o
disponibilidad definitiva del nombre: la consulta autenticada obtuvo E404 y la
aceptación final depende del registro en el momento de publicar.

Referencia: [publicación de confianza de npm](https://docs.npmjs.com/trusted-publishers/).
