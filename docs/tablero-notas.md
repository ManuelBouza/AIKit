# Tablero local de notas

Desde PowerShell en la raíz del repositorio, prepara el entorno con
`uv sync --locked`. Después genera y abre la vista de consulta con:

```powershell
uv run --locked python scripts/tablero_notas.py
```

Para regenerar sin abrir el navegador, añade `--sin-abrir`. El archivo generado
está en `.aikit/tablero-notas/index.html`, ignorado por Git. El tablero incluye
los cambios locales sin commit y muestra su fecha de generación. Vuelve a ejecutar
el comando después de cambiar las notas; no se actualiza automáticamente.

El índice `notas/IDEAS.md` es la fuente de las tarjetas. Las secciones del índice
son agrupaciones históricas y el estado detallado se reproduce literalmente. Las
notas se muestran con formato, pero sus enlaces e imágenes se presentan como
texto con sus rutas para evitar abrir destinos o cargar contenido externo.
El tablero no edita archivos ni ejecuta acciones y no implica aprobar tareas.

Una fila inválida, una ruta insegura o una nota inexistente abortan la generación;
se informa el error, se conserva la última salida y no se abre como si fuera nueva.
La preparación inicial de dependencias puede requerir red; una vez sincronizado
el entorno, el generador y la página no necesitan conectarse a Internet.
