# Descubrimiento aislado de la skill — 2026-11-15

Se probó la fuente `packaging/skills/coordinacion-chats` con Codex CLI 0.153.4
en Windows mediante app-server stdio. Se siguió la
[API oficial de inicialización y skills/list](https://learn.chatgpt.com/docs/app-server).
No se crearon chats ni turnos de inferencia.

La primera prueba bajo `.aikit/` reconoció la skill, pero heredó también las
skills del repositorio padre; no se considera una prueba de aislamiento completo.
Se repitió en una carpeta temporal externa al repositorio, con proyecto vacío y
perfil Codex temporal, sin copiar autenticación ni configuración del perfil real.
Se copió exclusivamente la skill a `.agents/skills/coordinacion-chats` del proyecto
ficticio. El servidor se terminó al concluir la consulta.

Resultado de initialize → initialized → skills/list con forceReload:

- Una entrada `coordinacion-chats`, con descripción correcta, scope `repo`,
  enabled `true` y ruta dentro del proyecto ficticio.
- Ninguna skill procedente del checkout AIKit y ningún error de descubrimiento.
- Los dos archivos copiados conservaron sus hashes SHA-256; la referencia relativa
  `references/avisos.md` existe en la copia.
- Proceso de prueba con código 0. No se creó `coordinacion/` ni se instaló nada
  en los directorios descubribles del proyecto o perfil reales.

Evidencia ignorada por Git:
`.aikit/025-carga-externa-aikit-025-carga-4vdc9ifa/`, con resultado, respuesta
skills/list, transcript y stderr. Script local `.aikit/025-probar-carga.py`.
El stderr conserva un aviso de red al consultar el catálogo destacado de plugins;
no impidió el descubrimiento local ni se necesitó autenticación o inferencia.

Esto acredita descubrimiento y metadatos por el cliente real, e integridad de la
copia. No acredita lectura de la referencia por un modelo, selección implícita,
invocación en la interfaz de escritorio, ni coordinación de producción.
Las evaluaciones textuales previas mantienen su alcance separado. Las copias
temporales se conservaron para inspección, fuera del proyecto activo.
