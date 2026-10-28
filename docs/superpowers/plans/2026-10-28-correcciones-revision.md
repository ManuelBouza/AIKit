# Correcciones de la revisión funcional

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Corregir las discrepancias de política, protección y distribución manual
detectadas en la revisión funcional, sin empaquetar aún el complemento.

**Architecture:** Mantener la selección razonada en el coordinador y un intento
por llamada. Comprobar restricciones antes de inferencia en el destino y fallar
si no pueden acreditarse. Reutilizar las skills existentes de desarrollo.

**Tech Stack:** Python tipado, biblioteca estándar, uv, pytest, Ruff y mypy.

**Spec:** Hallazgos aceptados por el usuario en la revisión funcional y
`docs/principios-aikit.md`.

## Global Constraints

- Conservar gratuitos → Go → alternativas adecuadas → Codex; bloquear `openai`
  directo y conservar GPT de otros proveedores.
- No interceptar subagentes Codex ni alterar Superpowers.
- No modificar privacidad, cuentas, credenciales ni configuración ajena.
- No construir instalador ni sandbox propios; no prometer rollback automático.

## Review Focus

Configuración ausente, JSON inválido, reglas contradictorias, reglas con
comodines y respaldos dentro de rutas descubribles deben tener resultado explícito.

## Tareas

### 1. Política sin opciones engañosas

- [x] Probar que la política solo admite `prefer_free` booleano; rechazar opciones
  desconocidas. El motivo sigue siendo obligatorio en todos los casos.
- [x] Observar el fallo, simplificar `load_policy` y `policy.json`, verificar.

### 2. Protección del destino antes de inferencia

- [x] Probar rechazo si las fuentes no acreditan bloqueo directo OpenAI y
  subdelegación interna, también con fuentes inválidas o reglas contradictorias.
- [x] Observar los fallos e implementar comprobación conservadora con
  `debug config --standalone`. No escribir archivos del proyecto de destino.
- [x] Probar que un proyecto configurado correctamente admite ejecución, mientras
  Go/GPT sigue disponible, y que el diagnóstico no expone contenido sensible.

### 3. Documentación, instalación y verificación

- [x] Aclarar que las preferencias se aplican por instrucciones al coordinador;
  el adaptador no evalúa capacidad suficiente ni selecciona automáticamente.
- [x] Situar respaldos fuera de directorios de skills y plugins descubribles.
- [x] Documentar timeout por proceso, cambios parciales y responsabilidad del
  aislamiento; mantener empaquetado y propagación global como pendientes.
- [x] Ejecutar pytest, Ruff, mypy y validador de skill. Revisar el conjunto con
  un revisor independiente, corregir hallazgos y registrar evidencia.
- [x] Actualizar la copia personal con respaldo no descubrible y hashes.
- [x] Guardar en Git; no publicar nuevos cambios sin solicitud.
