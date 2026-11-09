# Instalar AIKit desde este repositorio

Esta vía requiere acceso autorizado al repositorio privado, Git, Python, Node.js
y npm. Es una instalación personal; el flujo de Context7 ausente todavía debe
comprobarse en una cuenta real.

1. Clona el repositorio y abre PowerShell en su raíz.
2. Descarga las dependencias de compilación y exporta el complemento a una ruta
   nueva, fuera de un paquete previo:

   ```powershell
   npm ci --prefix packages/aikit-installer
   python scripts/build_aikit.py --output .aikit/catalogo-personal
   ```

3. En esa misma raíz, registra el catálogo e instala el complemento:

   ```powershell
   codex plugin marketplace add .aikit/catalogo-personal
   codex plugin add aikit-preferencias@aikit-preferencias-local
   ```

4. Abre un chat nuevo en Codex e invoca `aikit-setup`. Indica si deseas aplicar
   las preferencias al perfil global o al repositorio actual. Revisa la vista
   previa. El setup busca las herramientas recomendadas y solicita autorización
   antes de instalar las que falten; algunas acciones pueden requerir la
   interfaz de complementos o una conexión adicional.

El constructor exige una salida que aún no exista. Para actualizar, vuelve a
exportar en una ruta nueva y sigue el procedimiento de actualización del catálogo
disponible en el cliente; este recorrido entre PC aún no está verificado. No
instales directamente desde la raíz del checkout, que contiene otros componentes
y puede contener archivos locales ignorados.
