# Guion de exposición: Fuga de la Prisión

La presentación empieza con los objetivos, las reglas, los controles y las tecnologías. Después explica la arquitectura y la POO. Las 25 fichas de clases sirven para ampliar ejemplos o responder preguntas. Al final se muestran pruebas reales del código y se cierran las conclusiones.

## Relación con el informe y la rúbrica

| Apartado del informe | Diapositivas | Qué explicar |
| --- | --- | --- |
| I. Resumen ejecutivo | 2 | Qué busca conseguir el jugador. |
| II. Introducción | 3 a 6 | Objetivo académico, reglas, controles y herramientas. |
| III. Diseño de arquitectura | 7 y 12 a 37 | Organización general, UML completo y clases. |
| IV. Fundamentos de POO | 8 a 10 | Los seis fundamentos y los dos patrones. |
| VI. Resultados parciales | 11 y 38 a 41 | Funciones del juego, Git y pruebas. |
| VII. Conclusiones | 42 | Resultados y aprendizaje del proyecto. |
| VIII. Anexos | 12 a 37 | UML, fragmentos y fichas de apoyo. |

La estructura docente omite el apartado V. El cierre se coloca después del material de apoyo para terminar con las pruebas y las conclusiones, como se solicitó.

La rúbrica evalúa arquitectura (6 puntos), fundamentos POO (6), resultados parciales (3) y exposición oral (5). Las pruebas respaldan los resultados; cada integrante también debe poder explicar el código y sus aportes reales.

## 1. Portada

Presentar al equipo y el nombre del proyecto. Anunciar el recorrido: objetivos, funcionamiento, herramientas, POO y comprobación del juego.

## 2. Objetivos del juego

“El jugador debe escapar de una prisión. Primero abre su celda; luego busca llaves y salidas evitando a los guardias. La campaña tiene tres zonas de sigilo y una arena final. En esa arena debe vencer las tres capas del Alcaide, recoger su llave y alcanzar la salida.”

Estos son los objetivos del jugador. Los objetivos académicos se explican en la siguiente diapositiva.

## 3. Objetivos del proyecto

“Nuestro objetivo académico es aplicar la programación orientada a objetos en un juego funcional. Organizamos las responsabilidades en 25 clases y representamos su estructura en UML. También usamos State y Observer, y trabajamos con Git y GitHub para conservar e integrar los cambios.”

Los seis fundamentos de la rúbrica son asociación, agregación, composición, encapsulamiento, herencia y polimorfismo. La abstracción también está presente en las clases base. State y Observer son patrones de diseño.

## 4. Reglas del juego

Explicar la llave y la salida antes de hablar de los enemigos. Los pasos producen ruido: correr se escucha desde más lejos y el sigilo reduce ese ruido. Las cámaras alertan a los guardias; el contacto con un guardia provoca la captura. En el Patio, recoger la llave abre atajos de regreso.

El jefe empieza con 216 puntos de vida divididos en tres capas de 72. Al agotarse una capa aumenta la dificultad. El jugador tiene cinco puntos de vida en la arena. La llave final queda disponible cuando el jefe llega a cero.

El puntaje total posible es 3400: cuatro llaves de 100, cuatro salidas de 500 y 1000 por vencer al jefe.

## 5. Controles

Mostrar movimiento y sigilo en una demostración breve. Para abrir la celda hay que mantener E durante dos segundos junto a su puerta. Shift activa dos segundos de carrera con cinco de recarga. Espacio dispara hacia el jefe e IJKL permite elegir una dirección.

P o Escape pausa y continúa. Enter pasa al siguiente nivel cuando este ya se completó. R reintenta tras perder y reinicia la campaña tras ganar. N empieza desde cero después de una derrota o entre niveles.

## 6. Tecnologías utilizadas

- **Python:** contiene las clases, sus atributos y métodos, y las reglas del juego.
- **Pygame:** permite abrir la ventana, leer el teclado y dibujar la partida.
- **Mermaid.js:** conserva el UML en un archivo de texto que se puede editar y convertir en imagen.
- **Git y GitHub:** Git registra las versiones; GitHub permite compartir el repositorio e integrar aportes.
- **unittest:** ejecuta escenarios preparados y comprueba sus resultados mediante aserciones.

El informe registra Python 3.13.7 y Pygame 2.6.1 como entorno de comprobación. `ast` y `re` son módulos de Python utilizados en las pruebas de documentación.

## 7. Arquitectura

El esquema resume ocho clases para presentar la organización. **El UML completo reúne las 25 clases** y está enlazado en la diapositiva 12 y en la página 7 del informe.

Juego coordina la campaña; Nivel reúne los objetos y reglas de una etapa; Vista dibuja; Mapa resuelve paredes y caminos; Puntaje conserva los puntos. Personaje es la base abstracta de Prisionero y Guardia.

En las relaciones UML, el rombo negro indica composición, el blanco agregación, el triángulo herencia y la flecha discontinua dependencia. Las fichas conservan las cajas del diagrama con sus miembros.

## 8. Asociación, agregación y composición

- **Asociación:** `Personaje` guarda la referencia a su `Nivel` mediante `self.nivel = nivel`, para consultar el entorno.
- **Agregación:** `Nivel` recibe el `Puntaje` creado por `Juego`. Los niveles comparten ese mismo objeto durante la campaña.
- **Composición:** `Nivel` construye su propio `Mapa` con `self.mapa = Mapa(PLANOS[indice])`.

Para distinguirlas, explicar quién crea cada objeto y quién lo recibe. Una referencia entre objetos, por sí sola, no explica toda la relación.

## 9. Herencia, polimorfismo y encapsulamiento

- **Herencia:** `Prisionero` y `Guardia` derivan de `Personaje` y aprovechan sus datos y operaciones comunes.
- **Abstracción:** `Personaje` define la base y exige implementar `update()`; las clases concretas completan ese comportamiento.
- **Polimorfismo:** `Nivel` recorre los personajes y llama `personaje.update()`. El prisionero responde al teclado y cada guardia aplica su lógica de vigilancia, usando la misma operación.
- **Encapsulamiento:** `Puntaje` concentra la validación en `set_valor()` y permite consultar con `get_valor()`. Rechaza valores que no sean enteros no negativos y notifica los cambios válidos. El guion bajo de `_valor` señala uso interno por convención de Python.

## 10. Patrones State y Observer

**State:** Juego delega la entrada y la actualización en el estado activo. Jugando avanza el nivel; Pausa detiene la simulación; Derrota, Victoria y NivelCompletado deciden qué opciones permite la partida. Todos siguen la interfaz de EstadoJuego. Los modos del guardia, como PERSIGUE, se controlan con una variable y condiciones.

**Observer:** Juego suscribe PanelPuntaje a Puntaje. Cuando `set_valor()` cambia el valor, Puntaje llama a `_notificar()` y cada observador recibe `actualizar_puntaje()`. Vista dibuja el valor conservado por el panel. Los fragmentos mostrados pertenecen a distintos métodos de Juego y Puntaje.

## 11. Resultados parciales y Git

Demostrar una función breve: abrir la celda, moverse y pausar. Mostrar que hay vigilancia, llaves, salidas y una campaña de cuatro niveles. El informe registra una comprobación completa y capturas de esa campaña.

Los commits visibles son ejemplos del historial: cfaba6e, plan inicial; 8917f20, prototipo y pruebas; f3cd9fe, informe y diagramas. Abrir el historial del repositorio y explicar aportes reales del equipo.

La rúbrica solicita un avance, pero no proporciona una fórmula para calcularlo. Explicar funciones comprobables sin asignar un porcentaje inventado.

## 12 a 37. UML y fichas de las clases

La diapositiva 12 enlaza el UML completo y muestra el setter del puntaje. Las fichas siguientes contienen la función de cada clase, su relación con la POO, un fragmento de código y la fuente.

El informe actual tiene siete páginas. La explicación completa del código está en `docs/Explicacion_de_clases.md` y el resumen de las 25 clases en `entrega/Guia_POO_25_clases.md`.

| Clase | Diapositiva |
| --- | --- |
| Juego | 13 |
| EstadoJuego | 14 |
| Jugando | 15 |
| Pausa | 16 |
| Derrota | 17 |
| Victoria | 18 |
| NivelCompletado | 19 |
| Nivel | 20 |
| PuertaCelda | 21 |
| Mapa | 22 |
| Personaje | 23 |
| Prisionero | 24 |
| Guardia | 25 |
| HabilidadCarrera | 26 |
| SistemaRuido | 27 |
| Camara | 28 |
| Llave | 29 |
| PuertaSalida | 30 |
| Puntaje | 31 |
| ObservadorPuntaje | 32 |
| PanelPuntaje | 33 |
| Proyectil | 34 |
| Alcaide | 35 |
| Combate | 36 |
| Vista | 37 |

## 38. Pruebas para detectar errores

“Para comprobar el juego usamos unittest. Cada prueba prepara una situación, ejecuta una acción y compara lo que ocurrió con lo que debería pasar. La revisión ejecutó 54 pruebas y todas pasaron.”

Los archivos `test_juego.py`, `test_mapa.py`, `test_vigilancia.py`, `test_campana.py` y `test_documentacion.py` agrupan las comprobaciones mostradas. Sus clases `TestCase` ayudan a probar el programa; las 25 clases del UML corresponden al juego.

Tres instrucciones que hay que saber explicar:

- `assertEqual(a, b)`: exige que ambos resultados sean iguales.
- `assertTrue(condicion)`: exige que la condición se cumpla.
- `assertRaises(ValueError)`: exige que una entrada inválida produzca ese error.

Si una condición no se cumple, unittest informa qué prueba falló. Tras corregir el problema, se ejecuta otra vez para comprobar que la regla funciona y que el cambio no rompe los casos anteriores.

## 39. Pruebas de paredes y puntaje

**Pared:** el caso intenta mover al jugador 1000 píxeles. `assertEqual()` compara la posición final con el límite de la puerta cerrada de la celda. Si la atraviesa o se detiene donde no corresponde, la prueba falla. `TAMANO` representa el tamaño de una celda del mapa y `radio` el espacio que ocupa el personaje.

**Puntaje:** el bucle ensaya `-1`, `1.5`, `True` y `"100"`. Son un negativo, un decimal, un booleano y un texto. `assertRaises(ValueError)` comprueba que el setter los rechace. El caso completo también acepta 250 y verifica que el panel reciba ese valor.

Las líneas de la diapositiva son fragmentos de `tests/test_juego.py`; se ejecutan dentro del escenario preparado por la prueba.

## 40. Pruebas de alarmas y capas del jefe

**Alarma:** el escenario coloca al prisionero delante de cada cámara de los tres mapas de sigilo. Comprueba que la cámara se active, que todos los guardias queden en PERSIGUE y que el estado continúe siendo Jugando. Así se revisa la regla de alertar sin provocar una derrota instantánea.

`all(...)` exige que la condición se cumpla para todos los guardias. `assertIsInstance(juego.estado, Jugando)` comprueba el tipo del estado activo.

**Capas:** la prueba prepara tandas de impactos y verifica que la vida quede en 144, 72 y 0. `restante` es el valor esperado en cada paso. `restante == 0` solo es verdadero al final; se compara con `llave.disponible` para comprobar que la llave no aparezca antes. El caso completo también revisa que una tanda no salte varias capas y que el premio no se repita.

Son escenarios preparados para comprobar reglas concretas. La comprobación de campaña descrita en el informe utiliza recorridos y disparos para completar los niveles.

## 41. Pruebas del UML y de la guía

**UML:** el código analiza las clases de `src` y extrae las cajas del archivo Mermaid. Compara conjuntos de nombres, atributos propios, métodos y relaciones de herencia. `set(cajas)` y `set(clases)` permiten comprobar que no falte ni sobre una clase.

**Guía:** `ast` lee la estructura del código Python. `ast.dump()` convierte esa estructura en una representación que se puede comparar. La prueba contrasta cada clase original con el bloque incluido en la explicación, para detectar documentación desactualizada.

Estos casos comprueban correspondencia estructural. La legibilidad del UML y el significado de sus relaciones también deben revisarse visualmente.

## 42. Conclusiones del proyecto

“El proyecto conecta los objetivos del juego con lo aprendido en el curso. Sus 25 clases separan responsabilidades y permiten mostrar los seis fundamentos POO, además de State y Observer. Python y Pygame ejecutan el juego; Mermaid comunica el diseño; Git y GitHub conservan el trabajo del equipo.”

“Las pruebas nos permiten repetir escenarios y comprobar reglas como las paredes, las alarmas y las capas del jefe. En esta revisión pasaron 54 casos. Esto respalda los resultados de esos escenarios y nos ayuda a detectar cambios que introduzcan errores. El aprendizaje fue mantener coherentes el funcionamiento del juego, sus clases y la documentación.”

Las pruebas cubren los casos definidos; no garantizan la ausencia absoluta de errores ni una calificación determinada. Cada integrante debe ensayar la explicación y los controles en el equipo que usará para exponer.
