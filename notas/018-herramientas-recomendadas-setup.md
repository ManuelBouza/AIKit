# 018 — Herramientas recomendadas durante setup

- Fecha: 2026-11-09
- Estado inicial: Pendiente de debatir
- Estado actual: Implementada e instalada; prueba de comportamiento pendiente

Manuel solicita que el setup de AIKit revise las herramientas recomendadas,
proponga las que falten y, con aprobación del usuario, gestione su instalación
desde los complementos. Debe comprobar primero si ya están instaladas. Por ahora
solo se recomienda Context7; la lista debe poder crecer. Context7 debe estar
disponible globalmente y BMAD solo se activa en proyectos que lo necesiten.

El 2026-11-09, la búsqueda de complementos confirmó Context7 instalado y
habilitado con alcance global en esta cuenta. Esto no demuestra su disponibilidad
en otras cuentas o PC. La búsqueda de complementos y las herramientas de
Context7 ya existentes cubren descubrimiento y consulta; no se crea otra skill.
La instalación de un complemento desde el directorio puede requerir interacción
o conexión del usuario según el cliente. No se debe presentar como completada
hasta verificarla.

La skill de setup consulta la lista ampliable `references/herramientas.md`,
comprueba estado y solicita aprobación para lo que falte. Si el cliente solo
admite sugerir o necesita interacción del usuario, lo comunica y vuelve a
verificar. La capacidad de instalación automática de complementos remotos no
está demostrada; no se presume. El complemento actualizado se instaló el
2026-11-09; falta comprobar el comportamiento de la skill actualizada y el caso
de Context7 ausente en una cuenta real.

## Comprobación aislada — 2026-11-09

El instalador se ejecutó con un `--codex-home` ficticio bajo `.aikit/`:
la vista previa incluyó la preferencia Context7, la instalación creó el archivo
en ese perfil y el estado posterior fue `current`. No se modificó la instalación
real de Context7. Esto comprueba los bloques de instrucciones, no la gestión
de complementos.

Una revisión independiente de la skill frente a estados ficticios (ausente,
aprobado, desconocido y habilitado) identificó las respuestas previstas en su
texto. No se ejecutó un gestor simulado ni se observó al modelo siguiendo esos
casos; por tanto no constituye una prueba de comportamiento. Sigue pendiente
probar ese flujo y verificar la instalación remota real cuando sea posible.

Posteriormente se realizó una [prueba ejecutable con un gestor ficticio](../docs/evidencias/prueba-setup-gestor-ficticio.md):
se observaron los casos presente, ausente, aprobación ficticia y consulta fallida.
En este último el agente informó de estado desconocido y no instaló. Sigue
pendiente verificar la instalación remota real.

## Entorno para prueba real — 2026-11-09

Se creó un `CODEX_HOME` aislado bajo `.aikit/` y `codex login status` informó
que no tenía sesión iniciada. El perfil actual sí tiene sesión y el catálogo
ya confirma Context7 globalmente. Por ello el perfil vacío no constituye por sí
solo una cuenta autenticada independiente con Context7 ausente. Queda pendiente
realizar la prueba en una cuenta autenticada que no lo tenga instalado; no se ha
desinstalado ni modificado el complemento real para crear esa condición.
