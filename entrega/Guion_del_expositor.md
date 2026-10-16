# Guion breve de exposición

El PPT sigue los siete apartados de la estructura docente. La portada y la continuación del punto 4 llevan el total a nueve diapositivas. La plantilla original omite el apartado V.

| Punto | Apartado | Diapositivas |
| --- | --- | --- |
| 1 | I. Resumen ejecutivo | 2 |
| 2 | II. Introducción | 3 |
| 3 | III. Diseño de arquitectura | 4 |
| 4 | IV. Fundamentos de POO | 5 y 6 |
| 5 | VI. Resultados parciales | 7 |
| 6 | VII. Conclusiones | 8 |
| 7 | VIII. Anexos | 9 |

## Criterios de evaluación

- Arquitectura: diapositiva 4, con ocho clases y sus relaciones (6 puntos).
- Fundamentos POO: diapositivas 5 y 6, con los seis conceptos y ejemplos (6 puntos).
- Resultados parciales: diapositiva 7, con interfaz, funciones e historial Git (3 puntos).
- Presentación oral: claridad y dominio durante toda la exposición (5 puntos).

El material apoya la exposición; cada integrante debe poder explicar los ejemplos y sus aportes reales.

## Diapositiva 1: Portada

Presentar al equipo y anunciar que la exposición seguirá los siete apartados de la estructura entregada. El criterio IV de la rúbrica evalúa la claridad y el dominio durante toda la exposición.

## Diapositiva 2: I. Resumen ejecutivo

Resumir el objetivo y la organización del proyecto sin explicar aún cada clase. State organiza los estados de la partida y Observer comunica los cambios del puntaje.

## Diapositiva 3: II. Introducción

Explicar el contexto del curso y el objetivo académico. Señalar brevemente al jugador, la llave y la salida en la captura. Las tecnologías se presentan por su función, sin entrar en detalles de instalación.

## Diapositiva 4: III. Diseño de arquitectura

El diagrama resume ocho de las 25 clases del juego. Juego coordina la campaña. Nivel reúne las reglas de una etapa. Vista dibuja. Mapa resuelve paredes y recorridos. Puntaje conserva los puntos. Personaje es la base abstracta de Prisionero y Guardia. El rombo negro indica composición, el blanco agregación, el triángulo herencia y la flecha discontinua dependencia. El UML completo con atributos está en el punto 7.

## Diapositiva 5: IV. Asociación, agregación y composición

Asociación: Personaje conserva una referencia a Nivel para consultar el mapa. Agregación: Juego crea Puntaje y se lo entrega a cada Nivel, conservando el mismo objeto durante la campaña. Composición: Nivel construye su Mapa al cargar la etapa. La diferencia se explica por cómo se obtiene el objeto y la responsabilidad de crearlo.

## Diapositiva 6: IV. Herencia, polimorfismo y encapsulamiento

Personaje define una base abstracta. Prisionero responde al teclado y Guardia decide su movimiento. Nivel.actualizar llama a update sin distinguir su tipo. Puntaje protege la regla de los enteros no negativos mediante sus métodos. El guion bajo de _valor señala uso interno por convención de Python, no una barrera de acceso. El fragmento completo del setter está en anexos.

## Diapositiva 7: VI. Resultados parciales y Git

Demostrar en el juego una función breve, por ejemplo abrir la celda y pausar. La verificación automática completó los cuatro niveles y pasó 54 pruebas. La rúbrica pide evidenciar al menos el avance señalado, pero no define una fórmula: mostrar funciones ejecutables sin inventar un porcentaje. Abrir el historial de Git: cfaba6e registra el plan, 8917f20 el prototipo y f3cd9fe la documentación. Cada integrante debe explicar un aporte real, sin deducirlo de los nombres configurados de los autores.

## Diapositiva 8: VII. Conclusiones

Relacionar cada conclusión con un ejemplo presentado. Los fundamentos se observan en objetos reales del juego. La separación de Mapa, SistemaRuido y Nivel permitió comprobar reglas de movimiento y vigilancia. Cerrar destacando lo aprendido, sin afirmar una calificación o un porcentaje de avance no medido.

## Diapositiva 9: VIII. Anexos

Material de apoyo para las preguntas. El UML íntegro reúne las 25 clases del juego y puede ampliarse desde el enlace. El setter rechaza valores inválidos, cambia _valor y notifica a los observadores. La estructura entregada omite el apartado V, por eso los siete puntos son I, II, III, IV, VI, VII y VIII.
