---
name: coordinacion-chats
description: Coordina avisos y acuses entre el coordinador de un proyecto y sus chats de tarea cuando el usuario solicita esa coordinación. No sustituye subagentes ni activa la coordinación de un proyecto por sí sola.
---

# Coordinación de chats

Aplica las instrucciones de [avisos y roles](references/avisos.md) cuando el
usuario haya activado la coordinación del proyecto y exista una asignación
identificable. Determina si actúas como coordinador o como chat de tarea y sigue
las responsabilidades de ese rol. Ante identidad o autorización insuficiente, conserva
la información como pendiente y explica la limitación.

La coordinación es local al proyecto y no exige Git, BMAD, OpenCode ni una
aplicación concreta. Usa las capacidades del cliente disponibles y autorizadas;
ofrece traslado manual cuando falte mensajería. Leer esta skill no crea chats,
instala herramientas, activa automatizaciones ni concede permisos.

El auxiliar de registro existente es un prototipo limitado y no se distribuye
con esta skill. No supongas que está instalado ni que autentica mensajes o
permite relevo, reasignación o nuevos ciclos. No declares registro verificado
sin un mecanismo disponible que lo acredite.
