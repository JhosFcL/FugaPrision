# Guion de exposición del parcial

Duración sugerida: 6 a 8 minutos. El reparto siguiente es una propuesta para ensayar; todos deben comprender las clases y ejecutar el juego.

## 1 Presentación y objetivo

**Jose Fernando Chavez Lozano, aproximadamente 1 minuto.**

“Nuestro proyecto se llama Fuga de la Prisión y corresponde a la temática 13. Es un videojuego 2D en Python. El jugador debe recoger una llave y escapar sin ser detectado por un guardia o una cámara. Para este parcial implementamos un primer nivel completo. La llave da 100 puntos y escapar suma 500 más.”

Mostrar la pantalla inicial. Identificar al prisionero stickman verde, el guardia stickman rojo, la cámara amarilla, la llave y la salida. Aclarar que se trata del avance de un nivel y que se agregarán niveles para el final.

## 2 Clases y relaciones

**Mickele Carlos Torres Velazco, aproximadamente 2 minutos.**

“Personaje reúne la posición y el movimiento. Prisionero y Guardia heredan de ella. El prisionero lee las teclas y el guardia patrulla. Nivel llama `update()` a ambos sin preguntar cuál es; cada uno responde a su manera. Eso es polimorfismo.”

“En la asociación, cada personaje guarda una referencia a su nivel. En la agregación, Nivel recibe el puntaje que Juego ya creó. En la composición, Nivel crea su prisionero, guardia, cámara, llave y salida. Hay dependencia cuando la cámara usa al prisionero para comprobar si lo ve, sin guardarlo. Para encapsular, el puntaje se cambia mediante un método que rechaza valores inválidos. Personaje es abstracta porque no se puede crear un personaje genérico sin definir cómo actúa.”

Mostrar el diagrama, las tres líneas del primer anexo, el bucle de `nivel.py` y el método `set_valor()` de `puntuacion.py`. Señalar el símbolo de cada relación sin leer todos los atributos de las nueve cajas.

## 3 Patrones de diseño

**Richard Aaron Soriano Cordova, aproximadamente 1 minuto y medio.**

“State separa Jugando, Pausa, Derrota y Victoria. Juego delega la entrada y la actualización en el estado activo. Por eso, en pausa no se actualizan posiciones ni temporizadores.”

Pausar con P y reanudar con Escape. Mostrar `estados.py`.

“Observer comunica los cambios del puntaje. Puntaje notifica a PanelPuntaje cuando sumamos puntos o reiniciamos. La clase Puntaje no conoce el dibujo de la pantalla. El panel se suscribe una sola vez.”

Mostrar `puntuacion.py` y la suscripción en `juego.py`. Los dos patrones implementados son State y Observer.

## 4 Demostración y pruebas

**Piero Cemei Romero Meza, aproximadamente 2 minutos.**

1. Mover al personaje contra un muro para mostrar la colisión.
2. Pulsar Shift y observar la carrera y su recarga.
3. Entrar en el campo visual del guardia; mostrar derrota y reiniciar con R.
4. Recoger la llave y señalar los 100 puntos.
5. Llegar a la salida y señalar los 600 puntos finales.

Ruta de ensayo para ganar: subir por el lado izquierdo y entrar al cuarto de la llave. Regresar por la misma entrada, bajar hasta el muro que separa al guardia y esperar cubierto a que cambie de dirección. Cruzar por el pasillo inferior de la zona central, rodear los obstáculos de la derecha y subir a la salida. La línea superior está bloqueada y no permite el atajo anterior.

“Ejecutamos veintidós pruebas automáticas. Revisan los muros, la visión del guardia y la cámara, el puntaje, la pausa y una ruta completa. La ruta llegó a la salida con 600 puntos. También falta hacer la prueba manual con teclado antes de exponer.”

Mostrar los resultados de las pruebas y una captura. Las capturas automáticas no sustituyen el ensayo con teclado.

## Preguntas que deben poder responder

- **¿Por qué no basta un solo archivo con todo?** Separar reglas, estados, puntaje y dibujo permite modificar y probar cada responsabilidad con menos dependencias.
- **¿Qué protege el puntaje?** Los métodos validan que un incremento sea un entero positivo. El prefijo `_` expresa uso interno en Python; no es una protección absoluta del lenguaje.
- **¿Por qué el guardia y la cámara no heredan de la misma clase?** La cámara se modeló como dispositivo de vigilancia. La jerarquía Personaje representa a los actores que se actualizan polimórficamente.
- **¿Qué pasa si se alcanza la salida al ser detectado?** Se procesa primero la detección y se pierde, sin conceder el premio de salida.
- **¿Cuántos niveles hay?** Uno implementado en el parcial. La ampliación multinivel está pendiente para el final.
- **¿Por qué no aparecen todas las clases en el UML?** El código tiene dieciocho clases y el diagrama muestra nueve clases clave para que las relaciones se lean con claridad. Las otras son los estados, la habilidad de correr, el observador del puntaje y la vista. La rúbrica pide ocho o más clases principales, no un inventario de todas.

## Antes de entregar

- Ensayar en el equipo donde se presentará; comprobar teclado, legibilidad y ventana de 1000 por 760 píxeles.
- Registrar los aportes reales de cada integrante. Los ocho commits revisados muestran dos nombres de autor configurados; por sí solos no identifican el trabajo de los cuatro integrantes.
- Si cambia el juego o el UML, actualizar también las capturas y el informe antes de subir la entrega.
