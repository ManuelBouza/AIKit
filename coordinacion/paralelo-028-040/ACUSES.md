# Recepción manual de avisos

Fecha: 2026-11-16. Solo el Coordinador administra este registro manual.
Los originales se copian íntegros desde las rutas informadas por sus chats;
el origen se contrasta con los metadatos nativos de los mensajes recibidos.
No son acuses transaccionales del auxiliar v1 ni aceptación técnica de entregas.

## 028-preparacion-visual-01 — revisión 1

- Origen nativo: chat `01a1e56b-ca0d-7370-b82d-7ca39b03e5ba`.
- Referencia contrastada en su historial: turno
  `01a1e586-ea1b-7c81-ae55-223665c6b69d`, llamada `send_message_to_thread`
  `exec-38058339-9503-4fd8-ad9d-f8c037dc3eaf`, destino Coordinador.
- Decisión: aplicado al seguimiento de coordinación.
- Estado declarado: Esperando al usuario por propuesta visual, sin impedir esa
  conversación directa. Disponibilidad aislada de BMAD pendiente antes de implementar.
- [Original](avisos/028-preparacion-visual-01.md).
- SHA-256 original y copia canónica idénticos:
  `3ffce77f97ced06f1cdbc5eb16df4d17a885e368f23ba77e70363aedf9468783`.
- Responsable de ejecución y consulta visual: Chat 028. El Coordinador mantiene
  visible la dependencia de herramientas y no solicita otra orden de arranque.

## 040-bloqueo-bmad-01 — revisión 1

- Origen nativo: chat `01a1e56b-ec96-7960-b2ee-7f1d3f7366fb`.
- Referencia contrastada en su historial: turno
  `01a1e587-0672-7ac0-97b1-2c1095116561`, llamada `send_message_to_thread`
  `exec-d21f617a-b9f4-42eb-acaa-e635db677e53`, destino Coordinador.
- Decisión: aplicado al seguimiento de coordinación.
- Estado declarado: Bloqueada por preparación de BMAD/dependencias. Fallo DNS
  antes de renderizar; no se inició implementación. Conservar evidencia del fallo
  y `.venv` local; no reintentar a ciegas ni eludir la parada del flujo.
- [Original](avisos/040-bloqueo-bmad-01.md).
- SHA-256 original y copia canónica idénticos:
  `fbbaee92994f1dee38f83a232b1c0c68992a40f281e6f1d567e6634c7ecaedc2`.
- Responsable del trabajo: Chat 040. Resolución del entorno pendiente; puede
  contrastar fuentes y plantear una solución concreta sin reinstalaciones ni
  ejecutar otra vez el flujo fallido sin resolver la condición de parada.

Los acuses confirman incorporación de estos avisos, no permisos adicionales.
Esperar respuesta del Coordinador no bloquea trabajo propio independiente permitido.

## Dependencia de entorno compartida

El Coordinador es responsable de preparar y coordinar una solución aislada para
BMAD y las dependencias de ambos worktrees. La condición de resolución será
acreditar configuración y flujo disponibles para cada raíz, intérprete y
dependencias utilizables, y salidas confinadas al checkout de cada tarea, sin
escrituras ni cambios de configuración en el principal. No basta resolver DNS
si sigue faltando la configuración local. Conservar la parada de 040 hasta
resolver y comunicar la condición concreta del fallo.

El encargo actual no autoriza instalar nuevas herramientas, alterar el perfil
ni ejecutar reintentos del flujo fallido. La preparación de entorno se concretará
como siguiente acción, prefiriendo recursos existentes y sin ampliar permisos.
028 puede seguir tratando su propuesta visual con el usuario.
