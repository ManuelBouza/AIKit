# Principios de evolución de AIKit

## Objetivo y estado actual

AIKit debe convertirse en un complemento instalable para reproducir preferencias
de Codex y distribuir distintas skills. Hoy contiene una skill de delegación a
OpenCode y su instalación manual. El empaquetado del complemento queda pendiente;
este documento establece los criterios que deberá cumplir.

## Explorar antes de implementar

Ante una petición de nueva skill o modificación:

1. Consulta el catálogo instalado y las herramientas disponibles. Lee los
   `SKILL.md` pertinentes; no decidas solo por el nombre.
2. Determina si la cobertura es completa, parcial o inexistente. Registra las
   capacidades consultadas y la necesidad pendiente en el diseño o descripción
   del cambio.
3. Si ya hay cobertura, usa la capacidad existente. Si falta una preferencia,
   evalúa resolverla con configuración antes de crear otra skill.
4. Implementa únicamente la parte que falte. Comprueba su activación junto a las
   skills relacionadas y documenta los límites de responsabilidad.

## Capacidades instaladas consultadas

Revisión del entorno de Manuel realizada el 28 de octubre de 2026. Este inventario
es orientativo: debe actualizarse consultando el entorno de destino.

| Necesidad | Capacidad existente | Papel de AIKit |
| --- | --- | --- |
| Crear o actualizar skills | `skill-creator` | Aportar requisitos y preferencias propias. |
| Instalar skills desde repositorios | `skill-installer` | Reutilizar su instalación cuando corresponda. |
| Descubrir y gestionar integraciones | `plugin-management` | Consultar sus capacidades antes de añadir otra integración. |
| Diseño, planes, pruebas, depuración y revisiones | Skills de Superpowers | Mantener sus flujos y roles. |
| Delegar ejecución a cuentas de OpenCode | `delegating-to-opencode` | Mantener el adaptador y la selección por tarea. |

La consulta de instrucciones confirma estas responsabilidades; no demuestra por
sí sola compatibilidad funcional ni que exista ya un instalador del complemento.

## Límites de integración

AIKit no debe sustituir los subagentes nativos, interceptar su creación ni
reescribir las skills de terceros. Cada skill debe tener una descripción de
activación acotada que evite competir con otra por tareas que ya están cubiertas.
Las preferencias del usuario prevalecen sobre los valores propuestos por AIKit.

## Criterios para distribuir el complemento

- Separar las preferencias portables de rutas, cuentas y credenciales locales.
- Documentar componentes, requisitos, activación y dependencias opcionales.
- Conservar la configuración ajena; detectar conflictos antes de modificarla.
- Permitir instalar, actualizar y retirar AIKit con restauración documentada.
- Validar en un entorno limpio y otro con Superpowers y skills relacionadas.
  Registrar configuración, resultado esperado y observado, incluidos conflictos
  de activación y cambios de configuración.

Estos criterios son requisitos pendientes de verificar al implementar el
empaquetado, no capacidades que el repositorio ya ofrezca.
