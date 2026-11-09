# Prueba de setup AIKit en ambos ámbitos

Fecha: 2026-11-08. Manuel autorizó instalar el complemento actualizado y probar
los ámbitos global y proyecto reales. El paquete exportado se instaló desde el
catálogo local de prueba `aikit-setup-prueba-20261108`.

En este chat se leyó la skill instalada y se siguieron sus instrucciones
manualmente. Se obtuvieron vistas previas y después se ejecutó el instalador
incluido. Ambos ámbitos devolvieron `changed`, con respaldo previo y respaldo
de Windows; las consultas `status` posteriores devolvieron `current` y versión
0.1.0. El proyecto ya contenía fuera de los bloques una preferencia equivalente
de Context7. Se eliminó esa copia manual tras la prueba y se conservó el bloque
gestionado por AIKit con el mismo contenido.

Esta prueba verifica la ejecución del instalador instalado en los dos destinos;
no demuestra que Codex Desktop descubra o invoque automáticamente la skill. La
instalación y configuración no activaron Delegating to OpenCode ni instalaron
Context7.
