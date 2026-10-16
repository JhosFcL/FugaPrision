# Guion de exposición del parcial

Duración sugerida: 6 a 8 minutos. El reparto es una propuesta para ensayar; todos deben comprender el código y ejecutar el juego.

## 1. Presentación y objetivo

**Jose Fernando Chavez Lozano, aproximadamente 1 minuto.**

“Nuestro proyecto es Fuga de la Prisión, temática 13. Es un videojuego 2D en Python y Pygame. El prisionero debe conseguir una llave y escapar evitando guardias y cámaras. La versión actual tiene tres zonas de sigilo y una arena final contra el Alcaide.”

Mostrar el primer nivel y sus controles. El prisionero empieza encerrado: acercarse a los barrotes y mantener E durante dos segundos para abrir la celda. El tercer mapa tiene galerías horizontales y la llave abre atajos para regresar. Señalar al prisionero verde, los guardias rojos, la cámara amarilla, la llave y la salida. Los pasos generan ruido: Ctrl reduce su alcance y correr lo aumenta. Un signo ? indica que un guardia investiga o busca y ! indica que persigue. Ver al jugador provoca persecución; la captura ocurre cuando lo alcanzan.

## 2. Clases y fundamentos POO

**Mickele Carlos Torres Velazco, aproximadamente 2 minutos.**

“El juego tiene 25 clases y todas aparecen en el UML. Cada caja presenta nombre, atributos y métodos. Los tipos de los atributos indican qué objetos guarda una clase: por ejemplo, Nivel guarda guardias de tipo Guardia y Combate guarda un jefe de tipo Alcaide.”

- **Asociación:** Personaje recibe y guarda su Nivel.
- **Agregación:** Nivel utiliza el Puntaje que Juego creó. El mismo objeto se conserva cuando cambia el nivel.
- **Composición:** Nivel crea sus personajes, cámaras, llave, salida y, en la arena, Combate. Prisionero crea HabilidadCarrera; Combate crea Alcaide y Proyectil.
- Mapa conserva las paredes y los caminos. SistemaRuido registra a los guardias y les avisa cuando pueden escuchar un paso. Ambas clases se crean dentro de Nivel y aparecen en el UML.
- **Herencia:** Prisionero y Guardia derivan de Personaje. Los cinco estados concretos derivan de EstadoJuego. PanelPuntaje deriva de ObservadorPuntaje.
- **Polimorfismo:** Nivel llama `personaje.update()` sin distinguir si es Prisionero o Guardia. Juego hace lo mismo con las operaciones de su estado actual.
- **Encapsulamiento:** Puntaje consulta y cambia `_valor` mediante métodos que validan el dato. El guion bajo indica uso interno por convención de Python.

Mostrar los rombos junto a las clases que contienen las partes y el triángulo apuntando a la clase base. Una flecha continua representa una referencia guardada y una discontinua representa un uso, como Camara al recibir Prisionero. Personaje y EstadoJuego son abstractas: cada clase hija debe implementar sus operaciones.

## 3. Patrones de diseño

**Richard Aaron Soriano Cordova, aproximadamente 1 minuto y medio.**

“State separa Jugando, Pausa, Derrota, Victoria y NivelCompletado. Juego delega la entrada y la actualización en su estado activo. Por eso la pausa congela movimiento, vigilancia, disparos y temporizadores. NivelCompletado espera Enter antes de cargar el siguiente mapa.”

Pausar con P y continuar con Escape. Mostrar `estados.py` y la delegación de `juego.py`.

“Observer comunica los cambios del puntaje. Puntaje notifica a PanelPuntaje, que hereda de ObservadorPuntaje. El panel recibe los puntos y Vista los muestra. Puntaje no necesita conocer el dibujo de la pantalla.”

Mostrar la suscripción en `juego.py` y los métodos de `puntuacion.py`.

## 4. Demostración y comprobaciones

**Piero Cemei Romero Meza, aproximadamente 2 minutos.**

1. Mover contra un muro y activar la carrera con Shift.
2. Correr cerca de una puerta para que el guardia investigue el ruido. Entrar en su mirada y mostrar la persecución; dejarse alcanzar y reintentar con R.
3. Recoger la llave: da 100 puntos. Escapar: suma 500 puntos.
4. Mostrar NivelCompletado y continuar con Enter. El puntaje se conserva.
5. Explicar la arena con sus capturas: Espacio apunta al jefe; IJKL fija la dirección del disparo. El Alcaide tiene tres capas de 72 puntos. Al romper una capa avisa del cambio y aumenta mucho la dificultad: coronas de 12, 40 y 84 proyectiles, mayor velocidad y menos espera entre ataques. La llave aparece solo tras agotar las tres capas.

La campaña completa da 3400 puntos: cuatro llaves, cuatro salidas y 1000 puntos por el jefe. Al perder, R repite el nivel y conserva solo los puntos de niveles anteriores; N empieza desde cero.

“Las 54 pruebas automáticas revisan paredes, ruido, investigación, persecución, captura, memoria de la última posición, puntaje, estados, transición de niveles y combate. La verificación completó los cuatro niveles con movimiento y disparos, sin desactivar enemigos, y generó catorce capturas.”

Para ensayar: usar las puertas entre los sectores, observar hacia dónde mira la patrulla y acercarse con Ctrl. Si un guardia persigue, usar la carrera para tomar distancia y rodear una pared o una cobertura para perder su visión. Ensayar el recorrido hasta la llave y la salida con teclado.

## Preguntas que deben poder responder

- **¿Cuántas clases y niveles hay?** 25 clases en `src` y cuatro niveles. Las clases de `tests` sirven para comprobar el juego y no son sus personajes o componentes.
- **¿Cómo se entera el guardia?** Escucha pasos que llegan por el mapa, ve al jugador o recibe una alerta de cámara. Al perderlo busca en la última posición conocida; no conoce su nueva posición oculta.
- **¿Qué pasa si la detección coincide con la salida?** La derrota tiene prioridad y no se concede el premio de salida.
- **¿Por qué Nivel recibe Puntaje?** Para conservar el mismo objeto al cambiar de nivel; eso permite mostrar la agregación.
- **¿Qué contiene Combate?** Un Alcaide y una lista de Proyectil creados por él; el UML muestra esos tipos y sus composiciones.
- **¿La ejecución automática equivale al ensayo con teclado?** Comprueba las reglas y genera las capturas, pero el equipo debe ensayar la demostración presencial.

## Antes de entregar

- Comprobar el juego y la legibilidad del UML en el equipo de exposición.
- Cada integrante debe poder explicar sus aportes reales y los conceptos POO del código.
- Subir los cambios revisados y mantener sincronizados código, Mermaid, imagen, explicación e informe.
