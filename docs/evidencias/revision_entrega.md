# Comprobación de la entrega

Fecha: 8 de octubre de 2026.

- Reglas del prototipo: 20 pruebas unittest satisfactorias, sin fallos ni errores. Detalle en `pruebas.txt` y `resultados.json`.
- Ruta completa: 872 actualizaciones a 1/120 s; victoria con 600 puntos, usando movimiento normal y sin teletransportes durante la ruta.
- Eventos Pygame: pausa con P, reanudación con Escape, pausa al perder foco, reinicio con R y cierre comprobados.
- Arranque de `main.ejecutar()`: ejecutado con SDL sin ventana y cerrado mediante evento QUIT; finalizó correctamente.
- Pantallas inicial, pausa, victoria y derrota: renderizadas por la clase Vista e inspeccionadas visualmente.
- Informe Word: exportado a PDF con Microsoft Word en segundo plano. El renderizador habitual no encontró LibreOffice; se utilizó el motor de Word como alternativa.
- Informe final: 12 páginas. Las doce imágenes de la exportación final se inspeccionaron; portada, tablas, diagramas, código, capturas y numeración legibles, sin recortes observados.
- Integrantes: comprobados los cuatro nombres en el texto del PDF exportado.
- Contenedor DOCX: comprobación de integridad ZIP satisfactoria.

El modo gráfico de las verificaciones fue SDL dummy. No se ha realizado una sesión humana con teclado ni se ha medido el rendimiento en el equipo de exposición. El ensayo del equipo sigue pendiente.

El script `tools/empaquetar.py` valida la integridad del ZIP y el SHA-256 de cada archivo empaquetado. El manifiesto se incluye dentro del ZIP. El historial se entrega como Git bundle para no distribuir cachés ni el entorno virtual.
