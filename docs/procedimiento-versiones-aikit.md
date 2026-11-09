# Primera publicación y actualizaciones de AIKit

Estado: procedimiento preparado; no se ha publicado. Cada publicación requiere
autorización expresa del usuario. Los comandos siguientes son instrucciones para
el momento de la publicación, no se ejecutaron como parte de esta preparación.

## Preparación común

1. Revisar código, licencias y cambios; resolver las limitaciones de Windows
   aceptables para la versión. Confirmar la identidad y disponibilidad de
   `@manuelbouza/aikit`, y que se publica desde la cuenta `manuelbouza`.
2. Fijar una nueva versión en `packages/aikit-installer/package.json` y su
   `package-lock.json`; actualizar notas de versión. En esta preparación el
   paquete sigue con `private: true`, que impide publicarlo.
3. Desde `packages/aikit-installer`, ejecutar `npm ci`, `npm test` y
   `npm pack --dry-run --json`. Revisar el listado: licencia, README, `dist` y
   plantillas; no debe incluir OpenCode ni datos privados. Probar un tarball real
   mediante `npx` con `CODEX_HOME` y caché ficticios, como en el README. Guardar
   el tarball aprobado y su `integrity` de `npm pack --json`.
4. Registrar resultados, revisar el diff y crear el commit de publicación.
   El push y la publicación son acciones separadas; no se autorizan por este
   procedimiento. Antes de publicar, cambiar `private` solo en la versión
   explícitamente aprobada y repetir las verificaciones del artefacto.

## Primera publicación: manual, con la cuenta del titular

La configuración de publicador de confianza se realiza en los ajustes del
paquete. Para evitar asumir que esos ajustes existen antes de crear el paquete,
se propone publicar la primera versión manualmente desde un checkout limpio,
tras revisión y autorización expresa. En la terminal del titular:

```powershell
npm whoami --registry=https://registry.npmjs.org
npm publish RUTA_DEL_TARBALL_APROBADO.tgz --access public --registry=https://registry.npmjs.org
```

El tarball debe proceder del commit aprobado con `private` retirado; no se debe
reconstruir entre su revisión y publicación. Un paquete con ámbito requiere
`--access public` para la primera publicación pública. Seguir la autenticación y
2FA que solicite npm; no compartir contraseñas ni códigos. Si falla, conservar
la salida y comprobar el registro antes de repetir: una respuesta ambigua no
demuestra que la publicación no ocurrió.

## Versiones posteriores: publicador de confianza

Una vez exista el paquete, preparar y revisar un workflow de publicación en
`.github/workflows/` y configurarlo en los ajustes del paquete de npm para el
repositorio `ManuelBouza/AIKit` y el nombre exacto del workflow. La publicación
de confianza requiere un runner alojado por GitHub, permiso `id-token: write`,
Node >=22.14 y npm >=11.5.1. Configurar la relación solo cuando se vaya a usar:
una configuración nueva caduca si su primera publicación no tiene éxito en dos
días. Considerar publicación escalonada para revisión con 2FA. El workflow y la
relación aún no están creados ni verificados.

Para cada actualización, incrementar la versión, repetir la preparación común y
autorizar de forma expresa el push y la publicación. No volver a publicar la
misma versión ni asumir que `latest` corresponde al artefacto validado.

## Verificación posterior

Consultar `npm view @manuelbouza/aikit version dist.integrity` y comparar versión
e integridad con el artefacto aprobado. En un perfil y caché ficticios ejecutar
`npx --yes @manuelbouza/aikit@VERSION install --dry-run`, después `install` y
`status`; comprobar respaldo y repetición. Sustituir `VERSION` por la versión
aprobada. Probar la actualización desde una versión anterior en otro perfil
ficticio. Registrar versión, comandos y resultado antes de recomendar uso global.

Referencias: [publicación de paquetes con ámbito](https://docs.npmjs.com/creating-and-publishing-scoped-public-packages/),
[publicadores de confianza](https://docs.npmjs.com/trusted-publishers/),
[publicación escalonada](https://docs.npmjs.com/staged-publishing/).
