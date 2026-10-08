# Guion de exposición del parcial

Duración sugerida: 6 a 8 minutos. El reparto siguiente es una propuesta para ensayar; todos deben comprender las clases y ejecutar el juego.

## 1 Presentación y objetivo

**Jose Fernando Chavez Lozano, aproximadamente 1 minuto.**

“Nuestro proyecto se llama Fuga de la Prisión y corresponde a la temática 13. Es un videojuego 2D en Python. El jugador debe recoger una llave y escapar sin ser detectado por un guardia o una cámara. Para este parcial implementamos un primer nivel completo. La llave da 100 puntos y escapar suma 500 más.”

Mostrar la pantalla inicial. Identificar al prisionero verde, el guardia rojo, la cámara amarilla, la llave y la salida. Aclarar que se trata del avance de un nivel y que se agregarán niveles para el final.

## 2 Clases y relaciones

**Mickele Carlos Torres Velazco, aproximadamente 1 minuto y medio.**

“Personaje es una clase abstracta. Prisionero y Guardia heredan de ella, pero cada uno implementa update de forma diferente. Nivel recorre los personajes y hace la misma llamada a ambos. Esa diferencia de comportamiento es el polimorfismo.”

Abrir `src/personajes.py` y el bucle de `src/nivel.py`. Mostrar que `Nivel` crea los objetos de su mapa y `Prisionero` crea `HabilidadCarrera`: son ejemplos de composición. Explicar la dependencia de `PuertaSalida.puede_salir(prisionero)`, que consulta al objeto recibido sin guardarlo.

## 3 Patrones de diseño

**Richard Aaron Soriano Cordova, aproximadamente 1 minuto y medio.**

“State separa Jugando, Pausa, Derrota y Victoria. Juego delega la entrada y la actualización en el estado activo. Por eso, en pausa no se actualizan posiciones ni temporizadores.”

Pausar con P y reanudar con Escape. Mostrar `src/estados.py`.

“Observer comunica los cambios del puntaje. Puntaje notifica a PanelPuntaje cuando sumamos puntos o reiniciamos. La clase Puntaje no conoce el dibujo de la pantalla. El panel se suscribe una sola vez.”

Mostrar `src/puntuacion.py` y la suscripción en `src/juego.py`. No afirmar que se implementó Factory Method: los dos patrones elegidos son State y Observer.

## 4 Demostración y pruebas

**Piero Cemei Romero Meza, aproximadamente 2 minutos.**

1. Mover al personaje contra un muro para mostrar la colisión.
2. Pulsar Shift y observar la carrera y su recarga.
3. Entrar en el campo visual del guardia; mostrar derrota y reiniciar con R.
4. Recoger la llave y señalar los 100 puntos.
5. Llegar a la salida y señalar los 600 puntos finales.

Ruta de ensayo para ganar: pasillo izquierdo hacia la llave, fila transitable superior hacia la derecha, pasar por encima de la cámara y bajar a la salida. No se necesita una opción especial ni modificar el código.

“Ejecutamos veinte pruebas automatizadas. Comprueban colisiones, visión, puntaje, pausa, reinicio, habilidad y una ruta completa. Los resultados están en la carpeta de evidencias. La ruta automatizada completó el nivel con 600 puntos.”

Mostrar `docs/evidencias/pruebas.txt`. Las capturas se obtuvieron con Pygame en modo sin ventana; no presentarlas como evidencia de una sesión humana. Antes de exponer, realizar y registrar ese ensayo con teclado.

## Preguntas que deben poder responder

- **¿Por qué no basta un solo archivo con todo?** Separar reglas, estados, puntaje y dibujo permite modificar y probar cada responsabilidad con menos dependencias.
- **¿Qué protege el puntaje?** Los métodos validan que un incremento sea un entero positivo. El prefijo `_` expresa uso interno en Python; no es una protección absoluta del lenguaje.
- **¿Por qué el guardia y la cámara no heredan de la misma clase?** La cámara se modeló como dispositivo de vigilancia. La jerarquía Personaje representa a los actores que se actualizan polimórficamente.
- **¿Qué pasa si se alcanza la salida al ser detectado?** Se procesa primero la detección y se pierde, sin conceder el premio de salida.
- **¿Cuántos niveles hay?** Uno implementado en el parcial. La ampliación multinivel está pendiente para el final.
- **¿Usan API?** Todavía no. Debe aclararse la contradicción entre el encabezado “sugerencia” y la redacción de la consigna.

## Antes de entregar

- Ensayar en el equipo donde se presentará; comprobar teclado, legibilidad y ventana de 1000 por 760 píxeles.
- Confirmar con el docente el alcance específico del parcial y la obligatoriedad de la API.
- Añadir sección y docente a la portada si la presentación del curso lo exige; no se proporcionaron esos datos.
- Conservar el informe, código y evidencias de la misma versión.
